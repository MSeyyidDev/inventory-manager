"""Assignment schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssignmentCreate(BaseModel):
    device_id: int = Field(..., examples=[1])
    employee_id: int = Field(..., examples=[1])
    note: str | None = Field(None, examples=["Replacement for retired laptop."])


class AssignmentReturn(BaseModel):
    note: str | None = None


class AssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    employee_id: int
    assigned_at: datetime
    returned_at: datetime | None
    note: str | None
    is_active: bool


class AssignmentReadDetail(AssignmentRead):
    device_model: str | None = None
    device_serial: str | None = None
    employee_name: str | None = None
