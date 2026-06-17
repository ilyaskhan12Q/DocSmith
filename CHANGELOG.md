# Changelog

All notable changes to DocSmith will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-06-17

### Added
- Stable release of v0.2.1 with integrated clean-code guidelines

### Refactored
- Extracted magic numbers into constants in `scorer.py` and `reviewer.py`
- Simplified framework detection with data-driven lookup
- Reused Markdown responses clean up utility between writer and refiner
- Removed redundant continue/empty instructions and comments across modules

## [0.1.0] - 2026-06-04

### Added

- **Core CLI** with `generate`, `analyze`, `config`, `cache`, and `version` commands
- **GitHub integration** with intelligent file selection and rate limit handling
- **Repository analysis engine**:
  - Dependency detection (Python, JavaScript, Rust, Go)
  - Framework detection (FastAPI, Flask, Django, Express, Typer, Click, and more)
  - API route detection (FastAPI, Flask, Django, Express)
  - CLI command detection (Typer, Click)
  - Code intelligence extraction (classes, functions, env variables)
- **Multi-provider AI support**:
  - Google Gemini (default)
  - OpenAI (GPT-4o)
  - Anthropic (Claude)
  - Mistral AI
- **Documentation generation pipeline**:
  - Intelligent planner with context-aware section planning
  - Jinja2 prompt templates for consistent output
  - Quality reviewer (catches hallucinations, missing sections, placeholders)
  - Multi-dimensional scorer (completeness, correctness, examples, usability, maintainability)
  - Auto-refiner for fixing review issues
- **9 document types**: README, CONTRIBUTING, SECURITY, ARCHITECTURE, API_REFERENCE, CHANGELOG, DEVELOPMENT_GUIDE, QUICKSTART, LICENSE
- **Interactive questionnaire** for customizing generation options
- **First-run setup wizard** for provider configuration
- **Repository analysis caching** with configurable TTL
- **Rich terminal UI** with progress bars, tables, and Markdown preview
- **Preview mode** for terminal output without file writing
- **65 unit tests** covering models, analysis, generation, and configuration
- **CI pipeline** with GitHub Actions (Python 3.10–3.13 matrix)
