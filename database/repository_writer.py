from sqlalchemy import select

from database.engine import session_scope
from models import Branch, Commit, PullRequest, Repository


class RepositoryWriter:

    def upsert_repository(self, repo: Repository) -> int:


        with session_scope() as session:

            existing = session.execute(
                select(Repository)
                .where(
                    Repository.repo_name == repo.repo_name,
                    Repository.owner == repo.owner,
                )
            ).scalar_one_or_none()

            if existing is not None:

                existing.description = repo.description
                existing.url = repo.url
                existing.updated_at = repo.updated_at

                session.flush()

                return existing.repo_id

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

            return repository.repo_id

    def replace_pull_requests(
        self,
        repo_id: int,
        pull_requests: list[PullRequest],
    ) -> None:

        with session_scope() as session:


            branch_ids = [
                row[0]
                for row in session.query(Branch.id)
                .filter(
                    Branch.repo_id == repo_id
                )
                .all()
            ]


            if branch_ids:

                # Find pull request IDs
                pr_ids = [
                    row[0]
                    for row in session.query(PullRequest.id)
                    .filter(
                        PullRequest.branch_id.in_(branch_ids)
                    )
                    .all()
                ]

                # Delete commits first
                if pr_ids:
                    session.query(Commit).filter(
                        Commit.pr_id.in_(pr_ids)
                    ).delete(
                        synchronize_session=False
                    )

                # Delete pull requests
                session.query(PullRequest).filter(
                    PullRequest.branch_id.in_(branch_ids)
                ).delete(
                    synchronize_session=False
                )

                # Delete branches
                session.query(Branch).filter(
                    Branch.repo_id == repo_id
                ).delete(
                    synchronize_session=False
                )



            for pull_request in pull_requests:

                self._insert_one_pull_request(
                    session,
                    repo_id,
                    pull_request,
                )

    def _insert_one_pull_request(
        self,
        session,
        repo_id: int,
        pull_request: PullRequest,
    ) -> None:


        branch_name = pull_request.branch.branch_name



        branch = session.execute(
            select(Branch)
            .where(
                Branch.repo_id == repo_id,
                Branch.branch_name == branch_name,
            )
        ).scalar_one_or_none()



        if branch is None:

            branch = Branch(
                repo_id=repo_id,
                branch_name=branch_name,
                is_default=False,
            )

            session.add(branch)
            session.flush()


        pull_request_row = PullRequest(
            branch_id=pull_request.branch_id,
            pr_number=pull_request.pr_number,
            title=pull_request.title,
            description=pull_request.description,
            state=pull_request.state,
            author=pull_request.author,
            created_at=pull_request.created_at,
            updated_at=pull_request.updated_at,
        )

        session.add(pull_request_row)