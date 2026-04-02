"""Continuous listening mode — background listener with stop words."""

import logging
import threading
import time

import speech_recognition as sr
from colorama import Fore, Style

from voice_claude.sender import send_to_claude
from voice_claude.transcriber import BaseTranscriber, TranscriptionError

logger = logging.getLogger("voice_claude.modes.continuous")

STOP_WORDS: set[str] = {"stop", "ieși", "exit", "quit", "oprește"}


def run(
    transcriber: BaseTranscriber,
    workdir: str = ".",
    device_index: int | None = None,
) -> None:
    """Listen continuously in the background; stop words or Ctrl+C to exit."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=device_index)

    stop_event = threading.Event()
    lock = threading.Lock()

    def callback(recognizer_: sr.Recognizer, audio: sr.AudioData) -> None:
        if stop_event.is_set():
            return

        try:
            text = transcriber.transcribe(audio)
        except TranscriptionError as exc:
            logger.error("Transcription failed: %s", exc)
            print(f"\n{Fore.RED}✗ Transcription error: {exc}{Style.RESET_ALL}")
            return

        if not text:
            return

        lower = text.strip().lower()
        if any(word in lower for word in STOP_WORDS):
            print(f"\n{Fore.YELLOW}Stop word detected (\"{text}\") — exiting.{Style.RESET_ALL}")
            stop_event.set()
            return

        print(f"\n{Fore.GREEN}✓ Heard:{Style.RESET_ALL} {text}")
        print(f"{Fore.CYAN}⟶ Sending to Claude…{Style.RESET_ALL}")

        with lock:
            send_to_claude(text, workdir=workdir)
        print()

    print(
        f"\n{Fore.CYAN}╔══════════════════════════════════════════╗{Style.RESET_ALL}"
        f"\n{Fore.CYAN}║  voice-claude · Continuous Mode          ║{Style.RESET_ALL}"
        f"\n{Fore.CYAN}╚══════════════════════════════════════════╝{Style.RESET_ALL}"
        f"\n"
        f"\n  Listening in the background…"
        f"\n  Say {Fore.RED}stop / exit / quit{Style.RESET_ALL} to end."
        f"\n  Or press {Fore.RED}Ctrl+C{Style.RESET_ALL}.\n"
    )

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    stop_listening = recognizer.listen_in_background(
        mic,
        callback,
        phrase_time_limit=15,
    )

    try:
        while not stop_event.is_set():
            time.sleep(0.2)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted — stopping listener.{Style.RESET_ALL}")

    stop_listening(wait_for_stop=True)
    print(f"{Fore.CYAN}Listener stopped. Goodbye!{Style.RESET_ALL}")
