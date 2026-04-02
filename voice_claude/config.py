"""Configuration and CLI argument parsing for voice-claude."""

import argparse
import logging
import sys

import speech_recognition as sr
from colorama import Fore, Style

logger = logging.getLogger("voice_claude")


def list_audio_devices() -> None:
    """List available audio input devices and exit."""
    print(f"{Fore.CYAN}Available audio input devices:{Style.RESET_ALL}\n")
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {Fore.GREEN}[{i}]{Style.RESET_ALL} {name}")
    print(f"\n{Fore.YELLOW}Use --device-index N to select a device.{Style.RESET_ALL}")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="voice-claude",
        description="Voice-controlled Claude Code agent — speak commands, get code.",
    )
    parser.add_argument(
        "--whisper",
        action="store_true",
        help="Use local Whisper model instead of Google Speech API",
    )
    parser.add_argument(
        "--lang",
        default="ro-RO",
        help="Language code for speech recognition (default: ro-RO)",
    )
    parser.add_argument(
        "--workdir",
        default=".",
        help="Working directory for Claude Code CLI (default: current directory)",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Enable continuous listening mode (background)",
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--device-index",
        type=int,
        default=None,
        help="Audio input device index (see --list-devices)",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio input devices and exit",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments, handle --list-devices, configure logging."""
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.list_devices:
        try:
            list_audio_devices()
        except Exception as exc:
            logger.error("Could not enumerate audio devices: %s", exc)
        sys.exit(0)

    return args
