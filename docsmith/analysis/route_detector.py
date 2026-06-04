"""Route detector — extract API endpoints from web framework code."""

from __future__ import annotations

import re

from docsmith.models.repo_context import APIEndpoint, FileInfo, Framework


def detect_routes(files: list[FileInfo], framework: Framework) -> list[APIEndpoint]:
    """Detect API routes/endpoints from source files.

    Args:
        files: Fetched file information with content.
        framework: Detected framework.

    Returns:
        List of detected API endpoints.
    """
    endpoints: list[APIEndpoint] = []

    for f in files:
        if not f.content or f.language not in ("python", "javascript", "typescript"):
            continue

        if framework == Framework.FASTAPI:
            endpoints.extend(_detect_fastapi_routes(f))
        elif framework == Framework.FLASK:
            endpoints.extend(_detect_flask_routes(f))
        elif framework == Framework.DJANGO:
            endpoints.extend(_detect_django_routes(f))
        elif framework == Framework.EXPRESS:
            endpoints.extend(_detect_express_routes(f))

    return endpoints


def _detect_fastapi_routes(f: FileInfo) -> list[APIEndpoint]:
    """Detect FastAPI route decorators."""
    endpoints = []
    # Match @app.get("/path") or @router.post("/path")
    pattern = re.compile(
        r'@\w+\.(get|post|put|delete|patch|options|head)\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    lines = f.content.splitlines()
    for i, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            method = match.group(1).upper()
            path = match.group(2)
            # Try to find handler name on next line
            handler = ""
            if i + 1 < len(lines):
                func_match = re.match(r"\s*(?:async\s+)?def\s+(\w+)", lines[i + 1])
                if func_match:
                    handler = func_match.group(1)
            endpoints.append(
                APIEndpoint(
                    method=method,
                    path=path,
                    handler=handler,
                )
            )
    return endpoints


def _detect_flask_routes(f: FileInfo) -> list[APIEndpoint]:
    """Detect Flask route decorators."""
    endpoints = []
    pattern = re.compile(
        r'@\w+\.route\(\s*["\']([^"\']+)["\'](?:.*?methods\s*=\s*\[([^\]]+)\])?',
    )
    lines = f.content.splitlines()
    for i, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            path = match.group(1)
            methods_str = match.group(2)
            methods = ["GET"]
            if methods_str:
                methods = [m.strip().strip("'\"") for m in methods_str.split(",")]
            handler = ""
            if i + 1 < len(lines):
                func_match = re.match(r"\s*def\s+(\w+)", lines[i + 1])
                if func_match:
                    handler = func_match.group(1)
            for method in methods:
                endpoints.append(
                    APIEndpoint(
                        method=method.upper(),
                        path=path,
                        handler=handler,
                    )
                )
    return endpoints


def _detect_django_routes(f: FileInfo) -> list[APIEndpoint]:
    """Detect Django URL patterns."""
    endpoints = []
    pattern = re.compile(r'path\(\s*["\']([^"\']+)["\'],\s*(\w+(?:\.\w+)?)')
    for match in pattern.finditer(f.content):
        endpoints.append(
            APIEndpoint(
                method="ANY",
                path=match.group(1),
                handler=match.group(2),
            )
        )
    return endpoints


def _detect_express_routes(f: FileInfo) -> list[APIEndpoint]:
    """Detect Express.js routes."""
    endpoints = []
    pattern = re.compile(r'(?:app|router)\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']')
    for match in pattern.finditer(f.content):
        endpoints.append(
            APIEndpoint(
                method=match.group(1).upper(),
                path=match.group(2),
            )
        )
    return endpoints
