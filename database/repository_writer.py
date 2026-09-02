"""
RepositoryWriter — writes repository.py, branch, and pull-request data
into the PostgreSQL database via SQLAlchemy ORM.

Every model follows the same FK convention: each entity has a
``<parent_table>_id`` column that points to the parent entity's ``id``
primary key. The root entity (``Repository``) has no parent, so it has
no such column.

Table relationships (all via ``<parent>_id`` → parent.id):

    Repository.id  (root, no parent)
      └─ Branch.repository_id  → Repository.id        (one repo has many branches)
           └─ PullRequest.branch_id  → Branch.id       (one branch has many PRs)
                └─ Commit.pull_request_id  → PullRequest.id  (one PR has many commits)
      └─ Contributor.repository_id  → Repository.id    (one repo has many contributors)

Flow for a typical /github/pull-requests request:

    1. github_request.py fetches live data from the GitHub API and returns
       a list of PullRequest ORM objects (each with an embedded Branch).

    2. RepositoryWriter.upsert_repository() inserts or updates the
       Repository row and returns its internal id.

    3. RepositoryWriter.replace_pull_requests() atomically replaces all
       branches + PRs + commits for that repository.py:
       - Delete existing commits, PRs, branches (inside one transaction)
       - Insert the new batch one by one via _insert_one_pull_request()

    4. RepositoryReader reads the data back and returns it as a JSON-safe
       dict to the controller.
"""

from sqlalchemy import delete, select

from database.engine import session_scope
from models import Branch, Commit, PullRequest, Repository


class RepositoryWriter:
    """Write repository.py and pull-request data into the PostgreSQL database.

    Uses the ORM models from ``models`` where every foreign key is named
    ``<parent_table>_id`` and points to the parent entity's ``id`` column.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def upsert_repository(self, repo: Repository) -> int:
        """Insert *repo* or update its description/URL/timestamp if it exists.

        Returns the internal auto-increment ``id`` of the ``Repository`` row.
        """
        with session_scope() as session:
            # Look for an existing row with the same repo_name + owner.
            existing = session.execute(
                select(Repository)
                .where(
                    Repository.repo_name == repo.repo_name,
                    Repository.owner == repo.owner,
                )
            ).scalar_one_or_none()

            if existing is not None:
                # Update the existing row in place.
                existing.description = repo.description
                existing.url = repo.url
                existing.updated_at = repo.updated_at
                session.flush()
                return existing.id

            # No existing row — insert a fresh one.
            repository = Repository(
                repo_name=repo.repo_name,
                owner=repo.owner,
                description=repo.description,
                url=repo.url,
                created_at=repo.created_at,
                updated_at=repo.updated_at,
            )
            session.add(repository)
            session.flush()
            return repository.id

    def replace_pull_requests(
        self,
        repo_id: int,
        pull_requests: list[PullRequest],
    ) -> None:
        """Atomically replace every pull request (and its branches/commits)
        for the given *repo_id*.

        Deletes existing rows inside a transaction so a partial failure
        rolls everything back cleanly.
        """
        with session_scope() as session:
            # --- Gather existing branch primary keys for this repo ---
            branch_ids = [
                row[0]
                for row in session.execute(
                    select(Branch.id).where(Branch.repository_id == repo_id)
                ).all()
            ]

            if branch_ids:
                # Find pull request primary keys linked to those branches.
                pr_ids = [
                    row[0]
                    for row in session.execute(
                        select(PullRequest.id).where(
                            PullRequest.branch_id.in_(branch_ids)
                        )
                    ).all()
                ]

                # Delete commits first (they reference pull requests).
                if pr_ids:
                    session.execute(
                        delete(Commit).where(Commit.pull_request_id.in_(pr_ids))
                    )

                # Delete pull requests.
                session.execute(
                    delete(PullRequest).where(
                        PullRequest.branch_id.in_(branch_ids)
                    )
                )

                # Delete branches.
                session.execute(
                    delete(Branch).where(Branch.repository_id == repo_id)
                )

            # --- Insert the fresh batch ---
            for pr in pull_requests:
                self._insert_one_pull_request(session, repo_id, pr)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _insert_one_pull_request(
        self,
        session,
        repo_id: int,
        pull_request: PullRequest,
    ) -> None:
        """Persist a single ``PullRequest`` (and its branch if new)."""
        branch_name = pull_request.branch.branch_name

        # Look up or create the branch row.
        branch = session.execute(
            select(Branch).where(
                Branch.repository_id == repo_id,
                Branch.branch_name == branch_name,
            )
        ).scalar_one_or_none()

        if branch is None:
            branch = Branch(
                repository_id=repo_id,
                branch_name=branch_name,
                is_default=False,
            )
            session.add(branch)
            session.flush()

        pull_request_row = PullRequest(
            branch_id=branch.id,
            pr_number=pull_request.pr_number,
            title=pull_request.title,
            description=pull_request.description,
            state=pull_request.state,
            author=pull_request.author,
            created_at=pull_request.created_at,
            updated_at=pull_request.updated_at,
        )
        session.add(pull_request_row)