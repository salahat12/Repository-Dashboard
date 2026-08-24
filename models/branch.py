from pydantic import BaseModel


class Branch(BaseModel):
    branch_id: int
    repo_id: int
    name: str
    is_default: bool
