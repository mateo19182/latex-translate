# LaTeX Translation Tool

A simple Python CLI tool to translate LaTeX files using LLM APIs while preserving math, citations, and LaTeX structure.

Created to translate my [thesis](https://github.com/mateo19182/TFG) from Galician to English.
The alternatives ([Translatex](https://github.com/habaneraa/TransLaTeX), [trsltx](https://github.com/phelluy/trsltx)) either did bad chunking or used weird APIs.

## Features

- Preserves LaTeX math, citations, references, and structure
- Translates regular text content
- Processes multiple files or directories
- Parallel processing for speed
- Works with OpenAI compatible APIs (OpenRouter, Anthropic, Google, etc.)

## Installation

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install requests tiktoken urllib3
```

## Usage

```bash
# Basic usage
uv run latex_translate.py \
  -i input.tex \
  --source-lang galician \
  --target-lang english \
  --api-key your-api-key

# Multiple files
uv run latex_translate.py \
  -i *.tex \
  -o translated/ \
  --source-lang galician \
  --target-lang english \
  --api-key your-api-key

# Dry run (test without API calls)
uv run latex_translate.py \
  -i input.tex \
  --source-lang galician \
  --target-lang english \
  --api-key dummy \
  --dry-run
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input .tex files or directories | - |
| `-o, --output` | Output directory | `./translated` |
| `--source-lang` | Source language | - |
| `--target-lang` | Target language | - |
| `--api-key` | API key | - |
| `--model` | Model to use | `anthropic/claude-3.5-sonnet` |
| `--parallel` | Number of parallel workers | `3` |
| `--dry-run` | Test without API calls | `False` |


## Output

Translated files are saved with language suffix: `input.tex` → `input_english.tex` in the `translated/` directory.
