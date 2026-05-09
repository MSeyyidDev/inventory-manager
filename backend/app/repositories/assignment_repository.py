"""Assignment repository."""

from __future__ import annotations

from sqlalchemy import desc, func, select
from sqlalchemy.orm import joinedload

from app.models.assignment import Assignment
from app.repositories.base import BaseRepository


class AssignmentRepository(BaseRepository[Assignment]):
    """Read/write operations for Assignment entities."""

    model = Assignment

    def active_for_device(self, device_id: int) -> Assignment | None:
        return self.db.execute(
            select(Assignment)
            .where(Assignment.device_id == device_id)
            .where(Assignment.returned_at.is_(None))
        ).scalar_one_or_none()

    def history_for_device(self, device_id: int) -> list[Assignment]:
        return list(
            self.db.execute(
                select(Assignment)
                .where(Assignment.device_id == device_id)
                .order_by(desc(Assignment.assigned_at))
                .options(joinedload(Assignment.employee))
            ).scalars()
        )

    def active_for_employee(self, employee_id: int) -> list[Assignment]:
        return list(
            self.db.execute(
                select(Assignment)
                .where(Assignment.employee_id == employee_id)
                .where(Assignment.returned_at.is_(None))
                .options(joinedload(Assignment.device))
            ).scalars()
        )

    def count_active(self) -> int:
        return int(
            self.db.execute(
                select(func.count(Assignment.id)).where(Assignment.returned_at.is_(None))
            ).scalar_one()
        )
