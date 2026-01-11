"""Programmatic stylesheet builder for Campaign Master GUI."""

from .dark_theme import ColorScheme


class StyleBuilder:
    """Builds QSS stylesheets programmatically from ColorScheme."""

    def __init__(self, colors: ColorScheme):
        """Initialize builder with a color scheme.

        Args:
            colors: ColorScheme instance defining all theme colors.
        """
        self.colors = colors

    def build_buttons(self) -> str:
        """Build button styles."""
        return f"""
QPushButton {{
    background-color: {self.colors.button_add};
    color: {self.colors.text_primary};
    border: none;
    border-radius: 4px;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: {self.colors.button_add_hover};
}}
QPushButton:pressed {{
    background-color: {self.colors.button_add_pressed};
}}
QPushButton:disabled {{
    background-color: {self.colors.button_add_disabled};
    color: #c0c0c0;
}}
QPushButton:focus {{
    outline: 2px solid {self.colors.button_add};
    outline-offset: 2px;
}}
QDialogButtonBox QPushButton {{
    min-width: 80px;
}}
"""

    def build_scrollbars(self) -> str:
        """Build scrollbar styles."""
        return f"""
QScrollBar:vertical {{
    background-color: {self.colors.primary_bg};
    width: 12px;
    border: none;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background-color: {self.colors.scrollbar_handle};
    border-radius: 6px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {self.colors.scrollbar_handle_hover};
}}
QScrollBar::handle:vertical:pressed {{
    background-color: {self.colors.scrollbar_handle_pressed};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: none;
}}
QScrollBar:horizontal {{
    background-color: {self.colors.primary_bg};
    height: 12px;
    border: none;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background-color: {self.colors.scrollbar_handle};
    border-radius: 6px;
    min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {self.colors.scrollbar_handle_hover};
}}
QScrollBar::handle:horizontal:pressed {{
    background-color: {self.colors.scrollbar_handle_pressed};
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {{
    background: none;
}}
"""

    def build_menus(self) -> str:
        """Build menu and menubar styles."""
        return f"""
QMenuBar {{
    background-color: {self.colors.menu_bg};
    color: {self.colors.text_primary};
    border-bottom: 1px solid {self.colors.menu_border};
    padding: 4px;
}}
QMenuBar::item {{
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background-color: {self.colors.menu_item_hover};
}}
QMenuBar::item:pressed {{
    background-color: {self.colors.menu_item_pressed};
}}
QMenu {{
    background-color: {self.colors.primary_bg};
    color: {self.colors.text_primary};
    border: 1px solid {self.colors.border_default};
    border-radius: 4px;
    padding: 4px;
}}
QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {self.colors.highlight};
}}
QMenu::separator {{
    height: 1px;
    background-color: {self.colors.border_default};
    margin: 4px 0px;
}}
"""

    def build_toolbar(self) -> str:
        """Build toolbar styles."""
        return f"""
QToolBar {{
    background-color: {self.colors.menu_bg};
    border-bottom: 1px solid {self.colors.menu_border};
    spacing: 8px;
    padding: 4px;
}}
QToolButton {{
    background-color: transparent;
    color: {self.colors.text_primary};
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 14px;
}}
QToolButton:hover {{
    background-color: {self.colors.menu_item_hover};
}}
QToolButton:pressed {{
    background-color: {self.colors.menu_item_pressed};
}}
"""

    def build_statusbar(self) -> str:
        """Build status bar styles."""
        return f"""
QStatusBar {{
    background-color: {self.colors.menu_bg};
    color: {self.colors.text_primary};
    border-top: 1px solid {self.colors.menu_border};
}}
QStatusBar::item {{
    border: none;
}}
"""

    def build_tabs(self) -> str:
        """Build tab widget styles."""
        return f"""
QTabWidget::pane {{
    border: 1px solid {self.colors.border_default};
    border-radius: 4px;
    background-color: {self.colors.primary_bg};
}}
QTabBar::tab {{
    background-color: {self.colors.tab_bg};
    color: {self.colors.text_primary};
    border: 1px solid {self.colors.border_default};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 8px 16px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {self.colors.tab_selected_bg};
    border-bottom: 1px solid {self.colors.tab_selected_bg};
}}
QTabBar::tab:hover {{
    background-color: {self.colors.highlight};
}}
"""

    def build_controls(self) -> str:
        """Build checkbox, radio button, and slider styles."""
        return f"""
QCheckBox {{
    color: {self.colors.text_primary};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {self.colors.border_default};
    border-radius: 4px;
    background-color: {self.colors.primary_bg};
}}
QCheckBox::indicator:hover {{
    border: 1px solid {self.colors.button_add};
}}
QCheckBox::indicator:checked {{
    background-color: {self.colors.button_add};
    border: 1px solid {self.colors.button_add};
}}
QCheckBox::indicator:disabled {{
    border: 1px solid {self.colors.disabled_border};
    background-color: {self.colors.disabled_bg};
}}
QRadioButton {{
    color: {self.colors.text_primary};
    spacing: 8px;
}}
QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {self.colors.border_default};
    border-radius: 9px;
    background-color: {self.colors.primary_bg};
}}
QRadioButton::indicator:hover {{
    border: 1px solid {self.colors.button_add};
}}
QRadioButton::indicator:checked {{
    background-color: {self.colors.button_add};
    border: 1px solid {self.colors.button_add};
}}
QRadioButton::indicator:disabled {{
    border: 1px solid {self.colors.disabled_border};
    background-color: {self.colors.disabled_bg};
}}
QSlider::groove:horizontal {{
    background-color: {self.colors.tertiary_bg};
    height: 4px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background-color: {self.colors.button_add};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
QSlider::handle:horizontal:hover {{
    background-color: {self.colors.button_add_hover};
}}
"""

    def build_misc(self) -> str:
        """Build tooltip, splitter, and progress bar styles."""
        return f"""
QToolTip {{
    background-color: {self.colors.tooltip_bg};
    color: {self.colors.text_primary};
    border: 1px solid {self.colors.border_default};
    border-radius: 4px;
    padding: 4px 8px;
}}
QSplitter::handle {{
    background-color: {self.colors.splitter_handle};
    border-radius: 2px;
}}
QSplitter::handle:horizontal {{
    width: 5px;
    margin: 2px 0;
}}
QSplitter::handle:vertical {{
    height: 5px;
    margin: 0 2px;
}}
QSplitter::handle:hover {{
    background-color: {self.colors.splitter_handle_hover};
}}
QSplitter::handle:pressed {{
    background-color: {self.colors.splitter_handle_pressed};
}}
QProgressBar {{
    background-color: {self.colors.progress_bg};
    border: 1px solid {self.colors.border_default};
    border-radius: 4px;
    text-align: center;
    color: {self.colors.text_primary};
    height: 20px;
}}
QProgressBar::chunk {{
    background-color: {self.colors.progress_chunk};
    border-radius: 3px;
}}
"""

    def build_all(self) -> str:
        """Build complete stylesheet by combining all style sections.

        Returns:
            Complete QSS stylesheet string.
        """
        sections = [
            self.build_buttons(),
            self.build_scrollbars(),
            self.build_menus(),
            self.build_toolbar(),
            self.build_statusbar(),
            self.build_tabs(),
            self.build_controls(),
            self.build_misc(),
        ]
        return "\n".join(sections)
