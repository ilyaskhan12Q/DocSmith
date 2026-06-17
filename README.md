<div align="center">

<img src="https://img.shields.io/badge/DocSmith-AI%20Documentation%20Engineer-blue?style=for-the-badge&logo=markdown&logoColor=white" alt="DocSmith">

# DocSmith

### AI-powered documentation engineer for GitHub repositories

[![PyPI version](https://img.shields.io/pypi/v/docsmith-ai?style=flat-square&color=blue)](https://pypi.org/project/docsmith-ai/)
[![Python](https://img.shields.io/pypi/pyversions/docsmith-ai?style=flat-square)](https://pypi.org/project/docsmith-ai/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/docsmith-ai/docsmith/ci.yml?style=flat-square&label=tests)](https://github.com/docsmith-ai/docsmith/actions)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square)](https://github.com/astral-sh/ruff)

**Stop writing docs manually.** DocSmith analyzes your GitHub repository, extracts real code intelligence, and generates production-ready documentation that references your actual architecture, APIs, and functions.

[Getting Started](#getting-started) •
[How It Works](#how-it-works) •
[Features](#features) •
[Providers](#ai-providers) •
[Contributing](#contributing)

</div>

---

## Why DocSmith?

Most doc generators produce **generic AI slop**. DocSmith is different:

- **Analyzes your actual codebase** — detects frameworks, dependencies, APIs, CLI commands, and architecture
- **Builds structured intelligence** — never sends raw code to an LLM; always analyzes first
- **Generates repo-specific docs** — every reference points to real code, real files, real functions
- **Reviews its own output** — catches hallucinations, missing sections, and broken references
- **Scores quality** — rates completeness, correctness, examples, usability (0–100)
- **Self-refines** — fixes issues automatically before output

## Demo

```bash
$ docsmith generate https://github.com/ilyaskhan12Q/Docsmith.git

    ____             _____           _ __  __
   / __ \____  _____/ ___/____ ___  (_) /_/ /_
  / / / / __ \/ ___/\__ \/ __ `__ \/ / __/ __ \
 / /_/ / /_/ / /__ ___/ / / / / / / / /_/ / / /
/_____/\____/\___//____/_/ /_/ /_/_/\__/_/ /_/

  v0.2.1 — AI-powered documentation engineer

 Analyzing tiangolo/fastapi...
✓ Repository metadata fetched
✓ File tree fetched (847 entries)
✓ Fetched 23 files
✓ Fetched 15 recent commits

✓ Analysis complete
  Language: python
  Framework: fastapi
  Dependencies: 12
  Functions: 34
  Classes: 18
  API Endpoints: 0

 Creating documentation plan...
✓ Plan created: 3 documents

  Generating documentation...
 Generating README.md...
✓ README.md (4.2s, 3847 chars)
 Generating CONTRIBUTING.md...
✓ CONTRIBUTING.md (3.1s, 2156 chars)
 Generating ARCHITECTURE.md...
✓ ARCHITECTURE.md (5.7s, 4521 chars)

 Reviewing documentation...
  README.md: ✓ passed (score: 91)
  CONTRIBUTING.md: ✓ passed (score: 88)
  ARCHITECTURE.md: ✓ passed (score: 93)

✓ Written 3 files to docsmith-output/

 Documentation Report

┌──────────────────┬─────────┬─────────┬────────┬──────────┐
│ Document         │  Score  │ Issues  │   Time │  Status  │
├──────────────────┼─────────┼─────────┼────────┼──────────┤
│ README.md        │  91/100 │  0C/0W  │  4.2s  │ ✓ Passed │
│ CONTRIBUTING.md  │  88/100 │  0C/1W  │  3.1s  │ ✓ Passed │
│ ARCHITECTURE.md  │  93/100 │  0C/0W  │  5.7s  │ ✓ Passed │
├──────────────────┼─────────┼─────────┼────────┼──────────┤
│ Overall          │  91/100 │         │        │          │
└──────────────────┴─────────┴─────────┴────────┴──────────┘

 Output: docsmith-output/
```

## Getting Started

### Installation

```bash
pip install docsmith-ai
```

Install with your preferred AI provider:

```bash
# Google Gemini (recommended)
pip install "docsmith-ai[gemini]"

# OpenAI
pip install "docsmith-ai[openai]"

# Anthropic Claude
pip install "docsmith-ai[anthropic]"

# All providers
pip install "docsmith-ai[all-providers]"
```

### First Run

DocSmith will launch a setup wizard on first run:

```bash
docsmith generate https://github.com/owner/repo
```

Or configure manually:

```bash
docsmith config
```

### Quick Generate

```bash
# Full interactive mode
docsmith generate https://github.com/owner/repo

# Quick mode (skip questionnaire, use defaults)
docsmith generate owner/repo --quick

# Preview in terminal
docsmith generate owner/repo --preview

# Custom output directory
docsmith generate owner/repo -o ./docs
```

## How It Works

DocSmith follows a structured pipeline — it never sends raw code to an LLM:

```
Repository URL
     │
     ▼
┌─────────────┐
│  GitHub API  │  Intelligent file selection
│   Fetcher    │  (prioritizes manifests, entry points, configs)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Analyzer   │  Extract dependencies, frameworks, routes,
│              │  CLI commands, classes, functions, env vars
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ RepoContext  │  Structured intelligence (Pydantic model)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Planner    │  Decides document structure based on analysis
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Writer     │  Generates docs using AI + Jinja2 templates
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Reviewer    │  Catches hallucinations, missing sections
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Scorer     │  Quality score (0-100) across 5 dimensions
└──────┬──────┘
       │
       ▼
   Output
```

## Features

### Document Types

| Document | Description |
|----------|-------------|
| `README` | Full project README with badges, install, usage |
| `CONTRIBUTING` | Contribution guide with dev setup |
| `SECURITY` | Security policy and vulnerability reporting |
| `ARCHITECTURE` | System overview with Mermaid diagrams |
| `API_REFERENCE` | Endpoints, commands, classes, functions |
| `CHANGELOG` | Generated from real commit history |
| `DEVELOPMENT_GUIDE` | Full dev environment setup |
| `QUICKSTART` | Minimal getting-started guide |

### Analysis Capabilities

- **Language Detection** — Python, JavaScript, TypeScript, Go, Rust, Java, and more
- **Framework Detection** — FastAPI, Flask, Django, Express, Next.js, React, Typer, Click
- **Dependency Extraction** — requirements.txt, pyproject.toml, package.json, Cargo.toml, go.mod
- **API Route Detection** — FastAPI, Flask, Django, Express endpoints
- **CLI Command Detection** — Typer and Click commands with arguments
- **Code Intelligence** — Public functions, classes, methods, signatures
- **Environment Variables** — From code and .env files

### Quality Scoring

Every generated document is scored on 5 dimensions:

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Correctness | 30% | References real repo content |
| Completeness | 25% | Covers all planned sections |
| Usability | 20% | Structure, readability, links |
| Examples | 15% | Code examples quality |
| Maintainability | 10% | Ease of keeping docs updated |

## AI Providers

| Provider | Model | Install Extra |
|----------|-------|---------------|
| Google Gemini | `gemini-2.0-flash` | `pip install "docsmith-ai[gemini]"` |
| OpenAI | `gpt-4o` | `pip install "docsmith-ai[openai]"` |
| Anthropic | `claude-sonnet-4-20250514` | `pip install "docsmith-ai[anthropic]"` |
| Mistral AI | `mistral-large-latest` | `pip install "docsmith-ai[mistral]"` |

Switch providers at any time:

```bash
docsmith config
```

## Architecture

```
docsmith/
├── ai/                    # AI provider abstraction
│   ├── providers/         # Gemini, OpenAI, Anthropic, Mistral
│   ├── prompts/           # Jinja2 prompt templates
│   └── orchestrator.py    # Provider factory + retry logic
├── analysis/              # Code intelligence extraction
│   ├── analyzer.py        # Main analysis orchestrator
│   ├── dependency_detector.py
│   ├── framework_detector.py
│   ├── route_detector.py
│   ├── cli_detector.py
│   └── architecture_builder.py
├── config/                # Settings + persistent storage
├── generation/            # Doc generation pipeline
│   ├── planner.py         # Creates document structure plans
│   ├── writer.py          # AI-powered doc generation
│   ├── reviewer.py        # Quality review pass
│   ├── scorer.py          # Multi-dimensional scoring
│   └── refiner.py         # Auto-fix review issues
├── github/                # GitHub API integration
│   ├── fetcher.py         # Intelligent file fetching
│   ├── parser.py          # Data transformation
│   └── repository_context.py  # RepoContext builder
├── models/                # Pydantic data models
├── output/                # File output + terminal preview
└── main.py                # Typer CLI entry point
```

## Development

```bash
# Clone the repo
git clone https://github.com/docsmith-ai/docsmith.git
cd docsmith

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev,all-providers]"

# Run tests
pytest -v

# Run with coverage
pytest --cov=docsmith --cov-report=term-missing

# Lint & format
ruff check .
ruff format .
```

## Roadmap

- [ ] **Local repo support** — analyze local directories without GitHub
- [ ] **Parallel generation** — generate multiple docs concurrently
- [ ] **Custom templates** — user-defined Jinja2 prompt templates
- [ ] **CI integration** — GitHub Action for automated doc updates
- [ ] **Diff mode** — show what changed vs existing docs
- [ ] **Multi-language prompts** — generate docs in any language
- [ ] **Plugin system** — custom analyzers and generators

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with  for developers who'd rather ship code than write docs.**

[ Back to top](#docsmith)

</div>

