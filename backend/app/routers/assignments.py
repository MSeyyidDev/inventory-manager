"""Assignment endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.routers.deps import get_assignment_service, map_domain_error
from app.schemas.assignment import AssignmentCreate, AssignmentRead, AssignmentReturn
from app.services.assignment_service import AssignmentService
from app.services.errors import DomainError

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post(
    "",
    response_model=AssignmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a device to an employee",
)
def assign(
    payload: AssignmentCreate, service: AssignmentService = Depends(get_assignment_service)
) -> AssignmentRead:
    try:
        return AssignmentRead.model_validate(service.assign(payload))
    except DomainError as exc:
        raise map_domain_error(exc) from exc


@router.post(
    "/{assignment_id}/return",
    response_model=AssignmentRead,
    summary="Return an assigned device",
)
def return_assignment(
    assignment_id: int,
    payload: AssignmentReturn,
    service: AssignmentService = Depends(get_assignment_service),
) -> AssignmentRead:
    try:
        return AssignmentRead.model_validate(service.return_device(assignment_id, payload))
    except DomainError as exc:
        raise map_domain_error(exc) from exc
