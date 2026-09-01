from sqlalchemy import select

from database.engine import session_scope
from models import Branch, PullRequest, Repository


class RepositoryReader:

    def load_repository(self, repo_id: int) -> Repository:

        with session_scope() as session:

            repository = session.get(
                Repository,
                repo_id
            )

            if repository is None:
                raise LookupError(
                    f"Repository {repo_id} was not found in the database."
                )

            return repository

    def load_pull_requests(
        self,
        repo_id: int
    ) -> list[PullRequest]:

        with session_scope() as session:

            stmt = (
                select(PullRequest)
                .join(
                    Branch,
                    Branch.branch_id == PullRequest.branch_id
                )
                .where(
                    Branch.repo_id == repo_id
                )
                .order_by(
                    PullRequest.created_at.desc(),
                    PullRequest.updated_at.desc()
                )
            )

            return list(
                session.execute(stmt).scalars().all()
            )