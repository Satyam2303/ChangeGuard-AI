from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from daytona import Daytona

from ..schemas import ChangePlan
from .risk_service import calculate_risk


class DaytonaService:
    def __init__(self, demo_repo: Path) -> None:
        self.daytona = Daytona()
        self.demo_repo = demo_repo

    @staticmethod
    def _test_count(output: str, label: str) -> int:
        match = re.search(rf"(\d+)\s+{label}", output)
        return int(match.group(1)) if match else 0

    def _upload_repo(self, sandbox: Any, remote_root: str) -> None:
        sandbox.fs.create_folder(remote_root, "755")
        sandbox.fs.create_folder(f"{remote_root}/tests", "755")
        for relative_path in (
            "app.py",
            "config.py",
            "requirements.txt",
            "tests/test_payment.py",
        ):
            sandbox.fs.upload_file(
                str(self.demo_repo / relative_path),
                f"{remote_root}/{relative_path}",
            )

    def validate(self, plan: ChangePlan) -> dict[str, Any]:
        started = time.perf_counter()
        sandbox = None
        remote_root = "/home/daytona/changeguard-demo"
        steps: list[dict[str, str]] = []
        logs: list[str] = []
        try:
            sandbox = self.daytona.create()
            steps.append({"name": "Creating Daytona sandbox", "status": "passed"})
            sandbox_id = sandbox.id

            self._upload_repo(sandbox, remote_root)
            steps.append({"name": "Uploading repository", "status": "passed"})

            install = sandbox.process.exec(
                "python -m pip install -r requirements.txt",
                cwd=remote_root,
                timeout=180,
            )
            logs.append(f"$ python -m pip install -r requirements.txt\n{install.result}")
            if install.exit_code != 0:
                raise RuntimeError(f"Dependency installation failed: {install.result}")
            steps.append({"name": "Installing dependencies", "status": "passed"})

            baseline = sandbox.process.exec(
                "python -m pytest -v",
                cwd=remote_root,
                timeout=120,
            )
            logs.append(f"$ python -m pytest -v  # baseline\n{baseline.result}")
            if baseline.exit_code != 0:
                raise RuntimeError(f"Baseline tests failed: {baseline.result}")
            steps.append({"name": "Running baseline tests", "status": "passed"})

            for change in plan.changes:
                if change.file != "config.py":
                    raise ValueError("MVP only permits changes to config.py")
                target = f"{remote_root}/{change.file}"
                content = sandbox.fs.download_file(target).decode("utf-8")
                if change.old_code not in content:
                    raise ValueError(f"Expected code not found in {change.file}")
                sandbox.fs.upload_file(
                    content.replace(change.old_code, change.new_code, 1).encode("utf-8"),
                    target,
                )
            steps.append({"name": "Applying AI-generated change", "status": "passed"})

            changed = sandbox.process.exec(
                "python -m pytest -v",
                cwd=remote_root,
                timeout=120,
            )
            logs.append(f"$ python -m pytest -v  # after change\n{changed.result}")
            passed = self._test_count(changed.result, "passed")
            failed = self._test_count(changed.result, "failed")
            steps.append(
                {
                    "name": "Running regression tests",
                    "status": "passed" if changed.exit_code == 0 else "failed",
                }
            )

            timeout_match = re.search(r"PAYMENT_TIMEOUT\s*=\s*(\d+)", plan.changes[0].new_code)
            timeout = int(timeout_match.group(1)) if timeout_match else None
            risk = calculate_risk(
                tests_failed=failed or (1 if changed.exit_code else 0),
                files_changed=plan.affected_files,
                requested_timeout=timeout,
            )
            steps.append({"name": "Calculating deterministic risk", "status": "passed"})
            steps.append({"name": "Generating validation report", "status": "passed"})
            return {
                "sandbox_id": sandbox_id,
                "sandbox_status": "created",
                "baseline": {"passed": True, "output": baseline.result},
                "after_change": {
                    "passed": changed.exit_code == 0,
                    "tests_passed": passed,
                    "tests_failed": failed,
                    "exit_code": changed.exit_code,
                    "output": changed.result,
                },
                "risk": risk,
                "steps": steps,
                "terminal_output": "\n\n".join(logs),
                "execution_time_seconds": round(time.perf_counter() - started, 2),
                "overall_status": "safe_to_approve" if changed.exit_code == 0 else "blocked",
            }
        except Exception as exc:
            steps.append({"name": "Validation failed closed", "status": "failed"})
            return {
                "sandbox_id": getattr(sandbox, "id", None),
                "sandbox_status": "error",
                "baseline": {"passed": False},
                "after_change": {"passed": False, "tests_passed": 0, "tests_failed": 1},
                "risk": calculate_risk(
                    tests_failed=1,
                    files_changed=plan.affected_files,
                    requested_timeout=None,
                    execution_error=True,
                ),
                "steps": steps,
                "terminal_output": "\n\n".join(logs),
                "error": str(exc),
                "execution_time_seconds": round(time.perf_counter() - started, 2),
                "overall_status": "blocked",
            }
        finally:
            if sandbox is not None:
                try:
                    sandbox.delete(wait=False)
                except Exception:
                    pass

