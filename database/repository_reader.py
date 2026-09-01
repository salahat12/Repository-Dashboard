from sqlalchemy import select

from database.engine import session_scope
from models import Branch, PullRequest, Repository


class RepositoryReader:

    def load_repository(self, repo_id: int) -> Repository:
        with session_scope() as session:
            repo = session.get(Repository, repo_id)
            if repo is None:
                raise LookupError(f"Repository {repo_id} was not found in the database.")
            return repo

    def load_pull_requests(self, repo_id: int) -> list[PullRequest]:
        with session_scope() as session:
            stmt = (
                select(PullRequest)
                .join(Branch, Branch.name == PullRequest.branch_name)
                .where(Branch.repo_id == repo_id)
                .order_by(PullRequest.created_at.desc(), PullRequest.updated_at.desc())
            )
            return list(session.execute(stmt).scalars().all())