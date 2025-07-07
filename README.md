# LaTeX Translation Tool

A Python CLI tool that translates LaTeX files using LLM APIs while preserving mathematical formulas, citations, labels, and LaTeX structure.

Built with modern Python tooling using [uv](https://docs.astral.sh/uv/) for fast, reliable dependency management.

## Features

- **Simple & Reliable**: Lets the LLM handle LaTeX preservation naturally instead of complex parsing
- **Smart Chunking**: Splits by LaTeX sections, then paragraphs while respecting token limits
- **Parallel Processing**: Translates multiple chunks concurrently for faster completion
- **Directory Support**: Process entire directories of LaTeX files at once
- **OpenAI-Compatible APIs**: Works with OpenRouter, OpenAI, and other compatible endpoints
- **Arbitrary Languages**: Translate between any source and target languages
- **Progress Tracking**: Shows detailed progress during translation
- **Dry Run Mode**: Test the tool without making API calls

## Installation

1. Install using uv (recommended):
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package
uv pip install .
```

Alternatively, install dependencies manually:
```bash
uv pip install requests tiktoken urllib3
```

### Why uv?

This project uses [uv](https://docs.astral.sh/uv/) for Python package management because:
- **Fast**: 10-100x faster than pip
- **Reliable**: Consistent dependency resolution
- **Easy**: Single tool for virtual environments and dependencies
- **Modern**: Built for Python 3.8+ with excellent pyproject.toml support

### Development Setup

```bash
# Clone and setup for development
git clone <repository-url>
cd latex-translate
uv sync                    # Install all dependencies + dev tools
uv run pytest            # Run tests
uv run black .            # Format code
uv run flake8            # Lint code
```

## Usage

### Basic Usage

```bash
# Using uv run (recommended)
uv run latex_translate.py \
  -i input.tex \
  --source-lang galician \
  --target-lang english \
  --api-key your-api-key

# Or if installed as package
latex-translate \
  -i input.tex \
  --source-lang galician \
  --target-lang english \
  --api-key your-api-key
```

### Advanced Usage

```bash
# Translate multiple files
uv run latex_translate.py \
  -i file1.tex file2.tex file3.tex \
  -o translated/ \
  --source-lang galician \
  --target-lang english \
  --api-key sk-your-key \
  --model anthropic/claude-3.5-sonnet \
  --verbose

# Translate entire directory with parallel processing
uv run latex_translate.py \
  -i chapters/ \
  -o translated/ \
  --source-lang spanish \
  --target-lang english \
  --api-key sk-your-key \
  --chunk-size 2500 \
  --parallel 5 \
  --verbose
```

### Dry Run

Test the tool without making API calls:
```bash
uv run latex_translate.py \
  -i input.tex \
  --source-lang galician \
  --target-lang english \
  --api-key dummy \
  --dry-run \
  --verbose
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | Input .tex files or directories (required) | - |
| `-o, --output` | Output directory | `./translated` |
| `--source-lang` | Source language (required) | - |
| `--target-lang` | Target language (required) | - |
| `--api-key` | API key (required) | - |
| `--endpoint` | API endpoint URL | `https://openrouter.ai/api/v1` |
| `--model` | Model to use | `anthropic/claude-3.5-sonnet` |
| `--chunk-size` | Target chunk size in tokens | `3000` |
| `--max-tokens` | Max tokens for API response | `4000` |
| `--temperature` | Translation temperature | `0.1` |
| `--parallel` | Number of parallel workers | `3` |
| `-v, --verbose` | Enable verbose logging | `False` |
| `--dry-run` | Test without API calls | `False` |

## What Gets Preserved

The tool automatically preserves these LaTeX elements without translation:

- **Math**: `$...$`, `$$...$$`, `\begin{equation}...\end{equation}`, etc.
- **Citations**: `\cite{}`, `\citep{}`, `\citet{}`, etc.
- **References**: `\ref{}`, `\eqref{}`, `\autoref{}`, etc.
- **Labels**: `\label{}`
- **Structure**: `\section{}`, `\chapter{}`, `\begin{}`, `\end{}`, etc.
- **Comments**: `% comments`

## What Gets Translated

The tool translates:

- Regular text content
- Text inside formatting commands: `\textbf{}`, `\textit{}`, `\emph{}`, etc.

## Examples

### Translate Galician to English
```bash
uv run latex_translate.py \
  -i thesis.tex \
  --source-lang "galician" \
  --target-lang "english" \
  --api-key your-openrouter-key
```

### Translate Multiple Files
```bash
uv run latex_translate.py \
  -i chapter1.tex chapter2.tex chapter3.tex \
  -o english_version/ \
  --source-lang "spanish" \
  --target-lang "english" \
  --api-key your-key \
  --verbose
```

### Translate Entire Directory
```bash
uv run latex_translate.py \
  -i thesis_chapters/ \
  -o english_thesis/ \
  --source-lang "galician" \
  --target-lang "english" \
  --api-key your-key \
  --model "openai/gpt-4" \
  --chunk-size 2000 \
  --verbose
```

## Output

Translated files are saved with the target language suffix:
- `input.tex` → `input_english.tex`
- `chapter1.tex` → `chapter1_english.tex`

## Error Handling

The tool includes robust error handling:
- Network timeouts and retries
- Rate limiting with automatic backoff
- Fallback to original text on translation failure
- Detailed logging with `--verbose` flag

## Supported APIs

Any OpenAI-compatible API should work, including:
- OpenRouter (default)
- OpenAI
- Azure OpenAI
- Local models with OpenAI-compatible endpoints

## Troubleshooting

1. **Connection errors**: Check your API key and endpoint
2. **Rate limiting**: The tool automatically handles rate limits
3. **Large files**: Increase `--chunk-size` if needed
4. **Encoding issues**: Files are read with UTF-8, fallback to latin-1

## License

This project is open source. Feel free to modify and distribute.
