from typing import Any


def calculate_risk(
    *,
    tests_failed: int,
    files_changed: list[str],
    requested_timeout: int | None,
    execution_error: bool = False,
) -> dict[str, Any]:
    score = 8
    reasons = ["Change scope is limited and explicit"]

    if any(path.endswith("config.py") for path in files_changed):
        score += 10
        reasons.append("Runtime configuration is modified")

    if tests_failed:
        score += 60
        reasons.append(f"{tests_failed} regression test(s) failed")
    else:
        reasons.append("All sandbox tests passed")

    if requested_timeout is not None and requested_timeout > 10:
        score += 9
        reasons.append("Timeout exceeds the enterprise safety threshold")

    if len(files_changed) > 5:
        score += 15
        reasons.append("More than five files are modified")

    if any(path.endswith(("requirements.txt", "pyproject.toml")) for path in files_changed):
        score += 10
        reasons.append("Dependency manifest is modified")

    if execution_error:
        score = 100
        reasons.append("Validation infrastructure failed; policy fails closed")

    score = min(score, 100)
    level = "low" if score <= 30 else "medium" if score <= 60 else "high"
    recommendation = "approve" if tests_failed == 0 and not execution_error else "reject"
    return {
        "score": score,
        "level": level,
        "reasons": reasons,
        "recommendation": recommendation,
    }

