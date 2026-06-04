"""Tests for configuration system."""

from unittest.mock import patch

from docsmith.config.settings import (
    AIProvider,
    DocSmithConfig,
    ProviderConfig,
)
from docsmith.config.storage import (
    load_config,
    save_config,
)


class TestDocSmithConfig:
    """Tests for config model."""

    def test_defaults(self):
        config = DocSmithConfig()
        assert config.active_provider == AIProvider.GEMINI
        assert config.cache_enabled is True
        assert config.use_emojis is True

    def test_is_configured(self):
        config = DocSmithConfig(
            providers={"gemini": ProviderConfig(api_key="test-key")},
        )
        assert config.is_configured is True

    def test_not_configured(self):
        config = DocSmithConfig()
        assert config.is_configured is False

    def test_get_model_default(self):
        config = DocSmithConfig()
        model = config.get_model()
        assert model == "gemini-2.5-flash"

    def test_get_model_custom(self):
        config = DocSmithConfig(
            providers={"gemini": ProviderConfig(api_key="k", model="gemini-pro")},
        )
        assert config.get_model() == "gemini-pro"


class TestConfigStorage:
    """Tests for config persistence."""

    def test_save_and_load(self, tmp_path):
        config_file = tmp_path / "config.json"
        config = DocSmithConfig(
            active_provider=AIProvider.OPENAI,
            providers={"openai": ProviderConfig(api_key="sk-test")},
        )

        with (
            patch("docsmith.config.storage.CONFIG_FILE", config_file),
            patch("docsmith.config.storage.CONFIG_DIR", tmp_path),
            patch("docsmith.config.storage.CACHE_DIR", tmp_path / "cache"),
        ):
            save_config(config)
            loaded = load_config()
            assert loaded.active_provider == AIProvider.OPENAI
            assert loaded.get_api_key() == "sk-test"

    def test_load_missing_config(self, tmp_path):
        config_file = tmp_path / "nonexistent.json"
        with (
            patch("docsmith.config.storage.CONFIG_FILE", config_file),
            patch("docsmith.config.storage.CONFIG_DIR", tmp_path),
            patch("docsmith.config.storage.CACHE_DIR", tmp_path / "cache"),
        ):
            config = load_config()
            assert config.active_provider == AIProvider.GEMINI  # Default
