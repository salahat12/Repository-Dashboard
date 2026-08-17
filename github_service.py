import httpx

from config import GITHUB_API_URL, GITHUB_TOKEN, REPO_NAME, REPO_OWNER
from models import IssueItem, IssuesSummary, RepoInfo


def _headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }


async def fetch_repo_info() -> RepoInfo:
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=_headers())

    repo = response.json()

    return RepoInfo(
        name=repo["name"],
        description=repo["description"],
        stars=repo["stargazers_count"],
        forks=repo["forks_count"],
        open_issues=repo["open_issues_count"],
        language=repo["language"],
    )


async def _search_count(client: httpx.AsyncClient, item_type: str, state: str) -> int:
    url = f"{GITHUB_API_URL}/search/issues"
    query = f"repo:{REPO_OWNER}/{REPO_NAME} type:{item_type} state:{state}"

    response = await client.get(
        url,
        headers=_headers(),
        params={"q": query, "per_page": 1},
    )

    result = response.json()

    return result["total_count"]


async def _fetch_recent_items(client: httpx.AsyncClient) -> list[tuple[str, IssueItem]]:
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues"

    params = {
        "per_page": 30,
        "state": "all",
        "sort": "created",
        "direction": "desc",
    }

    response = await client.get(url, headers=_headers(), params=params)
    data = response.json()

    items = []

    for item in data:
        cleaned_item = IssueItem(
            number=item["number"],
            title=item["title"],
            author=item["user"]["login"],
            state=item["state"],
            comments=item["comments"],
            labels=[label["name"] for label in item["labels"]],
            created_at=item["created_at"],
            updated_at=item["updated_at"],
            closed_at=item["closed_at"],
        )

        item_type = "pull_request" if "pull_request" in item else "issue"
        items.append((item_type, cleaned_item))

    return items


async def fetch_issues_summary() -> IssuesSummary:
    async with httpx.AsyncClient() as client:
        open_issues_count = await _search_count(client, "issue", "open")
        closed_issues_count = await _search_count(client, "issue", "closed")
        open_pull_requests_count = await _search_count(client, "pr", "open")
        closed_pull_requests_count = await _search_count(client, "pr", "closed")

        recent_items = await _fetch_recent_items(client)

    issues = [item for item_type, item in recent_items if item_type == "issue"]
    pull_requests = [item for item_type, item in recent_items if item_type == "pull_request"]

    return IssuesSummary(
        total_issues=open_issues_count + closed_issues_count,
        open_issues=open_issues_count,
        closed_issues=closed_issues_count,
        total_pull_requests=open_pull_requests_count + closed_pull_requests_count,
        open_pull_requests=open_pull_requests_count,
        closed_pull_requests=closed_pull_requests_count,
        issues=issues,
        pull_requests=pull_requests,
    )