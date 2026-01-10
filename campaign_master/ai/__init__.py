"""
AI completion module for CampaignMaster.

Provides AI-powered text completion for GUI form fields using multiple
provider backends (Anthropic, OpenAI, Ollama).
"""

from .protocol import AIProvider, CompletionRequest, CompletionResponse
from .service import AICompletionService

__all__ = [
    "AIProvider",
    "CompletionRequest",
    "CompletionResponse",
    "AICompletionService",
]
