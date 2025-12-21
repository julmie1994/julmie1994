"""Validation helpers for state-based slot extraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Any


@dataclass(frozen=True)
class SlotRule:
    name: str
    description: str


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _normalize_runway(value: Any) -> str:
    raw = _normalize_text(value)
    if not raw:
        return ""
    digits = "".join(ch for ch in raw if ch.isdigit())
    suffix = "".join(ch for ch in raw if ch.isalpha())
    return f"{digits}{suffix}" if digits else raw


STATE_EXPECTATIONS: dict[str, list[SlotRule]] = {
    "clearance": [
        SlotRule("callsign", "Aircraft callsign"),
        SlotRule("destination", "Destination airport"),
        SlotRule("runway", "Assigned runway"),
        SlotRule("qnh", "Altimeter setting (QNH)"),
    ],
    "taxi": [
        SlotRule("callsign", "Aircraft callsign"),
        SlotRule("runway", "Assigned runway"),
    ],
    "takeoff": [
        SlotRule("callsign", "Aircraft callsign"),
        SlotRule("runway", "Assigned runway"),
    ],
}


def _runway_matches(expected: Any, actual: Any) -> bool:
    expected_norm = _normalize_runway(expected)
    actual_norm = _normalize_runway(actual)
    if not expected_norm or not actual_norm:
        return False

    expected_digits = "".join(ch for ch in expected_norm if ch.isdigit())
    actual_digits = "".join(ch for ch in actual_norm if ch.isdigit())

    if not expected_digits or not actual_digits:
        return expected_norm == actual_norm

    return expected_digits == actual_digits


def _qnh_valid(value: Any) -> bool:
    text = _normalize_text(value)
    if not text:
        return False
    if not text.isdigit():
        return False
    qnh = int(text)
    return 900 <= qnh <= 1100


def validate(state: str, slots: Mapping[str, Any], normalized_text: str | None = None) -> dict[str, Any]:
    """Validate extracted slots for a given conversation state.

    Args:
        state: Current dialog state.
        slots: Mapping of slot names to extracted values.
        normalized_text: Normalized utterance text (optional, used for richer feedback).

    Returns:
        dict with keys: ok, missing, wrong, score, reasons
    """
    expected_rules = STATE_EXPECTATIONS.get(state, [])
    missing: list[str] = []
    wrong: list[str] = []
    reasons: list[str] = []

    for rule in expected_rules:
        value = slots.get(rule.name)
        if value is None or _normalize_text(value) == "":
            missing.append(rule.name)
            reasons.append(f"missing: {rule.name}")
            continue

        if rule.name == "runway":
            expected_runway = slots.get("expected_runway", value)
            if not _runway_matches(expected_runway, value):
                wrong.append(rule.name)
                reasons.append(f"runway mismatch: expected {expected_runway}, got {value}")
        elif rule.name == "qnh":
            if not _qnh_valid(value):
                wrong.append(rule.name)
                reasons.append(f"invalid qnh: {value}")

    if not expected_rules:
        reasons.append("no expectations configured for state")

    total = len(expected_rules)
    correct = max(total - len(missing) - len(wrong), 0)
    score = (correct / total) if total else 1.0

    if normalized_text:
        reasons.append(f"checked text: {normalized_text}")

    return {
        "ok": not missing and not wrong,
        "missing": missing,
        "wrong": wrong,
        "score": round(score, 2),
        "reasons": reasons,
    }


def _self_test() -> None:
    tests: Iterable[tuple[str, dict[str, Any], str, dict[str, Any]]] = [
        (
            "clearance",
            {"callsign": "DLH1", "destination": "EDDF", "runway": "27L", "qnh": "1013"},
            "dlh1 cleared to eddf runway 27 qnh 1013",
            {"ok": True, "missing": [], "wrong": []},
        ),
        (
            "clearance",
            {"callsign": "DLH1", "destination": "EDDF", "runway": "27", "qnh": "950"},
            "dlh1 cleared to eddf runway 27",
            {"ok": True, "missing": [], "wrong": []},
        ),
        (
            "clearance",
            {"callsign": "DLH1", "destination": "EDDF", "runway": "09", "qnh": "abc"},
            "dlh1 cleared to eddf runway 09",
            {"ok": False, "missing": [], "wrong": ["qnh"]},
        ),
        (
            "taxi",
            {"callsign": "DLH1"},
            "taxi to holding point",
            {"ok": False, "missing": ["runway"], "wrong": []},
        ),
    ]

    for state, slots, text, expected in tests:
        result = validate(state, slots, text)
        assert result["ok"] == expected["ok"], result
        assert result["missing"] == expected["missing"], result
        assert result["wrong"] == expected["wrong"], result

    print("validator self-tests passed")


if __name__ == "__main__":
    _self_test()
