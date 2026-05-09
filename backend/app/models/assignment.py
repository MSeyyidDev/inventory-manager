"""Assignment ORM model linking devices and employees over time."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.device import Device
    from app.models.employee import Employee


class Assignment(Base):
    """History of a device being assigned to an employee."""

    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    note: Mapped[str | None] = mapped_column(nullable=True)

    device: Mapped["Device"] = relationship(back_populates="assignments")
    employee: Mapped["Employee"] = relationship(back_populates="assignments")

    @property
    def is_active(self) -> bool:
        return self.returned_at is None
