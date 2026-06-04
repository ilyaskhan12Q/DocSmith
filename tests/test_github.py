"""Tests for the GitHub fetcher and parser modules."""

import pytest

from docsmith.github.fetcher import parse_repo_url
from docsmith.github.parser import (
    detect_language,
    extract_folder_structure,
    find_screenshots,
    is_config_file,
    is_entry_point,
    parse_fetched_files,
)


class TestParseRepoUrl:
    """Tests for parse_repo_url."""

    def test_full_https_url(self):
        owner, repo = parse_repo_url("https://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_url_with_trailing_slash(self):
        owner, repo = parse_repo_url("https://github.com/owner/repo/")
        assert owner == "owner"
        assert repo == "repo"

    def test_url_with_git_suffix(self):
        owner, repo = parse_repo_url("https://github.com/owner/repo.git")
        assert owner == "owner"
        assert repo == "repo"

    def test_shorthand(self):
        owner, repo = parse_repo_url("owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_without_protocol(self):
        owner, repo = parse_repo_url("github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_invalid_url(self):
        with pytest.raises(ValueError, match="Not a GitHub URL"):
            parse_repo_url("https://gitlab.com/owner/repo")

    def test_missing_repo(self):
        with pytest.raises(ValueError):
            parse_repo_url("https://github.com/owner")


class TestDetectLanguage:
    """Tests for language detection."""

    def test_python(self):
        assert detect_language("main.py") == "python"

    def test_javascript(self):
        assert detect_language("index.js") == "javascript"

    def test_typescript(self):
        assert detect_language("app.ts") == "typescript"

    def test_go(self):
        assert detect_language("main.go") == "go"

    def test_rust(self):
        assert detect_language("lib.rs") == "rust"

    def test_unknown(self):
        assert detect_language("data.bin") == ""


class TestEntryPointDetection:
    """Tests for entry point detection."""

    def test_main_py(self):
        assert is_entry_point("main.py") is True
        assert is_entry_point("src/main.py") is True

    def test_not_entry(self):
        assert is_entry_point("utils.py") is False


class TestConfigDetection:
    """Tests for config file detection."""

    def test_pyproject(self):
        assert is_config_file("pyproject.toml") is True

    def test_package_json(self):
        assert is_config_file("package.json") is True

    def test_not_config(self):
        assert is_config_file("main.py") is False


class TestParseFetchedFiles:
    """Tests for parse_fetched_files."""

    def test_basic(self):
        files = parse_fetched_files(
            {
                "main.py": "print('hello')",
                "pyproject.toml": "[project]\nname='test'",
            }
        )
        assert len(files) == 2
        assert files[0].path == "main.py"
        assert files[0].language == "python"
        assert files[0].is_entry_point is True
        assert files[1].is_config is True


class TestExtractFolderStructure:
    """Tests for folder structure extraction."""

    def test_basic(self):
        tree = [
            {"path": "src", "type": "tree"},
            {"path": "tests", "type": "tree"},
            {"path": "README.md", "type": "blob"},
            {"path": "src/main.py", "type": "blob"},
        ]
        folders = extract_folder_structure(tree)
        assert folders == ["src", "tests"]


class TestFindScreenshots:
    """Tests for screenshot detection."""

    def test_finds_images(self):
        tree = [
            {"path": "docs/screenshot.png", "type": "blob"},
            {"path": "images/demo.gif", "type": "blob"},
            {"path": "src/main.py", "type": "blob"},
        ]
        screenshots = find_screenshots(tree)
        assert len(screenshots) == 2

    def test_no_images(self):
        tree = [
            {"path": "src/main.py", "type": "blob"},
        ]
        assert find_screenshots(tree) == []
