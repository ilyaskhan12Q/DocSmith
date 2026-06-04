# AGENTS.md — DocSmith Repository Intelligence

> This file provides repository-level instructions for AI coding agents.
> Consult this before making any changes.

---

## Project Vision

DocSmith is an AI-powered documentation engineer CLI that analyzes GitHub repositories,
understands their structure, extracts intelligence, and generates production-ready documentation.

**Core Principle:** Every generated document must contain repository-specific information.
No generic AI slop. The output should feel like it was written by a human maintainer
who deeply understands the codebase.

---

## Architecture Rules

### Pipeline

```
Repository URL → GitHub Fetcher → Parser → Analyzer → RepoContext → Planner → Writer → Reviewer → Scorer → Output
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `docsmith/github/` | Fetch repository data via GitHub REST API |
| `docsmith/analysis/` | Extract structured intelligence from raw repo data |
| `docsmith/ai/` | AI provider abstraction + prompt management |
| `docsmith/generation/` | Plan, write, review, score documentation |
| `docsmith/config/` | Settings management and persistent storage |
| `docsmith/output/` | File output, preview, and summary display |
| `docsmith/models/` | Pydantic data models shared across modules |

### Key Constraints

1. **Never send raw repository content to the LLM.** Always go through the analysis pipeline first.
2. **Provider abstraction is mandatory.** All AI calls go through the provider interface.
3. **Pydantic models everywhere.** All data structures use Pydantic for validation.
4. **Rich terminal output.** All user-facing output uses the Rich library.
5. **Graceful error handling.** Every failure mode has an actionable error message.

---

## Coding Standards

- **Python 3.10+** with type hints on all function signatures
- **Pydantic v2** for all data models
- **`ruff`** for linting (`ruff check .`)
- **`ruff format`** for formatting (`ruff format .`)
- **`pytest`** for testing (`pytest -v`)
- **Docstrings** on all public classes and functions (Google style)
- **No wildcard imports**
- **No mutable default arguments**
- **Async-ready** where applicable (AI providers)

---

## Testing Commands

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=docsmith --cov-report=term-missing

# Run specific test module
pytest tests/test_analyzer.py -v

# Lint
ruff check .

# Format
ruff format .
```

---

## File Naming Conventions

- Snake_case for all Python files
- Models use singular nouns (`repo_context.py`, not `repo_contexts.py`)
- Providers use `<name>_provider.py` pattern (except Gemini which is `gemini.py`)
- Prompt templates use `.txt` extension in `docsmith/ai/prompts/`

---

## Dependencies

Core: `typer`, `rich`, `questionary`, `requests`, `pyperclip`, `pydantic`, `jinja2`

AI Providers: `google-generativeai`, `openai`, `anthropic`, `mistralai`

Dev: `pytest`, `pytest-cov`, `ruff`, `pytest-mock`

---

## Configuration

User config stored at `~/.docsmith/config.json`
Cache stored at `~/.docsmith/cache/`

First-run triggers an interactive setup wizard for provider selection and API key input.
