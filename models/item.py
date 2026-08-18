from typing import List, Optional

from pydantic import BaseModel


class Item(BaseModel):
    number: int
    title: str
    author: str
    state: str
    comments: int
    labels: List[str]
    created_at: str
    updated_at: str
    closed_at: Optional[str] = None
