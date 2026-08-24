import httpx

from config import GITHUB_API_URL, GITHUB_TOKEN, REPO_NAME, REPO_OWNER
from models import Pull_Request, Repository


def _headers():
    headers = {
        "Accept": "application/vnd.github+json",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


async def _fetch_repo_data(client: httpx.AsyncClient) -> dict:
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}"

    response = await client.get(url, headers=_headers())
    response.raise_for_status()

    return response.json()


async def fetch_repo_info() -> Repository:
    async with httpx.AsyncClient() as client:
        repo = await _fetch_repo_data(client)

    return Repository(
        repo_id=repo["id"],
        github_id=repo["id"],
        name=repo["name"],
        owner=repo["owner"]["login"],
        description=repo.get("description"),
        url=repo["html_url"],
        created_at=repo["created_at"],
        updated_at=repo["updated_at"],
    )


async def _fetch_recent_pull_requests(client: httpx.AsyncClient) -> list[Pull_Request]:
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
            Pull_Request(
                pr_id=item["id"],
                branch_id=None,
                number=item["number"],
                title=item["title"],
                description=item.get("body"),
                author=item["user"]["login"],
                state=item["state"],
                created_at=item["created_at"],
                updated_at=item["updated_at"],
            )
        )

    return pull_requests


async def fetch_pull_requests() -> list[Pull_Request]:
    async with httpx.AsyncClient() as client:
        recent_pull_requests = await _fetch_recent_pull_requests(client)

    return recent_pull_requests
