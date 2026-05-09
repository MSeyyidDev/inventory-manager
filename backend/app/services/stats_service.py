"""Stats service for dashboard overview."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.employee import Employee
from app.models.location import Location
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.device_repository import DeviceRepository
from app.schemas.stats import CountByKey, StatsOverview


class StatsService:
    """Aggregated counts for the dashboard."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.devices = DeviceRepository(db)
        self.assignments = AssignmentRepository(db)

    def overview(self) -> StatsOverview:
        total_devices = int(self.db.execute(select(func.count(Device.id))).scalar_one())
        total_employees = int(self.db.execute(select(func.count(Employee.id))).scalar_one())
        total_locations = int(self.db.execute(select(func.count(Location.id))).scalar_one())
        active_assignments = self.assignments.count_active()

        return StatsOverview(
            total_devices=total_devices,
            total_employees=total_employees,
            total_locations=total_locations,
            active_assignments=active_assignments,
            devices_by_type=[
                CountByKey(key=k, count=c) for k, c in self.devices.count_by(Device.type)
            ],
            devices_by_status=[
                CountByKey(key=k, count=c) for k, c in self.devices.count_by(Device.status)
            ],
            devices_by_location=[
                CountByKey(key=k, count=c) for k, c in self.devices.count_by_location()
            ],
        )
