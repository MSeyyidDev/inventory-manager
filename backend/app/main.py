"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.routers import assignments, devices, employees, locations, stats


def create_app() -> FastAPI:
    """Application factory."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "REST API for managing IT assets, employees, locations and device assignments.\n\n"
            "Built with FastAPI, SQLAlchemy 2.0 and Pydantic v2."
        ),
        openapi_tags=[
            {"name": "devices", "description": "Hardware assets and their lifecycle."},
            {"name": "employees", "description": "Staff members that may receive assigned devices."},
            {"name": "locations", "description": "Physical offices and remote sites."},
            {"name": "assignments", "description": "Device-to-employee assignment history."},
            {"name": "stats", "description": "Dashboard aggregates and KPIs."},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(devices.router)
    app.include_router(employees.router)
    app.include_router(locations.router)
    app.include_router(assignments.router)
    app.include_router(stats.router)

    @app.get("/health", tags=["stats"], summary="Liveness probe")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.on_event("startup")
    def _startup() -> None:
        init_db()

    return app


app = create_app()
