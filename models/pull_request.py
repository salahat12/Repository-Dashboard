from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Pull_Request(BaseModel):
    pr_id: int
    repo_id: int
    number: int
    title: str
    description: Optional[str] = None
    state: str
    author: str
    created_at: datetime
    updated_at: datetime
