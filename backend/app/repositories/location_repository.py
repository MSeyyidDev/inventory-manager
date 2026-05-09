"""Location repository."""

from __future__ import annotations

from sqlalchemy import select

from app.models.location import Location
from app.repositories.base import BaseRepository


class LocationRepository(BaseRepository[Location]):
    """Read/write operations for Location entities."""

    model = Location

    def get_by_name(self, name: str) -> Location | None:
        return self.db.execute(select(Location).where(Location.name == name)).scalar_one_or_none()
