from __future__ import annotations

from datetime import UTC, datetime
from threading import Lock

from ..models import ChangeRecord
from ..schemas import ChangePlan


class ChangeStore:
    def __init__(self) -> None:
        self._changes: dict[str, ChangeRecord] = {}
        self._counter = 0
        self._lock = Lock()

    def create(self, request: str, plan: ChangePlan) -> ChangeRecord:
        with self._lock:
            self._counter += 1
            change_id = f"CG-{self._counter:03d}"
            record = ChangeRecord(
                id=change_id,
                request=request,
                title=plan.title,
                initial_risk=plan.risk_level,
                files=plan.affected_files,
                plan=plan,
            )
            self._changes[change_id] = record
            return record

    def get(self, change_id: str) -> ChangeRecord | None:
        return self._changes.get(change_id)

    def list(self) -> list[ChangeRecord]:
        return list(reversed(self._changes.values()))

    def save(self, record: ChangeRecord) -> ChangeRecord:
        record.updated_at = datetime.now(UTC)
        self._changes[record.id] = record
        return record


change_store = ChangeStore()

