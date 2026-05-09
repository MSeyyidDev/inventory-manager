"""End-to-end API tests for assignments and stats."""

from __future__ import annotations


def _create_employee(client) -> int:
    r = client.post(
        "/employees",
        json={
            "first_name": "Linus",
            "last_name": "Torvalds",
            "email": "linus@example.com",
            "department": "Engineering",
            "role": "Engineer",
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


def _create_device(client, serial: str = "AS-001") -> int:
    r = client.post(
        "/devices",
        json={
            "type": "laptop",
            "manufacturer": "Apple",
            "model": "MacBook Pro 14",
            "serial_number": serial,
            "status": "available",
        },
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_assign_and_return_flow(client) -> None:
    employee_id = _create_employee(client)
    device_id = _create_device(client)

    r = client.post("/assignments", json={"device_id": device_id, "employee_id": employee_id})
    assert r.status_code == 201
    assignment = r.json()
    assert assignment["is_active"] is True

    # device should now show as assigned
    r = client.get(f"/devices/{device_id}")
    assert r.json()["status"] == "assigned"
    assert r.json()["assigned_to_id"] == employee_id

    # double-assign should conflict
    r = client.post("/assignments", json={"device_id": device_id, "employee_id": employee_id})
    assert r.status_code == 409

    # return
    r = client.post(f"/assignments/{assignment['id']}/return", json={"note": "ok"})
    assert r.status_code == 200
    assert r.json()["returned_at"] is not None


def test_device_history(client) -> None:
    employee_id = _create_employee(client)
    device_id = _create_device(client, serial="HIST-1")
    r = client.post("/assignments", json={"device_id": device_id, "employee_id": employee_id})
    assignment_id = r.json()["id"]
    client.post(f"/assignments/{assignment_id}/return", json={})

    r = client.get(f"/devices/{device_id}/history")
    assert r.status_code == 200
    history = r.json()
    assert len(history) == 1
    assert history[0]["employee_name"] == "Linus Torvalds"


def test_stats_overview(client) -> None:
    _create_employee(client)
    _create_device(client, serial="ST-1")
    _create_device(client, serial="ST-2")
    r = client.get("/stats/overview")
    assert r.status_code == 200
    body = r.json()
    assert body["total_devices"] == 2
    assert body["total_employees"] == 1
    assert any(item["count"] == 2 for item in body["devices_by_type"])
