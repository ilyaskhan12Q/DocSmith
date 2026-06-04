"""Repository context models — the structured intelligence extracted from a repo."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Language(str, Enum):
    """Detected primary programming language."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    OTHER = "other"


class Framework(str, Enum):
    """Detected framework."""

    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"
    EXPRESS = "express"
    NEXTJS = "nextjs"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SPRING = "spring"
    RAILS = "rails"
    LARAVEL = "laravel"
    GIN = "gin"
    ACTIX = "actix"
    TYPER = "typer"
    CLICK = "click"
    NONE = "none"


class PackageManager(str, Enum):
    """Detected package manager."""

    PIP = "pip"
    POETRY = "poetry"
    PDM = "pdm"
    UV = "uv"
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"
    CARGO = "cargo"
    GO_MOD = "go_mod"
    MAVEN = "maven"
    GRADLE = "gradle"
    UNKNOWN = "unknown"


class FileInfo(BaseModel):
    """Metadata about a fetched file."""

    path: str = Field(description="Relative path within the repository")
    content: str = Field(default="", description="File content (may be truncated)")
    size: int = Field(default=0, description="File size in bytes")
    language: str = Field(default="", description="Detected file language")
    is_entry_point: bool = Field(default=False, description="Whether this is an entry point")
    is_config: bool = Field(default=False, description="Whether this is a config file")


class DependencyInfo(BaseModel):
    """A detected project dependency."""

    name: str = Field(description="Package name")
    version: str = Field(default="*", description="Version constraint")
    is_dev: bool = Field(default=False, description="Whether this is a dev dependency")
    category: str = Field(default="runtime", description="Dependency category")


class FunctionInfo(BaseModel):
    """An important detected function."""

    name: str = Field(description="Function name")
    module: str = Field(default="", description="Module/file where defined")
    signature: str = Field(default="", description="Function signature")
    docstring: str = Field(default="", description="Function docstring")
    is_public: bool = Field(default=True, description="Whether publicly exported")
    decorators: list[str] = Field(default_factory=list, description="Applied decorators")


class ClassInfo(BaseModel):
    """An important detected class."""

    name: str = Field(description="Class name")
    module: str = Field(default="", description="Module/file where defined")
    bases: list[str] = Field(default_factory=list, description="Base classes")
    docstring: str = Field(default="", description="Class docstring")
    methods: list[str] = Field(default_factory=list, description="Public method names")
    is_public: bool = Field(default=True, description="Whether publicly exported")


class APIEndpoint(BaseModel):
    """A detected API endpoint (REST route)."""

    method: str = Field(description="HTTP method (GET, POST, etc.)")
    path: str = Field(description="Route path")
    handler: str = Field(default="", description="Handler function name")
    description: str = Field(default="", description="Endpoint description")
    parameters: list[str] = Field(default_factory=list, description="Path/query parameters")


class CLICommand(BaseModel):
    """A detected CLI command."""

    name: str = Field(description="Command name")
    description: str = Field(default="", description="Command description")
    arguments: list[str] = Field(default_factory=list, description="Positional arguments")
    options: list[str] = Field(default_factory=list, description="Options/flags")


class RepoContext(BaseModel):
    """The complete structured intelligence extracted from a repository.

    This is the central data model that flows through the entire pipeline.
    It is built by the analysis stage and consumed by the generation stage.
    """

    # Basic metadata
    name: str = Field(description="Repository name")
    full_name: str = Field(default="", description="owner/repo format")
    description: str = Field(default="", description="Repository description")
    url: str = Field(default="", description="Repository URL")
    default_branch: str = Field(default="main", description="Default branch name")
    stars: int = Field(default=0, description="Star count")
    forks: int = Field(default=0, description="Fork count")
    open_issues: int = Field(default=0, description="Open issue count")
    topics: list[str] = Field(default_factory=list, description="Repository topics/tags")
    license_name: str = Field(default="", description="License identifier")

    # Technical metadata
    language: Language = Field(default=Language.OTHER, description="Primary language")
    framework: Framework = Field(default=Framework.NONE, description="Detected framework")
    package_manager: PackageManager = Field(
        default=PackageManager.UNKNOWN, description="Package manager"
    )

    # Structural data
    folder_structure: list[str] = Field(
        default_factory=list, description="Top-level folder structure"
    )
    files: list[FileInfo] = Field(default_factory=list, description="Fetched file metadata")
    entry_points: list[str] = Field(default_factory=list, description="Entry point file paths")
    config_files: list[str] = Field(default_factory=list, description="Configuration file paths")

    # Code intelligence
    dependencies: list[DependencyInfo] = Field(
        default_factory=list, description="Detected dependencies"
    )
    functions: list[FunctionInfo] = Field(
        default_factory=list, description="Important public functions"
    )
    classes: list[ClassInfo] = Field(default_factory=list, description="Important public classes")
    api_endpoints: list[APIEndpoint] = Field(
        default_factory=list, description="Detected API endpoints"
    )
    cli_commands: list[CLICommand] = Field(
        default_factory=list, description="Detected CLI commands"
    )
    env_variables: list[str] = Field(
        default_factory=list, description="Referenced environment variables"
    )

    # Content intelligence
    has_readme: bool = Field(default=False, description="Has existing README")
    has_contributing: bool = Field(default=False, description="Has CONTRIBUTING guide")
    has_changelog: bool = Field(default=False, description="Has CHANGELOG")
    has_license: bool = Field(default=False, description="Has LICENSE file")
    has_docs_folder: bool = Field(default=False, description="Has docs/ folder")
    has_examples: bool = Field(default=False, description="Has examples/ folder")
    has_tests: bool = Field(default=False, description="Has tests/ folder")
    has_ci: bool = Field(default=False, description="Has CI configuration")
    has_docker: bool = Field(default=False, description="Has Dockerfile/docker-compose")
    screenshots: list[str] = Field(
        default_factory=list, description="Detected screenshot/image paths"
    )

    # Raw data for AI consumption
    raw_readme: str = Field(default="", description="Existing README content")
    recent_commits: list[dict[str, Any]] = Field(
        default_factory=list, description="Recent commit summaries"
    )

    def summary(self) -> str:
        """Generate a human-readable summary of the repo context."""
        lines = [
            f"Repository: {self.full_name or self.name}",
            f"Language: {self.language.value}",
            f"Framework: {self.framework.value}",
            f"Package Manager: {self.package_manager.value}",
            f"Dependencies: {len(self.dependencies)}",
            f"Functions: {len(self.functions)}",
            f"Classes: {len(self.classes)}",
            f"API Endpoints: {len(self.api_endpoints)}",
            f"CLI Commands: {len(self.cli_commands)}",
            f"Env Variables: {len(self.env_variables)}",
        ]
        return "\n".join(lines)
