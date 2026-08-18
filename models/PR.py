from typing import List

from pydantic import BaseModel

from models.item import Item


class PR(BaseModel):
    total_pull_requests: int
    open_pull_requests: int
    closed_pull_requests: int
    pull_requests: List[Item]
