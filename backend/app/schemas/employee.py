"""Employee schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeBase(BaseModel):
    first_name: str = Field(..., examples=["Ada"])
    last_name: str = Field(..., examples=["Lovelace"])
    email: EmailStr = Field(..., examples=["ada.lovelace@example.com"])
    department: str = Field(..., examples=["Engineering"])
    role: str = Field(..., examples=["Senior Backend Engineer"])
    location_id: int | None = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    department: str | None = None
    role: str | None = None
    location_id: int | None = None


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
