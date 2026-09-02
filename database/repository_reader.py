"""
RepositoryReader — reads repository.py and pull-request data back from the
PostgreSQL database via SQLAlchemy ORM.

This is the read side of the repository.py data access layer.  Callers use
it after the writer has saved fresh data, so they get a consistent
view of what is actually in the database (not just what was handed to
the writer).

Relationships used (all via ``<parent>_id`` → parent.id):

    Repository.id  (root)
      └─ Branch.repository_id  → Repository.id
           └─ PullRequest.branch_id  → Branch.id

``load_pull_requests`` joins through Branch to find every PR whose
branch belongs to the given repository.py.
"""

from sqlalchemy import select

from database.engine import session_scope
from models import Branch, PullRequest, Repository


class RepositoryReader:
    """Read repository.py and pull-request data from the database."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_repository(self, repo_id: int) -> Repository:
        """Return the ``Repository`` ORM object with the given *repo_id*.

        *repo_id* is the internal auto-increment ``id`` (not the GitHub
        numeric ID).  Raises ``LookupError`` if no such row exists.
        """
        with session_scope() as session:
            repository = session.get(Repository, repo_id)
            if repository is None:
                raise LookupError(
                    f"Repository {repo_id} was not found in the database."
                )
            return repository

    def load_pull_requests(self, repo_id: int) -> list[PullRequest]:
        """Return every ``PullRequest`` for the repository.py identified by
        *repo_id*, ordered newest-first by creation date.

        The query joins through ``Branch`` because pull requests are
        linked to branches, and branches carry the FK back to the
        repository.py (``Branch.repository_id`` → ``Repository.id``).
        """
        with session_scope() as session:
            # Join through Branch → PullRequest.
            # FK naming: Branch.repository_id → Repository.id, PullRequest.branch_id → Branch.id
            stmt = (
                select(PullRequest)
                .join(
                    Branch,
                    Branch.id == PullRequest.branch_id,
                )
                .where(Branch.repository_id == repo_id)
                .order_by(
                    PullRequest.created_at.desc(),
                    PullRequest.updated_at.desc(),
                )
            )
            return list(session.execute(stmt).scalars().all())