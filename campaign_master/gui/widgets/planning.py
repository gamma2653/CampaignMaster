from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar, cast

from PySide6 import QtCore, QtGui, QtWidgets

from ...content import api as content_api
from ...content import planning
from ..themes import ThemedWidget
from .ai_widgets import AILineEdit, AITextEdit


def _find_campaign_context(widget: QtWidgets.QWidget) -> dict[str, Any]:
    """Walk up the widget tree to find CampaignPlanEdit and extract context."""
    parent = widget.parent()
    while parent is not None:
        # Check if this is CampaignPlanEdit by looking for its attributes
        if hasattr(parent, "title") and hasattr(parent, "setting") and hasattr(parent, "summary"):
            parent = cast(CampaignPlanEdit, parent)
            try:
                return {
                    "campaign_title": parent.title.text(),
                    "campaign_version": parent.version.text(),
                    "campaign_setting": parent.setting.toPlainText(),
                    "campaign_summary": parent.summary.toPlainText(),
                    "campaign_storypoints": [obj.model_dump() for obj in parent.storypoints.get_objects()],
                    "campaign_storyline": [obj.model_dump() for obj in parent.storyline.get_objects()],
                    "campaign_characters": [obj.model_dump() for obj in parent.characters.get_objects()],
                    "campaign_locations": [obj.model_dump() for obj in parent.locations.get_objects()],
                    "campaign_items": [obj.model_dump() for obj in parent.items.get_objects()],
                    "campaign_rules": [obj.model_dump() for obj in parent.rules.get_objects()],
                    "campaign_objectives": [obj.model_dump() for obj in parent.objectives.get_objects()],
                }
            except Exception:
                pass
        parent = parent.parent()
    return {}


