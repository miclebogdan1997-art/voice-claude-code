"""Entry point for voice-claude CLI."""

import logging
import sys

from colorama import init as colorama_init

from voice_claude.config import parse_args
from voice_claude.sender import ClaudeNotFoundError
from voice_claude.transcriber import create_transcriber

logger = logging.getLogger("voice_claude")


def main(argv: list[str] | None = None) -> None:
    """Parse args, select mode, and run the voice loop."""
    colorama_init()
    args = parse_args(argv)

    transcriber = create_transcriber(
        whisper=args.whisper,
        lang=args.lang,
        model_size=args.model,
    )
    logger.info(
        "Using %s transcriber (lang=%s)",
        "Whisper" if args.whisper else "Google",
        args.lang,
    )

    try:
        if args.continuous:
            from voice_claude.modes.continuous import run
        else:
            # Try push-to-talk first; fall back to simple mode
            try:
                import keyboard  # noqa: F401

                from voice_claude.modes.push_to_talk import run
            except (ImportError, Exception):
                logger.info("keyboard not available — using simple mode (Enter to record)")
                from voice_claude.modes.simple import run

        run(
            transcriber=transcriber,
            workdir=args.workdir,
            device_index=args.device_index,
        )
    except ClaudeNotFoundError as exc:
        logger.error("%s", exc)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
