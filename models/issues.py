from typing import List

from pydantic import BaseModel

from models.item import Item


class Issues(BaseModel):
    total_issues: int
    open_issues: int
    closed_issues: int
    issues: List[Item]
