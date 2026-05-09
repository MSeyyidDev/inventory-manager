"""Tests for repository helper queries."""

from __future__ import annotations

from app.core.enums import DeviceStatus, DeviceType
from app.models.device import Device
from app.models.employee import Employee
from app.models.location import Location
from app.repositories.device_repository import DeviceRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.location_repository import LocationRepository


def test_location_repository_get_by_name(db_session) -> None:
    repo = LocationRepository(db_session)
    loc = Location(name="Berlin HQ", city="Berlin", country="Germany")
    repo.add(loc)
    repo.commit()
    assert repo.get_by_name("Berlin HQ") is not None
    assert repo.get_by_name("Nowhere") is None


def test_employee_repository_email_lookup(db_session) -> None:
    repo = EmployeeRepository(db_session)
    emp = Employee(
        first_name="Alan",
        last_name="Turing",
        email="alan@example.com",
        department="Engineering",
        role="Engineer",
    )
    repo.add(emp)
    repo.commit()
    assert repo.get_by_email("alan@example.com") is not None


def test_device_repository_count_by_type(db_session) -> None:
    repo = DeviceRepository(db_session)
    repo.add(
        Device(
            type=DeviceType.LAPTOP,
            manufacturer="Dell",
            model="X",
            serial_number="A",
            status=DeviceStatus.AVAILABLE,
        )
    )
    repo.add(
        Device(
            type=DeviceType.MONITOR,
            manufacturer="LG",
            model="Y",
            serial_number="B",
            status=DeviceStatus.AVAILABLE,
        )
    )
    repo.commit()
    counts = dict(repo.count_by(Device.type))
    assert counts[DeviceType.LAPTOP.value] == 1
    assert counts[DeviceType.MONITOR.value] == 1
