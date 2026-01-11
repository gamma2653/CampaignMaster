"""Theme management for Campaign Master GUI."""

from enum import Enum

from PySide6.QtWidgets import QApplication, QGroupBox, QWidget

from .colors import get_colors_for_type
from .dark_theme import DARK_COLORS, create_dark_palette
from .style_builder import StyleBuilder


class ThemeMode(Enum):
    """Available theme modes."""

    DARK = "dark"
    LIGHT = "light"  # Future enhancement


class ThemeManager:
    """Manages application theme loading and switching."""

    def __init__(self, app: QApplication):
        """Initialize theme manager.

        Args:
            app: The QApplication instance.
        """
        self.app = app
        self.current_mode = ThemeMode.DARK

    def load_theme(self, mode: ThemeMode = ThemeMode.DARK):
        """Load theme resources and apply to application.

        Args:
            mode: The theme mode to load (default: DARK).
        """
        if mode == ThemeMode.DARK:
            # Apply dark palette
            self.app.setPalette(create_dark_palette())

            # Generate and apply stylesheet programmatically
            builder = StyleBuilder(DARK_COLORS)
            self.app.setStyleSheet(builder.build_all())

            self.current_mode = mode
        # Future: elif mode == ThemeMode.LIGHT: ...


class ThemedWidget:
    """Mixin for widgets that need object-type-specific theming."""

    def apply_object_theme(self, widget: QWidget, obj_type: type):
        """Apply color-coded theme to a widget based on object type.

        Args:
            widget: The widget to apply theme to.
            obj_type: The domain object type (e.g., planning.Rule).
        """
        border_color, bg_color = get_colors_for_type(obj_type)

        # Create a darker input background for better contrast
        # Parse the bg_color hex and darken it by ~30%
        bg_int = int(bg_color.lstrip('#'), 16)
        r = (bg_int >> 16) & 0xFF
        g = (bg_int >> 8) & 0xFF
        b = bg_int & 0xFF

        # Darken by multiplying by 0.6
        input_r = int(r * 0.6)
        input_g = int(g * 0.6)
        input_b = int(b * 0.6)
        input_bg = f"#{input_r:02x}{input_g:02x}{input_b:02x}"

        stylesheet = f"""
            QWidget {{
                background-color: {bg_color};
            }}
            QGroupBox {{
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 16px;
                margin-top: 16px;
                background-color: {bg_color};
            }}
            QGroupBox::title {{
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
                padding: 0 8px;
            }}
            QFrame {{
                border: 1px solid {border_color};
                border-radius: 4px;
                background-color: {bg_color};
            }}
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {input_bg};
                color: #ffffff;
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 10px 8px;
                font-size: 14px;
                min-height: 18px;
                selection-background-color: rgba(255, 255, 255, 0.2);
                selection-color: #ffffff;
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {border_color};
                background-color: {input_bg};
            }}
            QLineEdit:read-only {{
                background-color: {input_bg};
                color: #a0a0a0;
                border: 1px solid rgba(85, 85, 85, 0.5);
            }}
            QComboBox {{
                background-color: {input_bg};
                color: #ffffff;
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 10px 8px;
                padding-right: 28px;
                font-size: 14px;
                min-height: 18px;
            }}
            QComboBox:hover {{
                border: 2px solid {border_color};
                padding: 9px 7px;
                padding-right: 27px;
            }}
            QComboBox:focus {{
                border: 2px solid {border_color};
                padding: 9px 7px;
                padding-right: 27px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {input_bg};
                color: #ffffff;
                border: 1px solid {border_color};
                selection-background-color: rgba(255, 255, 255, 0.2);
                selection-color: #ffffff;
            }}
            QSpinBox, QDoubleSpinBox {{
                background-color: {input_bg};
                color: #ffffff;
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 10px 8px;
                font-size: 14px;
                min-height: 18px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {border_color};
                padding: 9px 7px;
            }}
            QListWidget {{
                background-color: {input_bg};
                color: #ffffff;
                border: 1px solid {border_color};
                border-radius: 4px;
            }}
            QTableWidget {{
                background-color: {input_bg};
                color: #ffffff;
                border: 1px solid {border_color};
                border-radius: 4px;
                gridline-color: {border_color};
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            QHeaderView::section {{
                background-color: {bg_color};
                color: #ffffff;
                padding: 8px;
                border: none;
                border-bottom: 1px solid {border_color};
                border-right: 1px solid {border_color};
                font-weight: 600;
            }}
        """
        widget.setStyleSheet(stylesheet)

    def create_themed_container(self, obj_type: type, title: str = "") -> QGroupBox:
        """Create a QGroupBox with object-type-specific theming.

        Args:
            obj_type: The domain object type (e.g., planning.Rule).
            title: Optional title for the group box.

        Returns:
            A QGroupBox styled with the appropriate colors for the object type.
        """
        container = QGroupBox(title)
        self.apply_object_theme(container, obj_type)
        return container


__all__ = ["ThemeManager", "ThemedWidget", "ThemeMode"]
