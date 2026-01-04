"""FastAPI application."""

from fastapi import FastAPI

from scheduler.api.routes import courses
from scheduler.db import init_db

app = FastAPI(
    title="Graduate Course Scheduler",
    description="A lightweight course scheduling system for graduate students",
    version="0.2.0"
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Include routers
app.include_router(courses.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Graduate Course Scheduler API",
        "docs": "/docs",
        "version": "0.2.0"
    }
