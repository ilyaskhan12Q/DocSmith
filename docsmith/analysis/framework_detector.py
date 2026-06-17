"""Framework detector — identify web/CLI frameworks from code and dependencies."""

from __future__ import annotations

from docsmith.models.repo_context import DependencyInfo, FileInfo, Framework

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

_IMPORT_FRAMEWORK_MAP: dict[str, Framework] = {
    "fastapi": Framework.FASTAPI,
    "flask": Framework.FLASK,
    "django": Framework.DJANGO,
    "typer": Framework.TYPER,
    "click": Framework.CLICK,
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

    dep_names = {d.name.lower() for d in dependencies}
    for dep_name, framework in _DEPENDENCY_FRAMEWORK_MAP.items():
        if dep_name.lower() in dep_names:
            detected.append(framework)

    for f in files:
        if not f.content:
            continue
        content_lower = f.content.lower()
        for keyword, framework in _IMPORT_FRAMEWORK_MAP.items():
            if framework not in detected and (
                f"from {keyword}" in content_lower or f"import {keyword}" in content_lower
            ):
                detected.append(framework)

    if not detected:
        return Framework.NONE

    detected.sort(key=lambda f: _FRAMEWORK_PRIORITY.get(f, 0), reverse=True)
    return detected[0]
