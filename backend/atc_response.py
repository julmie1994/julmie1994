"""Deterministic ATC response generator.

This module renders ATC responses from the current state, extracted slots,
and validation output. It never uses an LLM.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping, Optional

from backend.state_machine import get_state
from backend.llm_renderer import render_with_llm


@dataclass(frozen=True)
class ATCResponse:
    text: str
    reason: str
    renderer: str


_MISSING_PROMPTS: dict[str, str] = {
    "callsign": "say again callsign",
    "position": "report position",
    "runway": "confirm runway",
    "qnh": "confirm QNH",
    "holding_point": "report holding point",
    "sector": "report sector",
    "altitude": "report altitude",
    "wind": "report wind",
    "time": "report time",
}


def _render_template(template: str, slots: Mapping[str, object]) -> str:
    try:
        return template.format(**slots)
    except KeyError:
        return template


def build_atc_response(
    state: str,
    *,
    scenario: str,
    slots: Mapping[str, object],
    validation: Mapping[str, object],
) -> ATCResponse:
    state_def = get_state(state, scenario=scenario)
    missing = validation.get("missing") or []
    wrong = validation.get("wrong") or []

    if missing:
        prompt = _MISSING_PROMPTS.get(str(missing[0]), f"report {missing[0]}")
        return ATCResponse(text=prompt, reason="missing_slot", renderer="deterministic")

    if wrong:
        return ATCResponse(text=f"confirm {wrong[0]}", reason="wrong_slot", renderer="deterministic")

    if state_def and state_def.atc_templates:
        rendered = _render_template(state_def.atc_templates[0], slots)
        response = ATCResponse(text=rendered, reason="template", renderer="deterministic")
    else:
        response = ATCResponse(text="roger", reason="default", renderer="deterministic")

    if os.getenv("LLM_RENDERER", "").lower() in {"1", "true", "yes"}:
        llm_text = render_with_llm(
            state=state,
            scenario=scenario,
            slots=slots,
            validation=validation,
            fallback=response.text,
        )
        if llm_text:
            return ATCResponse(text=llm_text, reason=response.reason, renderer="llm")
    return response
