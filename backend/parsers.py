"""Deterministic parsers for ICAO phraseology slots.

Parsers are intentionally lightweight and only interpret normalized tokens. They
are tolerant but never authoritative; the validator decides correctness.

Supported slots:
- Callsign (e.g., D-ABCD, OE-ABC, G-EZJK)
- Runway (e.g., 27, 09L)
- Altitude (e.g., 2500)
- Flight Level (e.g., FL100)
- QNH (e.g., 1013)
- Squawk (e.g., 4521)
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from backend.normalizer import NormalizationResult, Token, normalize_icao


@dataclass(frozen=True)
class ParsedSlot:
    name: str
    value: str
    confidence: float
    raw_tokens: List[str]


CALLSIGN_RE = re.compile(r"^(?P<prefix>[A-Z]{1,2})-?(?P<body>[A-Z0-9]{2,5})$")
RUNWAY_SUFFIX = {
    "l": "L",
    "left": "L",
    "r": "R",
    "right": "R",
    "c": "C",
    "center": "C",
    "centre": "C",
}


def parse_callsign(tokens: List[Token]) -> Optional[ParsedSlot]:
    """Parse callsign tokens into a normalized ICAO callsign string."""
    for idx, token in enumerate(tokens):
        value = token.normalized
        if CALLSIGN_RE.match(value):
            return ParsedSlot(name="callsign", value=value, confidence=token.confidence, raw_tokens=[token.raw])

        if idx + 1 < len(tokens):
            next_token = tokens[idx + 1]
            combined = f"{value}-{next_token.normalized}"
            if CALLSIGN_RE.match(combined):
                return ParsedSlot(
                    name="callsign",
                    value=combined,
                    confidence=min(token.confidence, next_token.confidence),
                    raw_tokens=[token.raw, next_token.raw],
                )

    nato_run: List[Token] = []
    for token in tokens + [Token(raw="", normalized="", kind="word", confidence=1.0)]:
        if token.kind == "nato":
            nato_run.append(token)
            continue

        if len(nato_run) >= 3:
            letters = "".join(item.normalized for item in nato_run)
            for prefix_len in (1, 2):
                if len(letters) > prefix_len:
                    candidate = f"{letters[:prefix_len]}-{letters[prefix_len:]}"
                    if CALLSIGN_RE.match(candidate):
                        return ParsedSlot(
                            name="callsign",
                            value=candidate,
                            confidence=min(item.confidence for item in nato_run),
                            raw_tokens=[item.raw for item in nato_run],
                        )
        nato_run = []

    return None


def parse_flight_level(tokens: List[Token]) -> Optional[ParsedSlot]:
    for token in tokens:
        if token.kind == "flight_level" and token.normalized.startswith("FL"):
            return ParsedSlot(
                name="flight_level",
                value=token.normalized,
                confidence=token.confidence,
                raw_tokens=[token.raw],
            )
    return None


def _consume_number_sequence(tokens: Iterable[Token]) -> tuple[str, List[str], float]:
    digits: List[str] = []
    raw_tokens: List[str] = []
    confidences: List[float] = []
    for token in tokens:
        if token.kind in {"number", "digits"} and token.normalized.isdigit():
            digits.append(token.normalized)
            raw_tokens.append(token.raw)
            confidences.append(token.confidence)
        else:
            break
    return "".join(digits), raw_tokens, min(confidences) if confidences else 0.0


def parse_runway(tokens: List[Token]) -> Optional[ParsedSlot]:
    for idx, token in enumerate(tokens):
        if token.normalized == "runway":
            digits, raw_tokens, confidence = _consume_number_sequence(tokens[idx + 1 :])
            if not digits:
                continue
            runway = digits.zfill(2)
            suffix = ""
            if idx + 1 + len(raw_tokens) < len(tokens):
                next_token = tokens[idx + 1 + len(raw_tokens)]
                suffix = RUNWAY_SUFFIX.get(next_token.normalized.lower(), "")
                if suffix:
                    raw_tokens.append(next_token.raw)
                    confidence = min(confidence, next_token.confidence)
            return ParsedSlot(
                name="runway",
                value=f"{runway}{suffix}",
                confidence=confidence,
                raw_tokens=[token.raw] + raw_tokens,
            )
    return None


def parse_altitude(tokens: List[Token]) -> Optional[ParsedSlot]:
    for idx, token in enumerate(tokens):
        if token.normalized in {"altitude", "alt", "height"}:
            digits, raw_tokens, confidence = _consume_number_sequence(tokens[idx + 1 :])
            if digits:
                return ParsedSlot(
                    name="altitude",
                    value=digits,
                    confidence=confidence,
                    raw_tokens=[token.raw] + raw_tokens,
                )
    return None


def parse_qnh(tokens: List[Token]) -> Optional[ParsedSlot]:
    for idx, token in enumerate(tokens):
        if token.normalized == "qnh":
            digits, raw_tokens, confidence = _consume_number_sequence(tokens[idx + 1 :])
            if digits:
                return ParsedSlot(
                    name="qnh",
                    value=digits,
                    confidence=confidence,
                    raw_tokens=[token.raw] + raw_tokens,
                )
    return None


def parse_squawk(tokens: List[Token]) -> Optional[ParsedSlot]:
    for idx, token in enumerate(tokens):
        if token.normalized == "squawk":
            digits, raw_tokens, confidence = _consume_number_sequence(tokens[idx + 1 :])
            if digits:
                return ParsedSlot(
                    name="squawk",
                    value=digits,
                    confidence=confidence,
                    raw_tokens=[token.raw] + raw_tokens,
                )
    return None


def parse_all(result: NormalizationResult) -> Dict[str, ParsedSlot]:
    """Parse all supported slots from a NormalizationResult."""
    slots: Dict[str, ParsedSlot] = {}
    for parser in (parse_callsign, parse_runway, parse_altitude, parse_flight_level, parse_qnh, parse_squawk):
        parsed = parser(result.tokens)
        if parsed:
            slots[parsed.name] = parsed
    return slots


if __name__ == "__main__":
    # Simple self-tests
    result = normalize_icao("Delta alpha bravo charlie runway two seven left")
    slots = parse_all(result)
    assert slots["callsign"].value == "D-ABC", slots
    assert slots["runway"].value == "27L", slots

    result = normalize_icao("Climb to altitude two five zero zero")
    slots = parse_all(result)
    assert slots["altitude"].value == "2500", slots

    result = normalize_icao("Flight level one zero zero")
    slots = parse_all(result)
    assert slots["flight_level"].value == "FL100", slots

    result = normalize_icao("QNH one zero one three squawk four five two one")
    slots = parse_all(result)
    assert slots["qnh"].value == "1013", slots
    assert slots["squawk"].value == "4521", slots

    print("Parser self-tests passed.")
