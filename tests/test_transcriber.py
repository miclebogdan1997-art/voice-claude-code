"""Tests for voice_claude.transcriber."""

from unittest.mock import MagicMock, patch

import pytest
import speech_recognition as sr

from voice_claude.transcriber import (
    GoogleTranscriber,
    TranscriptionError,
    WhisperTranscriber,
    create_transcriber,
)

# --- GoogleTranscriber ---


class TestGoogleTranscriber:
    def _make_audio(self) -> sr.AudioData:
        return sr.AudioData(b"\x00" * 1600, sample_rate=16000, sample_width=2)

    @patch.object(sr.Recognizer, "recognize_google", return_value="hello world")
    def test_transcribe_success(self, mock_google: MagicMock) -> None:
        t = GoogleTranscriber(lang="en-US")
        result = t.transcribe(self._make_audio())
        assert result == "hello world"
        mock_google.assert_called_once()

    @patch.object(sr.Recognizer, "recognize_google", side_effect=sr.UnknownValueError())
    def test_transcribe_unknown_value(self, mock_google: MagicMock) -> None:
        t = GoogleTranscriber()
        result = t.transcribe(self._make_audio())
        assert result is None

    @patch.object(sr.Recognizer, "recognize_google", side_effect=sr.RequestError("API down"))
    def test_transcribe_request_error(self, mock_google: MagicMock) -> None:
        t = GoogleTranscriber()
        with pytest.raises(TranscriptionError, match="Google API error"):
            t.transcribe(self._make_audio())


# --- WhisperTranscriber ---


class TestWhisperTranscriber:
    def _make_audio(self) -> sr.AudioData:
        # Minimal valid WAV-compatible audio
        return sr.AudioData(b"\x00" * 3200, sample_rate=16000, sample_width=2)

    @patch("voice_claude.transcriber.np")
    @patch("voice_claude.transcriber.WhisperTranscriber._load_model")
    def test_transcribe_success(self, mock_load: MagicMock, mock_np: MagicMock) -> None:
        fake_array = MagicMock()
        fake_array.astype.return_value.__truediv__ = MagicMock(return_value=MagicMock())
        mock_np.frombuffer.return_value = fake_array

        t = WhisperTranscriber(lang="ro-RO", model_size="tiny")

        mock_model = MagicMock()
        seg = MagicMock()
        seg.text = " salut lume "
        mock_model.transcribe.return_value = ([seg], MagicMock())
        t._model = mock_model

        result = t.transcribe(self._make_audio())
        assert result == "salut lume"
        mock_model.transcribe.assert_called_once()

    @patch("voice_claude.transcriber.np")
    @patch("voice_claude.transcriber.WhisperTranscriber._load_model")
    def test_transcribe_empty(self, mock_load: MagicMock, mock_np: MagicMock) -> None:
        fake_array = MagicMock()
        fake_array.astype.return_value.__truediv__ = MagicMock(return_value=MagicMock())
        mock_np.frombuffer.return_value = fake_array

        t = WhisperTranscriber()
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([], MagicMock())
        t._model = mock_model

        result = t.transcribe(self._make_audio())
        assert result is None

    @patch("voice_claude.transcriber.np")
    @patch("voice_claude.transcriber.WhisperTranscriber._load_model")
    def test_transcribe_error(self, mock_load: MagicMock, mock_np: MagicMock) -> None:
        fake_array = MagicMock()
        fake_array.astype.return_value.__truediv__ = MagicMock(return_value=MagicMock())
        mock_np.frombuffer.return_value = fake_array

        t = WhisperTranscriber()
        mock_model = MagicMock()
        mock_model.transcribe.side_effect = RuntimeError("model broken")
        t._model = mock_model

        with pytest.raises(TranscriptionError, match="Whisper error"):
            t.transcribe(self._make_audio())

    def test_lang_normalization(self) -> None:
        t = WhisperTranscriber(lang="ro-RO")
        assert t.lang == "ro"


# --- Factory ---


class TestFactory:
    def test_google_by_default(self) -> None:
        t = create_transcriber(whisper=False)
        assert isinstance(t, GoogleTranscriber)

    def test_whisper_when_requested(self) -> None:
        t = create_transcriber(whisper=True, model_size="tiny")
        assert isinstance(t, WhisperTranscriber)
