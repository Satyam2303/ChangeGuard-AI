from typing import Literal

from pydantic import BaseModel, Field


class ChangeRequest(BaseModel):
    request: str = Field(min_length=5, max_length=1000)


class CodeChange(BaseModel):
    file: str
    old_code: str
    new_code: str
    reason: str


class ChangePlan(BaseModel):
    title: str
    summary: str
    risk_level: Literal["low", "medium", "high"]
    affected_files: list[str]
    changes: list[CodeChange]


class DecisionRequest(BaseModel):
    reviewer: str = "Human Reviewer"
    rationale: str = "Reviewed validation evidence."

