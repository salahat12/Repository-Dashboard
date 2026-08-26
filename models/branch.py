from pydantic import BaseModel


class Branch(BaseModel):
    name: str
    repo_id: int
    is_default: bool
