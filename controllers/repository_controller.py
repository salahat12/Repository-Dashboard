import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models import Pull_Request, Repository
from database.repository_store import (
    load_pull_requests,
    load_repository,
    replace_pull_requests,
    upsert_repository,
)
from services.github_request import fetch_pull_requests, fetch_repo_info
import psycopg2

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/github", response_model=Repository)
async def get_github_repo():
    try:
        repo = await fetch_repo_info()
        upsert_repository(repo)
        return load_repository(repo.repo_id)
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except (LookupError, psycopg2.Error) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/github/pull-requests", response_model=list[Pull_Request])
async def get_github_pull_requests():
    try:
        repo = await fetch_repo_info()
        pull_requests = await fetch_pull_requests()
        upsert_repository(repo)
        replace_pull_requests(repo.repo_id, pull_requests)
        return load_pull_requests(repo.repo_id)
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except (LookupError, psycopg2.Error) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )
