"""
AI Provider registry and factory functions.

Provides a registry of available AI providers and factory functions
for instantiating them by type name.
"""

from typing import TYPE_CHECKING

from .anthropic import AnthropicProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider

if TYPE_CHECKING:
    from .base import BaseProvider

PROVIDER_REGISTRY: dict[str, type["BaseProvider"]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}


def get_provider(
    provider_type: str,
    api_key: str = "",
    base_url: str = "",
    model: str = "",
) -> "BaseProvider":
    """
    Factory function to instantiate a provider by type.

    Args:
        provider_type: The provider type identifier (anthropic, openai, ollama)
        api_key: API key for authentication
        base_url: Base URL for API calls
        model: Model identifier

    Returns:
        An instantiated provider

    Raises:
        ValueError: If provider_type is not registered
    """
    if provider_type not in PROVIDER_REGISTRY:
        raise ValueError(
            f"Unknown provider: {provider_type}. "
            f"Available: {list(PROVIDER_REGISTRY.keys())}"
        )
    return PROVIDER_REGISTRY[provider_type](
        api_key=api_key, base_url=base_url, model=model
    )


def register_provider(name: str, provider_class: type["BaseProvider"]) -> None:
    """
    Register a new provider type.

    Args:
        name: The provider type identifier
        provider_class: The provider class to register
    """
    PROVIDER_REGISTRY[name] = provider_class


def get_available_provider_types() -> list[str]:
    """Return list of registered provider type identifiers."""
    return list(PROVIDER_REGISTRY.keys())


__all__ = [
    "AnthropicProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "PROVIDER_REGISTRY",
    "get_provider",
    "register_provider",
    "get_available_provider_types",
]
