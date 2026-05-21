"""API error response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Structured API error returned to clients."""

    error_code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
