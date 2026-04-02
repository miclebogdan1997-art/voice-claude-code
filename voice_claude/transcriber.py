"""Speech-to-text transcription backends."""

from __future__ import annotations

import io
import logging
import wave
from abc import ABC, abstractmethod

import speech_recognition as sr

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore[assignment]

logger = logging.getLogger("voice_claude.transcriber")


class TranscriptionError(Exception):
    """Raised when transcription fails."""


class BaseTranscriber(ABC):
    """Abstract base for speech transcribers."""

    @abstractmethod
    def transcribe(self, audio: sr.AudioData) -> str | None:
        """Transcribe audio data to text. Returns None if nothing recognised."""


class GoogleTranscriber(BaseTranscriber):
    """Online transcription via Google Speech Recognition API."""

    def __init__(self, lang: str = "ro-RO") -> None:
        self.lang = lang
        self._recognizer = sr.Recognizer()

    def transcribe(self, audio: sr.AudioData) -> str | None:
        try:
            text = self._recognizer.recognize_google(audio, language=self.lang)
            logger.debug("Google transcription: %s", text)
            return text  # type: ignore[return-value]
        except sr.UnknownValueError:
            logger.debug("Google could not understand audio")
            return None
        except sr.RequestError as exc:
            raise TranscriptionError(f"Google API error: {exc}") from exc


class WhisperTranscriber(BaseTranscriber):
    """Offline transcription via faster-whisper (loaded lazily)."""

    def __init__(self, lang: str = "ro", model_size: str = "base") -> None:
        self.lang = lang.split("-")[0]  # "ro-RO" → "ro"
        self.model_size = model_size
        self._model: object | None = None

    def _load_model(self) -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise ImportError(
                "faster-whisper is required for Whisper mode. "
                "Install with: pip install voice-claude[whisper]"
            ) from exc

        logger.info("Loading Whisper model '%s' (first call — may take a moment)…", self.model_size)
        self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio: sr.AudioData) -> str | None:
        if np is None:
            raise ImportError(
                "numpy is required for Whisper mode. "
                "Install with: pip install voice-claude[whisper]"
            )

        if self._model is None:
            self._load_model()

        wav_bytes = audio.get_wav_data(convert_rate=16000, convert_width=2)
        with io.BytesIO(wav_bytes) as buf:
            with wave.open(buf, "rb") as wf:
                frames = wf.readframes(wf.getnframes())

        audio_array = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

        try:
            segments, _info = self._model.transcribe(  # type: ignore[union-attr]
                audio_array,
                language=self.lang,
                beam_size=5,
            )
            text = " ".join(seg.text.strip() for seg in segments).strip()
            logger.debug("Whisper transcription: %s", text)
            return text or None
        except Exception as exc:
            raise TranscriptionError(f"Whisper error: {exc}") from exc


def create_transcriber(
    whisper: bool = False,
    lang: str = "ro-RO",
    model_size: str = "base",
) -> BaseTranscriber:
    """Factory: return the appropriate transcriber based on flags."""
    if whisper:
        return WhisperTranscriber(lang=lang, model_size=model_size)
    return GoogleTranscriber(lang=lang)
