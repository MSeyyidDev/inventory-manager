"""Device ORM model."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import DeviceStatus, DeviceType

if TYPE_CHECKING:
    from app.models.assignment import Assignment
    from app.models.location import Location


class Device(Base):
    """A hardware asset that may be assigned to an employee."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[DeviceType] = mapped_column(SAEnum(DeviceType), nullable=False, index=True)
    status: Mapped[DeviceStatus] = mapped_column(
        SAEnum(DeviceStatus), nullable=False, default=DeviceStatus.AVAILABLE, index=True
    )
    manufacturer: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    warranty_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)

    location: Mapped["Location | None"] = relationship(back_populates="devices")
    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
