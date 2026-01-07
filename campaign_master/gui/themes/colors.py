"""Color mapping for domain object types."""

from typing import Tuple

from ...content import planning
from .dark_theme import DARK_COLORS

# Map object types to their color scheme (border_color, background_color)
OBJECT_TYPE_COLORS: dict[type, Tuple[str, str]] = {
    planning.Rule: (DARK_COLORS.rule_border, DARK_COLORS.rule_bg),
    planning.Character: (DARK_COLORS.character_border, DARK_COLORS.character_bg),
    planning.Point: (DARK_COLORS.point_border, DARK_COLORS.point_bg),
    planning.Arc: (DARK_COLORS.arc_border, DARK_COLORS.arc_bg),
    planning.Segment: (DARK_COLORS.segment_border, DARK_COLORS.segment_bg),
    planning.Location: (DARK_COLORS.location_border, DARK_COLORS.location_bg),
    planning.Item: (DARK_COLORS.item_border, DARK_COLORS.item_bg),
    planning.Objective: (DARK_COLORS.objective_border, DARK_COLORS.objective_bg),
    planning.CampaignPlan: (DARK_COLORS.campaign_border, DARK_COLORS.campaign_bg),
}


def get_colors_for_type(obj_type: type) -> Tuple[str, str]:
    """Get (border_color, bg_color) for an object type.

    Args:
        obj_type: The domain object type (e.g., planning.Rule).

    Returns:
        Tuple of (border_color, background_color) as hex strings.
        Returns default colors if type not found.
    """
    return OBJECT_TYPE_COLORS.get(
        obj_type, (DARK_COLORS.border_default, DARK_COLORS.primary_bg)
    )
