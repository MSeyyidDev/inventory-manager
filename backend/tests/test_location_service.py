"""Tests for LocationService."""

from __future__ import annotations

import pytest

from app.schemas.location import LocationCreate, LocationUpdate
from app.services.errors import ConflictError, NotFoundError
from app.services.location_service import LocationService


def test_create_and_list(db_session) -> None:
    service = LocationService(db_session)
    loc = service.create(LocationCreate(name="Berlin HQ", city="Berlin", country="Germany"))
    assert loc.id is not None
    assert len(service.list()) == 1


def test_create_duplicate_raises(db_session) -> None:
    service = LocationService(db_session)
    service.create(LocationCreate(name="Berlin HQ", city="Berlin", country="Germany"))
    with pytest.raises(ConflictError):
        service.create(LocationCreate(name="Berlin HQ", city="Berlin", country="Germany"))


def test_get_missing_raises(db_session) -> None:
    service = LocationService(db_session)
    with pytest.raises(NotFoundError):
        service.get(999)


def test_update_changes_fields(db_session) -> None:
    service = LocationService(db_session)
    loc = service.create(LocationCreate(name="Munich", city="Munich", country="Germany"))
    updated = service.update(loc.id, LocationUpdate(address="Marienplatz 1"))
    assert updated.address == "Marienplatz 1"


def test_delete_removes(db_session) -> None:
    service = LocationService(db_session)
    loc = service.create(LocationCreate(name="Hamburg", city="Hamburg", country="Germany"))
    service.delete(loc.id)
    assert service.list() == []
