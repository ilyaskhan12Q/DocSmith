"""GitHub repository fetcher — intelligent data retrieval via REST API."""

from __future__ import annotations

import base64
from typing import Any
from urllib.parse import urlparse

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from docsmith import __version__

console = Console()

GITHUB_API = "https://api.github.com"

PRIORITY_FILES = [
    "README.md",
    "readme.md",
    "README.rst",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "go.sum",
    "Gemfile",
    "composer.json",
    "pom.xml",
    "build.gradle",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".env.example",
    ".env.sample",
    "LICENSE",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "ARCHITECTURE.md",
]

ENTRY_POINT_PATTERNS = [
    "main.py",
    "app.py",
    "cli.py",
    "server.py",
    "index.py",
    "__main__.py",
    "manage.py",
    "wsgi.py",
    "asgi.py",
    "index.js",
    "index.ts",
    "server.js",
    "server.ts",
    "app.js",
    "app.ts",
    "main.go",
    "main.rs",
    "Main.java",
    "Program.cs",
]

CONFIG_PATTERNS = [
    ".env",
    ".env.example",
    "config.py",
    "config.js",
    "config.ts",
    "settings.py",
    ".eslintrc",
    ".prettierrc",
    "tsconfig.json",
    "jest.config",
    "pytest.ini",
    "tox.ini",
    "ruff.toml",
]

MAX_FILE_SIZE = 100_000
MAX_FILES_TO_FETCH = 30


def parse_repo_url(url: str) -> tuple[str, str]:
    """Parse a GitHub URL into owner and repo name.

    Supports formats:
        - https://github.com/owner/repo
        - github.com/owner/repo
        - owner/repo

    Args:
        url: GitHub repository URL or shorthand.

    Returns:
        Tuple of (owner, repo).

    Raises:
        ValueError: If the URL cannot be parsed.
    """
    url = url.strip().rstrip("/")

    # Handle owner/repo shorthand
    if "/" in url and "://" not in url and "." not in url.split("/")[0]:
        parts = url.split("/")
        if len(parts) == 2:
            return parts[0], parts[1]

    # Handle full URLs
    parsed = urlparse(url if "://" in url else f"https://{url}")

    if "github.com" not in (parsed.hostname or ""):
        raise ValueError(f"Not a GitHub URL: {url}")

    path_parts = [p for p in parsed.path.strip("/").split("/") if p]

    if len(path_parts) < 2:
        raise ValueError(f"Cannot extract owner/repo from: {url}")

    owner = path_parts[0]
    repo = path_parts[1].removesuffix(".git")

    return owner, repo


