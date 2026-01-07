"""Theme management for Campaign Master GUI."""

import os
from enum import Enum

from PySide6.QtWidgets import QApplication, QGroupBox, QWidget

from .colors import get_colors_for_type
from .dark_theme import create_dark_palette


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

            # Load and apply stylesheet
            self.load_stylesheet("global.qss")

            self.current_mode = mode
        # Future: elif mode == ThemeMode.LIGHT: ...

    def load_stylesheet(self, filename: str):
        """Load QSS file and apply to application.

        Args:
            filename: Name of the stylesheet file in themes/styles/ directory.
        """
        theme_dir = os.path.dirname(__file__)
        qss_path = os.path.join(theme_dir, "styles", filename)

        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.app.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Warning: Could not find stylesheet: {qss_path}")
        except Exception as e:
            print(f"Error loading stylesheet {qss_path}: {e}")


class ThemedWidget:
    """Mixin for widgets that need object-type-specific theming."""

    def apply_object_theme(self, widget: QWidget, obj_type: type):
        """Apply color-coded theme to a widget based on object type.

        Args:
            widget: The widget to apply theme to.
            obj_type: The domain object type (e.g., planning.Rule).
        """
        border_color, bg_color = get_colors_for_type(obj_type)

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
