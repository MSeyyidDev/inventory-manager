"""Location endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.routers.deps import get_location_service, map_domain_error
from app.schemas.location import LocationCreate, LocationRead, LocationUpdate
from app.services.errors import DomainError
from app.services.location_service import LocationService

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationRead], summary="List all locations")
def list_locations(service: LocationService = Depends(get_location_service)) -> list[LocationRead]:
    return [LocationRead.model_validate(loc) for loc in service.list()]


@router.post(
    "",
    response_model=LocationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new location",
)
def create_location(
    payload: LocationCreate, service: LocationService = Depends(get_location_service)
) -> LocationRead:
    try:
        return LocationRead.model_validate(service.create(payload))
    except DomainError as exc:
        raise map_domain_error(exc) from exc


@router.get("/{location_id}", response_model=LocationRead, summary="Get a single location")
def get_location(
    location_id: int, service: LocationService = Depends(get_location_service)
) -> LocationRead:
    try:
        return LocationRead.model_validate(service.get(location_id))
    except DomainError as exc:
        raise map_domain_error(exc) from exc


@router.patch("/{location_id}", response_model=LocationRead, summary="Update a location")
def update_location(
    location_id: int,
    payload: LocationUpdate,
    service: LocationService = Depends(get_location_service),
) -> LocationRead:
    try:
        return LocationRead.model_validate(service.update(location_id, payload))
    except DomainError as exc:
        raise map_domain_error(exc) from exc


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete a location",
)
def delete_location(
    location_id: int, service: LocationService = Depends(get_location_service)
) -> Response:
    try:
        service.delete(location_id)
    except DomainError as exc:
        raise map_domain_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
