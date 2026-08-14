from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .schemas import ChangePlan


class ChangeRecord(BaseModel):
    id: str
    request: str
    title: str
    status: str = "planned"
    initial_risk: str
    files: list[str]
    plan: ChangePlan
    validation: dict[str, Any] | None = None
    approved_by: str | None = None
    rejected_by: str | None = None
    decision_rationale: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

