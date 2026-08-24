import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models import Pull_Request, Repository
from services.github_request import fetch_pull_requests, fetch_repo_info

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/github", response_model=Repository)
async def get_github_repo():
    try:
        return await fetch_repo_info()
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/github/pull-requests", response_model=list[Pull_Request])
async def get_github_pull_requests():
    try:
        return await fetch_pull_requests()
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )
