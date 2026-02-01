"""
Prompt builders for AI-powered note refinement and entity extraction.

Reusable by both GUI and web frontends.
"""

from typing import Any

from ..content.executing import RefinementMode
from .protocol import CompletionRequest

NARRATIVE_SYSTEM_PROMPT = (
    "You are a TTRPG session scribe. Transform rough session notes into flowing "
    "narrative prose. Use past tense, third person. Be concise but evocative. "
    "Preserve all factual details from the notes. Do not invent events that are "
    "not mentioned in the original notes."
)

STRUCTURED_SYSTEM_PROMPT = (
    "You are a TTRPG session scribe. Transform rough session notes into a "
    "structured summary with the following sections (omit empty sections):\n"
    "- **Key Events**: Major things that happened\n"
    "- **Decisions Made**: Choices the party or NPCs made\n"
    "- **Combat/Encounters**: Any fights or skill challenges\n"
    "- **Loot/Rewards**: Items, gold, or information gained\n"
    "- **Plot Developments**: Story threads advanced or revealed\n"
    "- **Open Threads**: Unresolved hooks or questions\n\n"
    "Be concise and factual. Do not invent events not in the original notes."
)

ENTITY_EXTRACTION_SYSTEM_PROMPT = (
    "You are a TTRPG session analyst. Given session notes and an entity name and type, "
    "extract all information from the notes that is relevant to that entity. "
    "If the entity is not mentioned or nothing relevant occurred, return an empty string. "
    "Be concise and factual."
)


def build_refinement_prompt(
    raw_notes: str,
    mode: RefinementMode,
    campaign_context: dict[str, Any] | None = None,
) -> CompletionRequest:
    """Build a CompletionRequest for session note refinement."""
    system_prompt = NARRATIVE_SYSTEM_PROMPT if mode == RefinementMode.NARRATIVE else STRUCTURED_SYSTEM_PROMPT

    prompt = f"Refine the following session notes:\n\n{raw_notes}"

    return CompletionRequest(
        prompt=prompt,
        context=campaign_context or {},
        max_tokens=2000,
        temperature=0.5,
        system_prompt=system_prompt,
    )


def build_entity_extraction_prompt(
    raw_session_notes: str,
    entity_name: str,
    entity_type: str,
    campaign_context: dict[str, Any] | None = None,
) -> CompletionRequest:
    """Build a CompletionRequest to extract entity-specific notes from session notes."""
    prompt = (
        f"Given the following session notes, extract information relevant to "
        f"the {entity_type} named '{entity_name}'.\n\n"
        f"Session notes:\n{raw_session_notes}"
    )

    return CompletionRequest(
        prompt=prompt,
        context=campaign_context or {},
        max_tokens=500,
        temperature=0.3,
        system_prompt=ENTITY_EXTRACTION_SYSTEM_PROMPT,
    )
