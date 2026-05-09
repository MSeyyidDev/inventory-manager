"""Device schemas."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import DeviceStatus, DeviceType


class DeviceBase(BaseModel):
    type: DeviceType = Field(..., examples=[DeviceType.LAPTOP])
    manufacturer: str = Field(..., examples=["Dell"])
    model: str = Field(..., examples=["Latitude 7440"])
    serial_number: str = Field(..., examples=["DLL-7440-9F31A2"])
    status: DeviceStatus = DeviceStatus.AVAILABLE
    purchase_date: date | None = None
    warranty_end: date | None = None
    notes: str | None = None
    location_id: int | None = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    type: DeviceType | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    status: DeviceStatus | None = None
    purchase_date: date | None = None
    warranty_end: date | None = None
    notes: str | None = None
    location_id: int | None = None


class DeviceRead(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assigned_to_id: int | None = Field(
        None, description="Employee currently in possession, if any."
    )
    assigned_to_name: str | None = None
