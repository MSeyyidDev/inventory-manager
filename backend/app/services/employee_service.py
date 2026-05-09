"""Employee service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services.errors import ConflictError, NotFoundError


class EmployeeService:
    """Business logic around employees."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = EmployeeRepository(db)

    def list_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        search: str | None = None,
        department: str | None = None,
    ) -> tuple[list[Employee], int]:
        return self.repo.list_paginated(
            page=page, page_size=page_size, search=search, department=department
        )

    def get(self, employee_id: int) -> Employee:
        emp = self.repo.get(employee_id)
        if emp is None:
            raise NotFoundError(f"Employee {employee_id} not found")
        return emp

    def create(self, payload: EmployeeCreate) -> Employee:
        if self.repo.get_by_email(payload.email) is not None:
            raise ConflictError(f"Employee email '{payload.email}' already exists")
        emp = Employee(**payload.model_dump())
        self.repo.add(emp)
        self.repo.commit()
        return emp

    def update(self, employee_id: int, payload: EmployeeUpdate) -> Employee:
        emp = self.get(employee_id)
        data = payload.model_dump(exclude_unset=True)
        if "email" in data and data["email"] != emp.email:
            if self.repo.get_by_email(data["email"]) is not None:
                raise ConflictError("Email already in use")
        for field, value in data.items():
            setattr(emp, field, value)
        self.repo.commit()
        return emp

    def delete(self, employee_id: int) -> None:
        emp = self.get(employee_id)
        self.repo.delete(emp)
        self.repo.commit()
