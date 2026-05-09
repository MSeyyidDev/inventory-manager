"""Device endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import PlainTextResponse

from app.core.enums import DeviceStatus, DeviceType
from app.routers.deps import get_assignment_service, get_device_service, map_domain_error
from app.schemas.assignment import AssignmentReadDetail
from app.schemas.common import Page
from app.schemas.device import DeviceCreate, DeviceRead, DeviceUpdate
from app.services.assignment_service import AssignmentService
from app.services.device_service import DeviceService
from app.services.errors import DomainError

router = APIRouter(prefix="/devices", tags=["devices"])


def _to_read(device, db_assignments: AssignmentService) -> DeviceRead:
    active = db_assignments.repo.active_for_device(device.id)
    employee_name = None
    employee_id = None
    if active is not None:
        employee_id = active.employee_id
        if active.employee is not None:
            employee_name = active.employee.full_name
    base = DeviceRead.model_validate(device)
    return base.model_copy(update={"assigned_to_id": employee_id, "assigned_to_name": employee_name})


@router.get(
    "",
    response_model=Page[DeviceRead],
    summary="List devices with pagination, search, sort and filters",
)
def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    type: DeviceType | None = Query(None, description="Filter by device type"),
    status_: DeviceStatus | None = Query(None, alias="status", description="Filter by status"),
    location_id: int | None = Query(None, description="Filter by location"),
    assigned_to: int | None = Query(None, description="Filter by current employee assignment"),
    search: str | None = Query(None, description="Match serial, model or manufacturer"),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
    service: DeviceService = Depends(get_device_service),
    assignments: AssignmentService = Depends(get_assignment_service),
) -> Page[DeviceRead]:
    items, total = service.list_paginated(
        page=page,
        page_size=page_size,
        type_=type,
        status=status_,
        location_id=location_id,
        assigned_to=assigned_to,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return Page[DeviceRead](
        items=[_to_read(d, assignments) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=DeviceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new device",
)
def create_device(
    payload: DeviceCreate,
    service: DeviceService = Depends(get_device_service),
    assignments: AssignmentService = Depends(get_assignment_service),
) -> DeviceRead:
    try:
        return _to_read(service.create(payload), assignments)
    except DomainError as exc:
        raise map_domain_error(exc) from exc


@router.get("/export-csv", response_class=PlainTextResponse, summary="Export all devices as CSV")
def export_csv(service: DeviceService = Depends(get_device_service)) -> PlainTextResponse:
    devices = service.repo.list_all()
    csv_text = service.export_csv(devices)
    return PlainTextResponse(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=devices.csv"},
    )


@router.post("/import-csv", summary="Bulk import devices from a CSV file")
async def import_csv(
    file: UploadFile = File(..., description="CSV file matching the export format"),
    service: DeviceService = Depends(get_device_service),
) -> dict[str, object]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="A CSV file is required")
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from exc
    created, skipped, errors = service.import_csv(text)
    return {"created": created, "skipped": skipped, "errors": errors}


@router.get("/{device_id}", response_model=DeviceRead, summary="Get a single device")
def get_device(
    device_id: int,
    service: DeviceService = Depends(get_device_service),
    assignments: AssignmentService = Depends(get_assignment_service),
) -> DeviceRead:
    try:
        return _to_read(service.get(device_id), assignments)
    except DomainError as exc:
        raise map_domain_error(exc) from exc


@router.patch("/{device_id}", response_model=DeviceRead, summary="Update a device")
def update_device(
    device_id: int,
    payload: DeviceUpdate,
    service: DeviceService = Depends(get_device_service),
    assignments: AssignmentService = Depends(get_assignment_service),
) -> DeviceRead:
    try:
        return _to_read(service.update(device_id, payload), assignments)
    except DomainError as exc:
        raise map_domain_error(exc) from exc


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete a device",
)
def delete_device(
    device_id: int, service: DeviceService = Depends(get_device_service)
) -> Response:
    try:
        service.delete(device_id)
    except DomainError as exc:
        raise map_domain_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{device_id}/history",
    response_model=list[AssignmentReadDetail],
    summary="Full assignment history for a device",
)
def device_history(
    device_id: int,
    service: DeviceService = Depends(get_device_service),
) -> list[AssignmentReadDetail]:
    try:
        history = service.history(device_id)
    except DomainError as exc:
        raise map_domain_error(exc) from exc
    detailed: list[AssignmentReadDetail] = []
    for a in history:
        item = AssignmentReadDetail.model_validate(a)
        if a.employee is not None:
            item = item.model_copy(update={"employee_name": a.employee.full_name})
        detailed.append(item)
    return detailed
