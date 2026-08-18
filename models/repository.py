from typing import Optional

from pydantic import BaseModel


class Repository(BaseModel):
	name: str
	description: Optional[str]
	stars: int
	forks: int
	open_issues: int
	language: Optional[str]