class CollapsibleSection(QtWidgets.QWidget):
    """A collapsible section widget with a header and expandable content."""

    def __init__(
        self,
        title: str = "",
        border_color: str = "#555555",
        bg_color: str = "#1a341a",
        parent=None,
        start_collapsed: bool = True,
    ):
        super().__init__(parent)
        self.border_color = border_color
        self.bg_color = bg_color
        self.is_collapsed = start_collapsed
        self.init_ui(title)

    def init_ui(self, title: str):
        """Initialize the UI components."""
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Set size policy to allow the section to expand/contract in splitters
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        # Create header button
        self.header_button = QtWidgets.QPushButton(title)
        self.header_button.setCheckable(True)
        self.header_button.setChecked(not self.is_collapsed)  # Checked = expanded
        self.header_button.clicked.connect(self.toggle_collapse)

        # Style the header button
        self.header_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.bg_color};
                border: 2px solid {self.border_color};
                border-radius: 8px;
                color: #ffffff;
                font-size: 16px;
                font-weight: 600;
                text-align: left;
                padding: 12px 16px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.05);
            }}
            QPushButton:checked {{
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
            }}
        """
        )

        # Create content widget
        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName("collapsibleContent")
        self.content_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_widget.setLayout(self.content_layout)

        # Style the content widget (use #id selector to avoid affecting children)
        self.content_widget.setStyleSheet(
            f"""
            QWidget#collapsibleContent {{
                background-color: {self.bg_color};
                border: 2px solid {self.border_color};
                border-top: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
        """
        )

        main_layout.addWidget(self.header_button)
        main_layout.addWidget(self.content_widget, 1)  # stretch factor 1

        self.setLayout(main_layout)

        # Set initial visibility based on collapsed state
        self.content_widget.setVisible(not self.is_collapsed)

        # Update arrow indicator
        self.update_arrow()

    def set_content(self, widget: QtWidgets.QWidget):
        """Set the content widget for this section."""
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Ensure the widget can expand
        widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        # Add new content with stretch
        self.content_layout.addWidget(widget, 1)

    def toggle_collapse(self):
        """Toggle the collapsed state."""
        self.is_collapsed = not self.header_button.isChecked()
        self.content_widget.setVisible(not self.is_collapsed)
        self.update_arrow()

    def update_arrow(self):
        """Update the arrow indicator based on collapsed state."""
        arrow = "▼" if not self.is_collapsed else "▶"
        current_text = self.header_button.text()

        # Remove existing arrow if present
        if current_text.startswith("▼ ") or current_text.startswith("▶ "):
            current_text = current_text[2:]

        self.header_button.setText(f"{arrow} {current_text}")


class IDDisplay(QtWidgets.QLineEdit):
    """
    A QLineEdit specialized for editing ID fields.
    """

    def __init__(
        self,
        model_type: type[planning.Object],
        id_value: Optional[planning.ID] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.model_type = model_type
        self.setText(
            str(id_value) if id_value else str(content_api.generate_id(prefix=self.model_type._default_prefix))
        )
        self.setToolTip("Will be auto-generated.")
        self.setReadOnly(True)

    def get_id(self) -> planning.ID:
        """Get the ID from the display field."""
        return planning.ID.from_str(self.text())


class IDSelect(QtWidgets.QComboBox):
    """
    A QComboBox specialized for selecting ID types.
    """

    def __init__(self, model_type: type[planning.Object], parent=None):
        super().__init__(parent)
        self.model_type = model_type
        self.populate()

    def populate(self):
        self.clear()
        all_ids = content_api.retrieve_ids(prefix=self.model_type._default_prefix)
        self.addItems([str(obj_id) for obj_id in all_ids])

    def get_selected_object(self) -> planning.ID:
        return planning.ID.from_str(self.currentText())

    def set_selected_id(self, obj_id: planning.ID):
        """Set the selected ID in the combo box."""
        id_str = str(obj_id)
        index = self.findText(id_str)
        if index >= 0:
            self.setCurrentIndex(index)


class IDSelectWithCreate(QtWidgets.QWidget):
    """
    A widget combining IDSelect dropdown with a 'Create New' button.
    Allows selecting an existing object or creating a new one.
    """

    def __init__(
        self,
        model_type: type[planning.Object],
        selected_id: Optional[planning.ID] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.model_type = model_type
        self.selected_id = selected_id
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Dropdown for selecting existing IDs
        self.id_select = IDSelect(self.model_type)
        if self.selected_id:
            self.id_select.set_selected_id(self.selected_id)

        # Create New button
        self.create_button = QtWidgets.QPushButton("Create New")
        self.create_button.clicked.connect(self.create_new_object)
        self.create_button.setMaximumWidth(100)

        layout.addWidget(self.id_select, stretch=1)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

    def create_new_object(self):
        """Open a dialog to create a new object of the model type."""
        # Map model types to their edit widget class names
        edit_widget_map = {
            planning.Point: "PointEdit",
            planning.Rule: "RuleEdit",
            planning.Objective: "ObjectiveEdit",
            planning.Segment: "SegmentEdit",
            planning.Arc: "ArcEdit",
            planning.Item: "ItemEdit",
            planning.Character: "CharacterEdit",
            planning.Location: "LocationEdit",
        }

        edit_widget_class_name = edit_widget_map.get(self.model_type)
        if not edit_widget_class_name:
            QtWidgets.QMessageBox.warning(
                self,
                "Not Supported",
                f"Creating {self.model_type.__name__} objects is not supported.",
            )
            return

        # Open an edit dialog to create a new object
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"Create New {self.model_type.__name__}")
        dialog.setMinimumWidth(400)
        dialog_layout = QtWidgets.QVBoxLayout()

        # Get the edit widget class from globals
        edit_widget_class = globals()[edit_widget_class_name]
        edit_widget = edit_widget_class(parent=dialog)
        dialog_layout.addWidget(edit_widget)

        # Add OK/Cancel buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)

        dialog.setLayout(dialog_layout)

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # Export the form data and create in database
            form_data = edit_widget.export_content()
            content_api._create_object(form_data, proto_user_id=0)

            # Refresh the dropdown and select the new ID
            self.id_select.populate()
            self.id_select.set_selected_id(form_data.obj_id)
        else:
            # Dialog was cancelled - release the unused ID
            content_api.release_id(edit_widget.obj_id.get_id(), proto_user_id=0)

    def get_selected_id(self) -> Optional[planning.ID]:
        """Get the currently selected ID."""
        if self.id_select.currentText():
            return self.id_select.get_selected_object()
        return None

    def set_selected_id(self, obj_id: planning.ID):
        """Set the selected ID."""
        self.id_select.set_selected_id(obj_id)


class StrListEdit(QtWidgets.QWidget):
    """
    A widget to edit a list of strings with splitter-based resizing.
    """

    def __init__(self, items: Optional[list[str]] = None, parent=None):
        super().__init__(parent)
        self.items = items if items else []
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create vertical splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)

        # List widget (resizable)
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.addItems(self.items)
        splitter.addWidget(self.list_widget)

        # Buttons in container (fixed max height)
        button_container = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)

        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        self.add_button.clicked.connect(self.add_item)
        self.remove_button.clicked.connect(self.remove_item)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        button_container.setLayout(button_layout)
        button_container.setFixedHeight(50)
        splitter.addWidget(button_container)

        # Configure splitter
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(5)
        splitter.setStretchFactor(0, 1)  # List widget gets all extra space
        splitter.setStretchFactor(1, 0)  # Button container stays fixed
        splitter.setSizes([150, 50])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def add_item(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Add Item", "Item:")
        if ok and text:
            self.list_widget.addItem(text)

    def remove_item(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.list_widget.takeItem(self.list_widget.row(item))

    def get_items(self) -> list[str]:
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]


class IDListEdit(QtWidgets.QWidget):
    """
    A widget to edit a list of IDs with splitter-based resizing.
    """

    def __init__(
        self,
        model_type: type[planning.Object],
        ids: Optional[list[planning.ID]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.model_type = model_type
        self.ids = ids if ids else []
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create vertical splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)

        # List widget (resizable)
        self.list_widget = QtWidgets.QListWidget()
        for id_value in self.ids:
            self.list_widget.addItem(str(id_value))
        splitter.addWidget(self.list_widget)

        # Buttons in container (fixed max height)
        button_container = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)

        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        self.add_button.clicked.connect(self.add_id)
        self.remove_button.clicked.connect(self.remove_id)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        button_container.setLayout(button_layout)
        button_container.setFixedHeight(50)
        splitter.addWidget(button_container)

        # Configure splitter
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(5)
        splitter.setStretchFactor(0, 1)  # List widget gets all extra space
        splitter.setStretchFactor(1, 0)  # Button container stays fixed
        splitter.setSizes([150, 50])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def add_id(self):
        id_select_dialog = QtWidgets.QDialog(self)
        id_select_dialog.setWindowTitle("Select ID")
        dialog_layout = QtWidgets.QVBoxLayout()

        id_select = IDSelect(self.model_type)
        dialog_layout.addWidget(id_select)

        # button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.ButtonRole. | QtWidgets.QDialogButtonBox.Cancel)
        # button_box.accepted.connect(id_select_dialog.accept)
        # button_box.rejected.connect(id_select_dialog.reject)
        # dialog_layout.addWidget(button_box)

        id_select_dialog.setLayout(dialog_layout)

        if id_select_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            selected_id = id_select.get_selected_object()
            self.list_widget.addItem(str(selected_id))

    def remove_id(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.list_widget.takeItem(self.list_widget.row(item))

    def get_ids(self) -> list[planning.ID]:
        return [planning.ID.from_str(self.list_widget.item(i).text()) for i in range(self.list_widget.count())]


T = TypeVar("T", bound=planning.Object)


class ListEdit(QtWidgets.QWidget, Generic[T]):
    """
    A widget to edit a list of objects with splitter-based resizing.
    """

    def __init__(
        self,
        model_type: type[T],
        objects: Optional[list[T]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.model_type = model_type
        self.objects: list[T] = objects if objects else []
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Set size policy to allow expanding within parent splitters
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        # List widget (resizable) - no internal splitter needed, just the list and buttons
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        for object_ in self.objects:
            self.list_widget.addItem(str(object_.obj_id))
        self.list_widget.setMinimumHeight(50)
        self.list_widget.itemDoubleClicked.connect(self.edit_object)

        # Buttons in container
        button_container = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)

        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        self.add_button.clicked.connect(self.add_object)
        self.remove_button.clicked.connect(self.remove_object)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        button_container.setLayout(button_layout)
        button_container.setFixedHeight(50)

        main_layout.addWidget(self.list_widget, 1)  # stretch factor 1
        main_layout.addWidget(button_container)
        self.setLayout(main_layout)
        self.setMinimumHeight(100)

    def add_object(self):
        # Create a mapping from model types to their edit widgets
        edit_widget_map = {
            planning.Point: "PointEdit",
            planning.Rule: "RuleEdit",
            planning.Objective: "ObjectiveEdit",
            planning.Segment: "SegmentEdit",
            planning.Arc: "ArcEdit",
            planning.Item: "ItemEdit",
            planning.Character: "CharacterEdit",
            planning.Location: "LocationEdit",
        }

        # Check if this model type has a dedicated edit widget
        edit_widget_class_name = edit_widget_map.get(self.model_type)

        if edit_widget_class_name:
            # Open an edit dialog to create a new object
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(f"Add {self.model_type.__name__}")
            dialog_layout = QtWidgets.QVBoxLayout()

            # Get the edit widget class from globals (all edit widgets are in this module)
            edit_widget_class = globals()[edit_widget_class_name]
            edit_widget = edit_widget_class(parent=dialog)
            dialog_layout.addWidget(edit_widget)

            # Add OK/Cancel buttons
            button_box = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            dialog_layout.addWidget(button_box)

            dialog.setLayout(dialog_layout)

            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                # Export the form data (which includes the ID generated by IDDisplay)
                form_data = edit_widget.export_content()
                # Create the object in the database using the form data
                # Note: _create_object uses the ID from form_data instead of generating a new one
                content_api._create_object(form_data, proto_user_id=0)
                # Add to the list (use form_data directly since it's already a Pydantic object)
                self.list_widget.addItem(str(form_data.obj_id))
                self.objects.append(cast(T, form_data))
            else:
                # Dialog was cancelled - release the unused ID
                content_api.release_id(edit_widget.obj_id.get_id(), proto_user_id=0)
        else:
            # Fallback to the old selection dialog for types without edit widgets
            object_select_dialog = QtWidgets.QDialog(self)
            object_select_dialog.setWindowTitle("Select Item")
            dialog_layout = QtWidgets.QVBoxLayout()

            object_select = IDSelect(self.model_type)
            dialog_layout.addWidget(object_select)

            object_select_dialog.setLayout(dialog_layout)

            if object_select_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                selected_id = object_select.get_selected_object()
                # Retrieve the full object from the database using the ID
                obj = content_api.retrieve_object(selected_id)
                if obj:
                    self.list_widget.addItem(str(selected_id))
                    self.objects.append(cast(T, obj))

    def remove_object(self):
        selected_items_widgets = self.list_widget.selectedItems()
        if not selected_items_widgets:
            return
        for item_widget in selected_items_widgets:
            item = self.objects[self.list_widget.row(item_widget)]
            self.objects.remove(item)
            self.list_widget.takeItem(self.list_widget.row(item_widget))

    def edit_object(self, item: QtWidgets.QListWidgetItem):
        """Open the edit dialog for the double-clicked item."""
        row = self.list_widget.row(item)
        obj = self.objects[row]

        edit_widget_map = {
            planning.Point: "PointEdit",
            planning.Rule: "RuleEdit",
            planning.Objective: "ObjectiveEdit",
            planning.Segment: "SegmentEdit",
            planning.Arc: "ArcEdit",
            planning.Item: "ItemEdit",
            planning.Character: "CharacterEdit",
            planning.Location: "LocationEdit",
        }

        edit_widget_class_name = edit_widget_map.get(self.model_type)
        if not edit_widget_class_name:
            return

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"Edit {self.model_type.__name__}")
        dialog_layout = QtWidgets.QVBoxLayout()

        # Pass the existing object to the edit widget to pre-populate the form
        edit_widget_class = globals()[edit_widget_class_name]
        edit_widget = edit_widget_class(obj, parent=dialog)
        dialog_layout.addWidget(edit_widget)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)

        dialog.setLayout(dialog_layout)

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # Export the updated form data
            form_data = edit_widget.export_content()
            # Update the object in the database
            content_api.update_object(form_data, proto_user_id=0)
            # Update in our local list
            self.objects[row] = cast(T, form_data)
            # Update the list item display
            item.setText(str(form_data.obj_id))

    def get_objects(self) -> list[T]:
        """Return the list of objects."""
        return self.objects


class RuleEdit(QtWidgets.QWidget, ThemedWidget):
    """
    Contains a form to populate/edit a Rule object.

    Fields:
    name: str
    description: str
    """

    def __init__(self, rule: Optional[planning.Rule] = None, parent=None):
        super().__init__(parent)
        self.rule = rule
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        container = self.create_themed_container(planning.Rule, "Rule")
        self.form_layout = QtWidgets.QFormLayout()

        self.obj_id = IDDisplay(planning.Rule, self.rule.obj_id if self.rule else None)
        self.description = AITextEdit(
            self.rule.description if self.rule else "",
            field_name="description",
            entity_type="Rule",
            entity_context_func=self._get_entity_context,
        )
        self.effect = AITextEdit(
            self.rule.effect if self.rule else "",
            field_name="effect",
            entity_type="Rule",
            entity_context_func=self._get_entity_context,
        )
        self.components = StrListEdit(self.rule.components if self.rule else [])

        container.setLayout(self.form_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        self.update_layout()

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "description": self.description.toPlainText(),
            "effect": self.effect.toPlainText(),
            "components": self.components.get_items(),
        }
        context.update(_find_campaign_context(self))
        return context

    def update_layout(self):
        self.form_layout.addRow("ID:", self.obj_id)
        self.form_layout.addRow("Description:", self.description)
        self.form_layout.addRow("Effect:", self.effect)
        self.form_layout.addRow("Components:", self.components)

    def export_content(self) -> planning.Rule:
        """Export the form data as a Rule object."""
        return planning.Rule(
            obj_id=self.obj_id.get_id(),  # type: ignore[arg-type]
            description=self.description.toPlainText(),
            effect=self.effect.toPlainText(),
            components=self.components.get_items(),
        )


class ObjectiveEdit(QtWidgets.QWidget, ThemedWidget):
    """
    Contains a form to populate/edit an Objective object.

    Fields:
    description: str
    components: list[str]
    prerequisites: list[ID]
    """

    def __init__(self, objective: Optional[planning.Objective] = None, parent=None):
        super().__init__(parent)
        self.objective = objective
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        container = self.create_themed_container(planning.Objective, "Objective")
        self.form_layout = QtWidgets.QFormLayout()

        self.obj_id = IDDisplay(planning.Objective, self.objective.obj_id if self.objective else None)
        self.description = AITextEdit(
            self.objective.description if self.objective else "",
            field_name="description",
            entity_type="Objective",
            entity_context_func=self._get_entity_context,
        )
        self.components = StrListEdit(self.objective.components if self.objective else [])
        self.prerequisites = IDListEdit(planning.Objective, self.objective.prerequisites if self.objective else [])

        container.setLayout(self.form_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        self.update_layout()

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "description": self.description.toPlainText(),
            "components": self.components.get_items(),
        }
        context.update(_find_campaign_context(self))
        return context

    def update_layout(self):
        self.form_layout.addRow("ID:", self.obj_id)
        self.form_layout.addRow("Description:", self.description)
        self.form_layout.addRow("Components:", self.components)
        self.form_layout.addRow("Prerequisites:", self.prerequisites)

    def export_content(self) -> planning.Objective:
        """Export the form data as an Objective object."""
        return planning.Objective(
            obj_id=self.obj_id.get_id(),  # type: ignore[arg-type]
            description=self.description.toPlainText(),
            components=self.components.get_items(),
            prerequisites=self.prerequisites.get_ids(),
        )


class PointEdit(QtWidgets.QWidget, ThemedWidget):
    """
    Contains a form to populate/edit a Point object.

    Fields:
    name: str
    description: str
    objective: Optional[ID]
    """

    def __init__(self, point: Optional[planning.Point] = None, parent=None):
        super().__init__(parent)
        self.point = point
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        container = self.create_themed_container(planning.Point, "Story Point")
        self.form_layout = QtWidgets.QFormLayout()

        self.obj_id = IDDisplay(planning.Point, self.point.obj_id if self.point else None)
        self.name = AILineEdit(
            self.point.name if self.point else "",
            field_name="name",
            entity_type="Point",
            entity_context_func=self._get_entity_context,
        )
        self.description = AITextEdit(
            self.point.description if self.point else "",
            field_name="description",
            entity_type="Point",
            entity_context_func=self._get_entity_context,
        )
        self.objective = IDSelect(planning.Objective)

        container.setLayout(self.form_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        self.update_layout()

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "name": self.name.text(),
            "description": self.description.toPlainText(),
        }
        context.update(_find_campaign_context(self))
        return context

    def update_layout(self):
        self.form_layout.addRow("ID:", self.obj_id)
        self.form_layout.addRow("Name:", self.name)
        self.form_layout.addRow("Description:", self.description)
        self.form_layout.addRow("Objective ID:", self.objective)

    def export_content(self) -> planning.Point:
        """Export the form data as a Point object."""
        # Get objective ID, handling empty selection
        objective_id = None
        if self.objective.currentText():
            objective_id = self.objective.get_selected_object()

        return planning.Point(
            obj_id=self.obj_id.get_id(),  # type: ignore[arg-type]
            name=self.name.text(),
            description=self.description.toPlainText(),
            objective=objective_id,
        )


class SegmentEdit(QtWidgets.QWidget, ThemedWidget):
    """
    Contains a form to populate/edit a Segment object.

    Fields:
    name: str
    description: str
    start: ID (reference to Point)
    end: ID (reference to Point)
    """

    def __init__(self, segment: Optional[planning.Segment] = None, parent=None):
        super().__init__(parent)
        self.segment = segment
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        container = self.create_themed_container(planning.Segment, "Segment")
        self.form_layout = QtWidgets.QFormLayout()

        self.obj_id = IDDisplay(planning.Segment, self.segment.obj_id if self.segment else None)
        self.name = AILineEdit(
            self.segment.name if self.segment else "",
            field_name="name",
            entity_type="Segment",
            entity_context_func=self._get_entity_context,
        )
        self.description = AITextEdit(
            self.segment.description if self.segment else "",
            field_name="description",
            entity_type="Segment",
            entity_context_func=self._get_entity_context,
        )
        # Use IDSelectWithCreate to allow selecting existing Points or creating new ones
        self.start = IDSelectWithCreate(
            planning.Point,
            selected_id=self.segment.start if self.segment else None,
        )
        self.end = IDSelectWithCreate(
            planning.Point,
            selected_id=self.segment.end if self.segment else None,
        )

        container.setLayout(self.form_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        self.update_layout()

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "name": self.name.text(),
            "description": self.description.toPlainText(),
        }
        context.update(_find_campaign_context(self))
        return context

    def update_layout(self):
        self.form_layout.addRow("ID:", self.obj_id)
        self.form_layout.addRow("Name:", self.name)
        self.form_layout.addRow("Description:", self.description)
        self.form_layout.addRow("Start Point:", self.start)
        self.form_layout.addRow("End Point:", self.end)

    def export_content(self) -> planning.Segment:
        """Export the form data as a Segment object."""
        # Get the selected Point IDs from the IDSelectWithCreate widgets
        start_id = self.start.get_selected_id()
        end_id = self.end.get_selected_id()

        # Use default ID if none selected
        default_id = planning.ID(prefix="P", numeric=0)

        return planning.Segment(
            obj_id=self.obj_id.get_id(),  # type: ignore[arg-type]
            name=self.name.text(),
            description=self.description.toPlainText(),
            start=start_id if start_id else default_id,
            end=end_id if end_id else default_id,
        )


class ArcEdit(QtWidgets.QWidget, ThemedWidget):
    """
    Contains a form to populate/edit an Arc object.

    Fields:
    name: str
    description: str
    segments: list[Segment]
    """

    def __init__(self, arc: Optional[planning.Arc] = None, parent=None):
        super().__init__(parent)
        self.arc = arc
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        container = self.create_themed_container(planning.Arc, "Story Arc")
        self.form_layout = QtWidgets.QFormLayout()

        self.obj_id = IDDisplay(planning.Arc, self.arc.obj_id if self.arc else None)
        self.name = AILineEdit(
            self.arc.name if self.arc else "",
            field_name="name",
            entity_type="Arc",
            entity_context_func=self._get_entity_context,
        )
        self.description = AITextEdit(
            self.arc.description if self.arc else "",
            field_name="description",
            entity_type="Arc",
            entity_context_func=self._get_entity_context,
        )
        # Use ListEdit to properly manage segments with add/remove functionality
        self.segments = ListEdit[planning.Segment](
            planning.Segment,
            objects=self.arc.segments if self.arc else [],
        )

        container.setLayout(self.form_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        self.update_layout()

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "name": self.name.text(),
            "description": self.description.toPlainText(),
        }
        context.update(_find_campaign_context(self))
        return context

    def update_layout(self):
        self.form_layout.addRow("ID:", self.obj_id)
        self.form_layout.addRow("Name:", self.name)
        self.form_layout.addRow("Description:", self.description)
        self.form_layout.addRow("Segments:", self.segments)

    def export_content(self) -> planning.Arc:
        """Export the form data as an Arc object."""
        return planning.Arc(
            obj_id=self.obj_id.get_id(),  # type: ignore[arg-type]
            name=self.name.text(),
            description=self.description.toPlainText(),
            segments=self.segments.get_objects(),
        )


class MapEdit[K, V](QtWidgets.QWidget):
    """
    A widget to edit a mapping of strings to strings with splitter-based resizing.
    """

    def __init__(
        self,
        map_: Optional[dict[K, V]] = None,
        k_v_labels: tuple[str, str] = ("Key", "Value"),
        parent=None,
    ):
        super().__init__(parent)
        self.map_ = map_ if map_ else {}
        self.k_v_labels = k_v_labels
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create vertical splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)

        # Table widget (resizable)
        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(self.k_v_labels)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.populate_table()
        splitter.addWidget(self.table_widget)

        # Buttons in container (fixed max height)
        button_container = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 4, 0, 0)

        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        self.add_button.clicked.connect(self.add_entry)
        self.remove_button.clicked.connect(self.remove_entry)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        button_container.setLayout(button_layout)
        button_container.setFixedHeight(50)
        splitter.addWidget(button_container)

        # Configure splitter
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(5)
        splitter.setStretchFactor(0, 1)  # Table widget gets all extra space
        splitter.setStretchFactor(1, 0)  # Button container stays fixed
        splitter.setSizes([150, 50])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def populate_table(self):
        self.table_widget.setRowCount(0)
        for key, value in self.map_.items():
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            self.table_widget.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(key)))
            self.table_widget.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(value)))

    def add_entry(self):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

    def remove_entry(self):
        selected_rows = set()
        for item in self.table_widget.selectedItems():
            selected_rows.add(item.row())
        for row in sorted(selected_rows, reverse=True):
            self.table_widget.removeRow(row)

    def get_map(self) -> dict[str, str]:
        result = {}
        for row in range(self.table_widget.rowCount()):
            key_item = self.table_widget.item(row, 0)
            value_item = self.table_widget.item(row, 1)
            if key_item and value_item:
                result[key_item.text()] = value_item.text()
        return result


class ItemEdit(QtWidgets.QWidget, ThemedWidget):
    """
    Contains a form to populate/edit an Item object.

    Fields:
    name: str
    description: str
    attributes: dict[str, str]
    """

    def __init__(self, item: Optional[planning.Item] = None, parent=None):
        super().__init__(parent)
        self.item = item
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        container = self.create_themed_container(planning.Item, "Item")
        self.form_layout = QtWidgets.QFormLayout()

        self.obj_id = IDDisplay(planning.Item, self.item.obj_id if self.item else None)
        self.name = AILineEdit(
            self.item.name if self.item else "",
            field_name="name",
            entity_type="Item",
            entity_context_func=self._get_entity_context,
        )
        self.type_ = AILineEdit(
            self.item.type_ if self.item else "",
            field_name="type",
            entity_type="Item",
            entity_context_func=self._get_entity_context,
        )
        self.description = AITextEdit(
            self.item.description if self.item else "",
            field_name="description",
            entity_type="Item",
            entity_context_func=self._get_entity_context,
        )
        self.properties = MapEdit[str, str](self.item.properties if self.item else {})

        container.setLayout(self.form_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        self.update_layout()

    def update_layout(self):
        self.form_layout.addRow("ID:", self.obj_id)
        self.form_layout.addRow("Name:", self.name)
        self.form_layout.addRow("Type:", self.type_)
        self.form_layout.addRow("Description:", self.description)
        self.form_layout.addRow("Properties:", self.properties)

    def export_content(self) -> planning.Item:
        """Export the form data as an Item object."""
        return planning.Item(
            obj_id=self.obj_id.get_id(),  # type: ignore[arg-type]
            name=self.name.text(),
            type_=self.type_.text(),
            description=self.description.toPlainText(),
            properties=self.properties.get_map(),
        )

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "name": self.name.text(),
            "type": self.type_.text(),
            "description": self.description.toPlainText(),
        }
        context.update(_find_campaign_context(self))
        return context


class CharacterEdit(QtWidgets.QWidget, ThemedWidget):
    """
    Contains a form to populate/edit a Character object.

    Fields:
    name: str
    description: str
    attributes: dict[str, str]
    """

    def __init__(self, character: Optional[planning.Character] = None, parent=None):
        super().__init__(parent)
        self.character = character
        self.init_ui()

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        container = self.create_themed_container(planning.Character, "Character")
        self.form_layout = QtWidgets.QFormLayout()

        self.obj_id = IDDisplay(planning.Character, self.character.obj_id if self.character else None)
        self.name = AILineEdit(
            self.character.name if self.character else "",
            field_name="name",
            entity_type="Character",
            entity_context_func=self._get_entity_context,
        )
        self.role = AILineEdit(
            self.character.role if self.character else "",
            field_name="role",
            entity_type="Character",
            entity_context_func=self._get_entity_context,
        )
        self.backstory = AITextEdit(
            self.character.backstory if self.character else "",
            field_name="backstory",
            entity_type="Character",
            entity_context_func=self._get_entity_context,
        )
        self.attributes = MapEdit[str, int](self.character.attributes if self.character else {})
        self.skills = MapEdit[str, int](self.character.skills if self.character else {})
        self.storylines = IDListEdit(planning.Arc, self.character.storylines if self.character else [])
        self.inventory = IDListEdit(planning.Item, self.character.inventory if self.character else [])

        container.setLayout(self.form_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        self.update_layout()

    def update_layout(self):
        self.form_layout.addRow("ID:", self.obj_id)
        self.form_layout.addRow("Name:", self.name)
        self.form_layout.addRow("Role:", self.role)
        self.form_layout.addRow("Backstory:", self.backstory)
        self.form_layout.addRow("Attributes:", self.attributes)
        self.form_layout.addRow("Skills:", self.skills)
        self.form_layout.addRow("Storylines:", self.storylines)
        self.form_layout.addRow("Inventory:", self.inventory)

    def export_content(self) -> planning.Character:
        """Export the form data as a Character object."""
        # Note: MapEdit.get_map() returns dict[str, str], but we need dict[str, int] for attributes and skills
        # Converting the values to int
        attributes_dict = {k: int(v) if v.isdigit() else 0 for k, v in self.attributes.get_map().items()}
        skills_dict = {k: int(v) if v.isdigit() else 0 for k, v in self.skills.get_map().items()}

        return planning.Character(
            obj_id=self.obj_id.get_id(),  # type: ignore[arg-type]
            name=self.name.text(),
            role=self.role.text(),
            backstory=self.backstory.toPlainText(),
            attributes=attributes_dict,
            skills=skills_dict,
            storylines=self.storylines.get_ids(),
            inventory=self.inventory.get_ids(),
        )

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "name": self.name.text(),
            "role": self.role.text(),
            "backstory": self.backstory.toPlainText(),
        }
        context.update(_find_campaign_context(self))
        return context


class LocationEdit(QtWidgets.QWidget, ThemedWidget):
    """
    Contains a form to populate/edit a Location object.

    Fields:
    name: str
    description: str
    properties: dict[str, str]
    """

    def __init__(self, location: Optional[planning.Location] = None, parent=None):
        super().__init__(parent)
        self.location = location
        self.init_ui()

    @property
    def coords(self):
        if self.location and self.location.coords:
            return self.location.coords
        return None

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout()
        container = self.create_themed_container(planning.Location, "Location")
        self.form_layout = QtWidgets.QFormLayout()

        self.obj_id = IDDisplay(planning.Location, self.location.obj_id if self.location else None)
        self.name = AILineEdit(
            self.location.name if self.location else "",
            field_name="name",
            entity_type="Location",
            entity_context_func=self._get_entity_context,
        )
        self.description = AITextEdit(
            self.location.description if self.location else "",
            field_name="description",
            entity_type="Location",
            entity_context_func=self._get_entity_context,
        )
        self.neighboring_locations = IDListEdit(
            planning.Location,
            self.location.neighboring_locations if self.location else [],
        )
        self._latitude = QtWidgets.QLineEdit(
            str(self.location.coords[0]) if self.location and self.location.coords else ""
        )
        self._longitude = QtWidgets.QLineEdit(
            str(self.location.coords[1]) if self.location and self.location.coords else ""
        )
        self._altitude = QtWidgets.QLineEdit(
            str(self.location.coords[2])
            if self.location and self.location.coords and len(self.location.coords) == 3
            else ""
        )

        container.setLayout(self.form_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        self.update_layout()

    def update_layout(self):
        self.form_layout.addRow("ID:", self.obj_id)
        self.form_layout.addRow("Name:", self.name)
        self.form_layout.addRow("Description:", self.description)
        self.form_layout.addRow("Neighboring Locations:", self.neighboring_locations)
        self.form_layout.addRow("Latitude:", self._latitude)
        self.form_layout.addRow("Longitude:", self._longitude)
        self.form_layout.addRow("Altitude (optional):", self._altitude)

    def export_content(self) -> planning.Location:
        """Export the form data as a Location object."""
        # Parse coordinates
        coords = None
        try:
            lat_text = self._latitude.text().strip()
            lon_text = self._longitude.text().strip()
            alt_text = self._altitude.text().strip()

            if lat_text and lon_text:
                lat = float(lat_text)
                lon = float(lon_text)
                if alt_text:
                    alt = float(alt_text)
                    coords = (lat, lon, alt)
                else:
                    coords = (lat, lon)
        except ValueError:
            # If parsing fails, leave coords as None
            pass

        return planning.Location(
            obj_id=self.obj_id.get_id(),  # type: ignore[arg-type]
            name=self.name.text(),
            description=self.description.toPlainText(),
            neighboring_locations=self.neighboring_locations.get_ids(),
            coords=coords,
        )

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "name": self.name.text(),
            "description": self.description.toPlainText(),
        }
        context.update(_find_campaign_context(self))
        return context


class CampaignPlanEdit(QtWidgets.QWidget, ThemedWidget):
    """
    Contains a form to populate/edit a CampaignPlan object.

    Fields:
    name: str
    description: str
    objectives: list[Objective]
    arcs: list[Arc]
    items: list[Item]
    characters: list[Character]
    locations: list[Location]
    """

    def __init__(self, campaign_plan: Optional[planning.CampaignPlan] = None, parent=None):
        super().__init__(parent)
        self.campaign_plan = campaign_plan
        self.init_ui()

    def init_ui(self):
        from ..themes.colors import get_colors_for_type

        # Main layout - no scroll area so splitters can divide available space
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Metadata section (non-collapsible)
        metadata_group = QtWidgets.QGroupBox("Campaign Metadata")
        border_color, bg_color = get_colors_for_type(planning.CampaignPlan)
        metadata_group.setStyleSheet(
            f"""
            QGroupBox {{
                border: 2px solid {border_color};
                border-radius: 8px;
                background-color: {bg_color};
                padding: 16px;
                margin-top: 8px;
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
            }}
            QGroupBox::title {{
                color: #ffffff;
                padding: 0 8px;
            }}
        """
        )
        metadata_group.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        metadata_container_layout = QtWidgets.QVBoxLayout()
        metadata_container_layout.setContentsMargins(0, 0, 0, 0)
        metadata_container_layout.setSpacing(8)

        # Top form layout for simple fields
        top_form_layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(
            planning.CampaignPlan,
            self.campaign_plan.obj_id if self.campaign_plan else None,
        )
        self.title = QtWidgets.QLineEdit(self.campaign_plan.title if self.campaign_plan else "")
        self.version = QtWidgets.QLineEdit(self.campaign_plan.version if self.campaign_plan else "")
        top_form_layout.addRow("ID:", self.obj_id)
        top_form_layout.addRow("Title:", self.title)
        top_form_layout.addRow("Version:", self.version)
        metadata_container_layout.addLayout(top_form_layout)

        # Splitter for resizable TextEdit fields
        text_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        text_splitter.setChildrenCollapsible(False)
        text_splitter.setHandleWidth(8)

        # Setting container
        setting_container = QtWidgets.QWidget()
        setting_container.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        setting_layout = QtWidgets.QVBoxLayout()
        setting_layout.setContentsMargins(0, 0, 0, 0)
        setting_layout.setSpacing(2)
        setting_label = QtWidgets.QLabel("Setting:")
        self.setting = AITextEdit(
            self.campaign_plan.setting if self.campaign_plan else "",
            field_name="setting",
            entity_type="CampaignPlan",
            entity_context_func=self._get_entity_context,
        )
        self.setting.setMinimumHeight(30)
        self.setting.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        setting_layout.addWidget(setting_label)
        setting_layout.addWidget(self.setting, 1)
        setting_container.setLayout(setting_layout)
        text_splitter.addWidget(setting_container)

        # Summary container
        summary_container = QtWidgets.QWidget()
        summary_container.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        summary_layout = QtWidgets.QVBoxLayout()
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(2)
        summary_label = QtWidgets.QLabel("Summary:")
        self.summary = AITextEdit(
            self.campaign_plan.summary if self.campaign_plan else "",
            field_name="summary",
            entity_type="CampaignPlan",
            entity_context_func=self._get_entity_context,
        )
        self.summary.setMinimumHeight(30)
        self.summary.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        summary_layout.addWidget(summary_label)
        summary_layout.addWidget(self.summary, 1)
        summary_container.setLayout(summary_layout)
        text_splitter.addWidget(summary_container)

        text_splitter.setSizes([100, 100])
        metadata_container_layout.addWidget(text_splitter, 1)
        metadata_group.setLayout(metadata_container_layout)

        # Create list widgets
        self.storypoints = ListEdit(planning.Point, self.campaign_plan.storypoints if self.campaign_plan else [])
        self.storyline = ListEdit(planning.Arc, self.campaign_plan.storyline if self.campaign_plan else [])
        self.items = ListEdit(planning.Item, self.campaign_plan.items if self.campaign_plan else [])
        self.rules = ListEdit(planning.Rule, self.campaign_plan.rules if self.campaign_plan else [])
        self.objectives = ListEdit(
            planning.Objective,
            self.campaign_plan.objectives if self.campaign_plan else [],
        )
        self.characters = ListEdit(
            planning.Character,
            self.campaign_plan.characters if self.campaign_plan else [],
        )
        self.locations = ListEdit(
            planning.Location,
            self.campaign_plan.locations if self.campaign_plan else [],
        )

        # Create collapsible sections with color coding
        sections: list[tuple[str, QtWidgets.QWidget, type[planning.Object]]] = [
            ("Story Points", self.storypoints, planning.Point),
            ("Storyline Arcs", self.storyline, planning.Arc),
            ("Rules", self.rules, planning.Rule),
            ("Objectives", self.objectives, planning.Objective),
            ("Characters", self.characters, planning.Character),
            ("Items", self.items, planning.Item),
            ("Locations", self.locations, planning.Location),
        ]

        # Scroll area for the collapsible sections (so they can scroll if needed)
        sections_scroll = QtWidgets.QScrollArea()
        sections_scroll.setWidgetResizable(True)
        sections_scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        sections_scroll.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        # Container for sections inside scroll area
        sections_container = QtWidgets.QWidget()
        sections_layout = QtWidgets.QVBoxLayout()
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(8)

        for title, widget, ObjectType in sections:
            border_color, bg_color = get_colors_for_type(ObjectType)
            section = CollapsibleSection(title, border_color, bg_color)
            section.set_content(widget)
            sections_layout.addWidget(section)

        sections_layout.addStretch()
        sections_container.setLayout(sections_layout)
        sections_scroll.setWidget(sections_container)

        # Create a main splitter to allow resizing between metadata and sections
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(8)
        main_splitter.addWidget(metadata_group)
        main_splitter.addWidget(sections_scroll)
        main_splitter.setSizes([300, 500])

        main_layout.addWidget(main_splitter, 1)

        # Add save/export buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save to Database")
        self.save_button.setToolTip("Save campaign to database (Ctrl+S)")
        self.save_button.clicked.connect(self.save_to_database)
        button_layout.addWidget(self.save_button)

        self.export_button = QtWidgets.QPushButton("Export to JSON")
        self.export_button.setToolTip("Export campaign to JSON file")
        self.export_button.clicked.connect(self.export_to_json)
        button_layout.addWidget(self.export_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def update_layout(self):
        # No longer needed - layout is set up in init_ui
        pass

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        return {
            "title": self.title.text(),
            "version": self.version.text(),
            "setting": self.setting.toPlainText(),
            "summary": self.summary.toPlainText(),
        }

    def export_content(self) -> planning.CampaignPlan:
        """Export the form data as a CampaignPlan object."""
        return planning.CampaignPlan(
            obj_id=self.obj_id.get_id(),  # type: ignore[arg-type]
            title=self.title.text(),
            version=self.version.text(),
            setting=self.setting.toPlainText(),
            summary=self.summary.toPlainText(),
            storypoints=self.storypoints.get_objects(),
            storyline=self.storyline.get_objects(),
            items=self.items.get_objects(),
            rules=self.rules.get_objects(),
            objectives=self.objectives.get_objects(),
            characters=self.characters.get_objects(),
            locations=self.locations.get_objects(),
        )

    def save_to_database(self):
        """Handle save button click - delegate to main window."""
        main_window = self.window()
        if hasattr(main_window, "save_campaign"):
            main_window.save_campaign()  # type: ignore

    def export_to_json(self):
        """Handle export button click - delegate to main window."""
        main_window = self.window()
        if hasattr(main_window, "export_campaign"):
            main_window.export_campaign()  # type: ignore
