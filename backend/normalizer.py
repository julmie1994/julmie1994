"""ICAO VFR phraseology normalizer.

This module normalizes STT text into a deterministic, structured form. It handles:
- ICAO numbers (tree/fife/niner, flight levels)
- NATO alphabet (alpha bravo kilo -> ABK) with simple fuzzy matching
- Contextual corrections (to/too -> two, for -> four)

The result is a `NormalizationResult` object with raw text, normalized text,
per-token details, and confidence hints.

Integration in STT flow (backend):
1) Call `normalize_icao(stt_text)` after STT completes.
2) Pass `normalized_text` and `tokens` to parsers/validators.
3) Store `confidence_hints` to explain potentially fuzzy matches.
"""
from __future__ import annotations

from dataclasses import dataclass
import difflib
import re
from typing import Iterable, List


@dataclass(frozen=True)
class Token:
    raw: str
    normalized: str
    kind: str
    confidence: float


@dataclass(frozen=True)
class NormalizationResult:
    raw_text: str
    normalized_text: str
    tokens: List[Token]
    confidence_hints: List[str]


NATO_WORDS = {
    "alpha": "A",
    "bravo": "B",
    "charlie": "C",
    "delta": "D",
    "echo": "E",
    "foxtrot": "F",
    "golf": "G",
    "hotel": "H",
    "india": "I",
    "juliet": "J",
    "kilo": "K",
    "lima": "L",
    "mike": "M",
    "november": "N",
    "oscar": "O",
    "papa": "P",
    "quebec": "Q",
    "romeo": "R",
    "sierra": "S",
    "tango": "T",
    "uniform": "U",
    "victor": "V",
    "whiskey": "W",
    "xray": "X",
    "yankee": "Y",
    "zulu": "Z",
}

NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "tree": "3",
    "four": "4",
    "for": "4",
    "five": "5",
    "fife": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "niner": "9",
}

CONTEXT_NUMBERS = {
    "to": "two",
    "too": "two",
    "for": "four",
}

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def _tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())


def _fuzzy_match(token: str, choices: Iterable[str], cutoff: float = 0.8) -> tuple[str | None, float]:
    best = difflib.get_close_matches(token, list(choices), n=1, cutoff=cutoff)
    if not best:
        return None, 0.0
    match = best[0]
    ratio = difflib.SequenceMatcher(a=token, b=match).ratio()
    return match, ratio


def _is_number_token(token: str) -> bool:
    return token.isdigit() or token in NUMBER_WORDS


def normalize_icao(raw_text: str) -> NormalizationResult:
    """Normalize ICAO phraseology text.

    Args:
        raw_text: Raw STT output.

    Returns:
        NormalizationResult with normalized text, tokens, and confidence hints.
    """
    tokens = _tokenize(raw_text)
    normalized_tokens: List[Token] = []
    confidence_hints: List[str] = []

    idx = 0
    while idx < len(tokens):
        token = tokens[idx]

        # Flight level handling: "flight level one zero zero" -> FL100
        if token == "flight" and idx + 1 < len(tokens) and tokens[idx + 1] == "level":
            digits: List[str] = []
            j = idx + 2
            while j < len(tokens) and _is_number_token(tokens[j]):
                if tokens[j].isdigit():
                    digits.extend(list(tokens[j]))
                else:
                    digits.append(NUMBER_WORDS[tokens[j]])
                j += 1
            if digits:
                normalized_tokens.append(
                    Token(raw="flight level", normalized=f"FL{''.join(digits)}", kind="flight_level", confidence=1.0)
                )
                idx = j
                continue

        # Contextual corrections: to/too/for -> two/four when adjacent to number word
        if token in CONTEXT_NUMBERS:
            prev_num = idx > 0 and _is_number_token(tokens[idx - 1])
            next_num = idx + 1 < len(tokens) and _is_number_token(tokens[idx + 1])
            if prev_num or next_num:
                normalized = NUMBER_WORDS[CONTEXT_NUMBERS[token]]
                normalized_tokens.append(
                    Token(raw=token, normalized=normalized, kind="number", confidence=0.75)
                )
                confidence_hints.append(f"context-normalized '{token}' -> '{normalized}'")
                idx += 1
                continue

        # Exact number word
        if token in NUMBER_WORDS:
            normalized_tokens.append(Token(raw=token, normalized=NUMBER_WORDS[token], kind="number", confidence=1.0))
            idx += 1
            continue

        # Digits
        if token.isdigit():
            normalized_tokens.append(Token(raw=token, normalized=token, kind="digits", confidence=1.0))
            idx += 1
            continue

        # NATO alphabet exact
        if token in NATO_WORDS:
            normalized_tokens.append(Token(raw=token, normalized=NATO_WORDS[token], kind="nato", confidence=1.0))
            idx += 1
            continue

        # NATO alphabet fuzzy
        nato_match, ratio = _fuzzy_match(token, NATO_WORDS.keys())
        if nato_match:
            normalized_tokens.append(
                Token(raw=token, normalized=NATO_WORDS[nato_match], kind="nato", confidence=ratio)
            )
            confidence_hints.append(f"fuzzy NATO match '{token}' -> '{nato_match}' ({ratio:.2f})")
            idx += 1
            continue

        # Default: passthrough
        normalized_tokens.append(Token(raw=token, normalized=token, kind="word", confidence=1.0))
        idx += 1

    normalized_text = _join_tokens(normalized_tokens)
    return NormalizationResult(
        raw_text=raw_text,
        normalized_text=normalized_text,
        tokens=normalized_tokens,
        confidence_hints=confidence_hints,
    )


def _join_tokens(tokens: List[Token]) -> str:
    output: List[str] = []
    for token in tokens:
        if token.kind == "nato" and output and output[-1].isalpha() and output[-1].isupper():
            output[-1] = output[-1] + token.normalized
        else:
            output.append(token.normalized)
    return " ".join(output)


if __name__ == "__main__":
    # Simple self-tests
    result = normalize_icao("Flight level one zero zero")
    assert result.normalized_text == "FL100", result

    result = normalize_icao("alpha bravo kilo")
    assert result.normalized_text == "ABK", result

    result = normalize_icao("tree fife niner")
    assert result.normalized_text == "3 5 9", result

    result = normalize_icao("climb to flight level one zero zero")
    assert result.normalized_text == "climb to FL100", result

    print("Normalizer self-tests passed.")
