"""Reusable FastAPI dependencies."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.assignment_service import AssignmentService
from app.services.device_service import DeviceService
from app.services.employee_service import EmployeeService
from app.services.errors import ConflictError, DomainError, NotFoundError
from app.services.location_service import LocationService
from app.services.stats_service import StatsService


def get_location_service(db: Session = Depends(get_db)) -> LocationService:
    return LocationService(db)


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    return EmployeeService(db)


def get_device_service(db: Session = Depends(get_db)) -> DeviceService:
    return DeviceService(db)


def get_assignment_service(db: Session = Depends(get_db)) -> AssignmentService:
    return AssignmentService(db)


def get_stats_service(db: Session = Depends(get_db)) -> StatsService:
    return StatsService(db)


def map_domain_error(exc: DomainError) -> HTTPException:
    """Translate a domain error into an HTTPException."""
    if isinstance(exc, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, ConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
