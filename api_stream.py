"""triagepath — streaming API (SSE) over the analysis graph.

WS1 (React streaming frontend): the JD wants streaming responses, intermediate
output display, reasoning transparency, and a human-review (escalation) UI.
This module turns the existing graph stream into Server-Sent Events so a React
frontend can render the agent's live timeline as it runs, then resume at the
human-review interrupt.

Run: uvicorn api_stream:app --reload  (or import app from api.py)
"""

from __future__ import annotations

import json
import os
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.presets import load_preset
from app.run_analysis import analyze_website, build_runtime, resume_review, run_analysis
from domain.models import Assumptions, BrandProfile, Sector

router = APIRouter(prefix="/api")


class AnalysisRequest(BaseModel):
    name: str = Field(default="", description="Business name (required unless url/preset)")
    sector: str = Field(default="", description="Sector: D2C, B2B, SaaS, ...")
    free_text: str = Field(default="", description="Free-form description of the business")
    preset: str | None = Field(default=None, description="Preset profile: lumea, saas")
    url: str = Field(default="", description="Analyze a website (LLM extracts brand + tasks)")
    team_size: int = Field(default=1, ge=1)
    hourly_rate: float = Field(default=50.0, gt=0)
    weeks_per_month: float = Field(default=4.33, gt=0)
    llm_provider: str = Field(default="mock", description="mock, ollama or groq")
    model: str = Field(default="llama-3.3-70b-versatile")


class ReviewRequest(BaseModel):
    thread_id: str
    action: str = Field(..., description="approve, edit or reject")
    hourly_rate: float | None = None
    weeks_per_month: float | None = None
    tasks: list | None = None


def _runtime(req: AnalysisRequest):
    return build_runtime(
        provider=req.llm_provider,
        api_key=os.environ.get("GROQ_API_KEY", ""),
        model=req.model,
        checkpoint_db=os.environ.get("CHECKPOINT_DB", "triagepath_checkpoints.db"),
        ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
    )


def _build_brand(req: AnalysisRequest) -> BrandProfile:
    if req.url:
        return analyze_website(
            url=req.url,
            provider=req.llm_provider,
            api_key=os.environ.get("GROQ_API_KEY", ""),
            model=req.model,
            ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    if req.preset:
        return load_preset(req.preset)
    if not req.name:
        raise HTTPException(status_code=422, detail="name is required without preset/url")
    sector = Sector(req.sector.upper()) if req.sector else Sector.OTHER
    return BrandProfile(
        name=req.name,
        sector=sector,
        team_size=req.team_size,
        free_text=req.free_text,
        notes=req.free_text,
    )


def _sse(event: str, data: dict) -> str:
    """Serialize one SSE frame."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"


def drive_stream(app, config: dict, payload):
    """Yield one (event, data) frame per graph chunk.

    Mirrors ``graph.driver.drive`` but streams each chunk instead of collecting
    them all, so the frontend sees nodes light up in real time (reasoning
    transparency). ``__interrupt__`` (human review) is surfaced as its own event.
    """
    final: dict = {}
    for chunk in app.stream(payload, config=config):
        for key, update in chunk.items():
            if key == "__interrupt__":
                yield ("interrupt", {"payload": update[0].value})
                continue
            events = update.get("events") or []
            final.update(update)
            if events:
                yield ("node", {"node": key, "message": events[0]})
    yield ("done", {"final": final, "thread_id": config["configurable"]["thread_id"]})


@router.post("/analyze/stream")
def analyze_stream(req: AnalysisRequest):
    """Stream an analysis as Server-Sent Events."""
    try:
        brand = _build_brand(req)
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"brand build failed: {e}")

    assumptions = Assumptions(hourly_rate_eur=req.hourly_rate, weeks_per_month=req.weeks_per_month)
    if brand.default_assumptions:
        assumptions = brand.default_assumptions

    runtime = _runtime(req)
    thread_id = f"run-{int(time.time() * 1000)}"
    config = {"configurable": {"thread_id": thread_id}}

    def gen():
        yield _sse("thread", {"thread_id": thread_id})
        try:
            for event, data in drive_stream(runtime.app, config, {"brand": brand, "assumptions": assumptions}):
                yield _sse(event, data)
        except Exception as e:  # noqa: BLE001
            yield _sse("error", {"message": str(e)})

    return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.post("/review")
def review(req: ReviewRequest):
    """Resume a paused run at the human-review interrupt."""
    config = {"configurable": {"thread_id": req.thread_id}}
    runtime = _runtime(AnalysisRequest())
    assumptions = None
    if req.hourly_rate is not None or req.weeks_per_month is not None:
        assumptions = Assumptions(
            hourly_rate_eur=req.hourly_rate if req.hourly_rate is not None else 50.0,
            weeks_per_month=req.weeks_per_month if req.weeks_per_month is not None else 4.33,
        )
    try:
        result = resume_review(runtime, config, req.action, assumptions=assumptions, tasks=req.tasks)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"resume failed: {e}")
    return {"thread_id": req.thread_id, "final": result.final or {}, "events": result.events or []}


# Re-export the sync single-shot endpoint under the same prefix for compat.
def _sync_analyze(req: AnalysisRequest):
    brand = _build_brand(req)
    assumptions = Assumptions(hourly_rate_eur=req.hourly_rate, weeks_per_month=req.weeks_per_month)
    if brand.default_assumptions:
        assumptions = brand.default_assumptions
    runtime = _runtime(req)
    result = run_analysis(brand=brand, assumptions=assumptions, runtime=runtime)
    return {"thread_id": result.thread_id, "final": result.final or {}, "interrupted": result.interrupted, "events": result.events or []}
