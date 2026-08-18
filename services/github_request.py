import httpx

from config import GITHUB_API_URL, GITHUB_TOKEN, REPO_NAME, REPO_OWNER
from models import Item, Issues, PR, Repository


def _headers():
    headers = {
        "Accept": "application/vnd.github+json",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


async def fetch_repo_info() -> Repository:
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=_headers())
        response.raise_for_status()

    repo = response.json()

    return Repository(
        name=repo["name"],
        description=repo["description"],
        stars=repo["stargazers_count"],
        forks=repo["forks_count"],
        open_issues=repo["open_issues_count"],
        language=repo["language"],
    )


async def _search_count(client: httpx.AsyncClient, item_type: str, state: str) -> int:
    url = f"{GITHUB_API_URL}/search/issues"
    query = f"repo:{REPO_OWNER}/{REPO_NAME} is:{item_type} is:{state}"

    response = await client.get(
        url,
        headers=_headers(),
        params={"q": query, "per_page": 1},
    )
    response.raise_for_status()

    result = response.json()

    if "total_count" not in result:
        raise RuntimeError(f"GitHub search failed: {result}")

    return result["total_count"]


async def _fetch_recent_issues(client: httpx.AsyncClient) -> list[Item]:
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues"

    params = {
        "per_page": 30,
        "state": "all",
        "sort": "created",
        "direction": "desc",
    }

    response = await client.get(url, headers=_headers(), params=params)
    response.raise_for_status()
    data = response.json()

    issues = []

    for item in data:
        if "pull_request" in item:
            continue

        issues.append(
            Item(
                number=item["number"],
                title=item["title"],
                author=item["user"]["login"],
                state=item["state"],
                comments=item["comments"],
                labels=[label["name"] for label in item.get("labels", [])],
                created_at=item["created_at"],
                updated_at=item["updated_at"],
                closed_at=item["closed_at"],
            )
        )

    return issues


async def fetch_issues() -> Issues:
    async with httpx.AsyncClient() as client:
        open_issues_count = await _search_count(client, "issue", "open")
        closed_issues_count = await _search_count(client, "issue", "closed")
        recent_issues = await _fetch_recent_issues(client)

    return Issues(
        total_issues=open_issues_count + closed_issues_count,
        open_issues=open_issues_count,
        closed_issues=closed_issues_count,
        issues=recent_issues,
    )


async def _fetch_recent_pull_requests(client: httpx.AsyncClient) -> list[Item]:
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/pulls"

    params = {
        "per_page": 30,
        "state": "all",
        "sort": "created",
        "direction": "desc",
    }

    response = await client.get(url, headers=_headers(), params=params)
    response.raise_for_status()
    data = response.json()

    pull_requests = []

    for item in data:
        pull_requests.append(
            Item(
                number=item["number"],
                title=item["title"],
                author=item["user"]["login"],
                state=item["state"],
                comments=item["comments"],
                labels=[label["name"] for label in item.get("labels", [])],
                created_at=item["created_at"],
                updated_at=item["updated_at"],
                closed_at=item["closed_at"],
            )
        )

    return pull_requests


async def fetch_pull_requests() -> PR:
    async with httpx.AsyncClient() as client:
        open_pull_requests_count = await _search_count(client, "pr", "open")
        closed_pull_requests_count = await _search_count(client, "pr", "closed")
        recent_pull_requests = await _fetch_recent_pull_requests(client)

    return PR(
        total_pull_requests=open_pull_requests_count + closed_pull_requests_count,
        open_pull_requests=open_pull_requests_count,
        closed_pull_requests=closed_pull_requests_count,
        pull_requests=recent_pull_requests,
    )
