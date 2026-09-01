from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from controllers.repository_controller import router as repository_router
from database.connection import init_db

app = FastAPI()

# Initialize database on startup
init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(repository_router)
