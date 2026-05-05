"""
FastAPI application for the Competitive Analysis Research Tool.

Exposes REST endpoints to submit analysis requests and retrieve results.
Runs the LangGraph in a background thread so the API remains responsive.

Endpoints:
    POST /analyze     — Submit a new competitive analysis request.
    GET  /analyze/{run_id} — Poll for the status and result of a run.
    GET  /health      — Health check.

Usage:
    uvicorn src.api:app --reload
"""

import uuid
import threading
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.graph.graph_builder import build_research_graph
from src.graph.state import ResearchState


# ---------------------------------------------------------------------------
# In-memory run store
# ---------------------------------------------------------------------------
# Maps run_id -> dict with keys: status, report, subtasks, errors, raw_state.
# Runs are ephemeral — lost on server restart. Swap for Redis/DB in production.
_runs: dict[str, dict[str, Any]] = {}

# Build the graph once at startup (shared across requests).
_graph = build_research_graph()

app = FastAPI(
    title="Competitive Analysis Tool",
    version="0.1.0",
    description="AI-powered competitive analysis using LangGraph, RAG, and web search.",
)


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze."""

    company: str
    model: str = "gpt-4o-mini"


class AnalyzeResponse(BaseModel):
    """Immediate response for a submitted analysis."""

    run_id: str
    status: str = "pending"


class RunStatusResponse(BaseModel):
    """Status and result of an analysis run."""

    run_id: str
    status: str
    report: str = ""
    subtasks: list[dict] = []
    errors: list[str] = []


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"


# ---------------------------------------------------------------------------
# Background execution helpers
# ---------------------------------------------------------------------------

def _execute_analysis(run_id: str, company: str, model: str) -> None:
    """Run the LangGraph in a background thread and store the result.

    Args:
        run_id: UUID string for this run.
        company: Company name to analyze.
        model: OpenAI model identifier.
    """
    try:
        _runs[run_id]["status"] = "running"

        initial_state: ResearchState = {
            "original_query": company,
            "subtasks": [],
            "current_subtask_idx": 0,
            "notes": [],
            "retry_count": 0,
            "max_retries": 3,
            "final_report": "",
            "errors": [],
        }

        final_state = _graph.invoke(
            initial_state,
            config={"configurable": {"thread_id": run_id}},
        )

        _runs[run_id].update({
            "status": "completed",
            "report": final_state.get("final_report", ""),
            "subtasks": final_state.get("subtasks", []),
            "errors": final_state.get("errors", []),
        })

    except Exception as exc:
        _runs[run_id].update({
            "status": "error",
            "errors": [str(exc)],
        })


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/analyze", response_model=AnalyzeResponse, status_code=202)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """Submit a competitive analysis request.

    The analysis runs in a background thread. Returns immediately with
    a ``run_id`` that can be used to poll for results via ``GET /analyze/{run_id}``.

    **Request body:**
    ```json
    { "company": "NVIDIA", "model": "gpt-4o-mini" }
    ```

    **Response (202 Accepted):**
    ```json
    { "run_id": "a1b2c3d4-...", "status": "pending" }
    ```
    """
    run_id = str(uuid.uuid4())
    _runs[run_id] = {"status": "pending", "report": "", "subtasks": [], "errors": []}

    thread = threading.Thread(
        target=_execute_analysis,
        args=(run_id, req.company, req.model),
        daemon=True,
    )
    thread.start()

    return AnalyzeResponse(run_id=run_id, status="pending")


@app.get("/analyze/{run_id}", response_model=RunStatusResponse)
async def get_analysis(run_id: str) -> RunStatusResponse:
    """Get the status and result of an analysis run.

    Poll this endpoint with the ``run_id`` returned from ``POST /analyze``.

    - While running: ``status`` is ``"pending"`` or ``"running"``.
    - When done: ``status`` is ``"completed"`` and ``report`` is populated.
    - On error: ``status`` is ``"error"`` and ``errors`` lists details.

    Args:
        run_id: UUID returned from POST /analyze.

    Returns:
        Run status, report Markdown, subtasks, and any errors.

    Raises:
        404: If the run_id does not exist.
    """
    run = _runs.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return RunStatusResponse(
        run_id=run_id,
        status=run.get("status", "unknown"),
        report=run.get("report", ""),
        subtasks=run.get("subtasks", []),
        errors=run.get("errors", []),
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint.

    Returns ``{ "status": "ok" }`` when the service is running.
    """
    return HealthResponse()