# MinMind Python Package

AI integrations for the MinMind Mind Palace.

## Setup

```bash
# From project root
uv venv minmind --python 3.13
source minmind/bin/activate  # or `minmind/Scripts/activate` on Windows
uv pip install -e "./python[dev]"
```

## Environment Variables

Set your API keys:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"  # optional
```

## Usage

The Python package is primarily called by the Rust CLI, but can also be used directly:

### Extract an article

```bash
python -m minmind.cli extract "https://example.com/article"
```

### Summarize an article

```bash
python -m minmind.cli summarize <article-id> --provider anthropic --prompt "Summarize concisely"
```

## Development

```bash
# Run tests
pytest

# Lint
ruff check .
ruff format .
```
