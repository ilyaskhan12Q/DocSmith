# Contributing to DocSmith

Thank you for considering contributing to DocSmith! 🎉

## 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/docsmith.git
   cd docsmith
   ```
3. **Set up** the development environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -e ".[dev,all-providers]"
   ```

## 🔧 Development Workflow

### Branch naming

- `feat/description` — new features
- `fix/description` — bug fixes
- `docs/description` — documentation changes
- `refactor/description` — code refactoring

### Making changes

1. Create a branch: `git checkout -b feat/my-feature`
2. Make your changes
3. Run tests: `pytest -v`
4. Run lints: `ruff check . && ruff format --check .`
5. Commit: `git commit -m "feat: add my feature"`
6. Push: `git push origin feat/my-feature`
7. Open a Pull Request

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=docsmith --cov-report=term-missing

# Run a specific test file
pytest tests/test_analyzer.py -v
```

## 📐 Code Style

We use **ruff** for both linting and formatting:

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

### Style rules

- Python 3.10+ with type hints on all function signatures
- Pydantic v2 for all data models
- Google-style docstrings on all public classes and functions
- No wildcard imports
- No mutable default arguments

## 📁 Project Structure

| Directory | Purpose |
|-----------|---------|
| `docsmith/ai/` | AI provider abstraction + prompts |
| `docsmith/analysis/` | Code intelligence extraction |
| `docsmith/config/` | Settings and persistent storage |
| `docsmith/generation/` | Doc planning, writing, review, scoring |
| `docsmith/github/` | GitHub API integration |
| `docsmith/models/` | Pydantic data models |
| `docsmith/output/` | File output and terminal preview |
| `tests/` | Test suite |

## 📝 Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `test:` — tests
- `refactor:` — code refactoring
- `chore:` — maintenance

## 🐛 Reporting Bugs

Open an issue with:
- DocSmith version (`docsmith version`)
- Python version
- Steps to reproduce
- Expected vs actual behavior

## 💡 Feature Requests

Open an issue with the `enhancement` label describing:
- The problem you're trying to solve
- Your proposed solution
- Alternative approaches you've considered

---

Thank you for helping make DocSmith better! ❤️
