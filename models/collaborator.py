from pydantic import BaseModel


class Collaborator(BaseModel):
    collaborator_id: int
    repo_id: int
    github_id: int
    username: str
    permission: str
