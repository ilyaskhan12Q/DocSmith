"""Dependency detector — extract project dependencies from manifest files."""

from __future__ import annotations

import json
import re

from docsmith.models.repo_context import DependencyInfo, FileInfo, PackageManager


def detect_package_manager(files: list[FileInfo]) -> PackageManager:
    """Detect the package manager from available config files."""
    paths = {f.path.rsplit("/", 1)[-1] for f in files}
    if "pyproject.toml" in paths:
        # Check for poetry/pdm/uv
        for f in files:
            if f.path.endswith("pyproject.toml"):
                if "[tool.poetry]" in f.content:
                    return PackageManager.POETRY
                if "[tool.pdm]" in f.content:
                    return PackageManager.PDM
                if "[tool.uv]" in f.content:
                    return PackageManager.UV
                return PackageManager.PIP
    if "requirements.txt" in paths or "setup.py" in paths:
        return PackageManager.PIP
    if "package.json" in paths:
        for f in files:
            if f.path.endswith("yarn.lock"):
                return PackageManager.YARN
            if f.path.endswith("pnpm-lock.yaml"):
                return PackageManager.PNPM
        return PackageManager.NPM
    if "Cargo.toml" in paths:
        return PackageManager.CARGO
    if "go.mod" in paths:
        return PackageManager.GO_MOD
    return PackageManager.UNKNOWN


def extract_dependencies(files: list[FileInfo]) -> list[DependencyInfo]:
    """Extract dependencies from all detected manifest files."""
    deps: list[DependencyInfo] = []
    for f in files:
        basename = f.path.rsplit("/", 1)[-1]
        if basename == "requirements.txt":
            deps.extend(_parse_requirements_txt(f.content))
        elif basename == "pyproject.toml":
            deps.extend(_parse_pyproject_toml(f.content))
        elif basename == "package.json":
            deps.extend(_parse_package_json(f.content))
        elif basename == "Cargo.toml":
            deps.extend(_parse_cargo_toml(f.content))
        elif basename == "go.mod":
            deps.extend(_parse_go_mod(f.content))
    return deps


def _parse_requirements_txt(content: str) -> list[DependencyInfo]:
    """Parse requirements.txt format."""
    deps = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*([>=<~!]+.+)?", line)
        if match:
            deps.append(
                DependencyInfo(
                    name=match.group(1),
                    version=match.group(2) or "*",
                )
            )
    return deps


def _parse_pyproject_toml(content: str) -> list[DependencyInfo]:
    """Parse dependencies from pyproject.toml (basic TOML parsing)."""
    deps = []
    in_deps = False
    in_dev_deps = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[project]":
            continue
        if "dependencies" in stripped and "=" in stripped and "[" in stripped:
            in_deps = True
            in_dev_deps = "dev" in stripped or "optional" in stripped
            continue
        if stripped.startswith("[") and in_deps:
            in_deps = False
            in_dev_deps = False
            continue
        if stripped == "]":
            in_deps = False
            continue
        if in_deps:
            # Parse "package>=version" from quoted strings
            match = re.search(r'"([a-zA-Z0-9_\-\.]+)\s*([>=<~!].*?)?"', stripped)
            if match:
                deps.append(
                    DependencyInfo(
                        name=match.group(1),
                        version=match.group(2) or "*",
                        is_dev=in_dev_deps,
                    )
                )
    return deps


def _parse_package_json(content: str) -> list[DependencyInfo]:
    """Parse package.json dependencies."""
    deps = []
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return deps
    for name, version in (data.get("dependencies") or {}).items():
        deps.append(DependencyInfo(name=name, version=version))
    for name, version in (data.get("devDependencies") or {}).items():
        deps.append(DependencyInfo(name=name, version=version, is_dev=True))
    return deps


def _parse_cargo_toml(content: str) -> list[DependencyInfo]:
    """Parse Cargo.toml dependencies (basic)."""
    deps = []
    in_deps = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped in ("[dependencies]", "[dev-dependencies]"):
            in_deps = True
            continue
        if stripped.startswith("[") and in_deps:
            in_deps = False
            continue
        if in_deps and "=" in stripped:
            parts = stripped.split("=", 1)
            name = parts[0].strip()
            version = parts[1].strip().strip('"').strip("'")
            deps.append(DependencyInfo(name=name, version=version))
    return deps


def _parse_go_mod(content: str) -> list[DependencyInfo]:
    """Parse go.mod dependencies."""
    deps = []
    in_require = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("require ("):
            in_require = True
            continue
        if stripped == ")" and in_require:
            in_require = False
            continue
        if in_require:
            parts = stripped.split()
            if len(parts) >= 2:
                deps.append(DependencyInfo(name=parts[0], version=parts[1]))
        elif stripped.startswith("require "):
            parts = stripped.split()
            if len(parts) >= 3:
                deps.append(DependencyInfo(name=parts[1], version=parts[2]))
    return deps
