"""Employee repository."""

from __future__ import annotations

from sqlalchemy import func, select

from app.models.employee import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    """Read/write operations for Employee entities."""

    model = Employee

    def get_by_email(self, email: str) -> Employee | None:
        return self.db.execute(
            select(Employee).where(Employee.email == email)
        ).scalar_one_or_none()

    def list_paginated(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        department: str | None = None,
    ) -> tuple[list[Employee], int]:
        stmt = select(Employee)
        count_stmt = select(func.count()).select_from(Employee)

        if search:
            like = f"%{search.lower()}%"
            condition = (
                Employee.first_name.ilike(like)
                | Employee.last_name.ilike(like)
                | Employee.email.ilike(like)
            )
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        if department:
            stmt = stmt.where(Employee.department == department)
            count_stmt = count_stmt.where(Employee.department == department)

        total = self.db.execute(count_stmt).scalar_one()
        items = list(
            self.db.execute(
                stmt.order_by(Employee.last_name, Employee.first_name)
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).scalars()
        )
        return items, total
