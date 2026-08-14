from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..models import ChangeRecord
from ..schemas import ChangeRequest, DecisionRequest
from ..services.ai_service import create_plan
from ..services.change_service import change_store
from ..services.daytona_service import DaytonaService


router = APIRouter(prefix="/api/changes", tags=["changes"])
DEMO_REPO = Path(__file__).resolve().parents[3] / "demo-repo"


def _get_change(change_id: str) -> ChangeRecord:
    record = change_store.get(change_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Change not found")
    return record


@router.get("")
def list_changes() -> list[ChangeRecord]:
    return change_store.list()


@router.post("", status_code=201)
def create_change(payload: ChangeRequest) -> ChangeRecord:
    try:
        plan = create_plan(payload.request)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Unable to create a safe plan: {exc}") from exc
    return change_store.create(payload.request, plan)


@router.get("/{change_id}")
def get_change(change_id: str) -> ChangeRecord:
    return _get_change(change_id)


@router.post("/{change_id}/validate")
def validate_change(change_id: str) -> ChangeRecord:
    record = _get_change(change_id)
    if record.status in {"approved", "rejected"}:
        raise HTTPException(status_code=409, detail="A decided change cannot be revalidated")
    record.status = "validating"
    change_store.save(record)
    record.validation = DaytonaService(DEMO_REPO).validate(record.plan)
    record.status = "validated" if record.validation["overall_status"] == "safe_to_approve" else "blocked"
    return change_store.save(record)


@router.get("/{change_id}/validation")
def get_validation(change_id: str) -> dict:
    record = _get_change(change_id)
    if record.validation is None:
        raise HTTPException(status_code=404, detail="Validation has not been run")
    return record.validation


@router.post("/{change_id}/approve")
def approve_change(change_id: str, payload: DecisionRequest) -> ChangeRecord:
    record = _get_change(change_id)
    if not record.validation or record.validation["overall_status"] != "safe_to_approve":
        raise HTTPException(status_code=409, detail="Only a passing validation can be approved")
    record.status = "approved"
    record.approved_by = payload.reviewer
    record.decision_rationale = payload.rationale
    return change_store.save(record)


@router.post("/{change_id}/reject")
def reject_change(change_id: str, payload: DecisionRequest) -> ChangeRecord:
    record = _get_change(change_id)
    if record.validation is None:
        raise HTTPException(status_code=409, detail="Run validation before making a decision")
    record.status = "rejected"
    record.rejected_by = payload.reviewer
    record.decision_rationale = payload.rationale
    return change_store.save(record)

