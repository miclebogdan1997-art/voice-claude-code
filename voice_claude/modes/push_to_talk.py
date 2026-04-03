"""Push-to-talk mode — hold Space to record, release to send."""

import logging
import sys
import time

import speech_recognition as sr
from colorama import Fore, Style

from voice_claude.sender import send_to_claude
from voice_claude.transcriber import BaseTranscriber, TranscriptionError

logger = logging.getLogger("voice_claude.modes.push_to_talk")


def _check_keyboard() -> None:
    """Import keyboard and give a helpful message if unavailable."""
    try:
        import keyboard  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "The 'keyboard' package is required for push-to-talk mode. "
            "Install with: pip install voice-claude[hotkey]"
        ) from exc
    except Exception as exc:
        if sys.platform == "linux":
            print(
                f"{Fore.RED}keyboard requires root on Linux.{Style.RESET_ALL}\n"
                f"Run with {Fore.YELLOW}sudo{Style.RESET_ALL}, or add your user to the "
                f"{Fore.YELLOW}input{Style.RESET_ALL} group and use uinput.\n"
            )
        raise RuntimeError(f"Could not initialise keyboard listener: {exc}") from exc


def run(
    transcriber: BaseTranscriber,
    workdir: str = ".",
    device_index: int | None = None,
) -> None:
    """Hold Space to record; release to transcribe & send. Q or Ctrl+C to exit."""
    _check_keyboard()
    import keyboard

    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=device_index)

    print(
        f"\n{Fore.CYAN}╔══════════════════════════════════════════╗{Style.RESET_ALL}"
        f"\n{Fore.CYAN}║  voice-claude · Push-to-Talk Mode        ║{Style.RESET_ALL}"
        f"\n{Fore.CYAN}╚══════════════════════════════════════════╝{Style.RESET_ALL}"
        f"\n"
        f"\n  Hold  {Fore.GREEN}Space{Style.RESET_ALL} to record."
        f"\n  Press {Fore.RED}Q{Style.RESET_ALL} to quit.\n"
    )

    try:
        while True:
            if keyboard.is_pressed("q"):
                print(f"\n{Fore.YELLOW}Exiting push-to-talk mode.{Style.RESET_ALL}")
                break

            if keyboard.is_pressed("space"):
                print(f"{Fore.GREEN}● Recording — keep holding Space…{Style.RESET_ALL}", end="\r")
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    # Wait until Space is released, collecting audio
                    audio = recognizer.listen(
                        source,
                        timeout=30,
                        phrase_time_limit=30,
                    )

                print(f"{Fore.CYAN}⟳ Transcribing…{Style.RESET_ALL}                        ")
                try:
                    text = transcriber.transcribe(audio)
                except TranscriptionError as exc:
                    logger.error("Transcription failed: %s", exc)
                    print(f"{Fore.RED}✗ {exc}{Style.RESET_ALL}\n")
                    continue

                if not text:
                    print(f"{Fore.RED}✗ Could not understand audio.{Style.RESET_ALL}\n")
                    continue

                print(f"{Fore.GREEN}✓ Heard:{Style.RESET_ALL} {text}")
                print(f"{Fore.CYAN}⟶ Sending to Claude…{Style.RESET_ALL}\n")
                send_to_claude(text, workdir=workdir)
                print()

                # Small delay so we don't immediately re-trigger
                time.sleep(0.5)
            else:
                time.sleep(0.05)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted — exiting.{Style.RESET_ALL}")
