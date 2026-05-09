"""End-to-end API tests for device endpoints."""

from __future__ import annotations


def _create(client, **overrides):
    payload = {
        "type": "laptop",
        "manufacturer": "Dell",
        "model": "Latitude 7440",
        "serial_number": "API-001",
        "status": "available",
    }
    payload.update(overrides)
    return client.post("/devices", json=payload)


def test_health(client) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_list_devices(client) -> None:
    r = _create(client)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["serial_number"] == "API-001"

    r = client.get("/devices")
    assert r.status_code == 200
    payload = r.json()
    assert payload["total"] == 1
    assert payload["items"][0]["serial_number"] == "API-001"


def test_filter_devices_by_type(client) -> None:
    _create(client, serial_number="L1", type="laptop")
    _create(client, serial_number="M1", type="monitor")
    r = client.get("/devices", params={"type": "monitor"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["type"] == "monitor"


def test_search_devices(client) -> None:
    _create(client, serial_number="SEARCH-9", model="MacBook Pro 14")
    r = client.get("/devices", params={"search": "MacBook"})
    assert r.json()["total"] == 1


def test_update_device(client) -> None:
    r = _create(client)
    device_id = r.json()["id"]
    r = client.patch(f"/devices/{device_id}", json={"notes": "battery replaced"})
    assert r.status_code == 200
    assert r.json()["notes"] == "battery replaced"


def test_delete_device(client) -> None:
    r = _create(client)
    device_id = r.json()["id"]
    r = client.delete(f"/devices/{device_id}")
    assert r.status_code == 204
    r = client.get(f"/devices/{device_id}")
    assert r.status_code == 404


def test_csv_export_and_import_endpoint(client) -> None:
    _create(client, serial_number="EXP-1")
    r = client.get("/devices/export-csv")
    assert r.status_code == 200
    assert "EXP-1" in r.text

    csv_payload = (
        "type,manufacturer,model,serial_number,status,purchase_date,warranty_end,notes,location_id\n"
        "laptop,Lenovo,ThinkPad,IMP-1,available,,,,\n"
    )
    r = client.post(
        "/devices/import-csv",
        files={"file": ("d.csv", csv_payload, "text/csv")},
    )
    assert r.status_code == 200
    assert r.json()["created"] == 1
