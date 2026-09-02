import httpx

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from database.repository_reader import RepositoryReader
from database.repository_writer import RepositoryWriter
from services.github_request import fetch_pull_requests, fetch_repo_info


router = APIRouter()

templates = Jinja2Templates(directory="templates")

reader = RepositoryReader()
writer = RepositoryWriter()


@router.get("/github")
async def get_github_repo():
    try:
        repo = await fetch_repo_info()

        # Save the repository and get its database ID
        repo_id = writer.upsert_repository(repo)

        # Load the repository from the database
        repository = reader.load_repository(repo_id)

        return {
            "repo_id": repository.pk,
            "repo_name": repository.repo_name,
            "owner": repository.owner,
            "description": repository.description,
            "url": repository.url,
            "created_at": repository.created_at,
            "updated_at": repository.updated_at,
        }

    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}"
        ) from exc


@router.get("/github/pull-requests")
async def get_github_pull_requests():
    try:
        repo = await fetch_repo_info()
        pull_requests = await fetch_pull_requests()

        # Save the repository and get its database ID
        repo_id = writer.upsert_repository(repo)

        # Save the pull requests
        writer.replace_pull_requests(
            repo_id,
            pull_requests
        )

        # Load the pull requests from the database
        pull_requests_from_db = reader.load_pull_requests(repo_id)

        return [
            {
                "pr_id": pr.id,
                "pr_number": pr.pr_number,
                "title": pr.title,
                "description": pr.description,
                "author": pr.author,
                "state": pr.state,
                "created_at": pr.created_at,
                "updated_at": pr.updated_at,
            }
            for pr in pull_requests_from_db
        ]

    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {exc}"
        ) from exc


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )