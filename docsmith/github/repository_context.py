"""Repository context builder — assembles RepoContext from raw GitHub data."""

from __future__ import annotations

from typing import Any

from docsmith.github.parser import (
    extract_folder_structure,
    find_screenshots,
    parse_fetched_files,
)
from docsmith.models.repo_context import (
    Language,
    RepoContext,
)

# Map GitHub language names to our enum
_LANGUAGE_MAP: dict[str, Language] = {
    "python": Language.PYTHON,
    "javascript": Language.JAVASCRIPT,
    "typescript": Language.TYPESCRIPT,
    "go": Language.GO,
    "rust": Language.RUST,
    "java": Language.JAVA,
    "c#": Language.CSHARP,
    "c++": Language.CPP,
    "ruby": Language.RUBY,
    "php": Language.PHP,
    "swift": Language.SWIFT,
    "kotlin": Language.KOTLIN,
}


def _detect_language(metadata: dict) -> Language:
    """Detect primary language from GitHub metadata."""
    lang = (metadata.get("language") or "").lower()
    return _LANGUAGE_MAP.get(lang, Language.OTHER)


def build_repo_context(raw_data: dict[str, Any]) -> RepoContext:
    """Build a RepoContext from raw fetched GitHub data.

    Args:
        raw_data: Dict from GitHubFetcher.fetch_repository().

    Returns:
        Populated RepoContext.
    """
    metadata = raw_data.get("metadata") or {}
    tree = raw_data.get("tree") or []
    files_dict = raw_data.get("files") or {}
    commits = raw_data.get("commits") or []

    files = parse_fetched_files(files_dict)
    folder_structure = extract_folder_structure(tree)
    screenshots = find_screenshots(tree)

    # Detect content presence
    tree_paths = {e.get("path", "") for e in tree}
    lower_paths = {p.lower() for p in tree_paths}

    # Extract README content
    raw_readme = ""
    for key in ("README.md", "readme.md", "README.rst"):
        if key in files_dict:
            raw_readme = files_dict[key]
            break

    ctx = RepoContext(
        name=metadata.get("name", ""),
        full_name=metadata.get("full_name", ""),
        description=metadata.get("description") or "",
        url=metadata.get("html_url") or "",
        default_branch=metadata.get("default_branch", "main"),
        stars=metadata.get("stargazers_count", 0),
        forks=metadata.get("forks_count", 0),
        open_issues=metadata.get("open_issues_count", 0),
        topics=metadata.get("topics") or [],
        license_name=(metadata.get("license") or {}).get("spdx_id", ""),
        language=_detect_language(metadata),
        folder_structure=folder_structure,
        files=files,
        entry_points=[f.path for f in files if f.is_entry_point],
        config_files=[f.path for f in files if f.is_config],
        has_readme=any(p in lower_paths for p in ("readme.md", "readme.rst")),
        has_contributing="contributing.md" in lower_paths,
        has_changelog="changelog.md" in lower_paths,
        has_license=any(p.startswith("license") for p in lower_paths),
        has_docs_folder="docs" in folder_structure,
        has_examples=any(d in folder_structure for d in ("examples", "example")),
        has_tests=any(d in folder_structure for d in ("tests", "test", "__tests__")),
        has_ci=".github" in folder_structure or ".circleci" in folder_structure,
        has_docker=any("dockerfile" in p or "docker-compose" in p for p in lower_paths),
        screenshots=screenshots,
        raw_readme=raw_readme,
        recent_commits=commits,
    )

    return ctx
