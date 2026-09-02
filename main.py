"""
Repository Dashboard — FastAPI Application Entry Point
=======================================================

This is the top-level glue that holds everything together. It wires up the
web framework, serves the frontend, and registers the API routes.

How a single page load flows through this application:

1. BROWSER opens http://localhost:8000/dashboard
   The FastAPI app (created on line 6) receives the request.

2. ROUTING — the request hits the /dashboard endpoint, which is defined in
   controllers/repository_controller.py and registered here on line 9 via
   app.include_router(). That endpoint:
     a. Calls services/github_request.py to fetch fresh data from the GitHub
        REST API (repo info + pull requests for apache/superset).
     b. Passes that data to database/repository_writer.py which saves it into
        PostgreSQL using SQLAlchemy ORM models (models/__init__.py).
     c. Reads the data back out via database/repository_reader.py.
     d. Renders templates/index.html (Jinja2) and returns the HTML page.

3. FRONTEND — the browser receives index.html which already includes
   static/script.js and static/style.css (served from the /static mount on
   line 8). The JS runs fetchData() on page load, which calls the two API
   endpoints (/github and /github/pull-requests) again to get the latest
   data, then renders the stats cards, charts (Chart.js), and PR table.

Key files behind each layer:
  - Routers/endpoints   : controllers/repository_controller.py
  - GitHub API calls    : services/github_request.py
  - Database writes     : database/repository_writer.py
  - Database reads      : database/repository_reader.py
  - ORM models          : models/__init__.py  (Repository, Branch, PullRequest,
                                Commit, Contributor, Push)
  - DB connection       : database/engine.py  (SQLAlchemy engine, session factory,
                                ensure_schema() to auto-create tables)
  - HTML template       : templates/index.html
  - Frontend JS         : static/script.js
  - Frontend CSS        : static/style.css

Running the server:
  .venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
  Then open http://localhost:8000/dashboard
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from controllers.repository_controller import router as repository_router

# Create the FastAPI application instance.
# "app" is the convention FastAPI/VICE use; uvicorn discovers it by name
# when you run:  uvicorn main:app
app = FastAPI()

# Mount the /static directory so that browsers can load CSS, JS, images, etc.
# Visiting /static/script.js serves static/script.js from disk.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register all API routes from the repository.py controller.
# This adds the following endpoints to the app:
#   GET /github              → repository.py info (fetched from GitHub + DB)
#   GET /github/pull-requests → list of pull requests
#   GET /dashboard           → HTML dashboard page
app.include_router(repository_router)
