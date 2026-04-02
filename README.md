# voice-claude

[![PyPI version](https://img.shields.io/pypi/v/voice-claude)](https://pypi.org/project/voice-claude/)
[![Python](https://img.shields.io/pypi/pyversions/voice-claude)](https://pypi.org/project/voice-claude/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/bogdanmicle/voice-claude-code/actions/workflows/ci.yml/badge.svg)](https://github.com/bogdanmicle/voice-claude-code/actions/workflows/ci.yml)

Voice-controlled agent for **Claude Code CLI** — speak commands in any language, get code.

Supports **Google Speech API** (online) and **Whisper** (offline) for transcription,
with Romanian (`ro-RO`) as the default language.

## System Requirements

- **Python 3.11+**
- **Claude Code CLI** installed and available in PATH ([instructions](https://docs.anthropic.com/en/docs/claude-code))
- **Microphone** (working audio input device)
- On Linux: `portaudio19-dev` (`sudo apt install portaudio19-dev`)
- On macOS: `portaudio` (`brew install portaudio`)

## Installation

```bash
# Basic install (Google Speech API)
pip install voice-claude

# With offline Whisper support
pip install "voice-claude[whisper]"

# With push-to-talk hotkey (Space)
pip install "voice-claude[hotkey]"

# Everything
pip install "voice-claude[whisper,hotkey]"

# From source (development)
git clone https://github.com/bogdanmicle/voice-claude-code.git
cd voice-claude-code
pip install -e ".[whisper,hotkey,dev]"
```

## Usage

### Simple mode (press Enter to record)
```bash
voice-claude --lang ro-RO
```

### Push-to-talk mode (hold Space)
```bash
# Requires the [hotkey] extra
voice-claude --lang ro-RO
```

### Continuous mode (background listening)
```bash
voice-claude --continuous --lang ro-RO
```

### With offline Whisper
```bash
voice-claude --whisper --model base --lang ro-RO
```

### Other options
```bash
# List available audio devices
voice-claude --list-devices

# Select a specific microphone
voice-claude --device-index 2

# Custom working directory
voice-claude --workdir ~/my-project

# Verbose logging
voice-claude --verbose
```

## Comparison with built-in `/voice` in Claude Code

| Feature | `/voice` built-in | voice-claude |
|---|---|---|
| Language | English | **Any language** (default `ro-RO`) |
| Offline mode | No | **Yes** (Whisper) |
| Push-to-talk | No | **Yes** (Space) |
| Continuous listening | No | **Yes** |
| Microphone selection | No | **Yes** (`--device-index`) |
| Model customization | No | **Yes** (`--model tiny/base/small/medium`) |

**Key advantage:** full support for Romanian and offline operation with Whisper.

## Contributing

Contributions are welcome! Open an [issue](https://github.com/bogdanmicle/voice-claude-code/issues)
or submit a pull request.

```bash
# Development setup
pip install -e ".[whisper,hotkey,dev]"

# Run tests
pytest tests/ -v

# Linting
ruff check .
```

## License

MIT
