"""
Main window for the Campaign Master GUI application.

Provides navigation, menu system, and manages the overall application structure.
"""

from PySide6 import QtCore, QtGui, QtWidgets

from campaign_master.content import api as content_api
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
        self.setup_toolbar()
        self.setup_menu_bar()
        self.setup_welcome_screen()

    def setup_toolbar(self):
        """Create toolbar with quick access buttons."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)

        # New campaign button
        new_action = QtGui.QAction("New", self)
        new_action.setToolTip("Create new campaign (Ctrl+N)")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_campaign)
        toolbar.addAction(new_action)

        # Load campaign button
        load_action = QtGui.QAction("Load", self)
        load_action.setToolTip("Load campaign from JSON (Ctrl+O)")
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_campaign)
        toolbar.addAction(load_action)

        # Save to database button
        self.save_action = QtGui.QAction("Save", self)
        self.save_action.setToolTip("Save campaign to database (Ctrl+S)")
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_campaign)
        self.save_action.setEnabled(False)  # Disabled until campaign opened
        toolbar.addAction(self.save_action)

        # Export to JSON button
        self.export_action = QtGui.QAction("Export", self)
        self.export_action.setToolTip("Export campaign to JSON (Ctrl+Shift+S)")
        self.export_action.setShortcut("Ctrl+Shift+S")
        self.export_action.triggered.connect(self.export_campaign)
        self.export_action.setEnabled(False)  # Disabled until campaign opened
        toolbar.addAction(self.export_action)

        toolbar.addSeparator()

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

        save_action = QtGui.QAction("&Save to Database", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_campaign)
        file_menu.addAction(save_action)

        export_action = QtGui.QAction("&Export to JSON...", self)
        export_action.setShortcut("Ctrl+Shift+S")
        export_action.triggered.connect(self.export_campaign)
        file_menu.addAction(export_action)

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

        # Enable save/export actions
        self.save_action.setEnabled(True)
        self.export_action.setEnabled(True)

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

                # Enable save/export actions
                self.save_action.setEnabled(True)
                self.export_action.setEnabled(True)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error Loading Campaign", f"Failed to load campaign:\n{str(e)}"
                )

    def save_campaign(self):
        """Save current campaign to database."""
        if not hasattr(self, "current_editor") or self.current_editor is None:
            QtWidgets.QMessageBox.warning(
                self, "No Campaign", "No campaign is currently open."
            )
            return

        try:
            # Export campaign data from editor
            campaign = self.current_editor.export_content()

            # Save to database (proto_user_id=0 for GUI mode)
            if self.current_editor.campaign_plan is not None:
                content_api.update_object(campaign, proto_user_id=0)
                message = "Campaign saved to database successfully."
            else:
                content_api._create_object(campaign, proto_user_id=0)
                message = "Campaign created in database successfully."
                self.current_editor.campaign_plan = campaign

            QtWidgets.QMessageBox.information(self, "Save Successful", message)

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error Saving Campaign",
                f"Failed to save campaign to database:\n{str(e)}"
            )

    def export_campaign(self):
        """Export current campaign to JSON file."""
        if not hasattr(self, "current_editor") or self.current_editor is None:
            QtWidgets.QMessageBox.warning(
                self, "No Campaign", "No campaign is currently open."
            )
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Campaign", "", "JSON Files (*.json)"
        )

        if file_path:
            try:
                # Ensure .json extension
                if not file_path.endswith('.json'):
                    file_path += '.json'

                # Export campaign data from editor
                campaign = self.current_editor.export_content()

                # Write to JSON file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(campaign.model_dump_json(indent=2))

                QtWidgets.QMessageBox.information(
                    self, "Export Successful",
                    f"Campaign exported to:\n{file_path}"
                )

            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error Exporting Campaign",
                    f"Failed to export campaign:\n{str(e)}"
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
