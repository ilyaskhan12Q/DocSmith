"""Framework detector — identify web/CLI frameworks from code and dependencies."""

from __future__ import annotations

from docsmith.models.repo_context import DependencyInfo, FileInfo, Framework

# Framework detection rules: (dependency_name, framework)
_DEPENDENCY_FRAMEWORK_MAP: dict[str, Framework] = {
    "fastapi": Framework.FASTAPI,
    "flask": Framework.FLASK,
    "django": Framework.DJANGO,
    "express": Framework.EXPRESS,
    "next": Framework.NEXTJS,
    "react": Framework.REACT,
    "vue": Framework.VUE,
    "@angular/core": Framework.ANGULAR,
    "typer": Framework.TYPER,
    "click": Framework.CLICK,
    "gin-gonic/gin": Framework.GIN,
    "actix-web": Framework.ACTIX,
    "spring-boot": Framework.SPRING,
    "rails": Framework.RAILS,
    "laravel/framework": Framework.LARAVEL,
}

# Priority order for framework detection (higher = more important)
_FRAMEWORK_PRIORITY: dict[Framework, int] = {
    Framework.FASTAPI: 10,
    Framework.DJANGO: 10,
    Framework.FLASK: 9,
    Framework.NEXTJS: 10,
    Framework.EXPRESS: 8,
    Framework.REACT: 7,
    Framework.VUE: 7,
    Framework.ANGULAR: 7,
    Framework.TYPER: 6,
    Framework.CLICK: 5,
    Framework.GIN: 8,
    Framework.ACTIX: 8,
    Framework.SPRING: 9,
    Framework.RAILS: 9,
    Framework.LARAVEL: 9,
}


def detect_framework(
    dependencies: list[DependencyInfo],
    files: list[FileInfo],
) -> Framework:
    """Detect the primary framework used in the project.

    Uses dependency names and file content analysis to identify frameworks.
    When multiple frameworks are detected, returns the highest priority one.

    Args:
        dependencies: Detected project dependencies.
        files: Fetched file information.

    Returns:
        The detected Framework enum value.
    """
    detected: list[Framework] = []

    # Check dependencies
    dep_names = {d.name.lower() for d in dependencies}
    for dep_name, framework in _DEPENDENCY_FRAMEWORK_MAP.items():
        if dep_name.lower() in dep_names:
            detected.append(framework)

    # Check file content for import patterns
    for f in files:
        if not f.content:
            continue
        content_lower = f.content.lower()

        if "from fastapi" in content_lower or "import fastapi" in content_lower:
            if Framework.FASTAPI not in detected:
                detected.append(Framework.FASTAPI)
        if "from flask" in content_lower or "import flask" in content_lower:
            if Framework.FLASK not in detected:
                detected.append(Framework.FLASK)
        if "from django" in content_lower or "import django" in content_lower:
            if Framework.DJANGO not in detected:
                detected.append(Framework.DJANGO)
        if "import typer" in content_lower or "from typer" in content_lower:
            if Framework.TYPER not in detected:
                detected.append(Framework.TYPER)
        if "import click" in content_lower or "from click" in content_lower:
            if Framework.CLICK not in detected:
                detected.append(Framework.CLICK)

    if not detected:
        return Framework.NONE

    # Return highest priority
    detected.sort(key=lambda f: _FRAMEWORK_PRIORITY.get(f, 0), reverse=True)
    return detected[0]
