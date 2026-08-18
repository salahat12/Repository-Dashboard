from typing import List, Optional

from pydantic import BaseModel


class IssueItem(BaseModel):
	number: int
	title: str
	author: str
	state: str
	type: str  # "issue" or "pull_request"
	comments: int
	labels: List[str]
	created_at: str
	updated_at: str
	closed_at: Optional[str]
