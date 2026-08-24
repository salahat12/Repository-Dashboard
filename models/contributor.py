from pydantic import BaseModel


class Contributor(BaseModel):
    contributor_id: int
    repo_id: int
    github_id: int
    username: str
    permission: str
