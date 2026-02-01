"""
Main window for the Campaign Master GUI application.

Provides navigation, menu system, and manages the overall application structure.
"""

from typing import cast

from PySide6 import QtCore, QtGui, QtWidgets

from campaign_master.ai import AICompletionService
from campaign_master.content import api as content_api
from campaign_master.content import executing, planning
from campaign_master.gui.dialogs import AgentSettingsDialog
from campaign_master.gui.widgets.executing import CampaignExecutionEdit
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
        self.setup_actions()
        self.setup_menu_bar()
        self.setup_welcome_screen()

    def setup_actions(self):
        """Create actions for the menu."""
        # New campaign action
        self.new_action = QtGui.QAction("&New Campaign", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_campaign)

        # Load campaign from database action
        self.load_action = QtGui.QAction("&Load Campaign from Database", self)
        self.load_action.setShortcut("Ctrl+O")
        self.load_action.triggered.connect(self.load_campaign)

        # Import campaign from JSON action
        self.import_action = QtGui.QAction("&Import Campaign from JSON...", self)
        self.import_action.setShortcut("Ctrl+I")
        self.import_action.triggered.connect(self.import_campaign)

        # Save to database action
        self.save_action = QtGui.QAction("&Save to Database", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_campaign)
        self.save_action.setEnabled(False)  # Disabled until campaign opened

        # Export to JSON action
        self.export_action = QtGui.QAction("&Export to JSON...", self)
        self.export_action.setShortcut("Ctrl+Shift+S")
        self.export_action.triggered.connect(self.export_campaign)
        self.export_action.setEnabled(False)  # Disabled until campaign opened

        # Exit action
        self.exit_action = QtGui.QAction("E&xit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.close)

        # Agent actions
        self.configure_agents_action = QtGui.QAction("&Configure Agents...", self)
        self.configure_agents_action.setShortcut("Ctrl+Shift+A")
        self.configure_agents_action.triggered.connect(self.show_agent_settings)

        # Execution actions
        self.new_execution_action = QtGui.QAction("New E&xecution", self)
        self.new_execution_action.setShortcut("Ctrl+Shift+N")
        self.new_execution_action.triggered.connect(self.new_execution)

        self.load_execution_action = QtGui.QAction("Load Execution from &Database", self)
        self.load_execution_action.setShortcut("Ctrl+Shift+O")
        self.load_execution_action.triggered.connect(self.load_execution)

        self.enable_ai_action = QtGui.QAction("&Enable AI Completions", self)
        self.enable_ai_action.setCheckable(True)
        self.enable_ai_action.setChecked(True)
        self.enable_ai_action.triggered.connect(self.toggle_ai_completions)

    def setup_menu_bar(self):
        """Create menu bar with File, Edit, Help menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.import_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.export_action)

        file_menu.addSeparator()

        file_menu.addAction(self.exit_action)

        # Execution menu
        execution_menu = menubar.addMenu("E&xecution")
        execution_menu.addAction(self.new_execution_action)
        execution_menu.addAction(self.load_execution_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        # Future: Add edit operations

        # Agents menu
        agents_menu = menubar.addMenu("&Agents")
        agents_menu.addAction(self.configure_agents_action)
        agents_menu.addSeparator()

        # Default agent submenu (populated dynamically)
        self.default_agent_menu = agents_menu.addMenu("Set &Default Agent")
        self.update_default_agent_menu()

        agents_menu.addSeparator()
        agents_menu.addAction(self.enable_ai_action)

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
            "A companion application for TTRPG game masters,\n" "supporting campaign planning and execution."
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
        new_btn.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                font-weight: 600;
            }
        """
        )
        new_btn.clicked.connect(self.new_campaign)
        button_layout.addWidget(new_btn)

        button_layout.addSpacing(20)

        load_btn = QtWidgets.QPushButton("Load from Database")
        load_btn.setMinimumWidth(200)
        load_btn.setMinimumHeight(40)
        load_btn.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                font-weight: 600;
            }
        """
        )
        load_btn.clicked.connect(self.load_campaign)
        button_layout.addWidget(load_btn)

        button_layout.addSpacing(20)

        import_btn = QtWidgets.QPushButton("Import from JSON")
        import_btn.setMinimumWidth(200)
        import_btn.setMinimumHeight(40)
        import_btn.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                font-weight: 600;
            }
        """
        )
        import_btn.clicked.connect(self.import_campaign)
        button_layout.addWidget(import_btn)

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

    def import_campaign(self):
        """Import campaign from JSON file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import Campaign", "", "JSON Files (*.json);;All Files (*)"
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
                    self,
                    "Error Importing Campaign",
                    f"Failed to import campaign:\n{str(e)}",
                )

    def load_campaign(self):
        """Load campaign from database."""
        try:
            # Retrieve all campaigns from database
            campaigns = content_api.retrieve_objects(planning.CampaignPlan, proto_user_id=0)
            campaigns = cast(list[planning.CampaignPlan], campaigns)

            if not campaigns:
                QtWidgets.QMessageBox.information(
                    self,
                    "No Campaigns",
                    "No campaigns found in the database.\n\nCreate a new campaign or import one from a JSON file.",
                )
                return

            # Create dialog to select campaign
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Load Campaign from Database")
            dialog.setMinimumWidth(500)
            dialog.setMinimumHeight(400)

            layout = QtWidgets.QVBoxLayout()

            # Instructions
            label = QtWidgets.QLabel("Select a campaign to load:")
            layout.addWidget(label)

            # Campaign list
            list_widget = QtWidgets.QListWidget()
            for campaign in campaigns:
                item_text = f"{campaign.title or 'Untitled Campaign'} (ID: {campaign.obj_id})"
                if campaign.summary:
                    item_text += f"\n  {campaign.summary[:100]}{'...' if len(campaign.summary) > 100 else ''}"
                item = QtWidgets.QListWidgetItem(item_text)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, campaign)
                list_widget.addItem(item)

            list_widget.setCurrentRow(0)
            layout.addWidget(list_widget)

            # Delete handler function
            def delete_selected_campaign():
                current_item = list_widget.currentItem()
                if not current_item:
                    return

                campaign = current_item.data(QtCore.Qt.ItemDataRole.UserRole)

                # Confirmation dialog
                reply = QtWidgets.QMessageBox.question(
                    dialog,
                    "Confirm Deletion",
                    f"Are you sure you want to delete '{campaign.title or 'Untitled Campaign'}'?\n\n"
                    "This action cannot be undone.",
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                    QtWidgets.QMessageBox.StandardButton.No,
                )

                if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                    try:
                        # Delete from database
                        content_api.delete_object(campaign.obj_id, proto_user_id=0)

                        # Remove from list
                        list_widget.takeItem(list_widget.row(current_item))

                        # Check if list is empty
                        if list_widget.count() == 0:
                            QtWidgets.QMessageBox.information(
                                dialog,
                                "No Campaigns",
                                "No campaigns found in the database.",
                            )
                            dialog.reject()

                    except Exception as e:
                        QtWidgets.QMessageBox.critical(
                            dialog,
                            "Delete Failed",
                            f"Failed to delete campaign: {str(e)}",
                        )

            # Update delete button state based on selection
            def update_delete_button():
                delete_button.setEnabled(list_widget.currentItem() is not None)

            # Buttons
            button_box = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            delete_button = QtWidgets.QPushButton("Delete")
            button_box.addButton(delete_button, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)

            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            delete_button.clicked.connect(delete_selected_campaign)
            list_widget.itemSelectionChanged.connect(update_delete_button)

            layout.addWidget(button_box)

            dialog.setLayout(layout)

            # Show dialog and get result
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                current_item = list_widget.currentItem()
                if current_item:
                    campaign = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
                    editor = CampaignPlanEdit(campaign)
                    self.central_widget.addWidget(editor)
                    self.central_widget.setCurrentWidget(editor)
                    self.current_editor = editor

                    # Enable save/export actions
                    self.save_action.setEnabled(True)
                    self.export_action.setEnabled(True)

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error Loading Campaign",
                f"Failed to load campaigns from database:\n{str(e)}",
            )

    def save_campaign(self):
        """Save current campaign to database."""
        if not hasattr(self, "current_editor") or self.current_editor is None:
            QtWidgets.QMessageBox.warning(self, "No Campaign", "No campaign is currently open.")
            return

        # Route to execution save if current editor is an execution
        if isinstance(self.current_editor, CampaignExecutionEdit):
            self.save_execution()
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
                self,
                "Error Saving Campaign",
                f"Failed to save campaign to database:\n{str(e)}",
            )

    def export_campaign(self):
        """Export current campaign to JSON file."""
        if not hasattr(self, "current_editor") or self.current_editor is None:
            QtWidgets.QMessageBox.warning(self, "No Campaign", "No campaign is currently open.")
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Campaign", "", "JSON Files (*.json)")

        if file_path:
            try:
                # Ensure .json extension
                if not file_path.endswith(".json"):
                    file_path += ".json"

                # Export campaign data from editor
                campaign = self.current_editor.export_content()

                # Write to JSON file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(campaign.model_dump_json(indent=2))

                QtWidgets.QMessageBox.information(self, "Export Successful", f"Campaign exported to:\n{file_path}")

            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error Exporting Campaign",
                    f"Failed to export campaign:\n{str(e)}",
                )

    def new_execution(self):
        """Create a new campaign execution."""
        editor = CampaignExecutionEdit()
        self.central_widget.addWidget(editor)
        self.central_widget.setCurrentWidget(editor)
        self.current_editor = editor
        self.save_action.setEnabled(True)

    def load_execution(self):
        """Load a campaign execution from database."""
        try:
            executions = content_api.retrieve_objects(executing.CampaignExecution, proto_user_id=0)
            executions = cast(list[executing.CampaignExecution], executions)

            if not executions:
                QtWidgets.QMessageBox.information(
                    self,
                    "No Executions",
                    "No executions found in the database.\n\nCreate a new execution first.",
                )
                return

            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Load Execution from Database")
            dialog.setMinimumWidth(500)
            dialog.setMinimumHeight(400)

            layout = QtWidgets.QVBoxLayout()
            label = QtWidgets.QLabel("Select an execution to load:")
            layout.addWidget(label)

            list_widget = QtWidgets.QListWidget()
            for ex in executions:
                item_text = f"{ex.title or 'Untitled Session'} (ID: {ex.obj_id})"
                if ex.session_date:
                    item_text += f" - {ex.session_date}"
                item = QtWidgets.QListWidgetItem(item_text)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, ex)
                list_widget.addItem(item)

            list_widget.setCurrentRow(0)
            layout.addWidget(list_widget)

            button_box = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

            dialog.setLayout(layout)

            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                current_item = list_widget.currentItem()
                if current_item:
                    ex = current_item.data(QtCore.Qt.ItemDataRole.UserRole)
                    editor = CampaignExecutionEdit(ex)
                    self.central_widget.addWidget(editor)
                    self.central_widget.setCurrentWidget(editor)
                    self.current_editor = editor
                    self.save_action.setEnabled(True)

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error Loading Execution",
                f"Failed to load executions from database:\n{str(e)}",
            )

    def save_execution(self):
        """Save the current execution to database."""
        if not isinstance(self.current_editor, CampaignExecutionEdit):
            return

        try:
            execution = self.current_editor.export_content()

            if self.current_editor.execution is not None:
                content_api.update_object(execution, proto_user_id=0)
                message = "Execution saved to database successfully."
            else:
                content_api._create_object(execution, proto_user_id=0)
                message = "Execution created in database successfully."
                self.current_editor.execution = execution

            QtWidgets.QMessageBox.information(self, "Save Successful", message)

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error Saving Execution",
                f"Failed to save execution to database:\n{str(e)}",
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

    def show_agent_settings(self):
        """Open the agent configuration dialog."""
        dialog = AgentSettingsDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.update_default_agent_menu()

    def toggle_ai_completions(self, enabled: bool):
        """Enable or disable AI completions."""
        AICompletionService.instance().set_enabled(enabled)

    def update_default_agent_menu(self):
        """Update the default agent submenu from database."""
        self.default_agent_menu.clear()

        try:
            agents = content_api.retrieve_objects(planning.AgentConfig, proto_user_id=0)

            if not agents:
                no_agents_action = QtGui.QAction("(No agents configured)", self)
                no_agents_action.setEnabled(False)
                self.default_agent_menu.addAction(no_agents_action)
                return

            action_group = QtGui.QActionGroup(self)
            action_group.setExclusive(True)

            for agent in agents:
                agent = cast(planning.AgentConfig, agent)
                if agent.is_enabled:
                    action = QtGui.QAction(agent.name or "(unnamed)", self)
                    action.setCheckable(True)
                    action.setChecked(agent.is_default)
                    action.setData(str(agent.obj_id))
                    action.triggered.connect(
                        lambda checked, agent_id=str(agent.obj_id): self.set_default_agent(agent_id)
                    )
                    action_group.addAction(action)
                    self.default_agent_menu.addAction(action)

        except Exception:
            pass  # Silently fail if database not ready

    def set_default_agent(self, agent_id: str):
        """Set a specific agent as the default."""
        service = AICompletionService.instance()
        if service.set_default_agent_by_id(agent_id):
            # Update is_default flags in database
            try:
                agents = content_api.retrieve_objects(planning.AgentConfig, proto_user_id=0)
                for agent in agents:
                    agent = cast(planning.AgentConfig, agent)
                    should_be_default = str(agent.obj_id) == agent_id
                    if agent.is_default != should_be_default:
                        agent.is_default = should_be_default
                        content_api.update_object(agent, proto_user_id=0)
            except Exception:
                pass
