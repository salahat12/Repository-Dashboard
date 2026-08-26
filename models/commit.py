from datetime import datetime

from pydantic import BaseModel


class Commit(BaseModel):
    sha: str
    pr_id: int
    message: str
    author: str
    committed_at: datetime
