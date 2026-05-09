"""Repositories: data-access layer, one class per aggregate root."""

from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.location_repository import LocationRepository

__all__ = [
    "AssignmentRepository",
    "DeviceRepository",
    "EmployeeRepository",
    "LocationRepository",
]
