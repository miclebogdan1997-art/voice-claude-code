"""Send transcribed commands to Claude Code CLI."""

import logging
import shutil
import subprocess

logger = logging.getLogger("voice_claude.sender")


class ClaudeNotFoundError(RuntimeError):
    """Raised when the 'claude' CLI executable is not found in PATH."""


def send_to_claude(command: str, workdir: str = ".") -> int:
    """Run a command through Claude Code CLI and return the exit code.

    Output is streamed live to the terminal (not captured).
    Raises ClaudeNotFoundError if the claude executable is missing.
    """
    if shutil.which("claude") is None:
        raise ClaudeNotFoundError(
            "The 'claude' CLI was not found in PATH. "
            "Install it from https://docs.anthropic.com/en/docs/claude-code"
        )

    logger.info("Sending to Claude: %s", command)
    result = subprocess.run(
        ["claude", "-p", command],
        cwd=workdir,
    )
    logger.debug("Claude exited with code %d", result.returncode)
    return result.returncode
