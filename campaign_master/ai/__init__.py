"""
AI completion module for CampaignMaster.

Provides AI-powered text completion for GUI form fields using multiple
provider backends (Anthropic, OpenAI, Ollama).
"""

from .protocol import AIProvider, CompletionRequest, CompletionResponse

__all__ = [
    "AIProvider",
    "CompletionRequest",
    "CompletionResponse",
    "AICompletionService",
]


def __getattr__(name: str):
    """Lazy import for AICompletionService to avoid PySide6 dependency in web mode."""
    if name == "AICompletionService":
        from .service import AICompletionService

        return AICompletionService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
