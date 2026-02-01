"""Tests for GUI execution widgets (ExecutionEntryEdit and CampaignExecutionEdit)."""

import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
from PySide6 import QtCore, QtWidgets

from campaign_master.content import executing, planning


@pytest.fixture(scope="module")
def qapp():
    """Module-scoped QApplication for all GUI tests."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    yield app


@pytest.fixture
def entry():
    """Create a sample ExecutionEntry."""
    return executing.ExecutionEntry(
        entity_id=planning.ID(prefix="C", numeric=1),
        entity_type="Character",
        status=executing.ExecutionStatus.IN_PROGRESS,
        raw_notes="Found the goblin",
        refined_notes="A goblin was encountered in the cave",
    )


@pytest.fixture
def execution():
    """Create a sample CampaignExecution."""
    return executing.CampaignExecution(
        obj_id=planning.ID(prefix="EX", numeric=1),
        campaign_plan_id=planning.ID(prefix="CampPlan", numeric=0),
        title="Session One",
        session_date="2025-01-15",
        raw_session_notes="The party entered the dungeon.",
        refined_session_notes="",
        refinement_mode=executing.RefinementMode.NARRATIVE,
        entries=[
            executing.ExecutionEntry(
                entity_id=planning.ID(prefix="C", numeric=1),
                entity_type="Character",
                status=executing.ExecutionStatus.NOT_ENCOUNTERED,
                raw_notes="",
                refined_notes="",
            ),
            executing.ExecutionEntry(
                entity_id=planning.ID(prefix="L", numeric=2),
                entity_type="Location",
                status=executing.ExecutionStatus.COMPLETED,
                raw_notes="Party visited",
                refined_notes="The party explored the area",
            ),
        ],
    )


class TestExecutionEntryEdit:
    """Tests for the ExecutionEntryEdit widget."""

    def test_create_with_no_entry(self, qapp):
        """Widget should be created with default empty state."""
        from campaign_master.gui.widgets.executing import ExecutionEntryEdit

        widget = ExecutionEntryEdit()
        assert widget.entity_id_label.text() == ""
        assert widget.entity_type_label.text() == ""
        assert widget.raw_notes.toPlainText() == ""
        assert widget.refined_notes.toPlainText() == ""

    def test_create_with_entry(self, qapp, entry):
        """Widget should display entry data when initialized with an entry."""
        from campaign_master.gui.widgets.executing import ExecutionEntryEdit

        widget = ExecutionEntryEdit(entry)
        assert widget.entity_id_label.text() == str(entry.entity_id)
        assert widget.entity_type_label.text() == "Character"
        assert widget.raw_notes.toPlainText() == "Found the goblin"
        assert widget.refined_notes.toPlainText() == "A goblin was encountered in the cave"

    def test_entity_id_is_readonly(self, qapp, entry):
        """Entity ID field should be read-only."""
        from campaign_master.gui.widgets.executing import ExecutionEntryEdit

        widget = ExecutionEntryEdit(entry)
        assert widget.entity_id_label.isReadOnly()

    def test_refined_notes_is_readonly(self, qapp, entry):
        """Refined notes field should be read-only."""
        from campaign_master.gui.widgets.executing import ExecutionEntryEdit

        widget = ExecutionEntryEdit(entry)
        assert widget.refined_notes.isReadOnly()

    def test_status_combo_values(self, qapp, entry):
        """Status combo should contain all ExecutionStatus values."""
        from campaign_master.gui.widgets.executing import ExecutionEntryEdit

        widget = ExecutionEntryEdit(entry)
        status_values = [widget.status_combo.itemData(i) for i in range(widget.status_combo.count())]
        for status in executing.ExecutionStatus:
            assert status.value in status_values

    def test_status_combo_reflects_entry(self, qapp, entry):
        """Status combo should show the entry's current status."""
        from campaign_master.gui.widgets.executing import ExecutionEntryEdit

        widget = ExecutionEntryEdit(entry)
        assert widget.status_combo.currentData() == executing.ExecutionStatus.IN_PROGRESS.value

    def test_export_entry(self, qapp, entry):
        """export_entry should return an ExecutionEntry matching the widget state."""
        from campaign_master.gui.widgets.executing import ExecutionEntryEdit

        widget = ExecutionEntryEdit(entry)
        exported = widget.export_entry()

        assert exported.entity_id == entry.entity_id
        assert exported.entity_type == "Character"
        assert exported.status == executing.ExecutionStatus.IN_PROGRESS
        assert exported.raw_notes == "Found the goblin"
        assert exported.refined_notes == "A goblin was encountered in the cave"

    def test_export_after_edit(self, qapp, entry):
        """export_entry should reflect changes made by the user."""
        from campaign_master.gui.widgets.executing import ExecutionEntryEdit

        widget = ExecutionEntryEdit(entry)

        # Simulate user edits
        widget.raw_notes.setPlainText("Updated notes")
        widget.status_combo.setCurrentIndex(widget.status_combo.findData(executing.ExecutionStatus.COMPLETED.value))

        exported = widget.export_entry()
        assert exported.raw_notes == "Updated notes"
        assert exported.status == executing.ExecutionStatus.COMPLETED

    def test_export_with_invalid_id(self, qapp):
        """export_entry should handle invalid entity ID gracefully."""
        from campaign_master.gui.widgets.executing import ExecutionEntryEdit

        widget = ExecutionEntryEdit()
        widget.entity_id_label.setText("invalid-id-format")
        exported = widget.export_entry()
        assert exported.entity_id.prefix == "MISC"
        assert exported.entity_id.numeric == 0


