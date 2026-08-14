from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.changes import router as changes_router


load_dotenv()

app = FastAPI(
    title="ChangeGuard AI",
    description="Human-governed validation of AI-generated changes in Daytona sandboxes.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(changes_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ChangeGuard AI"}