class GitHubFetcher:
    """Fetches repository data from GitHub REST API.

    Uses intelligent file selection to stay within token limits while
    maximizing the information extracted from the repository.
    """

    def __init__(self, token: str = "") -> None:
        """Initialize the fetcher.

        Args:
            token: Optional GitHub personal access token for higher rate limits.
        """
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": f"DocSmith/{__version__}",
            }
        )
        if token:
            self.session.headers["Authorization"] = f"token {token}"

    def _get(self, endpoint: str, params: dict | None = None) -> dict | list | None:
        """Make a GET request to the GitHub API.

        Args:
            endpoint: API endpoint path.
            params: Optional query parameters.

        Returns:
            JSON response data, or None on failure.
        """
        url = f"{GITHUB_API}{endpoint}"
        try:
            resp = self.session.get(url, params=params, timeout=30)

            if resp.status_code == 403:
                remaining = resp.headers.get("X-RateLimit-Remaining", "?")
                console.print(f"[red]✗ GitHub API rate limit hit (remaining: {remaining})[/red]")
                console.print("[dim]Tip: Set a GitHub token with `docsmith config`[/dim]")
                return None

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.Timeout:
            console.print("[red]✗ GitHub API request timed out[/red]")
            return None
        except requests.exceptions.ConnectionError:
            console.print("[red]✗ Could not connect to GitHub API[/red]")
            return None
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗ GitHub API error: {e}[/red]")
            return None

    def fetch_repo_metadata(self, owner: str, repo: str) -> dict[str, Any] | None:
        """Fetch basic repository metadata.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Repository metadata dict, or None on failure.
        """
        return self._get(f"/repos/{owner}/{repo}")

    def fetch_repo_tree(self, owner: str, repo: str, branch: str = "main") -> list[dict] | None:
        """Fetch the repository file tree (recursive).

        Args:
            owner: Repository owner.
            repo: Repository name.
            branch: Branch to fetch from.

        Returns:
            List of tree entries, or None on failure.
        """
        data = self._get(f"/repos/{owner}/{repo}/git/trees/{branch}", {"recursive": "1"})
        if data and isinstance(data, dict):
            return data.get("tree", [])
        return None

    def fetch_file_content(self, owner: str, repo: str, path: str) -> str | None:
        """Fetch a single file's content.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: File path within the repository.

        Returns:
            Decoded file content, or None on failure.
        """
        data = self._get(f"/repos/{owner}/{repo}/contents/{path}")
        if not data or not isinstance(data, dict):
            return None

        # Skip large files
        size = data.get("size", 0)
        if size > MAX_FILE_SIZE:
            return None

        encoding = data.get("encoding", "")
        content = data.get("content", "")

        if encoding == "base64" and content:
            try:
                return base64.b64decode(content).decode("utf-8", errors="replace")
            except Exception:
                return None

        return content or None

    def fetch_recent_commits(self, owner: str, repo: str, count: int = 15) -> list[dict[str, Any]]:
        """Fetch recent commit summaries.

        Args:
            owner: Repository owner.
            repo: Repository name.
            count: Number of commits to fetch.

        Returns:
            List of commit summary dicts.
        """
        data = self._get(f"/repos/{owner}/{repo}/commits", {"per_page": str(count)})
        if not data or not isinstance(data, list):
            return []

        commits = []
        for commit in data:
            commit_data = commit.get("commit", {})
            commits.append(
                {
                    "sha": commit.get("sha", "")[:7],
                    "message": commit_data.get("message", "").split("\n")[0],
                    "author": commit_data.get("author", {}).get("name", ""),
                    "date": commit_data.get("author", {}).get("date", ""),
                }
            )
        return commits

    def fetch_repository(self, owner: str, repo: str) -> dict[str, Any]:
        """Fetch comprehensive repository data using intelligent file selection.

        This is the main entry point. It fetches metadata, identifies important
        files, and retrieves their contents — all while staying within limits.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Dict containing all fetched data.
        """
        result: dict[str, Any] = {
            "metadata": None,
            "tree": [],
            "files": {},
            "commits": [],
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching repository metadata...", total=None)
            metadata = self.fetch_repo_metadata(owner, repo)
            if not metadata:
                console.print(f"[red]✗ Could not fetch repository: {owner}/{repo}[/red]")
                return result
            result["metadata"] = metadata
            progress.update(task, description="✓ Repository metadata fetched")

            branch = metadata.get("default_branch", "main")
            progress.update(task, description="Fetching file tree...")
            tree = self.fetch_repo_tree(owner, repo, branch)
            if tree:
                result["tree"] = tree
            progress.update(task, description=f"✓ File tree fetched ({len(tree or [])} entries)")

            files_to_fetch = self._select_important_files(tree or [])
            progress.update(
                task,
                description=f"Fetching {len(files_to_fetch)} important files...",
            )

            for filepath in files_to_fetch:
                content = self.fetch_file_content(owner, repo, filepath)
                if content is not None:
                    result["files"][filepath] = content

            progress.update(
                task,
                description=f"✓ Fetched {len(result['files'])} files",
            )

            progress.update(task, description="Fetching recent commits...")
            result["commits"] = self.fetch_recent_commits(owner, repo)
            progress.update(
                task,
                description=f"✓ Fetched {len(result['commits'])} recent commits",
            )

        return result

    def _select_important_files(self, tree: list[dict]) -> list[str]:
        """Intelligently select the most important files to fetch.

        Priority order:
        1. Priority files (README, package manifests, etc.)
        2. Entry points
        3. Config files
        4. Source files in src/ or lib/ directories

        Args:
            tree: Repository file tree.

        Returns:
            List of file paths to fetch, capped at MAX_FILES_TO_FETCH.
        """
        selected: list[str] = []
        blob_paths = [entry["path"] for entry in tree if entry.get("type") == "blob"]

        for pattern in PRIORITY_FILES:
            for path in blob_paths:
                if path == pattern or path.endswith(f"/{pattern}"):
                    if path not in selected:
                        selected.append(path)

        for pattern in ENTRY_POINT_PATTERNS:
            for path in blob_paths:
                basename = path.rsplit("/", 1)[-1]
                if basename == pattern and path not in selected:
                    selected.append(path)

        for pattern in CONFIG_PATTERNS:
            for path in blob_paths:
                basename = path.rsplit("/", 1)[-1]
                if basename.startswith(pattern) and path not in selected:
                    selected.append(path)

        source_dirs = {"src", "lib", "app", "pkg", "cmd", "internal"}
        for path in blob_paths:
            parts = path.split("/")
            if len(parts) >= 2 and parts[0] in source_dirs:
                if path.endswith(("__init__.py", "mod.rs", "index.ts", "index.js")):
                    if path not in selected:
                        selected.append(path)

        for path in blob_paths:
            if "/" not in path and path not in selected:
                ext = path.rsplit(".", 1)[-1] if "." in path else ""
                if ext in {"py", "js", "ts", "go", "rs"}:
                    selected.append(path)

        return selected[:MAX_FILES_TO_FETCH]
