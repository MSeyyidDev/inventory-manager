"""Device service: CRUD, filtering, CSV import/export."""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import Iterable

from sqlalchemy.orm import Session

from app.core.enums import DeviceStatus, DeviceType
from app.models.assignment import Assignment
from app.models.device import Device
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.services.errors import ConflictError, NotFoundError


CSV_COLUMNS = [
    "type",
    "manufacturer",
    "model",
    "serial_number",
    "status",
    "purchase_date",
    "warranty_end",
    "notes",
    "location_id",
]


class DeviceService:
    """Business logic around devices."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DeviceRepository(db)
        self.assignments = AssignmentRepository(db)

    def list_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        type_: DeviceType | None = None,
        status: DeviceStatus | None = None,
        location_id: int | None = None,
        assigned_to: int | None = None,
        search: str | None = None,
        sort_by: str = "id",
        sort_dir: str = "asc",
    ) -> tuple[list[Device], int]:
        return self.repo.list_paginated(
            page=page,
            page_size=page_size,
            type_=type_,
            status=status,
            location_id=location_id,
            assigned_to=assigned_to,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

    def get(self, device_id: int) -> Device:
        device = self.repo.get(device_id)
        if device is None:
            raise NotFoundError(f"Device {device_id} not found")
        return device

    def create(self, payload: DeviceCreate) -> Device:
        if self.repo.get_by_serial(payload.serial_number) is not None:
            raise ConflictError(f"Serial number '{payload.serial_number}' already exists")
        device = Device(**payload.model_dump())
        self.repo.add(device)
        self.repo.commit()
        return device

    def update(self, device_id: int, payload: DeviceUpdate) -> Device:
        device = self.get(device_id)
        data = payload.model_dump(exclude_unset=True)
        if "serial_number" in data and data["serial_number"] != device.serial_number:
            if self.repo.get_by_serial(data["serial_number"]) is not None:
                raise ConflictError("Serial number already in use")
        for field, value in data.items():
            setattr(device, field, value)
        self.repo.commit()
        return device

    def delete(self, device_id: int) -> None:
        device = self.get(device_id)
        self.repo.delete(device)
        self.repo.commit()

    def history(self, device_id: int) -> list[Assignment]:
        self.get(device_id)
        return self.assignments.history_for_device(device_id)

    # ---- CSV ----------------------------------------------------------------

    def export_csv(self, devices: Iterable[Device]) -> str:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for d in devices:
            writer.writerow(
                {
                    "type": d.type.value,
                    "manufacturer": d.manufacturer,
                    "model": d.model,
                    "serial_number": d.serial_number,
                    "status": d.status.value,
                    "purchase_date": d.purchase_date.isoformat() if d.purchase_date else "",
                    "warranty_end": d.warranty_end.isoformat() if d.warranty_end else "",
                    "notes": d.notes or "",
                    "location_id": d.location_id or "",
                }
            )
        return buffer.getvalue()

    def import_csv(self, content: str) -> tuple[int, int, list[str]]:
        """Import devices from a CSV string. Returns (created, skipped, errors)."""
        created = 0
        skipped = 0
        errors: list[str] = []
        reader = csv.DictReader(io.StringIO(content))
        for line_no, row in enumerate(reader, start=2):
            try:
                serial = (row.get("serial_number") or "").strip()
                if not serial:
                    raise ValueError("missing serial_number")
                if self.repo.get_by_serial(serial) is not None:
                    skipped += 1
                    continue
                device = Device(
                    type=DeviceType(row["type"].strip().lower()),
                    manufacturer=(row.get("manufacturer") or "").strip(),
                    model=(row.get("model") or "").strip(),
                    serial_number=serial,
                    status=DeviceStatus((row.get("status") or "available").strip().lower()),
                    purchase_date=_parse_date(row.get("purchase_date")),
                    warranty_end=_parse_date(row.get("warranty_end")),
                    notes=(row.get("notes") or "").strip() or None,
                    location_id=int(row["location_id"]) if row.get("location_id") else None,
                )
                self.repo.add(device)
                created += 1
            except Exception as exc:  # noqa: BLE001
                errors.append(f"line {line_no}: {exc}")
        self.repo.commit()
        return created, skipped, errors


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    raw = raw.strip()
    if not raw:
        return None
    return datetime.fromisoformat(raw).date()
