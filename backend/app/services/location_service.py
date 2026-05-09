"""Location service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.location import Location
from app.repositories.location_repository import LocationRepository
from app.schemas.location import LocationCreate, LocationUpdate
from app.services.errors import ConflictError, NotFoundError


class LocationService:
    """Business logic around locations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = LocationRepository(db)

    def list(self) -> list[Location]:
        return self.repo.list_all()

    def get(self, location_id: int) -> Location:
        loc = self.repo.get(location_id)
        if loc is None:
            raise NotFoundError(f"Location {location_id} not found")
        return loc

    def create(self, payload: LocationCreate) -> Location:
        if self.repo.get_by_name(payload.name) is not None:
            raise ConflictError(f"Location '{payload.name}' already exists")
        loc = Location(**payload.model_dump())
        self.repo.add(loc)
        self.repo.commit()
        return loc

    def update(self, location_id: int, payload: LocationUpdate) -> Location:
        loc = self.get(location_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(loc, field, value)
        self.repo.commit()
        return loc

    def delete(self, location_id: int) -> None:
        loc = self.get(location_id)
        self.repo.delete(loc)
        self.repo.commit()
