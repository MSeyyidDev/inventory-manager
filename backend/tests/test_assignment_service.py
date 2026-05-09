"""Tests for AssignmentService."""

from __future__ import annotations

import pytest

from app.core.enums import DeviceStatus, DeviceType
from app.schemas.assignment import AssignmentCreate, AssignmentReturn
from app.schemas.device import DeviceCreate
from app.schemas.employee import EmployeeCreate
from app.services.assignment_service import AssignmentService
from app.services.device_service import DeviceService
from app.services.employee_service import EmployeeService
from app.services.errors import ConflictError, NotFoundError


@pytest.fixture()
def fixtures(db_session):
    devices = DeviceService(db_session)
    employees = EmployeeService(db_session)
    device = devices.create(
        DeviceCreate(
            type=DeviceType.LAPTOP,
            manufacturer="Apple",
            model="MacBook Pro",
            serial_number="MBP-001",
        )
    )
    employee = employees.create(
        EmployeeCreate(
            first_name="Grace",
            last_name="Hopper",
            email="grace@example.com",
            department="Engineering",
            role="Staff Engineer",
        )
    )
    return device, employee


def test_assign_marks_device_assigned(db_session, fixtures) -> None:
    device, employee = fixtures
    service = AssignmentService(db_session)
    assignment = service.assign(AssignmentCreate(device_id=device.id, employee_id=employee.id))
    assert assignment.is_active
    assert device.status == DeviceStatus.ASSIGNED


def test_double_assign_conflict(db_session, fixtures) -> None:
    device, employee = fixtures
    service = AssignmentService(db_session)
    service.assign(AssignmentCreate(device_id=device.id, employee_id=employee.id))
    with pytest.raises(ConflictError):
        service.assign(AssignmentCreate(device_id=device.id, employee_id=employee.id))


def test_return_releases_device(db_session, fixtures) -> None:
    device, employee = fixtures
    service = AssignmentService(db_session)
    assignment = service.assign(AssignmentCreate(device_id=device.id, employee_id=employee.id))
    closed = service.return_device(assignment.id, AssignmentReturn(note="cleaned"))
    assert closed.returned_at is not None
    assert device.status == DeviceStatus.AVAILABLE


def test_return_already_closed(db_session, fixtures) -> None:
    device, employee = fixtures
    service = AssignmentService(db_session)
    assignment = service.assign(AssignmentCreate(device_id=device.id, employee_id=employee.id))
    service.return_device(assignment.id, AssignmentReturn())
    with pytest.raises(ConflictError):
        service.return_device(assignment.id, AssignmentReturn())


def test_assign_unknown_device(db_session, fixtures) -> None:
    _, employee = fixtures
    service = AssignmentService(db_session)
    with pytest.raises(NotFoundError):
        service.assign(AssignmentCreate(device_id=9999, employee_id=employee.id))
