"""Audio-to-text helper using faster-whisper.

This module is optional; if faster-whisper or ffmpeg is unavailable, callers
should surface a clear error to the user.
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class STTSegment:
    text: str
    start: float
    end: float
    avg_logprob: float
    no_speech_prob: float
    compression_ratio: float


@dataclass(frozen=True)
class STTTranscript:
    text: str
    segments: List[STTSegment]


_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    from faster_whisper import WhisperModel  # noqa: PLC0415

    model_size = os.getenv("WHISPER_MODEL", "base")
    device = os.getenv("WHISPER_DEVICE", "cpu")
    compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    _MODEL = WhisperModel(model_size, device=device, compute_type=compute_type)
    return _MODEL


def transcribe_audio(
    audio_bytes: bytes,
    *,
    language: Optional[str] = "en",
    filename: Optional[str] = None,
) -> STTTranscript:
    model = _get_model()
    suffix = ".webm"
    if filename and "." in filename:
        suffix = os.path.splitext(filename)[1] or suffix
    with tempfile.NamedTemporaryFile(suffix=suffix) as temp_file:
        temp_file.write(audio_bytes)
        temp_file.flush()
        segments, info = model.transcribe(
            temp_file.name,
            language=language,
            beam_size=5,
            vad_filter=True,
        )

    collected: List[STTSegment] = []
    texts: List[str] = []
    for segment in segments:
        texts.append(segment.text.strip())
        collected.append(
            STTSegment(
                text=segment.text.strip(),
                start=segment.start,
                end=segment.end,
                avg_logprob=segment.avg_logprob,
                no_speech_prob=segment.no_speech_prob,
                compression_ratio=segment.compression_ratio,
            )
        )

    return STTTranscript(text=" ".join(texts).strip(), segments=collected)
