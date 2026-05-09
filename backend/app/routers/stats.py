"""Stats / dashboard endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.routers.deps import get_stats_service
from app.schemas.stats import StatsOverview
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=StatsOverview, summary="Aggregated dashboard counts")
def overview(service: StatsService = Depends(get_stats_service)) -> StatsOverview:
    return service.overview()
