"""Main analyzer — orchestrates all analysis sub-modules to populate RepoContext."""

from __future__ import annotations

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from docsmith.analysis.architecture_builder import (
    extract_classes,
    extract_env_variables,
    extract_functions,
)
from docsmith.analysis.cli_detector import detect_cli_commands
from docsmith.analysis.dependency_detector import detect_package_manager, extract_dependencies
from docsmith.analysis.framework_detector import detect_framework
from docsmith.analysis.route_detector import detect_routes
from docsmith.models.repo_context import RepoContext

console = Console()


def analyze_repository(ctx: RepoContext) -> RepoContext:
    """Run the full analysis pipeline on a RepoContext.

    Populates the context with:
    - Package manager
    - Dependencies
    - Framework
    - Functions and classes
    - API endpoints
    - CLI commands
    - Environment variables

    Args:
        ctx: Partially populated RepoContext (from repository_context builder).

    Returns:
        Fully populated RepoContext.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing repository...", total=None)

        # 1. Package manager
        progress.update(task, description="Detecting package manager...")
        ctx.package_manager = detect_package_manager(ctx.files)

        # 2. Dependencies
        progress.update(task, description="Extracting dependencies...")
        ctx.dependencies = extract_dependencies(ctx.files)

        # 3. Framework
        progress.update(task, description="Detecting framework...")
        ctx.framework = detect_framework(ctx.dependencies, ctx.files)

        # 4. Functions & classes
        progress.update(task, description="Extracting code intelligence...")
        ctx.functions = extract_functions(ctx.files)
        ctx.classes = extract_classes(ctx.files)

        # 5. API endpoints
        progress.update(task, description="Detecting API routes...")
        ctx.api_endpoints = detect_routes(ctx.files, ctx.framework)

        # 6. CLI commands
        progress.update(task, description="Detecting CLI commands...")
        ctx.cli_commands = detect_cli_commands(ctx.files, ctx.framework)

        # 7. Environment variables
        progress.update(task, description="Extracting environment variables...")
        ctx.env_variables = extract_env_variables(ctx.files)

        progress.update(task, description="✓ Analysis complete")

    return ctx
