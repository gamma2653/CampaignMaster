"""
Agent Settings Dialog for configuring AI completion providers.
"""

from typing import cast

from PySide6 import QtCore, QtWidgets

from campaign_master.ai import AICompletionService
from campaign_master.ai.providers import get_available_provider_types, get_provider
from campaign_master.content import api as content_api
from campaign_master.content import planning
from campaign_master.util import get_basic_logger

logger = get_basic_logger(__name__)


class AgentSettingsDialog(QtWidgets.QDialog):
    """Dialog for configuring AI agents."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure AI Agents")
        self.setMinimumSize(700, 550)

        self._proto_user_id = 0  # GUI uses global scope
        self._current_agent: planning.AgentConfig | None = None
        self._agents: list[planning.AgentConfig] = []

        self.init_ui()
        self.load_agents()

    def init_ui(self):
        """Initialize the dialog UI."""
        main_layout = QtWidgets.QVBoxLayout(self)

        # Create splitter for list and form
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        # Left side - agent list
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        list_label = QtWidgets.QLabel("Configured Agents:")
        left_layout.addWidget(list_label)

        self.agent_list = QtWidgets.QListWidget()
        self.agent_list.itemSelectionChanged.connect(self.on_agent_selected)
        left_layout.addWidget(self.agent_list)

        # List buttons
        list_buttons = QtWidgets.QHBoxLayout()
        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.clicked.connect(self.add_agent)
        self.remove_button = QtWidgets.QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_agent)
        self.remove_button.setEnabled(False)
        list_buttons.addWidget(self.add_button)
        list_buttons.addWidget(self.remove_button)
        left_layout.addLayout(list_buttons)

        splitter.addWidget(left_widget)

        # Right side - configuration form
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)

        form_label = QtWidgets.QLabel("Agent Configuration:")
        right_layout.addWidget(form_label)

        # Form in a scroll area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        form_container = QtWidgets.QWidget()
        form_layout = QtWidgets.QFormLayout(form_container)
        form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Name
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("e.g., My Claude Agent")
        form_layout.addRow("Name:", self.name_edit)

        # Provider type
        self.provider_combo = QtWidgets.QComboBox()
        self.provider_combo.addItems(get_available_provider_types())
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        form_layout.addRow("Provider:", self.provider_combo)

        # Model selection
        self.model_combo = QtWidgets.QComboBox()
        self.model_combo.setEditable(True)  # Allow custom model names
        form_layout.addRow("Model:", self.model_combo)

        # API Key
        self.api_key_edit = QtWidgets.QLineEdit()
        self.api_key_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("sk-... or $ENV_VAR_NAME")
        form_layout.addRow("API Key:", self.api_key_edit)

        # Show/hide API key button
        show_key_button = QtWidgets.QPushButton("Show")
        show_key_button.setCheckable(True)
        show_key_button.toggled.connect(
            lambda checked: self.api_key_edit.setEchoMode(
                QtWidgets.QLineEdit.EchoMode.Normal if checked else QtWidgets.QLineEdit.EchoMode.Password
            )
        )
        show_key_button.toggled.connect(lambda checked: show_key_button.setText("Hide" if checked else "Show"))
        api_key_row = QtWidgets.QHBoxLayout()
        api_key_row.addWidget(self.api_key_edit)
        api_key_row.addWidget(show_key_button)
        form_layout.addRow("", api_key_row)

        # Base URL
        self.base_url_edit = QtWidgets.QLineEdit()
        self.base_url_edit.setPlaceholderText("http://localhost:11434 (for Ollama)")
        form_layout.addRow("Base URL:", self.base_url_edit)

        # Temperature
        self.temperature_spin = QtWidgets.QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.7)
        self.temperature_spin.setToolTip("0.0 = deterministic, higher = more creative")
        form_layout.addRow("Temperature:", self.temperature_spin)

        # Max tokens
        self.max_tokens_spin = QtWidgets.QSpinBox()
        self.max_tokens_spin.setRange(50, 8000)
        self.max_tokens_spin.setValue(500)
        self.max_tokens_spin.setSingleStep(50)
        form_layout.addRow("Max Tokens:", self.max_tokens_spin)

        # System prompt
        self.system_prompt_edit = QtWidgets.QTextEdit()
        self.system_prompt_edit.setPlaceholderText("Optional: Additional instructions for the AI...")
        self.system_prompt_edit.setMaximumHeight(100)
        form_layout.addRow("Custom Prompt:", self.system_prompt_edit)

        # Checkboxes
        checkbox_layout = QtWidgets.QHBoxLayout()
        self.default_checkbox = QtWidgets.QCheckBox("Set as default")
        self.default_checkbox.setToolTip("Use this agent for AI completions")
        self.enabled_checkbox = QtWidgets.QCheckBox("Enabled")
        self.enabled_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.default_checkbox)
        checkbox_layout.addWidget(self.enabled_checkbox)
        checkbox_layout.addStretch()
        form_layout.addRow("", checkbox_layout)

        scroll.setWidget(form_container)
        right_layout.addWidget(scroll)

        # Test connection button
        self.test_button = QtWidgets.QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        right_layout.addWidget(self.test_button)

        # Status label
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setWordWrap(True)
        right_layout.addWidget(self.status_label)

        splitter.addWidget(right_widget)

        # Set splitter sizes
        splitter.setSizes([200, 500])

        main_layout.addWidget(splitter)

        # Dialog buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Save | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_and_close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        # Apply initial provider change
        self.on_provider_changed(self.provider_combo.currentText())

        # Disable form until agent selected
        self.set_form_enabled(False)

    def set_form_enabled(self, enabled: bool):
        """Enable or disable the configuration form."""
        self.name_edit.setEnabled(enabled)
        self.provider_combo.setEnabled(enabled)
        self.model_combo.setEnabled(enabled)
        self.api_key_edit.setEnabled(enabled)
        self.base_url_edit.setEnabled(enabled)
        self.temperature_spin.setEnabled(enabled)
        self.max_tokens_spin.setEnabled(enabled)
        self.system_prompt_edit.setEnabled(enabled)
        self.default_checkbox.setEnabled(enabled)
        self.enabled_checkbox.setEnabled(enabled)
        self.test_button.setEnabled(enabled)

    def load_agents(self):
        """Load agents from database."""
        self._agents = cast(
            list[planning.AgentConfig],
            content_api.retrieve_objects(
                planning.AgentConfig,
                proto_user_id=self._proto_user_id,
            ),
        )

        self.agent_list.clear()
        for agent in self._agents:
            item = QtWidgets.QListWidgetItem(agent.name or "(unnamed)")
            item.setData(QtCore.Qt.ItemDataRole.UserRole, agent)
            if agent.is_default:
                item.setText(f"{agent.name or '(unnamed)'} (default)")
            if not agent.is_enabled:
                palette = QtWidgets.QApplication.palette()
                item.setForeground(palette.text())
            self.agent_list.addItem(item)

    def on_agent_selected(self):
        """Handle agent selection change."""
        items = self.agent_list.selectedItems()
        if not items:
            self._current_agent = None
            self.remove_button.setEnabled(False)
            self.set_form_enabled(False)
            self.clear_form()
            return

        self.remove_button.setEnabled(True)
        self.set_form_enabled(True)

        agent: planning.AgentConfig = items[0].data(QtCore.Qt.ItemDataRole.UserRole)
        self._current_agent = agent
        self.populate_form(agent)

    def populate_form(self, agent: planning.AgentConfig):
        """Populate form with agent data."""
        self.name_edit.setText(agent.name)

        # Set provider and update model list
        idx = self.provider_combo.findText(agent.provider_type)
        if idx >= 0:
            self.provider_combo.setCurrentIndex(idx)

        # Set model after provider (so list is populated)
        self.model_combo.setCurrentText(agent.model)

        self.api_key_edit.setText(agent.api_key)
        self.base_url_edit.setText(agent.base_url)
        self.temperature_spin.setValue(agent.temperature)
        self.max_tokens_spin.setValue(agent.max_tokens)
        self.system_prompt_edit.setPlainText(agent.system_prompt)
        self.default_checkbox.setChecked(agent.is_default)
        self.enabled_checkbox.setChecked(agent.is_enabled)

        self.status_label.setText("")

    def clear_form(self):
        """Clear the configuration form."""
        self.name_edit.clear()
        self.provider_combo.setCurrentIndex(0)
        self.model_combo.clear()
        self.api_key_edit.clear()
        self.base_url_edit.clear()
        self.temperature_spin.setValue(0.7)
        self.max_tokens_spin.setValue(500)
        self.system_prompt_edit.clear()
        self.default_checkbox.setChecked(False)
        self.enabled_checkbox.setChecked(True)
        self.status_label.setText("")

    def on_provider_changed(self, provider_type: str):
        """Handle provider type change - update available models."""
        self.model_combo.clear()

        if not provider_type:
            return

        try:
            provider = get_provider(provider_type)
            models = provider.get_available_models()
            self.model_combo.addItems(models)
        except Exception as e:
            logger.warning("Could not get models for %s: %s", provider_type, e)

        # Show/hide base URL based on provider
        is_ollama = provider_type == "ollama"
        self.base_url_edit.setVisible(True)
        if is_ollama:
            self.base_url_edit.setPlaceholderText("http://localhost:11434")
        else:
            self.base_url_edit.setPlaceholderText("Optional: Override API base URL")

    def add_agent(self):
        """Add a new agent configuration."""
        # Create new agent with generated ID
        agent = content_api.create_object(
            planning.AgentConfig,
            proto_user_id=self._proto_user_id,
        )
        agent = cast(planning.AgentConfig, agent)
        agent.name = "New Agent"
        agent.provider_type = "anthropic"
        agent.model = "claude-sonnet-4-20250514"

        # Save to database
        content_api.update_object(agent, proto_user_id=self._proto_user_id)

        # Reload list and select new item
        self.load_agents()
        self.agent_list.setCurrentRow(self.agent_list.count() - 1)

    def remove_agent(self):
        """Remove the selected agent configuration."""
        if not self._current_agent:
            return

        reply = QtWidgets.QMessageBox.question(
            self,
            "Remove Agent",
            f"Are you sure you want to remove '{self._current_agent.name}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            content_api.delete_object(
                cast(planning.ID, self._current_agent.obj_id),
                proto_user_id=self._proto_user_id,
            )
            self._current_agent = None
            self.load_agents()

    def save_current_agent(self) -> bool:
        """Save the current agent configuration."""
        if not self._current_agent:
            return True

        # Validate
        if not self.name_edit.text().strip():
            self.status_label.setText("Error: Name is required")
            self.status_label.setStyleSheet("color: red;")
            return False

        if not self.model_combo.currentText().strip():
            self.status_label.setText("Error: Model is required")
            self.status_label.setStyleSheet("color: red;")
            return False

        # Update agent from form
        self._current_agent.name = self.name_edit.text().strip()
        self._current_agent.provider_type = self.provider_combo.currentText()
        self._current_agent.model = self.model_combo.currentText().strip()
        self._current_agent.api_key = self.api_key_edit.text()
        self._current_agent.base_url = self.base_url_edit.text().strip()
        self._current_agent.temperature = self.temperature_spin.value()
        self._current_agent.max_tokens = self.max_tokens_spin.value()
        self._current_agent.system_prompt = self.system_prompt_edit.toPlainText()
        self._current_agent.is_enabled = self.enabled_checkbox.isChecked()

        # Handle default flag - ensure only one default
        if self.default_checkbox.isChecked():
            # Unset other defaults
            for agent in self._agents:
                if agent.obj_id != self._current_agent.obj_id and agent.is_default:
                    agent.is_default = False
                    content_api.update_object(agent, proto_user_id=self._proto_user_id)
            self._current_agent.is_default = True
        else:
            self._current_agent.is_default = False

        # Save to database
        content_api.update_object(self._current_agent, proto_user_id=self._proto_user_id)

        return True

    def test_connection(self):
        """Test connection to the configured provider."""
        provider_type = self.provider_combo.currentText()
        api_key = self.api_key_edit.text()
        base_url = self.base_url_edit.text()
        model = self.model_combo.currentText()

        # Resolve environment variable
        if api_key.startswith("$"):
            import os

            env_var = api_key[1:]
            api_key = os.environ.get(env_var, "")
            if not api_key:
                self.status_label.setText(f"Error: Environment variable {env_var} not set")
                self.status_label.setStyleSheet("color: red;")
                return

        self.status_label.setText("Testing connection...")
        self.status_label.setStyleSheet("color: gray;")
        QtWidgets.QApplication.processEvents()

        service = AICompletionService.instance()
        success, message = service.test_connection(provider_type, api_key, base_url, model)

        if success:
            self.status_label.setText(f"Success: {message}")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText(f"Error: {message}")
            self.status_label.setStyleSheet("color: red;")

    def save_and_close(self):
        """Save all changes and close the dialog."""
        if self.save_current_agent():
            # Reload the AI service's default agent
            AICompletionService.instance().load_default_agent()
            self.accept()
