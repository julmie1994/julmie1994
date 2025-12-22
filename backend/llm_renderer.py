"""Optional LLM renderer for ATC responses.

This module is strictly optional and never decides correctness. It only
receives structured data and formats a response with markers.
"""
from __future__ import annotations

import json
import os
from typing import Mapping, Optional
from urllib import request


def _build_payload(
    *,
    state: str,
    scenario: str,
    slots: Mapping[str, object],
    validation: Mapping[str, object],
    fallback: str,
) -> dict[str, object]:
    return {
        "state": state,
        "scenario": scenario,
        "slots": slots,
        "validation": validation,
        "fallback": fallback,
        "instructions": (
            "Return an ATC response in ICAO English. "
            "Wrap the final output in <ATC>...</ATC> and do not invent slots."
        ),
    }


def render_with_llm(
    *,
    state: str,
    scenario: str,
    slots: Mapping[str, object],
    validation: Mapping[str, object],
    fallback: str,
) -> Optional[str]:
    endpoint = os.getenv("LLM_ENDPOINT")
    if not endpoint:
        return None

    payload = _build_payload(
        state=state,
        scenario=scenario,
        slots=slots,
        validation=validation,
        fallback=fallback,
    )
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(endpoint, data=data, headers={"Content-Type": "application/json"})
    try:
        with request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
    except Exception:
        return None

    try:
        parsed = json.loads(body)
        return parsed.get("text")
    except json.JSONDecodeError:
        return None
