"""Device repository with rich filtering."""

from __future__ import annotations

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import joinedload

from app.core.enums import DeviceStatus, DeviceType
from app.models.assignment import Assignment
from app.models.device import Device
from app.repositories.base import BaseRepository


SORTABLE_FIELDS = {
    "id": Device.id,
    "type": Device.type,
    "manufacturer": Device.manufacturer,
    "model": Device.model,
    "serial_number": Device.serial_number,
    "status": Device.status,
    "purchase_date": Device.purchase_date,
}


class DeviceRepository(BaseRepository[Device]):
    """Read/write operations for Device entities."""

    model = Device

    def get_by_serial(self, serial: str) -> Device | None:
        return self.db.execute(
            select(Device).where(Device.serial_number == serial)
        ).scalar_one_or_none()

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
        stmt = select(Device).options(joinedload(Device.location))
        count_stmt = select(func.count()).select_from(Device)

        if type_ is not None:
            stmt = stmt.where(Device.type == type_)
            count_stmt = count_stmt.where(Device.type == type_)
        if status is not None:
            stmt = stmt.where(Device.status == status)
            count_stmt = count_stmt.where(Device.status == status)
        if location_id is not None:
            stmt = stmt.where(Device.location_id == location_id)
            count_stmt = count_stmt.where(Device.location_id == location_id)
        if search:
            like = f"%{search}%"
            condition = (
                Device.serial_number.ilike(like)
                | Device.model.ilike(like)
                | Device.manufacturer.ilike(like)
            )
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        if assigned_to is not None:
            active_subq = (
                select(Assignment.device_id)
                .where(Assignment.employee_id == assigned_to)
                .where(Assignment.returned_at.is_(None))
            )
            stmt = stmt.where(Device.id.in_(active_subq))
            count_stmt = count_stmt.where(Device.id.in_(active_subq))

        order_col = SORTABLE_FIELDS.get(sort_by, Device.id)
        stmt = stmt.order_by(desc(order_col) if sort_dir == "desc" else asc(order_col))

        total = self.db.execute(count_stmt).scalar_one()
        items = list(
            self.db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().unique()
        )
        return items, total

    def count_by(self, column) -> list[tuple[str, int]]:
        rows = self.db.execute(
            select(column, func.count(Device.id)).group_by(column)
        ).all()
        return [(str(r[0].value if hasattr(r[0], "value") else r[0]), int(r[1])) for r in rows]

    def count_by_location(self) -> list[tuple[str, int]]:
        from app.models.location import Location

        rows = self.db.execute(
            select(Location.name, func.count(Device.id))
            .join(Location, Location.id == Device.location_id, isouter=True)
            .group_by(Location.name)
        ).all()
        return [(str(name) if name else "Unassigned", int(count)) for name, count in rows]
