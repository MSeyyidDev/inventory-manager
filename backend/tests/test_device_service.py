"""Tests for DeviceService."""

from __future__ import annotations

from datetime import date

import pytest

from app.core.enums import DeviceStatus, DeviceType
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.services.device_service import DeviceService
from app.services.errors import ConflictError, NotFoundError


def _make_device(svc: DeviceService, **overrides) -> object:
    payload = {
        "type": DeviceType.LAPTOP,
        "manufacturer": "Dell",
        "model": "Latitude 7440",
        "serial_number": "DLL-7440-AAA",
        "status": DeviceStatus.AVAILABLE,
        "purchase_date": date(2024, 1, 15),
        "warranty_end": date(2027, 1, 15),
    }
    payload.update(overrides)
    return svc.create(DeviceCreate(**payload))


def test_create_and_get(db_session) -> None:
    service = DeviceService(db_session)
    device = _make_device(service)
    fetched = service.get(device.id)
    assert fetched.serial_number == "DLL-7440-AAA"


def test_duplicate_serial_conflict(db_session) -> None:
    service = DeviceService(db_session)
    _make_device(service)
    with pytest.raises(ConflictError):
        _make_device(service)


def test_filter_by_type_and_status(db_session) -> None:
    service = DeviceService(db_session)
    _make_device(service, serial_number="L1", type=DeviceType.LAPTOP)
    _make_device(service, serial_number="M1", type=DeviceType.MONITOR)
    _make_device(
        service,
        serial_number="S1",
        type=DeviceType.SERVER,
        status=DeviceStatus.MAINTENANCE,
    )
    items, total = service.list_paginated(type_=DeviceType.MONITOR)
    assert total == 1
    assert items[0].type == DeviceType.MONITOR

    items, total = service.list_paginated(status=DeviceStatus.MAINTENANCE)
    assert total == 1


def test_search_matches_partial(db_session) -> None:
    service = DeviceService(db_session)
    _make_device(service, serial_number="ABC-001", model="MacBook Pro")
    _make_device(service, serial_number="XYZ-002", model="ThinkPad X1")
    items, total = service.list_paginated(search="MacBook")
    assert total == 1
    assert items[0].model == "MacBook Pro"


def test_update_serial_conflict(db_session) -> None:
    service = DeviceService(db_session)
    a = _make_device(service, serial_number="A1")
    _make_device(service, serial_number="B1")
    with pytest.raises(ConflictError):
        service.update(a.id, DeviceUpdate(serial_number="B1"))


def test_csv_export_and_import_roundtrip(db_session) -> None:
    service = DeviceService(db_session)
    _make_device(service, serial_number="EXP-001")
    _make_device(service, serial_number="EXP-002", type=DeviceType.MONITOR)

    csv_text = service.export_csv(service.repo.list_all())
    assert "EXP-001" in csv_text
    # Wipe and re-import
    for d in service.repo.list_all():
        service.repo.delete(d)
    service.repo.commit()

    created, skipped, errors = service.import_csv(csv_text)
    assert created == 2
    assert skipped == 0
    assert errors == []


def test_csv_import_skips_duplicates(db_session) -> None:
    service = DeviceService(db_session)
    _make_device(service, serial_number="KEEP-001")
    csv_text = (
        "type,manufacturer,model,serial_number,status,purchase_date,warranty_end,notes,location_id\n"
        "laptop,Dell,Latitude,KEEP-001,available,,,,\n"
        "laptop,Dell,Latitude,NEW-002,available,,,,\n"
    )
    created, skipped, errors = service.import_csv(csv_text)
    assert created == 1
    assert skipped == 1
    assert errors == []


def test_get_missing(db_session) -> None:
    service = DeviceService(db_session)
    with pytest.raises(NotFoundError):
        service.get(99)
