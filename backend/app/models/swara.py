"""Swara mapping models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Swara(BaseModel):
    """One swara label with symbol and cents offset from Sa."""

    label: str
    symbol: str
    cents_from_sa: float


class SwaraMapResponse(BaseModel):
    """Response for GET /swara-map."""

    items: list[Swara] = Field(default_factory=list)
