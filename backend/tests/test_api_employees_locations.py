"""API tests for employee and location endpoints."""

from __future__ import annotations


def test_create_location_and_list(client) -> None:
    r = client.post("/locations", json={"name": "Berlin HQ", "city": "Berlin", "country": "Germany"})
    assert r.status_code == 201
    r = client.get("/locations")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_create_location_duplicate(client) -> None:
    payload = {"name": "Berlin HQ", "city": "Berlin", "country": "Germany"}
    client.post("/locations", json=payload)
    r = client.post("/locations", json=payload)
    assert r.status_code == 409


def test_employee_pagination(client) -> None:
    for i in range(5):
        client.post(
            "/employees",
            json={
                "first_name": f"Person{i}",
                "last_name": "Smith",
                "email": f"p{i}@example.com",
                "department": "Engineering",
                "role": "Engineer",
            },
        )
    r = client.get("/employees", params={"page": 1, "page_size": 3})
    body = r.json()
    assert body["total"] == 5
    assert len(body["items"]) == 3


def test_employee_devices_endpoint(client) -> None:
    r = client.post(
        "/employees",
        json={
            "first_name": "Margaret",
            "last_name": "Hamilton",
            "email": "margaret@example.com",
            "department": "Engineering",
            "role": "Lead",
        },
    )
    employee_id = r.json()["id"]
    r = client.get(f"/employees/{employee_id}/devices")
    assert r.status_code == 200
    assert r.json() == []
