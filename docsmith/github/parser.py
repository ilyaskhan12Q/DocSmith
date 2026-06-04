"""GitHub data parser — transforms raw API data into structured FileInfo objects."""

from __future__ import annotations

from docsmith.models.repo_context import FileInfo

EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".sh": "shell",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
    ".toml": "toml",
    ".md": "markdown",
    ".html": "html",
    ".css": "css",
}

ENTRY_POINT_NAMES = {
    "main.py",
    "app.py",
    "cli.py",
    "server.py",
    "manage.py",
    "wsgi.py",
    "asgi.py",
    "__main__.py",
    "index.js",
    "index.ts",
    "server.js",
    "app.js",
    "main.go",
    "main.rs",
}

CONFIG_BASENAMES = {
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "tsconfig.json",
    "Cargo.toml",
    "go.mod",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    ".env.example",
}


def detect_language(filepath: str) -> str:
    """Detect programming language from file extension."""
    for ext, lang in EXTENSION_LANGUAGE_MAP.items():
        if filepath.endswith(ext):
            return lang
    return ""


def is_entry_point(filepath: str) -> bool:
    """Check if a file is likely an entry point."""
    return filepath.rsplit("/", 1)[-1] in ENTRY_POINT_NAMES


def is_config_file(filepath: str) -> bool:
    """Check if a file is a configuration file."""
    return filepath.rsplit("/", 1)[-1] in CONFIG_BASENAMES


def parse_fetched_files(files: dict[str, str]) -> list[FileInfo]:
    """Parse fetched file data into structured FileInfo objects."""
    return [
        FileInfo(
            path=path,
            content=content,
            size=len(content.encode("utf-8")),
            language=detect_language(path),
            is_entry_point=is_entry_point(path),
            is_config=is_config_file(path),
        )
        for path, content in files.items()
    ]


def extract_folder_structure(tree: list[dict]) -> list[str]:
    """Extract top-level folder structure from a GitHub tree."""
    return sorted(
        entry["path"]
        for entry in tree
        if entry.get("type") == "tree" and "/" not in entry.get("path", "")
    )


def find_screenshots(tree: list[dict]) -> list[str]:
    """Find screenshot/image files in the repository."""
    image_exts = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
    image_dirs = {"docs", "images", "screenshots", "assets", "media", ".github"}
    images = []
    for entry in tree:
        path = entry.get("path", "")
        if entry.get("type") != "blob":
            continue
        if not any(path.lower().endswith(ext) for ext in image_exts):
            continue
        parts = path.split("/")
        if (
            (len(parts) >= 2 and parts[0].lower() in image_dirs)
            or "screenshot" in path.lower()
            or "demo" in path.lower()
        ):
            images.append(path)
    return images
