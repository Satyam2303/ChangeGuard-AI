import os
import re

from openai import OpenAI

from ..schemas import ChangePlan


SAFE_REQUEST = "Increase the payment API timeout from 2 seconds to 5 seconds."
DANGEROUS_REQUEST = "Increase the payment API timeout from 2 seconds to 60 seconds."


def _timeout_from_request(request: str) -> int:
    matches = re.findall(r"\b(\d+)\s*(?:seconds?|s)\b", request.lower())
    return int(matches[-1]) if matches else 5


def hardcoded_plan(request: str) -> ChangePlan:
    if "payment" not in request.lower() or "timeout" not in request.lower():
        raise ValueError("The deterministic MVP supports payment timeout requests only")
    timeout = _timeout_from_request(request)
    risk = "medium" if timeout <= 10 else "high"
    return ChangePlan(
        title="Increase payment timeout",
        summary=f"Update the payment API timeout from 2 seconds to {timeout} seconds.",
        risk_level=risk,
        affected_files=["config.py"],
        changes=[
            {
                "file": "config.py",
                "old_code": "PAYMENT_TIMEOUT = 2",
                "new_code": f"PAYMENT_TIMEOUT = {timeout}",
                "reason": "Apply the requested payment timeout configuration change.",
            }
        ],
    )


def create_plan(request: str) -> ChangePlan:
    if os.getenv("USE_OPENAI_PLANNER", "false").lower() != "true":
        return hardcoded_plan(request)

    client = OpenAI()
    response = client.responses.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
        input=(
            "You are an enterprise software change planner. Do not execute code. "
            "The available repository contains config.py with PAYMENT_TIMEOUT = 2. "
            "Only propose a literal replacement in config.py. Return JSON with keys "
            "title, summary, risk_level, affected_files, and changes; each change has "
            "file, old_code, new_code, reason. Request: " + request
        ),
        text_format=ChangePlan,
    )
    plan = response.output_parsed
    if plan is None:
        raise ValueError("Planner did not return a structured change plan")
    if len(plan.changes) != 1 or plan.affected_files != ["config.py"]:
        raise ValueError("Planner proposed a change outside the MVP safety boundary")
    for change in plan.changes:
        if (
            change.file != "config.py"
            or change.old_code != "PAYMENT_TIMEOUT = 2"
            or re.fullmatch(r"PAYMENT_TIMEOUT = \d+", change.new_code) is None
        ):
            raise ValueError("Planner proposed a change outside the MVP safety boundary")
    return plan
