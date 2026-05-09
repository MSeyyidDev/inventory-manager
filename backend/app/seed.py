"""Synthetic data seeder.

Creates a believable dataset:
    - 8 locations
    - 200 employees in 6 departments
    - 600 devices across 5 types with realistic manufacturers/models
    - 800 assignments (active + historical)

Run with: ``python -m app.seed``.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.core.enums import DeviceStatus, DeviceType
from app.models.assignment import Assignment
from app.models.device import Device
from app.models.employee import Employee
from app.models.location import Location

fake = Faker()
Faker.seed(42)
random.seed(42)


LOCATIONS = [
    {"name": "Berlin HQ", "city": "Berlin", "country": "Germany"},
    {"name": "Munich Office", "city": "Munich", "country": "Germany"},
    {"name": "Hamburg Office", "city": "Hamburg", "country": "Germany"},
    {"name": "Frankfurt Office", "city": "Frankfurt", "country": "Germany"},
    {"name": "Vienna Office", "city": "Vienna", "country": "Austria"},
    {"name": "Zurich Office", "city": "Zurich", "country": "Switzerland"},
    {"name": "Amsterdam Office", "city": "Amsterdam", "country": "Netherlands"},
    {"name": "Remote", "city": "Remote", "country": "Global"},
]

DEPARTMENTS = [
    "Engineering",
    "Product",
    "Design",
    "Sales",
    "Marketing",
    "Operations",
]

ROLES = {
    "Engineering": [
        "Backend Engineer",
        "Frontend Engineer",
        "Senior Backend Engineer",
        "Staff Engineer",
        "QA Engineer",
        "DevOps Engineer",
        "Engineering Manager",
    ],
    "Product": ["Product Manager", "Senior Product Manager", "Product Analyst"],
    "Design": ["Product Designer", "UX Researcher", "Design Lead"],
    "Sales": ["Account Executive", "Sales Engineer", "Sales Manager"],
    "Marketing": ["Marketing Manager", "Content Marketer", "Growth Specialist"],
    "Operations": ["IT Specialist", "People Ops", "Office Manager", "Finance Analyst"],
}

CATALOG: dict[DeviceType, list[tuple[str, list[str]]]] = {
    DeviceType.LAPTOP: [
        ("Apple", ["MacBook Pro 14", "MacBook Pro 16", "MacBook Air 13", "MacBook Air 15"]),
        ("Dell", ["Latitude 5440", "Latitude 7440", "XPS 13", "XPS 15", "Precision 5570"]),
        ("Lenovo", ["ThinkPad X1 Carbon", "ThinkPad T14", "ThinkPad P1", "ThinkPad L13"]),
        ("HP", ["EliteBook 840", "ProBook 450", "ZBook Studio"]),
    ],
    DeviceType.MONITOR: [
        ("Dell", ["UltraSharp U2723QE", "UltraSharp U2422H", "P2723D"]),
        ("LG", ["27UP850-W", "34WN80C-B", "27GP850-B"]),
        ("Samsung", ["Odyssey G7", "ViewFinity S8", "M8 Smart Monitor"]),
        ("BenQ", ["PD2725U", "EW3270U"]),
    ],
    DeviceType.SMARTPHONE: [
        ("Apple", ["iPhone 14", "iPhone 14 Pro", "iPhone 15", "iPhone 15 Pro"]),
        ("Samsung", ["Galaxy S23", "Galaxy S24", "Galaxy A54"]),
        ("Google", ["Pixel 7", "Pixel 8", "Pixel 8 Pro"]),
    ],
    DeviceType.SERVER: [
        ("Dell", ["PowerEdge R650", "PowerEdge R750", "PowerEdge R760"]),
        ("HPE", ["ProLiant DL380 Gen11", "ProLiant DL360 Gen11"]),
        ("Supermicro", ["SuperServer 2029U", "SuperServer 1029U"]),
    ],
    DeviceType.ACCESSORY: [
        ("Logitech", ["MX Master 3S", "MX Keys", "Brio 4K", "C920 Webcam"]),
        ("Apple", ["Magic Keyboard", "Magic Mouse", "Magic Trackpad"]),
        ("Cisco", ["Webex Desk Camera", "Headset 730"]),
        ("Jabra", ["Evolve2 75", "Evolve2 65", "Speak 510"]),
    ],
}


def _make_serial(manufacturer: str, model: str) -> str:
    code = "".join(c for c in (manufacturer + model) if c.isalnum()).upper()[:6]
    suffix = fake.bothify(text="??-####-####")
    return f"{code}-{suffix}"


def seed(db: Session) -> dict[str, int]:
    locations = [Location(**loc, address=fake.street_address()) for loc in LOCATIONS]
    db.add_all(locations)
    db.flush()

    employees: list[Employee] = []
    for _ in range(200):
        first = fake.first_name()
        last = fake.last_name()
        dept = random.choice(DEPARTMENTS)
        emp = Employee(
            first_name=first,
            last_name=last,
            email=f"{first.lower()}.{last.lower()}.{fake.random_int(100, 9999)}@example.com",
            department=dept,
            role=random.choice(ROLES[dept]),
            location_id=random.choice(locations).id,
        )
        employees.append(emp)
    db.add_all(employees)
    db.flush()

    devices: list[Device] = []
    used_serials: set[str] = set()
    for _ in range(600):
        device_type = random.choice(list(DeviceType))
        manufacturer, models = random.choice(CATALOG[device_type])
        model = random.choice(models)
        # ensure unique serial
        while True:
            serial = _make_serial(manufacturer, model)
            if serial not in used_serials:
                used_serials.add(serial)
                break

        purchase = fake.date_between(start_date="-4y", end_date="-1m")
        warranty = purchase + timedelta(days=365 * random.randint(1, 4))
        status = random.choices(
            [DeviceStatus.AVAILABLE, DeviceStatus.MAINTENANCE, DeviceStatus.RETIRED],
            weights=[80, 10, 10],
            k=1,
        )[0]
        device = Device(
            type=device_type,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial,
            status=status,
            purchase_date=purchase,
            warranty_end=warranty,
            location_id=random.choice(locations).id,
        )
        devices.append(device)
    db.add_all(devices)
    db.flush()

    assignments: list[Assignment] = []
    eligible = [d for d in devices if d.status != DeviceStatus.RETIRED]
    random.shuffle(eligible)

    # Active assignments (~ 55% of eligible devices)
    active_count = min(int(len(eligible) * 0.55), 500)
    for device in eligible[:active_count]:
        emp = random.choice(employees)
        assigned_at = datetime.utcnow() - timedelta(days=random.randint(5, 600))
        assignments.append(
            Assignment(
                device_id=device.id,
                employee_id=emp.id,
                assigned_at=assigned_at,
                returned_at=None,
            )
        )
        device.status = DeviceStatus.ASSIGNED

    # Historical assignments to reach ~800 total
    historical_target = 800 - len(assignments)
    history_pool = [d for d in devices if d.status != DeviceStatus.RETIRED]
    for _ in range(historical_target):
        device = random.choice(history_pool)
        emp = random.choice(employees)
        assigned_at = datetime.utcnow() - timedelta(days=random.randint(120, 1500))
        returned_at = assigned_at + timedelta(days=random.randint(20, 400))
        if returned_at > datetime.utcnow():
            returned_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        assignments.append(
            Assignment(
                device_id=device.id,
                employee_id=emp.id,
                assigned_at=assigned_at,
                returned_at=returned_at,
            )
        )

    db.add_all(assignments)
    db.commit()

    return {
        "locations": len(locations),
        "employees": len(employees),
        "devices": len(devices),
        "assignments": len(assignments),
    }


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        # Reset existing rows for an idempotent seed.
        db.query(Assignment).delete()
        db.query(Device).delete()
        db.query(Employee).delete()
        db.query(Location).delete()
        db.commit()
        counts = seed(db)
    finally:
        db.close()
    print("Seed complete:")
    for key, value in counts.items():
        print(f"  {key:>12}: {value}")


if __name__ == "__main__":
    main()
