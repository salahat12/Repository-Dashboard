from sqlalchemy.dialects.postgresql import insert as pg_insert

from database.engine import session_scope
from models import Branch, PullRequest, Repository


class RepositoryWriter:
    """All write paths for repository data. Kept separate from RepositoryReader
    so callers that only ever read never import/instantiate a writer."""

    def upsert_repository(self, repo: Repository) -> None:
        values = {
            "repo_id": repo.repo_id,
            "github_id": repo.github_id,
            "name": repo.name,
            "owner": repo.owner,
            "description": repo.description,
            "url": repo.url,
            "created_at": repo.created_at,
            "updated_at": repo.updated_at,
        }
        stmt = pg_insert(Repository).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Repository.repo_id],
            set_={key: value for key, value in values.items() if key != "repo_id"},
        )
        with session_scope() as session:
            session.execute(stmt)

    def replace_pull_requests(self, repo_id: int, pull_requests: list[PullRequest]) -> None:
        """Mirrors the original delete-then-reinsert semantics: every branch
        belonging to repo_id is dropped (cascading to its pull requests and
        commits via ON DELETE CASCADE) and rebuilt from the given list."""
        with session_scope() as session:
            session.query(Branch).filter(Branch.repo_id == repo_id).delete(
                synchronize_session=False
            )

            if len(pull_requests) > 1000:
                self._upsert_pull_requests_loop(session, repo_id, pull_requests)
            else:
                self._upsert_pull_requests_recursive(session, repo_id, pull_requests)

    def _upsert_pull_requests_loop(
            self, session, repo_id: int, pull_requests: list[PullRequest]
    ) -> None:
        for pull_request in pull_requests:
            self._upsert_one_pull_request(session, repo_id, pull_request)

    def _upsert_pull_requests_recursive(
            self, session, repo_id: int, pull_requests: list[PullRequest]
    ) -> None:
        # Base case: nothing left to insert.
        if not pull_requests:
            return

        pull_request, *remaining = pull_requests
        self._upsert_one_pull_request(session, repo_id, pull_request)

        # Recurse on the rest of the list.
        self._upsert_pull_requests_recursive(session, repo_id, remaining)

    def _upsert_one_pull_request(self, session, repo_id: int, pull_request: PullRequest) -> None:
        branch_stmt = pg_insert(Branch).values(
            name=pull_request.branch_name, repo_id=repo_id, is_default=False
        )
        branch_stmt = branch_stmt.on_conflict_do_update(
            index_elements=[Branch.name],
            set_={"repo_id": repo_id, "is_default": False},
        )
        session.execute(branch_stmt)

        pr_values = {
            "pr_id": pull_request.pr_id,
            "branch_name": pull_request.branch_name,
            "number": pull_request.number,
            "title": pull_request.title,
            "description": pull_request.description,
            "state": pull_request.state,
            "author": pull_request.author,
            "created_at": pull_request.created_at,
            "updated_at": pull_request.updated_at,
        }
        pr_stmt = pg_insert(PullRequest).values(**pr_values)
        pr_stmt = pr_stmt.on_conflict_do_update(
            index_elements=[PullRequest.pr_id],
            set_={key: value for key, value in pr_values.items() if key != "pr_id"},
        )
        session.execute(pr_stmt)