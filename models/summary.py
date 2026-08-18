from typing import List, Optional

from pydantic import BaseModel

from models.issue_item import IssueItem


class IssuesSummary(BaseModel):
    total_issues: int
    open_issues: int
    closed_issues: int
    total_pull_requests: int
    open_pull_requests: int
    closed_pull_requests: int
    recent_activity_count: int
    recent_comments_count: int
    latest_activity_at: Optional[str]
    issues: List[IssueItem]
    pull_requests: List[IssueItem]
