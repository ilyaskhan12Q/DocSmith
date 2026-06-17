"""Architecture builder — extract classes, functions, and env vars from source code."""

from __future__ import annotations

import re

from docsmith.models.repo_context import ClassInfo, FileInfo, FunctionInfo


def extract_functions(files: list[FileInfo]) -> list[FunctionInfo]:
    """Extract important public functions from source files."""
    functions: list[FunctionInfo] = []
    for f in files:
        if f.language == "python" and f.content:
            functions.extend(_extract_python_functions(f))
    return functions


def extract_classes(files: list[FileInfo]) -> list[ClassInfo]:
    """Extract important public classes from source files."""
    classes: list[ClassInfo] = []
    for f in files:
        if f.language == "python" and f.content:
            classes.extend(_extract_python_classes(f))
    return classes


def extract_env_variables(files: list[FileInfo]) -> list[str]:
    """Extract referenced environment variables from source files."""
    env_vars: set[str] = set()
    patterns = [
        re.compile(r'os\.environ\[?\.?get\(\s*["\']([A-Z_]+)["\']'),
        re.compile(r'os\.environ\[\s*["\']([A-Z_]+)["\']'),
        re.compile(r'os\.getenv\(\s*["\']([A-Z_]+)["\']'),
        re.compile(r"process\.env\.([A-Z_]+)"),
    ]
    for f in files:
        if not f.content:
            continue
        for pattern in patterns:
            for match in pattern.finditer(f.content):
                env_vars.add(match.group(1))

    for f in files:
        if ".env" in f.path and f.content:
            for line in f.content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    var_name = line.split("=", 1)[0].strip()
                    if var_name:
                        env_vars.add(var_name)

    return sorted(env_vars)


def _extract_docstring(lines: list[str], line_index: int) -> str:
    """Extract a docstring from the line immediately following the given index."""
    if line_index + 1 >= len(lines):
        return ""
    next_line = lines[line_index + 1].strip()
    if next_line.startswith('"""') or next_line.startswith("'''"):
        return next_line.strip('"').strip("'")
    return ""


def _extract_python_functions(f: FileInfo) -> list[FunctionInfo]:
    """Extract public Python functions (top-level only)."""
    functions = []
    lines = f.content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r"^def\s+(\w+)\(([^)]*)\)(?:\s*->\s*(.+))?\s*:", line)
        if match:
            name = match.group(1)
            if not name.startswith("_"):
                sig = f"def {name}({match.group(2)})"
                ret = match.group(3)
                if ret:
                    sig += f" -> {ret.strip()}"

                docstring = _extract_docstring(lines, i)

                decorators = []
                j = i - 1
                while j >= 0 and lines[j].strip().startswith("@"):
                    decorators.insert(0, lines[j].strip())
                    j -= 1

                functions.append(
                    FunctionInfo(
                        name=name,
                        module=f.path,
                        signature=sig,
                        docstring=docstring,
                        decorators=decorators,
                    )
                )
        i += 1
    return functions


def _extract_python_classes(f: FileInfo) -> list[ClassInfo]:
    """Extract public Python classes."""
    classes = []
    lines = f.content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r"^class\s+(\w+)(?:\(([^)]*)\))?\s*:", line)
        if match:
            name = match.group(1)
            if not name.startswith("_"):
                bases_str = match.group(2) or ""
                bases = [b.strip() for b in bases_str.split(",") if b.strip()]

                docstring = _extract_docstring(lines, i)

                methods = []
                j = i + 1
                while j < len(lines):
                    method_line = lines[j]
                    if method_line and not method_line[0].isspace() and method_line.strip():
                        break
                    method_match = re.match(r"\s+def\s+(\w+)", method_line)
                    if method_match:
                        method_name = method_match.group(1)
                        if not method_name.startswith("_") or method_name == "__init__":
                            methods.append(method_name)
                    j += 1

                classes.append(
                    ClassInfo(
                        name=name,
                        module=f.path,
                        bases=bases,
                        docstring=docstring,
                        methods=methods,
                    )
                )
        i += 1
    return classes
