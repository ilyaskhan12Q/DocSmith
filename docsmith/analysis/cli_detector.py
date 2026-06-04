"""CLI detector — extract CLI commands from Typer/Click applications."""

from __future__ import annotations

import re

from docsmith.models.repo_context import CLICommand, FileInfo, Framework


def detect_cli_commands(files: list[FileInfo], framework: Framework) -> list[CLICommand]:
    """Detect CLI commands from source files.

    Args:
        files: Fetched file information with content.
        framework: Detected framework.

    Returns:
        List of detected CLI commands.
    """
    commands: list[CLICommand] = []

    for f in files:
        if not f.content or f.language != "python":
            continue

        if framework == Framework.TYPER:
            commands.extend(_detect_typer_commands(f))
        elif framework == Framework.CLICK:
            commands.extend(_detect_click_commands(f))
        else:
            # Try both
            commands.extend(_detect_typer_commands(f))
            commands.extend(_detect_click_commands(f))

    return commands


def _detect_typer_commands(f: FileInfo) -> list[CLICommand]:
    """Detect Typer CLI commands."""
    commands = []
    lines = f.content.splitlines()

    for i, line in enumerate(lines):
        # Match @app.command() decorator
        match = re.search(r'@\w+\.command\(\s*(?:["\']([^"\']*)["\'])?\s*\)', line)
        if match:
            cmd_name = match.group(1) or ""
            # Get function name and docstring
            if i + 1 < len(lines):
                func_match = re.match(r"\s*def\s+(\w+)\(([^)]*)\)", lines[i + 1])
                if func_match:
                    func_name = func_match.group(1)
                    params = func_match.group(2)
                    if not cmd_name:
                        cmd_name = func_name.replace("_", "-")

                    # Extract description from docstring
                    desc = ""
                    if i + 2 < len(lines):
                        doc_match = re.match(r'\s*"""(.+?)"""', lines[i + 2])
                        if doc_match:
                            desc = doc_match.group(1)
                        elif '"""' in lines[i + 2]:
                            desc = lines[i + 2].strip().strip('"')

                    # Parse parameters
                    arguments = _extract_params(params)

                    commands.append(
                        CLICommand(
                            name=cmd_name,
                            description=desc,
                            arguments=arguments,
                        )
                    )

    return commands


def _detect_click_commands(f: FileInfo) -> list[CLICommand]:
    """Detect Click CLI commands."""
    commands = []
    lines = f.content.splitlines()

    for i, line in enumerate(lines):
        if "@click.command" in line or "@click.group" in line:
            # Find function def
            for j in range(i + 1, min(i + 5, len(lines))):
                func_match = re.match(r"\s*def\s+(\w+)\(([^)]*)\)", lines[j])
                if func_match:
                    name = func_match.group(1).replace("_", "-")
                    commands.append(CLICommand(name=name))
                    break

        # Detect @click.option and @click.argument
        if "@click.option" in line:
            opt_match = re.search(r'@click\.option\(\s*["\']([^"\']+)["\']', line)
            if opt_match and commands:
                commands[-1].options.append(opt_match.group(1))

    return commands


def _extract_params(params_str: str) -> list[str]:
    """Extract parameter names from a function signature string."""
    params = []
    for part in params_str.split(","):
        part = part.strip()
        if not part or part == "self" or part == "ctx":
            continue
        # Get just the parameter name
        name = part.split(":")[0].split("=")[0].strip()
        if name:
            params.append(name)
    return params
