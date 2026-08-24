from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Repository(BaseModel):
    repo_id: int
    github_id: int
    name: str
    owner: str
    description: Optional[str] = None
    url: str
    created_at: datetime
    updated_at: datetime
