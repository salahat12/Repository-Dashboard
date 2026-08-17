from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from github_service import fetch_issues_summary, fetch_repo_info
from models import IssuesSummary, RepoInfo

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/github", response_model=RepoInfo)
async def get_github_repo():
	repo = await fetch_repo_info()
	return repo


@app.get("/github/issues", response_model=IssuesSummary)
async def get_github_issues():
	return await fetch_issues_summary()


@app.get("/dashboard")
async def dashboard(request: Request):
	return templates.TemplateResponse(
		request=request,
		name="dashboard.html"
	)