"""Tests for voice_claude.sender."""

from unittest.mock import MagicMock, patch

import pytest

from voice_claude.sender import ClaudeNotFoundError, send_to_claude


class TestSendToClaude:
    @patch("voice_claude.sender.subprocess.run")
    @patch("voice_claude.sender.shutil.which", return_value="/usr/bin/claude")
    def test_success(self, mock_which: MagicMock, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0)
        rc = send_to_claude("fix the bug", workdir="/tmp")
        assert rc == 0
        mock_run.assert_called_once_with(
            ["claude", "-p", "fix the bug"],
            cwd="/tmp",
        )

    @patch("voice_claude.sender.subprocess.run")
    @patch("voice_claude.sender.shutil.which", return_value="/usr/bin/claude")
    def test_nonzero_exit(self, mock_which: MagicMock, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1)
        rc = send_to_claude("bad command")
        assert rc == 1

    @patch("voice_claude.sender.shutil.which", return_value=None)
    def test_claude_not_found(self, mock_which: MagicMock) -> None:
        with pytest.raises(ClaudeNotFoundError, match="not found in PATH"):
            send_to_claude("anything")

    @patch("voice_claude.sender.subprocess.run")
    @patch("voice_claude.sender.shutil.which", return_value="/usr/bin/claude")
    def test_default_workdir(self, mock_which: MagicMock, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0)
        send_to_claude("test")
        mock_run.assert_called_once_with(
            ["claude", "-p", "test"],
            cwd=".",
        )
