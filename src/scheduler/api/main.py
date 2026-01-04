"""FastAPI application."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from scheduler.api.routes import courses, auth
from scheduler.db import init_db

app = FastAPI(
    title="Graduate Course Scheduler",
    description="A lightweight course scheduling system for graduate students",
    version="1.1.0"
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(courses.router)


@app.get("/", include_in_schema=False)
def root():
    """Serve web UI."""
    return FileResponse("static/index.html")
