"""Application entrypoint: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`."""

from fastapi import FastAPI

from app.api import health


def create_app() -> FastAPI:
    app = FastAPI(title="Restaurant Booking System")
    app.include_router(health.router)
    return app


app = create_app()
