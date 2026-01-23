"""
Base provider class with common functionality.

Provides shared implementation for building prompts and handling
TTRPG-specific context in AI completions.
"""

from abc import ABC, abstractmethod
from typing import Iterator

from ...util import get_basic_logger
from ..protocol import CompletionRequest, CompletionResponse

logger = get_basic_logger(__name__)


class BaseProvider(ABC):
    """
    Abstract base class for AI providers.

    Provides common functionality for building prompts and handling
    TTRPG-specific context, while requiring subclasses to implement
    the actual API calls.
    """

    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        """
        Initialize the provider.

        Args:
            api_key: API key for authentication
            base_url: Base URL for API calls (optional for some providers)
            model: Model identifier
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        ...

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Provider type identifier."""
        ...

    @abstractmethod
    def validate_config(self, api_key: str, base_url: str, model: str) -> tuple[bool, str]:
        """Validate the provider configuration."""
        ...

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Return list of available model identifiers."""
        ...

    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Perform synchronous text completion."""
        ...

    @abstractmethod
    def complete_streaming(self, request: CompletionRequest) -> Iterator[str]:
        """Perform streaming text completion."""
        ...

    def build_system_prompt(self, request: CompletionRequest) -> str:
        """
        Build the system prompt with TTRPG context.

        Args:
            request: The completion request

        Returns:
            System prompt string
        """
        base_prompt = """You are an AI assistant helping a Game Master create content for a tabletop RPG campaign.

Your role:
- Provide creative, evocative completions that fit fantasy/RPG settings
- Be concise but descriptive - aim for quality over quantity
- Match the tone and style of any existing content
- Consider the context of the entity type being edited
- Use the provided campaign context to maintain consistency with existing characters, locations, and story elements

When completing text:
- Continue naturally from where the user left off
- Maintain consistency with any provided entity data and campaign context
- Reference existing characters, locations, or story elements when appropriate
- Use appropriate vocabulary for the field type (e.g., dramatic for backstories, precise for rules)"""

        if request.system_prompt:
            return f"{base_prompt}\n\nAdditional instructions:\n{request.system_prompt}"
        return base_prompt

    def build_user_prompt(self, request: CompletionRequest) -> str:
        """
        Build the user prompt with context information.

        Args:
            request: The completion request

        Returns:
            User prompt string with context
        """
        parts = []
        context = request.context

        # Add field context
        if "field_name" in context:
            parts.append(f"Field: {context['field_name']}")

        if "entity_type" in context:
            parts.append(f"Entity Type: {context['entity_type']}")

        # Add entity data if available
        if "entity_data" in context and context["entity_data"]:
            entity_info = []
            for key, value in context["entity_data"].items():
                if value:  # Only include non-empty values
                    entity_info.append(f"  {key}: {value}")
            if entity_info:
                parts.append("Current Entity Data:\n" + "\n".join(entity_info))

        # Add campaign context if available
        if "campaign_context" in context and context["campaign_context"]:
            campaign = context["campaign_context"]
            campaign_parts = []

            # Campaign metadata
            if campaign.get("title"):
                campaign_parts.append(f"Campaign: {campaign['title']}")
            if campaign.get("setting"):
                campaign_parts.append(f"Setting: {campaign['setting']}")
            if campaign.get("summary"):
                campaign_parts.append(f"Summary: {campaign['summary']}")

            # Characters (names and roles only for brevity)
            if campaign.get("characters"):
                chars = [
                    f"{c.get('name', 'Unknown')} ({c.get('role', 'unknown role')})"
                    for c in campaign["characters"]
                    if c.get("name")
                ]
                if chars:
                    campaign_parts.append(f"Characters: {', '.join(chars)}")

            # Locations
            if campaign.get("locations"):
                locs = [loc.get("name") for loc in campaign["locations"] if loc.get("name")]
                if locs:
                    campaign_parts.append(f"Locations: {', '.join(locs)}")

            # Story points
            if campaign.get("storypoints"):
                points = [p.get("name") for p in campaign["storypoints"] if p.get("name")]
                if points:
                    campaign_parts.append(f"Story Points: {', '.join(points)}")

            # Arcs
            if campaign.get("storyline"):
                arcs = [a.get("name") for a in campaign["storyline"] if a.get("name")]
                if arcs:
                    campaign_parts.append(f"Story Arcs: {', '.join(arcs)}")

            # Items
            if campaign.get("items"):
                items = [i.get("name") for i in campaign["items"] if i.get("name")]
                if items:
                    campaign_parts.append(f"Items: {', '.join(items)}")

            # Rules
            if campaign.get("rules"):
                rules = [r.get("name") for r in campaign["rules"] if r.get("name")]
                if rules:
                    campaign_parts.append(f"Rules: {', '.join(rules)}")

            # Objectives
            if campaign.get("objectives"):
                objectives = [o.get("name") for o in campaign["objectives"] if o.get("name")]
                if objectives:
                    campaign_parts.append(f"Objectives: {', '.join(objectives)}")

            if campaign_parts:
                parts.append("Campaign Context:\n" + "\n".join(campaign_parts))

        # Add the actual prompt/text to complete
        if request.prompt:
            if parts:
                parts.append(f"\nText to complete:\n{request.prompt}")
            else:
                parts.append(request.prompt)

        # Add instruction
        parts.append(
            "\nProvide a natural continuation or completion. " "Respond with only the completion text, no explanations."
        )

        return "\n".join(parts)
