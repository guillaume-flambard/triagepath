"""Ops Autopilot — FastAPI wrapper around the run-analysis graph.

Exposes the same entry points as the CLI (`graph.cli run`) over HTTP so the
agent lab can call it remotely. Provider default: mock (deterministic, no key).
"""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.presets import load_preset
from app.run_analysis import analyze_website, build_runtime, run_analysis
from domain.models import Assumptions, BrandProfile, Sector

app = FastAPI(title="Ops Autopilot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class AnalysisResponse(BaseModel):
    thread_id: str
    final: dict = Field(default_factory=dict)
    interrupted: dict | None = None
    events: list[tuple[str, str]] = Field(default_factory=list)


def _runtime(req: AnalysisRequest):
    return build_runtime(
        provider=req.llm_provider,
        api_key=os.environ.get("GROQ_API_KEY", ""),
        model=req.model,
        checkpoint_db=os.environ.get("CHECKPOINT_DB", "ops_autopilot_checkpoints.db"),
        ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ops-autopilot"}


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(req: AnalysisRequest) -> AnalysisResponse:
    runtime = _runtime(req)

    try:
        if req.url:
            brand = analyze_website(
                url=req.url,
                provider=req.llm_provider,
                api_key=os.environ.get("GROQ_API_KEY", ""),
                model=req.model,
                ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            )
        elif req.preset:
            brand = load_preset(req.preset)
        elif req.name or req.free_text:
            if not req.name:
                raise HTTPException(status_code=422, detail="name is required without preset/url")
            sector = Sector(req.sector.upper()) if req.sector else Sector.OTHER
            brand = BrandProfile(
                name=req.name,
                sector=sector,
                team_size=req.team_size,
                free_text=req.free_text,
                notes=req.free_text,
            )
        else:
            raise HTTPException(status_code=422, detail="provide preset, url, name or free_text")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"brand build failed: {e}")

    assumptions = Assumptions(
        hourly_rate_eur=req.hourly_rate,
        weeks_per_month=req.weeks_per_month,
    )
    if brand.default_assumptions:
        assumptions = brand.default_assumptions

    try:
        result = run_analysis(brand=brand, assumptions=assumptions, runtime=runtime)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"analysis failed: {e}")

    return AnalysisResponse(
        thread_id=result.thread_id,
        final=result.final or {},
        interrupted=result.interrupted,
        events=result.events or [],
    )
