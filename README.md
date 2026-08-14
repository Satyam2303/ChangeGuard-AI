# ChangeGuard AI

ChangeGuard AI is a hackathon MVP for validating AI-generated software changes before a human approves them. It creates a bounded change plan, executes the proposed modification only inside an ephemeral Daytona sandbox, runs the original and changed test suites, calculates deterministic risk, and requires an explicit approval or rejection.

## Proven demo flow

```text
Natural-language request
        ↓
Bounded AI change plan
        ↓
Human starts validation
        ↓
Ephemeral Daytona sandbox
        ↓
Baseline pytest → isolated change → regression pytest
        ↓
Deterministic risk report
        ↓
Human approval or rejection (no deployment)
```

Two controlled examples are built into the UI:

- `2 → 5 seconds`: tests pass, risk `18 / LOW`, recommendation `APPROVE`.
- `2 → 60 seconds`: policy test fails, risk `87 / HIGH`, recommendation `REJECT`; approval is blocked.

## Architecture

```text
React + Vite
    │ HTTP
FastAPI ─── In-memory change store
    ├── OpenAI structured planner (optional feature flag)
    ├── Deterministic risk engine
    └── Daytona SDK
          └── isolated copy of demo-repo + pytest
```

Generated code is never executed on the backend host. The backend only applies a literal, prevalidated `config.py` replacement inside Daytona. Every sandbox is deleted after evidence is collected. Approval never means deployment.

## Project layout

```text
frontend/                React workflow UI
backend/app/             FastAPI routes and services
backend/tests/           API and risk unit tests
demo-repo/               Controlled payment service target
test_daytona.py          Daytona connectivity smoke test
```

## Configure

Copy `.env.example` to `.env` and enter replacement credentials locally:

```env
DAYTONA_API_KEY=...
OPENAI_API_KEY=...
USE_OPENAI_PLANNER=false
OPENAI_MODEL=gpt-5.4-mini
```

`.env` is ignored by Git. Keep `USE_OPENAI_PLANNER=false` for the deterministic judging path. Set it to `true` only when you want OpenAI to produce the bounded structured plan; Daytona execution and deterministic risk remain unchanged.

## Run

Terminal 1:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Terminal 2:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. FastAPI documentation is available at `http://localhost:8000/docs`.

## Verify

```powershell
cd demo-repo
python -m pytest -q

cd ..\backend
$env:PYTHONPATH=(Get-Location).Path
python -m pytest -q

cd ..\frontend
npm run build
```

The real sandbox milestone has been verified for both examples: Daytona created the environment, ran the clean baseline, applied the isolated change, reran pytest, and returned evidence used by the risk engine.

## API

- `POST /api/changes`
- `GET /api/changes`
- `GET /api/changes/{id}`
- `POST /api/changes/{id}/validate`
- `GET /api/changes/{id}/validation`
- `POST /api/changes/{id}/approve`
- `POST /api/changes/{id}/reject`

## Deliberate MVP boundaries

There is no production deployment, authentication, GitHub PR mutation, Kubernetes, message queue, vector database, or complex persistence layer. Enterprise SSO, multi-tenancy, immutable long-term evidence storage, GitHub App integration, policy administration, and compliance exports belong to the roadmap described by the Forge artifacts, not this one-day MVP.

