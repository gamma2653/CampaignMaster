"""Dark theme configuration for Campaign Master GUI."""

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette


@dataclass
class ColorScheme:
    """Color definitions for dark theme."""

    # Base colors
    primary_bg: str = "#1a341a"
    secondary_bg: str = "#1f3f1f"
    tertiary_bg: str = "#2a4a2a"
    text_primary: str = "#ffffff"
    text_secondary: str = "#e0e0e0"
    text_disabled: str = "#a0a0a0"
    border_default: str = "#555555"

    # Button colors
    button_add: str = "#4CAF50"
    button_add_hover: str = "#45a049"
    button_add_pressed: str = "#3d8b40"
    button_add_disabled: str = "#888888"
    button_submit: str = "#008CBA"

    # Highlight colors
    highlight: str = "#3a5a3a"
    highlight_hover: str = "#4a6a4a"
    highlight_pressed: str = "#5a7a5a"

    # Scrollbar colors
    scrollbar_handle: str = "#3a5a3a"
    scrollbar_handle_hover: str = "#4a6a4a"
    scrollbar_handle_pressed: str = "#5a7a5a"

    # Menu colors
    menu_bg: str = "rgba(26, 52, 26, 0.8)"
    menu_border: str = "rgba(255, 255, 255, 0.1)"
    menu_item_hover: str = "rgba(255, 255, 255, 0.05)"
    menu_item_pressed: str = "rgba(255, 255, 255, 0.1)"

    # Tab colors
    tab_bg: str = "#2a4a2a"
    tab_selected_bg: str = "#1a341a"

    # Progress bar
    progress_chunk: str = "#4CAF50"
    progress_bg: str = "#2a4a2a"

    # Tooltip
    tooltip_bg: str = "#2a4a2a"

    # Splitter
    splitter_handle: str = "#3a5a3a"
    splitter_handle_hover: str = "#4CAF50"
    splitter_handle_pressed: str = "#45a049"

    # Disabled state
    disabled_bg: str = "#0f240f"
    disabled_border: str = "#444444"

    # Section colors (border, background)
    rule_border: str = "#82181a"
    rule_bg: str = "#460809"

    character_border: str = "#733e0a"
    character_bg: str = "#432004"

    point_border: str = "#0d542b"
    point_bg: str = "#032e15"

    arc_border: str = "#59168b"
    arc_bg: str = "#3c0366"

    segment_border: str = "#59168b"
    segment_bg: str = "#3c0366"

    location_border: str = "#0d542b"
    location_bg: str = "#032e15"

    item_border: str = "#1c398e"
    item_bg: str = "#162456"

    objective_border: str = "#59168b"
    objective_bg: str = "#3c0366"

    campaign_border: str = "#1c398e"
    campaign_bg: str = "#162456"


# Global instance
DARK_COLORS = ColorScheme()


def create_dark_palette() -> QPalette:
    """Create QPalette for dark theme.

    Returns:
        QPalette configured with dark theme colors.
    """
    palette = QPalette()

    # Window colors
    palette.setColor(QPalette.ColorRole.Window, QColor(DARK_COLORS.primary_bg))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(DARK_COLORS.text_primary))

    # Base colors (for text entry widgets)
    palette.setColor(QPalette.ColorRole.Base, QColor(DARK_COLORS.primary_bg))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(DARK_COLORS.secondary_bg))

    # Text colors
    palette.setColor(QPalette.ColorRole.Text, QColor(DARK_COLORS.text_primary))
    palette.setColor(
        QPalette.ColorRole.PlaceholderText, QColor(DARK_COLORS.text_disabled)
    )

    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(DARK_COLORS.tertiary_bg))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(DARK_COLORS.text_primary))

    # Highlight colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(DARK_COLORS.highlight))
    palette.setColor(
        QPalette.ColorRole.HighlightedText, QColor(DARK_COLORS.text_primary)
    )

    # Bright text (for tooltips, etc.)
    palette.setColor(QPalette.ColorRole.BrightText, QColor(DARK_COLORS.text_primary))

    # Link colors
    palette.setColor(QPalette.ColorRole.Link, QColor("#4CAF50"))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor("#45a049"))

    # Disabled state
    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.WindowText,
        QColor(DARK_COLORS.text_disabled),
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.Text,
        QColor(DARK_COLORS.text_disabled),
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.ButtonText,
        QColor(DARK_COLORS.text_disabled),
    )

    return palette
