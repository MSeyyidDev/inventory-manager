"""Domain enums shared across models, schemas and services."""

from __future__ import annotations

from enum import Enum


class DeviceType(str, Enum):
    """Top-level category of a hardware asset."""

    LAPTOP = "laptop"
    MONITOR = "monitor"
    SMARTPHONE = "smartphone"
    SERVER = "server"
    ACCESSORY = "accessory"


class DeviceStatus(str, Enum):
    """Lifecycle status of a device."""

    AVAILABLE = "available"
    ASSIGNED = "assigned"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"
