"""FastAPI app for ICAO VFR training demo.

This is a minimal runnable web app that exposes the STT pipeline and serves
a lightweight frontend to exercise the state machine.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.stt_audio import STTTranscript, transcribe_audio
from backend.stt_handler import handle_stt

BASE_DIR = Path(__file__).resolve().parents[1]


def _find_frontend_dir() -> Optional[Path]:
    candidates = [
        BASE_DIR / "frontend",
        Path.cwd() / "frontend",
        Path(__file__).resolve().parent / "frontend",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


FRONTEND_DIR = _find_frontend_dir()

app = FastAPI(title="ICAO VFR Trainer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class STTRequest(BaseModel):
    text: str = Field(..., description="Raw STT transcript or manual input.")
    state: str = Field(..., description="Current dialog state.")
    scenario: str = Field("graz_vfr_sector_e", description="Scenario identifier.")
    current_slots: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional known slots for validation."
    )


class STTResponse(BaseModel):
    text: str
    state: str
    normalized: str
    tokens: list[dict[str, Any]]
    slots: dict[str, Any]
    validation: dict[str, Any]
    next_state: str
    segments: Optional[list[dict[str, Any]]] = None
    atc_response: Optional[dict[str, Any]] = None


@app.get("/health")
def health() -> Mapping[str, str]:
    return {"status": "ok"}


@app.post("/stt", response_model=STTResponse)
def stt_endpoint(payload: STTRequest) -> Mapping[str, Any]:
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="text must not be empty")
    result = handle_stt(
        payload.text,
        payload.state,
        current_slots=payload.current_slots,
        scenario=payload.scenario,
    )
    return result


@app.post("/stt/audio", response_model=STTResponse)
async def stt_audio_endpoint(
    audio: UploadFile = File(...),
    state: str = Form(...),
    scenario: str = Form("graz_vfr_sector_e"),
    current_slots: Optional[str] = Form(None),
) -> Mapping[str, Any]:
    try:
        audio_bytes = await audio.read()
    except Exception as exc:  # pragma: no cover - transport errors
        raise HTTPException(status_code=400, detail=f"failed to read audio: {exc}") from exc

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="audio payload is empty")

    try:
        transcript = transcribe_audio(audio_bytes, language="en", filename=audio.filename)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="STT engine unavailable or failed to decode audio.",
        ) from exc

    parsed_slots: Optional[Dict[str, Any]] = None
    if current_slots:
        try:
            parsed_slots = json.loads(current_slots)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="current_slots must be valid JSON") from exc

    result = handle_stt(
        transcript.text,
        state,
        current_slots=parsed_slots,
        scenario=scenario,
    )
    result["segments"] = [
        {
            "text": segment.text,
            "start": segment.start,
            "end": segment.end,
            "avg_logprob": segment.avg_logprob,
            "no_speech_prob": segment.no_speech_prob,
            "compression_ratio": segment.compression_ratio,
        }
        for segment in transcript.segments
    ]
    return result


if FRONTEND_DIR:
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    if not FRONTEND_DIR:
        return HTMLResponse(
            "<h2>Frontend not available</h2><p>Run from the repo root so /frontend is visible.</p>",
            status_code=200,
        )
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse(
            "<h2>Frontend not available</h2><p>Missing frontend/index.html.</p>",
            status_code=200,
        )
    return FileResponse(index_path)
