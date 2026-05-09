"""Common pagination and response schemas."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: list[T]
    total: int = Field(..., description="Total number of records matching the query.")
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=200)
