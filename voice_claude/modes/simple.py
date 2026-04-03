"""Simple mode — press Enter to record, no hotkey dependency."""

import logging

import speech_recognition as sr
from colorama import Fore, Style

from voice_claude.sender import send_to_claude
from voice_claude.transcriber import BaseTranscriber, TranscriptionError

logger = logging.getLogger("voice_claude.modes.simple")

RECORD_SECONDS = 15


class MicrophoneError(Exception):
    """Raised when the microphone is not available."""


def run(
    transcriber: BaseTranscriber,
    workdir: str = ".",
    device_index: int | None = None,
) -> None:
    """Simple loop: press Enter → record → transcribe → send to Claude."""
    recognizer = sr.Recognizer()

    try:
        mic = sr.Microphone(device_index=device_index)
    except (OSError, AttributeError) as exc:
        raise MicrophoneError(f"Could not open microphone: {exc}") from exc

    print(
        f"\n{Fore.CYAN}╔══════════════════════════════════════════╗{Style.RESET_ALL}"
        f"\n{Fore.CYAN}║  voice-claude · Simple Mode              ║{Style.RESET_ALL}"
        f"\n{Fore.CYAN}╚══════════════════════════════════════════╝{Style.RESET_ALL}"
        f"\n"
        f"\n  Press {Fore.GREEN}Enter{Style.RESET_ALL} to start recording ({RECORD_SECONDS}s)."
        f"\n  Type  {Fore.RED}q{Style.RESET_ALL} + Enter to quit.\n"
    )

    while True:
        try:
            user_input = input(f"{Fore.YELLOW}▶ Ready — press Enter to record: {Style.RESET_ALL}")
        except (EOFError, KeyboardInterrupt):
            break

        if user_input.strip().lower() in ("q", "quit", "exit"):
            break

        print(f"{Fore.GREEN}● Recording for {RECORD_SECONDS}s — speak now…{Style.RESET_ALL}")
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(
                    source, timeout=RECORD_SECONDS, phrase_time_limit=RECORD_SECONDS
                )
        except sr.WaitTimeoutError:
            print(f"{Fore.RED}✗ No speech detected.{Style.RESET_ALL}\n")
            continue
        except OSError as exc:
            raise MicrophoneError(f"Microphone error during recording: {exc}") from exc

        print(f"{Fore.CYAN}⟳ Transcribing…{Style.RESET_ALL}")
        try:
            text = transcriber.transcribe(audio)
        except TranscriptionError as exc:
            logger.error("Transcription failed: %s", exc)
            print(f"{Fore.RED}✗ Transcription error: {exc}{Style.RESET_ALL}\n")
            continue

        if not text:
            print(f"{Fore.RED}✗ Could not understand audio.{Style.RESET_ALL}\n")
            continue

        print(f"{Fore.GREEN}✓ Heard:{Style.RESET_ALL} {text}")
        print(f"{Fore.CYAN}⟶ Sending to Claude…{Style.RESET_ALL}\n")
        send_to_claude(text, workdir=workdir)
        print()
