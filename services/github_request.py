"""
GitHub API service — fetches repository metadata and recent pull requests
from the GitHub REST API and returns them as SQLAlchemy ORM objects.

This module is the data-fetching layer.  It knows nothing about the
database; it only talks to GitHub over HTTP (via ``httpx``) and
constructs ORM model instances that the writer will later persist.

Endpoints used:
  * GET /repos/{owner}/{repo}         → repo info (name, description, URL,
                                         owner login, timestamps)
  * GET /repos/{owner}/{repo}/pulls  → list of open/closed pull requests
                                         (up to 30, sorted by creation date)

Authentication
-------------
If ``GITHUB_TOKEN`` is set (in ``.env`` or environment), requests include
an ``Authorization: Bearer ...`` header.  Without a token, the API still
works for public repositories but is rate-limited to 60 requests/hour.
With a token, the limit is 5000/hour.

Return types
------------
Both async functions return SQLAlchemy ORM objects from ``models``:

* ``fetch_repo_info()`` → ``Repository``
* ``fetch_pull_requests()`` → ``list[PullRequest]``

Each ``PullRequest`` carries an embedded ``Branch(branch_name=...)``,
which the writer uses to look up or create the corresponding branch row.
"""

import httpx
from models import Branch, PullRequest, Repository
from config import GITHUB_API_URL, GITHUB_TOKEN, REPO_NAME, REPO_OWNER


def _headers() -> dict:
    """Build the HTTP headers for GitHub API requests.

    Returns ``Authorization: Bearer ...`` when GITHUB_TOKEN is set,
    otherwise just the Accept header for the GitHub JSON media type.
    """
    headers = {
        "Accept": "application/vnd.github+json",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


async def _fetch_repo_data(client: httpx.AsyncClient) -> dict:
    """Fetch raw JSON for the repository from the GitHub API."""
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}"
    response = await client.get(url, headers=_headers())
    response.raise_for_status()
    return response.json()


async def fetch_repo_info() -> Repository:
    """Fetch repository metadata from GitHub and return a ``Repository`` ORM
    object.

    Calls ``GET /repos/{owner}/{repo}`` and maps the response fields
    onto a ``Repository`` instance.  The caller (controller) is
    responsible for persisting this to the database.
    """
    async with httpx.AsyncClient() as client:
        repo = await _fetch_repo_data(client)

    return Repository(
        repo_name=repo["name"],
        owner=repo["owner"]["login"],
        description=repo.get("description"),
        url=repo["html_url"],
        created_at=repo["created_at"],
        updated_at=repo["updated_at"],
    )


async def _fetch_recent_pull_requests(
    client: httpx.AsyncClient,
) -> list[PullRequest]:
    """Fetch up to 30 recent pull requests from the GitHub API.

    Uses the following query parameters:
      * per_page=30   — limit the response
      * state=all     — include both open and closed PRs
      * sort=created  — sort by creation date
      * direction=desc — newest first
    """
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
            PullRequest(
                branch=Branch(branch_name=item["head"]["ref"]),
                pr_number=item["number"],
                title=item["title"],
                description=item.get("body"),
                author=item["user"]["login"],
                state=item["state"],
                created_at=item["created_at"],
                updated_at=item["updated_at"],
            )
        )

    return pull_requests


async def fetch_pull_requests() -> list[PullRequest]:
    """Fetch recent pull requests from GitHub and return them as ORM objects.

    Calls ``GET /repos/{owner}/{repo}/pulls`` and constructs a list of
    ``PullRequest`` objects, each with an embedded ``Branch``.  The
    caller (controller) persists these via ``RepositoryWriter``.
    """
    async with httpx.AsyncClient() as client:
        recent_pull_requests = await _fetch_recent_pull_requests(client)

    return recent_pull_requests
