"""Documentation reviewer — checks generated docs for quality issues."""

from __future__ import annotations

import re

from docsmith.models.generated_document import GeneratedDocument, ReviewIssue, ReviewResult
from docsmith.models.repo_context import RepoContext

MIN_DOCUMENT_LENGTH = 200


def review_document(doc: GeneratedDocument, ctx: RepoContext) -> ReviewResult:
    """Review a generated document for common issues.

    Checks for:
    - Hallucinated features or commands
    - Missing critical sections
    - Broken or invalid paths
    - Placeholder content

    Args:
        doc: The generated document.
        ctx: Repository context for validation.

    Returns:
        ReviewResult with any found issues.
    """
    issues: list[ReviewIssue] = []

    content = doc.content

    issues.extend(_check_placeholders(content))
    issues.extend(_check_hallucinated_commands(content, ctx))
    issues.extend(_check_missing_sections(doc))
    issues.extend(_check_broken_references(content, ctx))

    if len(content) < MIN_DOCUMENT_LENGTH:
        issues.append(
            ReviewIssue(
                severity="critical",
                category="incomplete",
                description=f"Document is too short (less than {MIN_DOCUMENT_LENGTH} characters)",
                suggestion="Regenerate with more detail",
            )
        )

    passed = all(i.severity != "critical" for i in issues)

    return ReviewResult(
        issues=issues,
        passed=passed,
        summary=f"Found {len(issues)} issues ({sum(1 for i in issues if i.severity == 'critical')} critical)",
    )


def _check_placeholders(content: str) -> list[ReviewIssue]:
    """Check for placeholder/template content that wasn't filled in."""
    issues = []
    placeholders = [
        r"\[your[- ]",
        r"\[insert ",
        r"\[TODO",
        r"\[FIXME",
        r"<your[- ]",
        r"<insert ",
        r"lorem ipsum",
        r"your-username",
    ]
    for pattern in placeholders:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(
                ReviewIssue(
                    severity="warning",
                    category="placeholder",
                    description=f"Found placeholder content matching: {pattern}",
                    suggestion="Replace with actual repository-specific content",
                )
            )
    return issues


def _check_hallucinated_commands(content: str, ctx: RepoContext) -> list[ReviewIssue]:
    """Check for commands that reference non-existent tools."""
    issues = []

    # Check for wrong package manager commands
    pm = ctx.package_manager.value
    wrong_managers = {
        "pip": ["npm install", "yarn add", "cargo add"],
        "npm": ["pip install", "cargo add", "go get"],
        "cargo": ["pip install", "npm install"],
        "go_mod": ["pip install", "npm install"],
    }

    for wrong_cmd in wrong_managers.get(pm, []):
        if wrong_cmd in content:
            issues.append(
                ReviewIssue(
                    severity="warning",
                    category="hallucination",
                    description=f"Found '{wrong_cmd}' but project uses {pm}",
                    suggestion=f"Use the correct package manager: {pm}",
                )
            )

    return issues


def _check_missing_sections(doc: GeneratedDocument) -> list[ReviewIssue]:
    """Check for missing critical sections in README."""
    issues = []

    if doc.doc_type.value == "README":
        required_headers = ["install", "usage"]
        content_lower = doc.content.lower()
        for header in required_headers:
            if header not in content_lower:
                issues.append(
                    ReviewIssue(
                        severity="warning",
                        category="missing",
                        description=f"README is missing '{header}' section",
                        suggestion=f"Add a {header} section",
                    )
                )

    return issues


def _check_broken_references(content: str, ctx: RepoContext) -> list[ReviewIssue]:
    """Check for references to files/paths that don't exist."""
    issues = []

    # Extract referenced file paths
    path_pattern = re.compile(r"`([a-zA-Z_/][a-zA-Z0-9_./\-]+\.[a-zA-Z]+)`")
    known_paths = {f.path for f in ctx.files}
    known_paths.update(ctx.folder_structure)

    for match in path_pattern.finditer(content):
        ref_path = match.group(1)
        # Skip URLs and common patterns
        if ref_path.startswith("http") or ref_path.startswith("www"):
            continue
        if any(ref_path.endswith(ext) for ext in (".com", ".org", ".io")):
            continue
        # Only warn about specific file references, not general patterns
        if "/" in ref_path and ref_path not in known_paths:
            # Check if parent dir exists
            parent = ref_path.split("/")[0]
            _common_dirs = {
                "src", "lib", "docs", "tests", "test", "scripts", "config",
                "public", "static", "assets", "app", "pkg", "cmd", "internal",
                "dist", "build", "bin", "examples", "example",
            }
            if parent not in ctx.folder_structure and parent not in _common_dirs:
                issues.append(
                    ReviewIssue(
                        severity="info",
                        category="broken_reference",
                        description=f"Reference to '{ref_path}' — verify this path exists",
                        suggestion="Check if this file path is correct",
                    )
                )

    return issues
