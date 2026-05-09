"""Stats / dashboard schemas."""

from __future__ import annotations

from pydantic import BaseModel


class CountByKey(BaseModel):
    key: str
    count: int


class StatsOverview(BaseModel):
    total_devices: int
    total_employees: int
    total_locations: int
    active_assignments: int
    devices_by_type: list[CountByKey]
    devices_by_status: list[CountByKey]
    devices_by_location: list[CountByKey]
