from datetime import datetime

from pydantic import BaseModel


class Commit(BaseModel):
    commit_id: int
    branch_id: int
    sha: str
    message: str
    author: str
    committed_at: datetime
