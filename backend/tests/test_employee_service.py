"""Tests for EmployeeService."""

from __future__ import annotations

import pytest

from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.schemas.location import LocationCreate
from app.services.employee_service import EmployeeService
from app.services.errors import ConflictError, NotFoundError
from app.services.location_service import LocationService


def _make_employee(svc: EmployeeService, **overrides) -> object:
    payload = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "department": "Engineering",
        "role": "Backend Engineer",
        "location_id": None,
    }
    payload.update(overrides)
    return svc.create(EmployeeCreate(**payload))


def test_create_and_get(db_session) -> None:
    service = EmployeeService(db_session)
    emp = _make_employee(service)
    fetched = service.get(emp.id)
    assert fetched.email == "ada@example.com"
    assert fetched.full_name == "Ada Lovelace"


def test_create_duplicate_email_conflict(db_session) -> None:
    service = EmployeeService(db_session)
    _make_employee(service)
    with pytest.raises(ConflictError):
        _make_employee(service)


def test_pagination_and_search(db_session) -> None:
    service = EmployeeService(db_session)
    for i in range(15):
        _make_employee(
            service,
            first_name=f"Person{i}",
            last_name=f"Smith{i}",
            email=f"p{i}@example.com",
        )
    items, total = service.list_paginated(page=1, page_size=10)
    assert total == 15
    assert len(items) == 10

    items, total = service.list_paginated(page=1, page_size=10, search="Person3")
    assert total == 1


def test_update_email_conflict(db_session) -> None:
    service = EmployeeService(db_session)
    a = _make_employee(service, email="a@example.com")
    _make_employee(service, email="b@example.com")
    with pytest.raises(ConflictError):
        service.update(a.id, EmployeeUpdate(email="b@example.com"))


def test_attach_location(db_session) -> None:
    locations = LocationService(db_session)
    loc = locations.create(LocationCreate(name="Berlin HQ", city="Berlin", country="Germany"))
    employees = EmployeeService(db_session)
    emp = _make_employee(employees, location_id=loc.id)
    assert emp.location_id == loc.id


def test_get_missing(db_session) -> None:
    service = EmployeeService(db_session)
    with pytest.raises(NotFoundError):
        service.get(123)
