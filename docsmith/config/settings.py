"""DocSmith settings and configuration models."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class AIProvider(str, Enum):
    """Supported AI providers."""

    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"


# Default models per provider
DEFAULT_MODELS: dict[AIProvider, str] = {
    AIProvider.GEMINI: "gemini-2.5-flash",
    AIProvider.OPENAI: "gpt-4o",
    AIProvider.ANTHROPIC: "claude-sonnet-4-20250514",
    AIProvider.MISTRAL: "mistral-large-latest",
}

# Config directory
CONFIG_DIR = Path.home() / ".docsmith"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_DIR = CONFIG_DIR / "cache"

# Default output directory
DEFAULT_OUTPUT_DIR = "docsmith-output"


class ProviderConfig(BaseModel):
    """Configuration for a single AI provider."""

    api_key: str = Field(default="", description="API key for the provider")
    model: str = Field(default="", description="Model to use")
    max_tokens: int = Field(default=4096, description="Max tokens per request")
    temperature: float = Field(default=0.3, description="Generation temperature")


class DocSmithConfig(BaseModel):
    """Complete DocSmith configuration."""

    # AI provider settings
    active_provider: AIProvider = Field(
        default=AIProvider.GEMINI, description="Currently active AI provider"
    )
    providers: dict[str, ProviderConfig] = Field(
        default_factory=dict, description="Provider configurations"
    )

    # GitHub settings
    github_token: str = Field(default="", description="GitHub personal access token")

    # Output settings
    output_dir: str = Field(default=DEFAULT_OUTPUT_DIR, description="Output directory")

    # Generation defaults
    default_audience: str = Field(default="intermediate", description="Default audience level")
    default_tone: str = Field(default="professional", description="Default tone")
    use_emojis: bool = Field(default=True, description="Use emojis by default")
    include_badges: bool = Field(default=True, description="Include badges by default")

    # Cache settings
    cache_enabled: bool = Field(default=True, description="Enable analysis caching")
    cache_ttl_hours: int = Field(default=24, description="Cache TTL in hours")

    def get_provider_config(self) -> ProviderConfig:
        """Get the active provider's configuration."""
        key = self.active_provider.value
        if key not in self.providers:
            self.providers[key] = ProviderConfig(model=DEFAULT_MODELS.get(self.active_provider, ""))
        return self.providers[key]

    def get_api_key(self) -> str:
        """Get the active provider's API key."""
        return self.get_provider_config().api_key

    def get_model(self) -> str:
        """Get the active provider's model."""
        config = self.get_provider_config()
        return config.model or DEFAULT_MODELS.get(self.active_provider, "")

    @property
    def is_configured(self) -> bool:
        """Check if the active provider has an API key set."""
        return bool(self.get_api_key())
