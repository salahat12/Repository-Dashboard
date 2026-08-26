from __future__ import annotations

from pathlib import Path
from threading import Lock

from database.connection import get_connection
from models import Pull_Request, Repository

_schema_ready = False
_schema_lock = Lock()


def _ensure_schema() -> None:
    global _schema_ready

    if _schema_ready:
        return

    with _schema_lock:
        if _schema_ready:
            return

        connection = get_connection()
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT to_regclass('public.repository')")
                    schema_exists = cursor.fetchone()[0] is not None

                    if not schema_exists:
                        schema_sql = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
                        cursor.execute(schema_sql)

            _schema_ready = True
        finally:
            connection.close()


def upsert_repository(repo: Repository) -> None:
    _ensure_schema()

    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO repository (
                        repo_id,
                        github_id,
                        name,
                        owner,
                        description,
                        url,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (repo_id) DO UPDATE SET
                        github_id = EXCLUDED.github_id,
                        name = EXCLUDED.name,
                        owner = EXCLUDED.owner,
                        description = EXCLUDED.description,
                        url = EXCLUDED.url,
                        created_at = EXCLUDED.created_at,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        repo.repo_id,
                        repo.github_id,
                        repo.name,
                        repo.owner,
                        repo.description,
                        repo.url,
                        repo.created_at,
                        repo.updated_at,
                    ),
                )
    finally:
        connection.close()


def replace_pull_requests(repo_id: int, pull_requests: list[Pull_Request]) -> None:
    _ensure_schema()

    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM branch WHERE repo_id = %s", (repo_id,))

                for pull_request in pull_requests:
                    cursor.execute(
                        """
                        INSERT INTO branch (name, repo_id, is_default)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (name) DO UPDATE SET
                            repo_id = EXCLUDED.repo_id,
                            is_default = EXCLUDED.is_default
                        """,
                        (pull_request.branch_name, repo_id, False),
                    )
                    cursor.execute(
                        """
                        INSERT INTO pull_request (
                            pr_id,
                            branch_name,
                            number,
                            title,
                            description,
                            state,
                            author,
                            created_at,
                            updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (pr_id) DO UPDATE SET
                            branch_name = EXCLUDED.branch_name,
                            number = EXCLUDED.number,
                            title = EXCLUDED.title,
                            description = EXCLUDED.description,
                            state = EXCLUDED.state,
                            author = EXCLUDED.author,
                            created_at = EXCLUDED.created_at,
                            updated_at = EXCLUDED.updated_at
                        """,
                        (
                            pull_request.pr_id,
                            pull_request.branch_name,
                            pull_request.number,
                            pull_request.title,
                            pull_request.description,
                            pull_request.state,
                            pull_request.author,
                            pull_request.created_at,
                            pull_request.updated_at,
                        ),
                    )
    finally:
        connection.close()


def load_repository(repo_id: int) -> Repository:
    _ensure_schema()

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT repo_id, github_id, name, owner, description, url, created_at, updated_at
                FROM repository
                WHERE repo_id = %s
                """,
                (repo_id,),
            )
            row = cursor.fetchone()

        if row is None:
            raise LookupError(f"Repository {repo_id} was not found in the database.")

        return Repository(
            repo_id=row[0],
            github_id=row[1],
            name=row[2],
            owner=row[3],
            description=row[4],
            url=row[5],
            created_at=row[6],
            updated_at=row[7],
        )
    finally:
        connection.close()


def load_pull_requests(repo_id: int) -> list[Pull_Request]:
    _ensure_schema()

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    pr.pr_id,
                    pr.branch_name,
                    pr.number,
                    pr.title,
                    pr.description,
                    pr.state,
                    pr.author,
                    pr.created_at,
                    pr.updated_at
                FROM pull_request AS pr
                INNER JOIN branch AS b
                    ON b.name = pr.branch_name
                WHERE b.repo_id = %s
                ORDER BY pr.created_at DESC, pr.updated_at DESC
                """,
                (repo_id,),
            )
            rows = cursor.fetchall()

        return [
            Pull_Request(
                pr_id=row[0],
                branch_name=row[1],
                number=row[2],
                title=row[3],
                description=row[4],
                state=row[5],
                author=row[6],
                created_at=row[7],
                updated_at=row[8],
            )
            for row in rows
        ]
    finally:
        connection.close()
