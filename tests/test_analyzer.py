"""Tests for the analysis engine."""

from docsmith.analysis.architecture_builder import (
    extract_classes,
    extract_env_variables,
    extract_functions,
)
from docsmith.analysis.cli_detector import detect_cli_commands
from docsmith.analysis.dependency_detector import (
    detect_package_manager,
    extract_dependencies,
)
from docsmith.analysis.framework_detector import detect_framework
from docsmith.analysis.route_detector import detect_routes
from docsmith.models.repo_context import (
    DependencyInfo,
    FileInfo,
    Framework,
    PackageManager,
)


class TestDependencyDetector:
    """Tests for dependency detection."""

    def test_requirements_txt(self):
        files = [
            FileInfo(
                path="requirements.txt",
                content="fastapi>=0.100\nuvicorn\npydantic==2.0\n",
            )
        ]
        deps = extract_dependencies(files)
        assert len(deps) == 3
        assert deps[0].name == "fastapi"
        assert deps[0].version == ">=0.100"

    def test_package_json(self):
        files = [
            FileInfo(
                path="package.json",
                content='{"dependencies":{"express":"^4.18"},"devDependencies":{"jest":"^29"}}',
            )
        ]
        deps = extract_dependencies(files)
        assert len(deps) == 2
        assert any(d.name == "express" for d in deps)
        assert any(d.is_dev for d in deps)

    def test_detect_pip(self):
        files = [FileInfo(path="requirements.txt", content="flask")]
        assert detect_package_manager(files) == PackageManager.PIP

    def test_detect_npm(self):
        files = [FileInfo(path="package.json", content="{}")]
        assert detect_package_manager(files) == PackageManager.NPM

    def test_detect_cargo(self):
        files = [FileInfo(path="Cargo.toml", content="[package]")]
        assert detect_package_manager(files) == PackageManager.CARGO


class TestFrameworkDetector:
    """Tests for framework detection."""

    def test_detect_fastapi(self):
        deps = [DependencyInfo(name="fastapi")]
        files = [FileInfo(path="app.py", content="from fastapi import FastAPI")]
        assert detect_framework(deps, files) == Framework.FASTAPI

    def test_detect_flask(self):
        deps = [DependencyInfo(name="flask")]
        assert detect_framework(deps, []) == Framework.FLASK

    def test_detect_typer(self):
        deps = [DependencyInfo(name="typer")]
        assert detect_framework(deps, []) == Framework.TYPER

    def test_no_framework(self):
        assert detect_framework([], []) == Framework.NONE

    def test_priority_fastapi_over_typer(self):
        deps = [DependencyInfo(name="fastapi"), DependencyInfo(name="typer")]
        assert detect_framework(deps, []) == Framework.FASTAPI


class TestRouteDetector:
    """Tests for API route detection."""

    def test_fastapi_routes(self):
        files = [
            FileInfo(
                path="app.py",
                language="python",
                content='@app.get("/health")\nasync def health():\n    return {"ok": True}\n',
            )
        ]
        routes = detect_routes(files, Framework.FASTAPI)
        assert len(routes) == 1
        assert routes[0].method == "GET"
        assert routes[0].path == "/health"
        assert routes[0].handler == "health"

    def test_flask_routes(self):
        files = [
            FileInfo(
                path="app.py",
                language="python",
                content='@app.route("/users", methods=["GET", "POST"])\ndef users():\n    pass\n',
            )
        ]
        routes = detect_routes(files, Framework.FLASK)
        assert len(routes) == 2


class TestCLIDetector:
    """Tests for CLI command detection."""

    def test_typer_commands(self):
        files = [
            FileInfo(
                path="cli.py",
                language="python",
                content='@app.command()\ndef hello(name: str):\n    """Say hello."""\n    print(name)\n',
            )
        ]
        commands = detect_cli_commands(files, Framework.TYPER)
        assert len(commands) == 1
        assert commands[0].name == "hello"


class TestArchitectureBuilder:
    """Tests for code intelligence extraction."""

    def test_extract_functions(self):
        files = [
            FileInfo(
                path="utils.py",
                language="python",
                content='def add(a: int, b: int) -> int:\n    """Add two numbers."""\n    return a + b\n\ndef _private():\n    pass\n',
            )
        ]
        functions = extract_functions(files)
        assert len(functions) == 1
        assert functions[0].name == "add"
        assert "int" in functions[0].signature

    def test_extract_classes(self):
        files = [
            FileInfo(
                path="models.py",
                language="python",
                content='class User(BaseModel):\n    """A user model."""\n    def get_name(self):\n        pass\n    def _private(self):\n        pass\n',
            )
        ]
        classes = extract_classes(files)
        assert len(classes) == 1
        assert classes[0].name == "User"
        assert "BaseModel" in classes[0].bases

    def test_extract_env_vars(self):
        files = [
            FileInfo(
                path="config.py",
                language="python",
                content='import os\ndb_url = os.environ.get("DATABASE_URL")\nkey = os.getenv("API_KEY")\n',
            )
        ]
        env_vars = extract_env_variables(files)
        assert "DATABASE_URL" in env_vars
        assert "API_KEY" in env_vars

    def test_env_from_dotenv(self):
        files = [
            FileInfo(
                path=".env.example",
                content="DATABASE_URL=postgres://localhost\nSECRET_KEY=changeme\n",
            )
        ]
        env_vars = extract_env_variables(files)
        assert "DATABASE_URL" in env_vars
        assert "SECRET_KEY" in env_vars