class TestCampaignExecutionEdit:
    """Tests for the CampaignExecutionEdit widget."""

    @patch("campaign_master.gui.widgets.planning.content_api")
    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_create_with_no_execution(self, mock_exec_api, mock_plan_api, qapp):
        """Widget should create without errors when no execution is provided."""
        mock_exec_api.retrieve_objects.return_value = []
        mock_plan_api.generate_id.return_value = planning.ID(prefix="EX", numeric=0)
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit()
        assert widget.title_edit.text() == ""
        assert widget.session_date.text() == ""

    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_create_with_execution(self, mock_api, qapp, execution):
        """Widget should populate fields from execution data."""
        mock_api.retrieve_objects.return_value = []
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit(execution)
        assert widget.title_edit.text() == "Session One"
        assert widget.session_date.text() == "2025-01-15"
        assert widget.raw_session_notes.toPlainText() == "The party entered the dungeon."
        assert widget.refined_session_notes.toPlainText() == ""

    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_loads_existing_entries(self, mock_api, qapp, execution):
        """Widget should create entry widgets for each entry in the execution."""
        mock_api.retrieve_objects.return_value = []
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit(execution)
        assert len(widget.entry_widgets) == 2

    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_refinement_mode_combo(self, mock_api, qapp, execution):
        """Refinement mode combo should reflect execution data."""
        mock_api.retrieve_objects.return_value = []
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit(execution)
        assert widget.refinement_mode.currentData() == "narrative"

    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_export_content(self, mock_api, qapp, execution):
        """export_content should return a CampaignExecution with all form data."""
        mock_api.retrieve_objects.return_value = []
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit(execution)
        exported = widget.export_content()

        assert exported.title == "Session One"
        assert exported.session_date == "2025-01-15"
        assert exported.raw_session_notes == "The party entered the dungeon."
        assert exported.refinement_mode == executing.RefinementMode.NARRATIVE
        assert len(exported.entries) == 2

    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_export_after_title_edit(self, mock_api, qapp, execution):
        """export_content should reflect user edits to the title."""
        mock_api.retrieve_objects.return_value = []
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit(execution)
        widget.title_edit.setText("Edited Title")
        exported = widget.export_content()
        assert exported.title == "Edited Title"

    @patch("campaign_master.gui.widgets.planning.content_api")
    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_import_content(self, mock_exec_api, mock_plan_api, qapp):
        """import_content should update all form fields from a CampaignExecution."""
        mock_exec_api.retrieve_objects.return_value = []
        mock_plan_api.generate_id.return_value = planning.ID(prefix="EX", numeric=0)
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit()
        assert widget.title_edit.text() == ""

        new_execution = executing.CampaignExecution(
            obj_id=planning.ID(prefix="EX", numeric=5),
            campaign_plan_id=planning.ID(prefix="CampPlan", numeric=0),
            title="Imported Session",
            session_date="2025-12-25",
            raw_session_notes="Imported notes",
            refined_session_notes="Refined imported",
            refinement_mode=executing.RefinementMode.STRUCTURED,
            entries=[
                executing.ExecutionEntry(
                    entity_id=planning.ID(prefix="I", numeric=3),
                    entity_type="Item",
                    status=executing.ExecutionStatus.SKIPPED,
                ),
            ],
        )

        widget.import_content(new_execution)
        assert widget.title_edit.text() == "Imported Session"
        assert widget.session_date.text() == "2025-12-25"
        assert widget.raw_session_notes.toPlainText() == "Imported notes"
        assert widget.refined_session_notes.toPlainText() == "Refined imported"
        assert widget.refinement_mode.currentData() == "structured"
        assert len(widget.entry_widgets) == 1

    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_import_clears_previous_entries(self, mock_api, qapp, execution):
        """import_content should remove old entries before adding new ones."""
        mock_api.retrieve_objects.return_value = []
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit(execution)
        assert len(widget.entry_widgets) == 2

        empty_execution = executing.CampaignExecution(
            obj_id=planning.ID(prefix="EX", numeric=2),
            entries=[],
        )
        widget.import_content(empty_execution)
        assert len(widget.entry_widgets) == 0

    @patch("campaign_master.gui.widgets.planning.content_api")
    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_populate_without_plan_shows_warning(self, mock_exec_api, mock_plan_api, qapp):
        """Populate entries should show warning when no plan is selected."""
        mock_exec_api.retrieve_objects.return_value = []
        mock_plan_api.generate_id.return_value = planning.ID(prefix="EX", numeric=0)
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit()

        with patch.object(QtWidgets.QMessageBox, "warning") as mock_warn:
            widget._populate_entries_from_plan()
            mock_warn.assert_called_once()

    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_refine_without_ai_shows_warning(self, mock_api, qapp, execution):
        """Refine notes should show warning when AI is not configured."""
        mock_api.retrieve_objects.return_value = []
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit(execution)

        mock_service = MagicMock()
        mock_service.is_enabled.return_value = False
        mock_service.get_current_provider.return_value = None

        with patch(
            "campaign_master.gui.widgets.executing.AICompletionService.instance",
            return_value=mock_service,
        ):
            with patch.object(QtWidgets.QMessageBox, "warning") as mock_warn:
                widget._refine_session_notes()
                mock_warn.assert_called_once()

    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_refine_with_ai_updates_notes(self, mock_api, qapp, execution):
        """Successful AI refinement should update the refined notes field."""
        mock_api.retrieve_objects.return_value = []
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit(execution)

        mock_response = MagicMock()
        mock_response.text = "Refined by AI"

        mock_service = MagicMock()
        mock_service.is_enabled.return_value = True
        mock_service.get_current_provider.return_value = MagicMock()
        mock_service.complete.return_value = mock_response

        with patch(
            "campaign_master.gui.widgets.executing.AICompletionService.instance",
            return_value=mock_service,
        ):
            widget._refine_session_notes()

        assert widget.refined_session_notes.toPlainText() == "Refined by AI"

    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_ui_elements_exist(self, mock_api, qapp, execution):
        """Widget should have all expected UI elements."""
        mock_api.retrieve_objects.return_value = []
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit(execution)

        assert widget.title_edit is not None
        assert widget.session_date is not None
        assert widget.plan_select is not None
        assert widget.raw_session_notes is not None
        assert widget.refined_session_notes is not None
        assert widget.refinement_mode is not None
        assert widget.refine_button is not None
        assert widget.populate_button is not None
        assert widget.auto_extract_button is not None
        assert widget.save_button is not None

    @patch("campaign_master.gui.widgets.planning.content_api")
    @patch("campaign_master.gui.widgets.executing.content_api")
    def test_session_date_placeholder(self, mock_exec_api, mock_plan_api, qapp):
        """Session date field should have YYYY-MM-DD placeholder."""
        mock_exec_api.retrieve_objects.return_value = []
        mock_plan_api.generate_id.return_value = planning.ID(prefix="EX", numeric=0)
        from campaign_master.gui.widgets.executing import CampaignExecutionEdit

        widget = CampaignExecutionEdit()
        assert widget.session_date.placeholderText() == "YYYY-MM-DD"
