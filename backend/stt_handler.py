"""STT handler utilities.

Example response payload:
    {
        "text": "Delta alpha bravo charlie runway two seven left",
        "state": "taxi",
        "normalized": "D-ABC runway 27 L",
        "tokens": [
            {"raw": "delta", "normalized": "D", "kind": "nato", "confidence": 1.0},
            {"raw": "alpha", "normalized": "A", "kind": "nato", "confidence": 1.0},
            {"raw": "bravo", "normalized": "B", "kind": "nato", "confidence": 1.0},
            {"raw": "charlie", "normalized": "C", "kind": "nato", "confidence": 1.0},
            {"raw": "runway", "normalized": "runway", "kind": "word", "confidence": 1.0},
            {"raw": "two", "normalized": "2", "kind": "number", "confidence": 1.0},
            {"raw": "seven", "normalized": "7", "kind": "number", "confidence": 1.0},
            {"raw": "left", "normalized": "left", "kind": "word", "confidence": 1.0}
        ],
        "slots": {
            "callsign": {"value": "D-ABC", "confidence": 1.0, "raw_tokens": ["delta", "alpha", "bravo", "charlie"]},
            "runway": {"value": "27L", "confidence": 1.0, "raw_tokens": ["runway", "two", "seven", "left"]}
        },
        "validation": {
            "ok": true,
            "missing": [],
            "wrong": [],
            "score": 1.0,
            "reasons": ["checked text: D-ABC runway 27 L"]
        }
    }
"""
from __future__ import annotations

from typing import Any, Mapping

from backend.atc_response import build_atc_response
from backend.normalizer import normalize_icao
from backend.parsers import parse_all
from backend.state_machine import advance_state
from backend.validator import validate


def handle_stt(
    stt_text: str,
    state: str,
    *,
    current_slots: Mapping[str, Any] | None = None,
    scenario: str = "graz_vfr_sector_e",
) -> dict[str, Any]:
    """Process STT output into normalized text, parsed slots, and validation.

    Args:
        stt_text: Raw STT transcript.
        state: Current dialog state for validation.
        current_slots: Optional mapping of already known slot values
            (e.g., expected_runway) that should be included during validation.

    Returns:
        JSON-serializable dict including legacy fields (text, state) plus
        normalized, tokens, slots, and validation.
    """
    normalization = normalize_icao(stt_text)
    parsed_slots = parse_all(normalization)
    slot_values = {name: slot.value for name, slot in parsed_slots.items()}

    merged_slots = dict(current_slots or {})
    merged_slots.update(slot_values)

    validation = validate(
        state,
        merged_slots,
        normalized_text=normalization.normalized_text,
        scenario=scenario,
    )
    next_state = advance_state(state, validation, scenario=scenario)
    atc_response = build_atc_response(
        state,
        scenario=scenario,
        slots=merged_slots,
        validation=validation,
    )

    return {
        "text": stt_text,
        "state": state,
        "normalized": normalization.normalized_text,
        "tokens": [
            {
                "raw": token.raw,
                "normalized": token.normalized,
                "kind": token.kind,
                "confidence": token.confidence,
            }
            for token in normalization.tokens
        ],
        "slots": {
            name: {
                "value": slot.value,
                "confidence": slot.confidence,
                "raw_tokens": slot.raw_tokens,
            }
            for name, slot in parsed_slots.items()
        },
        "validation": validation,
        "next_state": next_state,
        "atc_response": {
            "text": atc_response.text,
            "reason": atc_response.reason,
            "renderer": atc_response.renderer,
        },
    }
