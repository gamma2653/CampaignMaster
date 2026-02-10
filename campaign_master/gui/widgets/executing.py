"""
GUI widgets for campaign execution tracking.

Provides form-based editing for CampaignExecution objects,
including entity status tracking and AI-powered note refinement.
"""

from typing import Any, Optional, cast

from PySide6 import QtCore, QtWidgets

from ...ai import AICompletionService
from ...ai.refinement import build_entity_extraction_prompt, build_refinement_prompt
from ...content import api as content_api
from ...content import executing, planning
from ..themes import ThemedWidget
from .ai_widgets import AITextEdit
from .planning import CollapsibleSection, IDDisplay, IDSelect


class ExecutionEntryEdit(QtWidgets.QWidget):
    """Widget for editing a single ExecutionEntry."""

    def __init__(
        self,
        entry: Optional[executing.ExecutionEntry] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.entry = entry
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QFormLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        # Entity ID display (read-only)
        self.entity_id_label = QtWidgets.QLineEdit(str(self.entry.entity_id) if self.entry else "")
        self.entity_id_label.setReadOnly(True)
        layout.addRow("Entity ID:", self.entity_id_label)

        # Entity type label
        self.entity_type_label = QtWidgets.QLabel(self.entry.entity_type if self.entry else "")
        layout.addRow("Type:", self.entity_type_label)

        # Status combo box
        self.status_combo = QtWidgets.QComboBox()
        for status in executing.ExecutionStatus:
            self.status_combo.addItem(status.value.replace("_", " ").title(), status.value)
        if self.entry:
            index = self.status_combo.findData(self.entry.status.value)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        layout.addRow("Status:", self.status_combo)

        # Raw notes
        self.raw_notes = QtWidgets.QTextEdit()
        self.raw_notes.setPlainText(self.entry.raw_notes if self.entry else "")
        self.raw_notes.setMinimumHeight(60)
        self.raw_notes.setPlaceholderText("Session notes for this entity...")
        layout.addRow("Raw Notes:", self.raw_notes)

        # Refined notes (read-only display)
        self.refined_notes = QtWidgets.QTextEdit()
        self.refined_notes.setPlainText(self.entry.refined_notes if self.entry else "")
        self.refined_notes.setReadOnly(True)
        self.refined_notes.setMinimumHeight(60)
        self.refined_notes.setPlaceholderText("AI-refined notes will appear here...")
        layout.addRow("Refined Notes:", self.refined_notes)

        self.setLayout(layout)

    def export_entry(self) -> executing.ExecutionEntry:
        """Export the form data as an ExecutionEntry."""
        entity_id_str = self.entity_id_label.text()
        try:
            entity_id = planning.ID.from_str(entity_id_str)
        except ValueError:
            entity_id = planning.ID(prefix="MISC", numeric=0)

        return executing.ExecutionEntry(
            entity_id=entity_id,
            entity_type=self.entity_type_label.text(),
            status=executing.ExecutionStatus(self.status_combo.currentData()),
            raw_notes=self.raw_notes.toPlainText(),
            refined_notes=self.refined_notes.toPlainText(),
        )


class CampaignExecutionEdit(QtWidgets.QWidget, ThemedWidget):
    """
    Form widget for editing a CampaignExecution object.

    Includes session notes, refinement controls, and entity status tracking.
    """

    def __init__(
        self,
        execution: Optional[executing.CampaignExecution] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.execution = execution
        self.entry_widgets: list[ExecutionEntryEdit] = []
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Metadata section
        metadata_group = QtWidgets.QGroupBox("Execution Metadata")
        meta_layout = QtWidgets.QFormLayout()

        self.obj_id = IDDisplay(
            executing.CampaignExecution,
            self.execution.obj_id if self.execution else None,
        )
        meta_layout.addRow("ID:", self.obj_id)

        self.title_edit = QtWidgets.QLineEdit(self.execution.title if self.execution else "")
        meta_layout.addRow("Title:", self.title_edit)

        self.session_date = QtWidgets.QLineEdit(self.execution.session_date if self.execution else "")
        self.session_date.setPlaceholderText("YYYY-MM-DD")
        meta_layout.addRow("Session Date:", self.session_date)

        # Campaign plan selector
        self.plan_select = QtWidgets.QComboBox()
        self._populate_plans()
        if self.execution and self.execution.campaign_plan_id.numeric > 0:
            plan_str = str(self.execution.campaign_plan_id)
            index = self.plan_select.findData(plan_str)
            if index >= 0:
                self.plan_select.setCurrentIndex(index)
        meta_layout.addRow("Campaign Plan:", self.plan_select)

        metadata_group.setLayout(meta_layout)
        main_layout.addWidget(metadata_group)

        # Session Notes section
        notes_group = QtWidgets.QGroupBox("Session Notes")
        notes_layout = QtWidgets.QVBoxLayout()

        notes_layout.addWidget(QtWidgets.QLabel("Raw Session Notes:"))
        self.raw_session_notes = AITextEdit(
            self.execution.raw_session_notes if self.execution else "",
            field_name="raw_session_notes",
            entity_type="CampaignExecution",
            placeholder="Type your raw session notes here...",
        )
        self.raw_session_notes.setMinimumHeight(100)
        notes_layout.addWidget(self.raw_session_notes)

        # Refinement controls
        refine_layout = QtWidgets.QHBoxLayout()

        refine_layout.addWidget(QtWidgets.QLabel("Mode:"))
        self.refinement_mode = QtWidgets.QComboBox()
        self.refinement_mode.addItem("Narrative", "narrative")
        self.refinement_mode.addItem("Structured", "structured")
        if self.execution:
            index = self.refinement_mode.findData(self.execution.refinement_mode.value)
            if index >= 0:
                self.refinement_mode.setCurrentIndex(index)
        refine_layout.addWidget(self.refinement_mode)

        self.refine_button = QtWidgets.QPushButton("Refine Notes")
        self.refine_button.clicked.connect(self._refine_session_notes)
        refine_layout.addWidget(self.refine_button)

        refine_layout.addStretch()
        notes_layout.addLayout(refine_layout)

        notes_layout.addWidget(QtWidgets.QLabel("Refined Session Notes:"))
        self.refined_session_notes = QtWidgets.QTextEdit()
        self.refined_session_notes.setPlainText(self.execution.refined_session_notes if self.execution else "")
        self.refined_session_notes.setReadOnly(True)
        self.refined_session_notes.setMinimumHeight(80)
        notes_layout.addWidget(self.refined_session_notes)

        notes_group.setLayout(notes_layout)
        main_layout.addWidget(notes_group)

        # Entity entries section
        entries_group = QtWidgets.QGroupBox("Entity Tracking")
        entries_layout = QtWidgets.QVBoxLayout()

        # Buttons
        entry_button_layout = QtWidgets.QHBoxLayout()
        self.populate_button = QtWidgets.QPushButton("Populate Entries from Plan")
        self.populate_button.clicked.connect(self._populate_entries_from_plan)
        entry_button_layout.addWidget(self.populate_button)

        self.auto_extract_button = QtWidgets.QPushButton("Auto-populate Entity Notes")
        self.auto_extract_button.clicked.connect(self._auto_extract_entity_notes)
        entry_button_layout.addWidget(self.auto_extract_button)

        entry_button_layout.addStretch()
        entries_layout.addLayout(entry_button_layout)

        # Scroll area for entries
        self.entries_scroll = QtWidgets.QScrollArea()
        self.entries_scroll.setWidgetResizable(True)
        self.entries_scroll.setMinimumHeight(200)

        self.entries_container = QtWidgets.QWidget()
        self.entries_container_layout = QtWidgets.QVBoxLayout()
        self.entries_container_layout.setContentsMargins(0, 0, 0, 0)
        self.entries_container.setLayout(self.entries_container_layout)
        self.entries_scroll.setWidget(self.entries_container)

        # Load existing entries
        if self.execution:
            for entry in self.execution.entries:
                self._add_entry_widget(entry)

        self.entries_container_layout.addStretch()
        entries_layout.addWidget(self.entries_scroll)

        entries_group.setLayout(entries_layout)
        main_layout.addWidget(entries_group)

        # Save button
        button_layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save to Database")
        self.save_button.clicked.connect(self._save_to_database)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _populate_plans(self):
        """Populate the campaign plan selector."""
        self.plan_select.clear()
        self.plan_select.addItem("-- None --", "")
        try:
            plans = content_api.retrieve_objects(planning.CampaignPlan, proto_user_id=0)
            plans = cast(list[planning.CampaignPlan], plans)
            for plan in plans:
                label = f"{plan.title or 'Untitled'} ({plan.obj_id})"
                self.plan_select.addItem(label, str(plan.obj_id))
        except Exception:
            pass

    def _add_entry_widget(self, entry: executing.ExecutionEntry):
        """Add an entry editing widget."""
        widget = ExecutionEntryEdit(entry)
        # Insert before the stretch
        count = self.entries_container_layout.count()
        insert_pos = max(0, count - 1)  # Before the stretch
        self.entries_container_layout.insertWidget(insert_pos, widget)
        self.entry_widgets.append(widget)

    def _populate_entries_from_plan(self):
        """Load entities from the linked campaign plan and create entry stubs."""
        plan_id_str = self.plan_select.currentData()
        if not plan_id_str:
            QtWidgets.QMessageBox.warning(self, "No Plan", "Select a campaign plan first.")
            return

        try:
            plan_id = planning.ID.from_str(plan_id_str)
            plan = content_api.retrieve_object(plan_id, proto_user_id=0)
            plan = cast(planning.CampaignPlan | None, plan)
            if not plan:
                QtWidgets.QMessageBox.warning(self, "Not Found", "Campaign plan not found.")
                return

            # Collect existing entity IDs to avoid duplicates
            existing_ids = set()
            for w in self.entry_widgets:
                e = w.export_entry()
                existing_ids.add(str(e.entity_id))

            new_entries = []
            entity_lists: list[tuple[list, str]] = [
                (plan.characters, "Character"),
                (plan.locations, "Location"),
                (plan.items, "Item"),
                (plan.storypoints, "Point"),
                (plan.objectives, "Objective"),
                (plan.rules, "Rule"),
            ]

            for entities, type_name in entity_lists:
                for entity in entities:
                    if str(entity.obj_id) not in existing_ids:
                        new_entries.append(
                            executing.ExecutionEntry(
                                entity_id=entity.obj_id,
                                entity_type=type_name,
                            )
                        )

            for entry in new_entries:
                self._add_entry_widget(entry)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to populate entries: {e}")

    def _refine_session_notes(self):
        """Refine session notes using AI."""
        service = AICompletionService.instance()
        if not service.is_enabled() or not service.get_current_provider():
            QtWidgets.QMessageBox.warning(self, "AI Not Available", "Configure and enable an AI agent first.")
            return

        raw_notes = self.raw_session_notes.toPlainText()
        if not raw_notes.strip():
            return

        mode = executing.RefinementMode(self.refinement_mode.currentData())
        request = build_refinement_prompt(raw_notes, mode)

        try:
            response = service.complete(request)
            if response and response.text:
                self.refined_session_notes.setPlainText(response.text)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Refinement Error", f"AI refinement failed: {e}")

    def _auto_extract_entity_notes(self):
        """Use AI to extract entity-specific notes from session notes."""
        service = AICompletionService.instance()
        if not service.is_enabled() or not service.get_current_provider():
            QtWidgets.QMessageBox.warning(self, "AI Not Available", "Configure and enable an AI agent first.")
            return

        raw_notes = self.raw_session_notes.toPlainText()
        if not raw_notes.strip():
            return

        for widget in self.entry_widgets:
            entry = widget.export_entry()
            entity_name = str(entry.entity_id)
            request = build_entity_extraction_prompt(
                raw_session_notes=raw_notes,
                entity_name=entity_name,
                entity_type=entry.entity_type,
            )
            try:
                response = service.complete(request)
                if response and response.text:
                    widget.refined_notes.setPlainText(response.text)
            except Exception:
                pass  # Continue with other entries

    def export_content(self) -> executing.CampaignExecution:
        """Export the form data as a CampaignExecution object."""
        plan_id_str = self.plan_select.currentData()
        if plan_id_str:
            campaign_plan_id = planning.ID.from_str(plan_id_str)
        else:
            campaign_plan_id = planning.ID(prefix="CampPlan", numeric=0)

        return executing.CampaignExecution(
            obj_id=self.obj_id.get_id(),  # type: ignore[arg-type]
            campaign_plan_id=campaign_plan_id,
            title=self.title_edit.text(),
            session_date=self.session_date.text(),
            raw_session_notes=self.raw_session_notes.toPlainText(),
            refined_session_notes=self.refined_session_notes.toPlainText(),
            refinement_mode=executing.RefinementMode(self.refinement_mode.currentData()),
            entries=[w.export_entry() for w in self.entry_widgets],
        )

    def import_content(self, execution: executing.CampaignExecution):
        """Import a CampaignExecution object into the form."""
        self.execution = execution
        self.obj_id.setText(str(execution.obj_id))
        self.title_edit.setText(execution.title)
        self.session_date.setText(execution.session_date)
        self.raw_session_notes.setPlainText(execution.raw_session_notes)
        self.refined_session_notes.setPlainText(execution.refined_session_notes)

        mode_index = self.refinement_mode.findData(execution.refinement_mode.value)
        if mode_index >= 0:
            self.refinement_mode.setCurrentIndex(mode_index)

        plan_str = str(execution.campaign_plan_id)
        plan_index = self.plan_select.findData(plan_str)
        if plan_index >= 0:
            self.plan_select.setCurrentIndex(plan_index)

        # Clear existing entry widgets
        for w in self.entry_widgets:
            w.setParent(None)
        self.entry_widgets.clear()

        for entry in execution.entries:
            self._add_entry_widget(entry)

    def _save_to_database(self):
        """Save the execution to database."""
        main_window = self.window()
        if hasattr(main_window, "save_execution"):
            main_window.save_execution()  # type: ignore
