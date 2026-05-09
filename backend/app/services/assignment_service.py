"""Assignment service: assign and return devices."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.enums import DeviceStatus
from app.models.assignment import Assignment
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.assignment import AssignmentCreate, AssignmentReturn
from app.services.errors import ConflictError, NotFoundError


class AssignmentService:
    """Business logic for assigning and returning devices."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AssignmentRepository(db)
        self.devices = DeviceRepository(db)
        self.employees = EmployeeRepository(db)

    def assign(self, payload: AssignmentCreate) -> Assignment:
        device = self.devices.get(payload.device_id)
        if device is None:
            raise NotFoundError(f"Device {payload.device_id} not found")
        employee = self.employees.get(payload.employee_id)
        if employee is None:
            raise NotFoundError(f"Employee {payload.employee_id} not found")
        if device.status == DeviceStatus.RETIRED:
            raise ConflictError("Cannot assign a retired device")
        if self.repo.active_for_device(device.id) is not None:
            raise ConflictError("Device is already assigned. Return it first.")

        assignment = Assignment(
            device_id=device.id,
            employee_id=employee.id,
            assigned_at=datetime.utcnow(),
            note=payload.note,
        )
        self.repo.add(assignment)
        device.status = DeviceStatus.ASSIGNED
        self.repo.commit()
        return assignment

    def return_device(self, assignment_id: int, payload: AssignmentReturn) -> Assignment:
        assignment = self.repo.get(assignment_id)
        if assignment is None:
            raise NotFoundError(f"Assignment {assignment_id} not found")
        if assignment.returned_at is not None:
            raise ConflictError("Assignment is already closed")

        assignment.returned_at = datetime.utcnow()
        if payload.note:
            existing = assignment.note or ""
            assignment.note = (existing + "\n" + payload.note).strip()

        device = self.devices.get(assignment.device_id)
        if device is not None and device.status == DeviceStatus.ASSIGNED:
            device.status = DeviceStatus.AVAILABLE

        self.repo.commit()
        return assignment

    def list_for_device(self, device_id: int) -> list[Assignment]:
        return self.repo.history_for_device(device_id)

    def list_for_employee(self, employee_id: int) -> list[Assignment]:
        return self.repo.active_for_employee(employee_id)
