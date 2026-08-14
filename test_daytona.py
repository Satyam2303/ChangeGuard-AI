"""Smoke test for Daytona sandbox creation and command execution."""

from dotenv import load_dotenv

from daytona import Daytona


load_dotenv()

daytona = Daytona()
sandbox = None
try:
    sandbox = daytona.create()
    response = sandbox.process.exec(
        "echo 'ChangeGuard Daytona sandbox working'"
    )

    if response.exit_code != 0:
        raise RuntimeError(
            f"Sandbox command failed ({response.exit_code}): {response.result}"
        )

    print(response.result)
finally:
    if sandbox is not None:
        sandbox.delete(wait=False)
