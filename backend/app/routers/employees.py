"""Employee endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status

from app.routers.deps import get_assignment_service, get_employee_service, map_domain_error
from app.schemas.assignment import AssignmentRead
from app.schemas.common import Page
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services.assignment_service import AssignmentService
from app.services.employee_service import EmployeeService
from app.services.errors import DomainError

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get(
    "",
    response_model=Page[EmployeeRead],
    summary="List employees with pagination, search and filtering",
)
def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    search: str | None = Query(None, description="Match against first/last name or email"),
    department: str | None = Query(None, description="Filter by department"),
    service: EmployeeService = Depends(get_employee_service),
) -> Page[EmployeeRead]:
    items, total = service.list_paginated(
        page=page, page_size=page_size, search=search, department=department
    )
    return Page[EmployeeRead](
        items=[EmployeeRead.model_validate(e) for e in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
)
def create_employee(
    payload: EmployeeCreate, service: EmployeeService = Depends(get_employee_service)
) -> EmployeeRead:
    try:
        return EmployeeRead.model_validate(service.create(payload))
    except DomainError as exc:
        raise map_domain_error(exc) from exc


@router.get("/{employee_id}", response_model=EmployeeRead, summary="Get a single employee")
def get_employee(
    employee_id: int, service: EmployeeService = Depends(get_employee_service)
) -> EmployeeRead:
    try:
        return EmployeeRead.model_validate(service.get(employee_id))
    except DomainError as exc:
        raise map_domain_error(exc) from exc


@router.patch("/{employee_id}", response_model=EmployeeRead, summary="Update an employee")
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeRead:
    try:
        return EmployeeRead.model_validate(service.update(employee_id, payload))
    except DomainError as exc:
        raise map_domain_error(exc) from exc


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete an employee",
)
def delete_employee(
    employee_id: int, service: EmployeeService = Depends(get_employee_service)
) -> Response:
    try:
        service.delete(employee_id)
    except DomainError as exc:
        raise map_domain_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{employee_id}/devices",
    response_model=list[AssignmentRead],
    summary="List devices currently assigned to this employee",
)
def employee_devices(
    employee_id: int,
    employees: EmployeeService = Depends(get_employee_service),
    assignments: AssignmentService = Depends(get_assignment_service),
) -> list[AssignmentRead]:
    try:
        employees.get(employee_id)
    except DomainError as exc:
        raise map_domain_error(exc) from exc
    return [AssignmentRead.model_validate(a) for a in assignments.list_for_employee(employee_id)]
