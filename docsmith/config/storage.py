"""Persistent storage for DocSmith configuration."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from docsmith.config.settings import (
    CACHE_DIR,
    CONFIG_DIR,
    CONFIG_FILE,
    DocSmithConfig,
)

console = Console()


def ensure_config_dir() -> None:
    """Create the config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> DocSmithConfig:
    """Load configuration from disk.

    Returns:
        DocSmithConfig with values from disk, or defaults if no config exists.
    """
    ensure_config_dir()

    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return DocSmithConfig.model_validate(data)
        except json.JSONDecodeError as e:
            console.print(f"[yellow] Config file is corrupted (invalid JSON): {e}[/yellow]")
            console.print("[dim]Using default configuration. Run `docsmith config` to reset.[/dim]")
        except Exception as e:
            console.print(f"[yellow] Could not read config file: {e}[/yellow]")
            console.print("[dim]Check file permissions at: {CONFIG_FILE}[/dim]")

    return DocSmithConfig()


def save_config(config: DocSmithConfig) -> None:
    """Save configuration to disk.

    Args:
        config: The configuration to persist.
    """
    ensure_config_dir()

    data = config.model_dump(mode="json")
    CONFIG_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def config_exists() -> bool:
    """Check if a configuration file exists."""
    return CONFIG_FILE.exists()


def get_cache_path(repo_full_name: str) -> Path:
    """Get the cache file path for a repository.

    Args:
        repo_full_name: Repository in owner/repo format.

    Returns:
        Path to the cache JSON file.
    """
    safe_name = repo_full_name.replace("/", "_")
    return CACHE_DIR / f"{safe_name}.json"


def load_cached_context(repo_full_name: str) -> dict | None:
    """Load cached repository context if available and not expired.

    Args:
        repo_full_name: Repository in owner/repo format.

    Returns:
        Cached context dict, or None if not available.
    """
    import time

    cache_path = get_cache_path(repo_full_name)
    if not cache_path.exists():
        return None

    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        config = load_config()

        cached_at = data.get("_cached_at", 0)
        ttl_seconds = config.cache_ttl_hours * 3600
        if time.time() - cached_at > ttl_seconds:
            return None

        return data
    except Exception:
        return None


def save_cached_context(repo_full_name: str, context_data: dict) -> None:
    """Save repository context to cache.

    Args:
        repo_full_name: Repository in owner/repo format.
        context_data: Context data to cache.
    """
    import time

    ensure_config_dir()
    cache_path = get_cache_path(repo_full_name)
    context_data["_cached_at"] = time.time()

    cache_path.write_text(
        json.dumps(context_data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def clear_cache() -> int:
    """Clear all cached repository data.

    Returns:
        Number of cache files removed.
    """
    count = 0
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()
            count += 1
    return count
