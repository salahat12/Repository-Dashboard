import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError

from models import PullRequest, Repository
from database.repository_reader import RepositoryReader
from database.repository_writer import RepositoryWriter
from services.github_request import fetch_pull_requests, fetch_repo_info

router = APIRouter()
templates = Jinja2Templates(directory="templates")

reader = RepositoryReader()
writer = RepositoryWriter()


@router.get("/github", response_model=Repository)
async def get_github_repo():
    try:
        repo = await fetch_repo_info()
        writer.upsert_repository(repo)
        return reader.load_repository(repo.repo_id)
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except (LookupError, SQLAlchemyError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/github/pull-requests", response_model=list[PullRequest])
async def get_github_pull_requests():
    try:
        repo = await fetch_repo_info()
        pull_requests = await fetch_pull_requests()
        writer.upsert_repository(repo)
        writer.replace_pull_requests(repo.repo_id, pull_requests)
        return reader.load_pull_requests(repo.repo_id)
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except (LookupError, SQLAlchemyError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )
