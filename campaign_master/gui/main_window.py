"""
Main window for the Campaign Master GUI application.

Provides navigation, menu system, and manages the overall application structure.
"""

from PySide6 import QtCore, QtGui, QtWidgets

from campaign_master.content import planning
from campaign_master.gui.widgets.planning import CampaignPlanEdit


class CampaignMasterWindow(QtWidgets.QMainWindow):
    """Main application window with menu bar and navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Campaign Master")
        self.setGeometry(100, 100, 1024, 768)

        # Central widget - stacked widget for switching views
        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Track current editor
        self.current_editor = None

        # Setup UI components
        self.setup_welcome_screen()
        self.setup_menu_bar()

    def setup_menu_bar(self):
        """Create menu bar with File, Edit, Help menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QtGui.QAction("&New Campaign", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_campaign)
        file_menu.addAction(new_action)

        load_action = QtGui.QAction("&Load Campaign", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_campaign)
        file_menu.addAction(load_action)

        save_action = QtGui.QAction("&Save Campaign", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_campaign)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QtGui.QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        # Future: Add edit operations

        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = QtGui.QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_welcome_screen(self):
        """Create welcome/landing screen."""
        welcome = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        # Title
        title_label = QtWidgets.QLabel("Welcome to Campaign Master!")
        title_font = QtGui.QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        layout.addSpacing(40)

        # Description
        desc_label = QtWidgets.QLabel(
            "A companion application for TTRPG game masters,\n"
            "supporting campaign planning and execution."
        )
        desc_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        layout.addSpacing(40)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        new_btn = QtWidgets.QPushButton("Create New Campaign")
        new_btn.setMinimumWidth(200)
        new_btn.setMinimumHeight(40)
        new_btn.clicked.connect(self.new_campaign)
        button_layout.addWidget(new_btn)

        button_layout.addSpacing(20)

        load_btn = QtWidgets.QPushButton("Load Existing Campaign")
        load_btn.setMinimumWidth(200)
        load_btn.setMinimumHeight(40)
        load_btn.clicked.connect(self.load_campaign)
        button_layout.addWidget(load_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        layout.addStretch()

        welcome.setLayout(layout)
        self.central_widget.addWidget(welcome)
        self.welcome_screen = welcome

    def new_campaign(self):
        """Create new campaign plan."""
        editor = CampaignPlanEdit()
        self.central_widget.addWidget(editor)
        self.central_widget.setCurrentWidget(editor)
        self.current_editor = editor

    def load_campaign(self):
        """Load campaign from JSON file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Campaign", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "r") as f:
                    campaign = planning.CampaignPlan.model_validate_json(f.read())
                editor = CampaignPlanEdit(campaign)
                self.central_widget.addWidget(editor)
                self.central_widget.setCurrentWidget(editor)
                self.current_editor = editor
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error Loading Campaign", f"Failed to load campaign:\n{str(e)}"
                )

    def save_campaign(self):
        """Save current campaign to JSON file."""
        if not hasattr(self, "current_editor") or self.current_editor is None:
            QtWidgets.QMessageBox.warning(
                self, "No Campaign", "No campaign is currently open."
            )
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Campaign", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                # TODO: Extract campaign data from editor
                # For now, show a message that this feature is not yet implemented
                QtWidgets.QMessageBox.information(
                    self,
                    "Save Not Implemented",
                    "Saving campaigns is not yet fully implemented.\n"
                    "This feature will be added in a future update.",
                )
                # Future implementation:
                # campaign = self.current_editor.get_campaign()
                # with open(file_path, 'w') as f:
                #     f.write(campaign.model_dump_json(indent=2))
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error Saving Campaign", f"Failed to save campaign:\n{str(e)}"
                )

    def show_about(self):
        """Show about dialog."""
        QtWidgets.QMessageBox.about(
            self,
            "About Campaign Master",
            "Campaign Master\n\n"
            "A companion application for TTRPG game masters.\n\n"
            "Supports campaign planning and execution in both\n"
            "GUI and web modes.",
        )
