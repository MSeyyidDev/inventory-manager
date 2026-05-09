"""Location schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LocationBase(BaseModel):
    name: str = Field(..., examples=["Berlin HQ"])
    city: str = Field(..., examples=["Berlin"])
    country: str = Field(..., examples=["Germany"])
    address: str | None = Field(None, examples=["Friedrichstrasse 1"])


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    country: str | None = None
    address: str | None = None


class LocationRead(LocationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
