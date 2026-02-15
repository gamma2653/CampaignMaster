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


def _create_edit_dialog(
    parent: QtWidgets.QWidget,
    title: str,
    edit_widget: QtWidgets.QWidget,
) -> QtWidgets.QDialog:
    """Create a standardized edit dialog with scroll area and OK/Cancel buttons.

    Args:
        parent: Parent widget for the dialog.
        title: Dialog window title.
        edit_widget: The edit widget to display inside the dialog.

    Returns:
        Configured QDialog (not yet exec'd).
    """
    dialog = QtWidgets.QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setMinimumWidth(550)
    dialog.setMinimumHeight(500)
    dialog.resize(600, 650)

    dialog_layout = QtWidgets.QVBoxLayout()

    # Wrap edit widget in scroll area
    scroll = QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
    scroll.setWidget(edit_widget)
    dialog_layout.addWidget(scroll, 1)

    # OK/Cancel buttons
    button_box = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
    )
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    dialog_layout.addWidget(button_box)

    dialog.setLayout(dialog_layout)
    return dialog


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

    object_created = QtCore.Signal(object)

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

        # Get the edit widget class from globals
        edit_widget_class = globals()[edit_widget_class_name]
        edit_widget = edit_widget_class()

        dialog = _create_edit_dialog(
            self,
            f"Create New {self.model_type.__name__}",
            edit_widget,
        )

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # Export the form data and create in database
            form_data = edit_widget.export_content()
            content_api._create_object(form_data, proto_user_id=0)

            # Refresh the dropdown and select the new ID
            self.id_select.populate()
            self.id_select.set_selected_id(form_data.obj_id)

            # Notify listeners that a new object was created
            self.object_created.emit(form_data)
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


# Map model types to their edit widget class names
_EDIT_WIDGET_MAP: dict[type[planning.Object], str] = {
    planning.Point: "PointEdit",
    planning.Rule: "RuleEdit",
    planning.Objective: "ObjectiveEdit",
    planning.Segment: "SegmentEdit",
    planning.Arc: "ArcEdit",
    planning.Item: "ItemEdit",
    planning.Character: "CharacterEdit",
    planning.Location: "LocationEdit",
}


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
        # Check if this model type has a dedicated edit widget
        edit_widget_class_name = _EDIT_WIDGET_MAP.get(self.model_type)

        if edit_widget_class_name:
            # Get the edit widget class from globals (all edit widgets are in this module)
            edit_widget_class = globals()[edit_widget_class_name]
            edit_widget = edit_widget_class()

            dialog = _create_edit_dialog(
                self,
                f"Add {self.model_type.__name__}",
                edit_widget,
            )

            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                # Export the form data (which includes the ID generated by IDDisplay)
                form_data = edit_widget.export_content()
                # Create the object in the database using the form data
                content_api._create_object(form_data, proto_user_id=0)
                # Add to the list
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

        edit_widget_class_name = _EDIT_WIDGET_MAP.get(self.model_type)
        if not edit_widget_class_name:
            return

        # Pass the existing object to the edit widget to pre-populate the form
        edit_widget_class = globals()[edit_widget_class_name]
        edit_widget = edit_widget_class(obj)

        dialog = _create_edit_dialog(
            self,
            f"Edit {self.model_type.__name__}",
            edit_widget,
        )

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # Export the updated form data
            form_data = edit_widget.export_content()
            # Update the object in the database
            content_api.update_object(form_data, proto_user_id=0)
            # Update in our local list
            self.objects[row] = cast(T, form_data)
            # Update the list item display
            item.setText(str(form_data.obj_id))

    def add_existing_object(self, obj: T):
        """Add an already-created object to the list without opening a dialog."""
        self.list_widget.addItem(str(obj.obj_id))
        self.objects.append(obj)

    def get_objects(self) -> list[T]:
        """Return the list of objects."""
        return self.objects


def _make_labeled_text_widget(
    label_text: str,
    text_edit: QtWidgets.QTextEdit,
) -> QtWidgets.QWidget:
    """Create a container with a label above a text edit widget."""
    container = QtWidgets.QWidget()
    container.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Expanding,
    )
    layout = QtWidgets.QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)
    label = QtWidgets.QLabel(label_text)
    layout.addWidget(label)
    layout.addWidget(text_edit, 1)
    container.setLayout(layout)
    return container


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
        container_layout = QtWidgets.QVBoxLayout()

        # Short fields in form layout
        form_layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Rule, self.rule.obj_id if self.rule else None)
        form_layout.addRow("ID:", self.obj_id)
        container_layout.addLayout(form_layout)

        # Text areas in vertical splitter
        self.description = AITextEdit(
            self.rule.description if self.rule else "",
            field_name="description",
            entity_type="Rule",
            entity_context_func=self._get_entity_context,
            placeholder="Describe the rule...",
        )
        self.effect = AITextEdit(
            self.rule.effect if self.rule else "",
            field_name="effect",
            entity_type="Rule",
            entity_context_func=self._get_entity_context,
            placeholder="Describe the rule's effect...",
        )

        text_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        text_splitter.setChildrenCollapsible(False)
        text_splitter.setHandleWidth(8)
        text_splitter.addWidget(_make_labeled_text_widget("Description:", self.description))
        text_splitter.addWidget(_make_labeled_text_widget("Effect:", self.effect))
        text_splitter.setSizes([100, 100])
        container_layout.addWidget(text_splitter, 1)

        # Components list below
        components_label = QtWidgets.QLabel("Components:")
        container_layout.addWidget(components_label)
        self.components = StrListEdit(self.rule.components if self.rule else [])
        container_layout.addWidget(self.components)

        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "description": self.description.toPlainText(),
            "effect": self.effect.toPlainText(),
            "components": self.components.get_items(),
        }
        context.update(_find_campaign_context(self))
        return context

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
        container_layout = QtWidgets.QVBoxLayout()

        # Short fields
        form_layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Objective, self.objective.obj_id if self.objective else None)
        form_layout.addRow("ID:", self.obj_id)
        container_layout.addLayout(form_layout)

        # Description text area with label
        desc_label = QtWidgets.QLabel("Description:")
        container_layout.addWidget(desc_label)
        self.description = AITextEdit(
            self.objective.description if self.objective else "",
            field_name="description",
            entity_type="Objective",
            entity_context_func=self._get_entity_context,
            placeholder="Describe the objective...",
        )
        container_layout.addWidget(self.description, 1)

        # Components list
        components_label = QtWidgets.QLabel("Components:")
        container_layout.addWidget(components_label)
        self.components = StrListEdit(self.objective.components if self.objective else [])
        container_layout.addWidget(self.components)

        # Prerequisites list
        prereqs_label = QtWidgets.QLabel("Prerequisites:")
        container_layout.addWidget(prereqs_label)
        self.prerequisites = IDListEdit(planning.Objective, self.objective.prerequisites if self.objective else [])
        container_layout.addWidget(self.prerequisites)

        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "description": self.description.toPlainText(),
            "components": self.components.get_items(),
        }
        context.update(_find_campaign_context(self))
        return context

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
        container_layout = QtWidgets.QVBoxLayout()

        # Short fields
        form_layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Point, self.point.obj_id if self.point else None)
        self.name = AILineEdit(
            self.point.name if self.point else "",
            field_name="name",
            entity_type="Point",
            entity_context_func=self._get_entity_context,
            placeholder="Story point name",
        )
        self.objective = IDSelect(planning.Objective)

        form_layout.addRow("ID:", self.obj_id)
        form_layout.addRow("Name:", self.name)
        form_layout.addRow("Objective ID:", self.objective)
        container_layout.addLayout(form_layout)

        # Description text area with label
        desc_label = QtWidgets.QLabel("Description:")
        container_layout.addWidget(desc_label)
        self.description = AITextEdit(
            self.point.description if self.point else "",
            field_name="description",
            entity_type="Point",
            entity_context_func=self._get_entity_context,
            placeholder="Describe this story point...",
        )
        container_layout.addWidget(self.description, 1)

        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "name": self.name.text(),
            "description": self.description.toPlainText(),
        }
        context.update(_find_campaign_context(self))
        return context

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
        container_layout = QtWidgets.QVBoxLayout()

        # Short fields
        form_layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Segment, self.segment.obj_id if self.segment else None)
        self.name = AILineEdit(
            self.segment.name if self.segment else "",
            field_name="name",
            entity_type="Segment",
            entity_context_func=self._get_entity_context,
            placeholder="Segment name",
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

        # Connect signals to propagate new points to the campaign's storypoints
        self.start.object_created.connect(self._on_point_created)
        self.end.object_created.connect(self._on_point_created)

        # View buttons for inspecting selected start/end points
        self.view_start_button = QtWidgets.QPushButton("View")
        self.view_start_button.setMaximumWidth(60)
        self.view_start_button.clicked.connect(lambda: self._view_point(self.start))
        self.view_end_button = QtWidgets.QPushButton("View")
        self.view_end_button.setMaximumWidth(60)
        self.view_end_button.clicked.connect(lambda: self._view_point(self.end))

        # Wrap start/end selectors with their View buttons
        start_row = QtWidgets.QHBoxLayout()
        start_row.setContentsMargins(0, 0, 0, 0)
        start_row.addWidget(self.start, 1)
        start_row.addWidget(self.view_start_button)
        start_container = QtWidgets.QWidget()
        start_container.setLayout(start_row)

        end_row = QtWidgets.QHBoxLayout()
        end_row.setContentsMargins(0, 0, 0, 0)
        end_row.addWidget(self.end, 1)
        end_row.addWidget(self.view_end_button)
        end_container = QtWidgets.QWidget()
        end_container.setLayout(end_row)

        form_layout.addRow("ID:", self.obj_id)
        form_layout.addRow("Name:", self.name)
        form_layout.addRow("Start Point:", start_container)
        form_layout.addRow("End Point:", end_container)
        container_layout.addLayout(form_layout)

        # Description text area with label
        desc_label = QtWidgets.QLabel("Description:")
        container_layout.addWidget(desc_label)
        self.description = AITextEdit(
            self.segment.description if self.segment else "",
            field_name="description",
            entity_type="Segment",
            entity_context_func=self._get_entity_context,
            placeholder="Describe this segment...",
        )
        container_layout.addWidget(self.description, 1)

        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def _on_point_created(self, point: planning.Point):
        """Propagate a newly created point to the parent campaign's storypoints list."""
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, CampaignPlanEdit):
                parent.storypoints.add_existing_object(point)
                return
            parent = parent.parent()

    def _view_point(self, id_select_widget: IDSelectWithCreate):
        """Open a read-only dialog to view the selected point."""
        selected_id = id_select_widget.get_selected_id()
        if not selected_id:
            return

        point = content_api.retrieve_object(selected_id)
        if not point or not isinstance(point, planning.Point):
            QtWidgets.QMessageBox.warning(
                self, "Not Found", f"Could not find Point {selected_id}."
            )
            return

        edit_widget = PointEdit(point)
        dialog = _create_edit_dialog(self, f"View Point {selected_id}", edit_widget)

        # Replace OK/Cancel with just Close for view-only
        button_box = dialog.findChild(QtWidgets.QDialogButtonBox)
        if button_box:
            button_box.clear()
            button_box.addButton(QtWidgets.QDialogButtonBox.StandardButton.Close)
            button_box.rejected.connect(dialog.reject)

        dialog.exec()

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "name": self.name.text(),
            "description": self.description.toPlainText(),
        }
        context.update(_find_campaign_context(self))
        return context

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
        container_layout = QtWidgets.QVBoxLayout()

        # Short fields
        form_layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Arc, self.arc.obj_id if self.arc else None)
        self.name = AILineEdit(
            self.arc.name if self.arc else "",
            field_name="name",
            entity_type="Arc",
            entity_context_func=self._get_entity_context,
            placeholder="Story arc name",
        )
        form_layout.addRow("ID:", self.obj_id)
        form_layout.addRow("Name:", self.name)
        container_layout.addLayout(form_layout)

        # Description text area with label
        desc_label = QtWidgets.QLabel("Description:")
        container_layout.addWidget(desc_label)
        self.description = AITextEdit(
            self.arc.description if self.arc else "",
            field_name="description",
            entity_type="Arc",
            entity_context_func=self._get_entity_context,
            placeholder="Describe this story arc...",
        )
        container_layout.addWidget(self.description, 1)

        # Segments list
        segments_label = QtWidgets.QLabel("Segments:")
        container_layout.addWidget(segments_label)
        self.segments = ListEdit[planning.Segment](
            planning.Segment,
            objects=self.arc.segments if self.arc else [],
        )
        container_layout.addWidget(self.segments)

        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def _get_entity_context(self) -> dict[str, Any]:
        """Get current entity data for AI context."""
        context = {
            "name": self.name.text(),
            "description": self.description.toPlainText(),
        }
        context.update(_find_campaign_context(self))
        return context

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
        container_layout = QtWidgets.QVBoxLayout()

        # Short fields
        form_layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Item, self.item.obj_id if self.item else None)
        self.name = AILineEdit(
            self.item.name if self.item else "",
            field_name="name",
            entity_type="Item",
            entity_context_func=self._get_entity_context,
            placeholder="Item name",
        )
        self.type_ = AILineEdit(
            self.item.type_ if self.item else "",
            field_name="type",
            entity_type="Item",
            entity_context_func=self._get_entity_context,
            placeholder="e.g. Weapon, Potion, Artifact",
        )
        form_layout.addRow("ID:", self.obj_id)
        form_layout.addRow("Name:", self.name)
        form_layout.addRow("Type:", self.type_)
        container_layout.addLayout(form_layout)

        # Description text area with label
        desc_label = QtWidgets.QLabel("Description:")
        container_layout.addWidget(desc_label)
        self.description = AITextEdit(
            self.item.description if self.item else "",
            field_name="description",
            entity_type="Item",
            entity_context_func=self._get_entity_context,
            placeholder="Describe the item...",
        )
        container_layout.addWidget(self.description, 1)

        # Properties map
        props_label = QtWidgets.QLabel("Properties:")
        container_layout.addWidget(props_label)
        self.properties = MapEdit[str, str](self.item.properties if self.item else {})
        container_layout.addWidget(self.properties)

        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

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
        container_layout = QtWidgets.QVBoxLayout()

        # Short fields
        form_layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Character, self.character.obj_id if self.character else None)
        self.name = AILineEdit(
            self.character.name if self.character else "",
            field_name="name",
            entity_type="Character",
            entity_context_func=self._get_entity_context,
            placeholder="Character name",
        )
        self.role = AILineEdit(
            self.character.role if self.character else "",
            field_name="role",
            entity_type="Character",
            entity_context_func=self._get_entity_context,
            placeholder="e.g. NPC, Villain, Ally",
        )
        form_layout.addRow("ID:", self.obj_id)
        form_layout.addRow("Name:", self.name)
        form_layout.addRow("Role:", self.role)
        container_layout.addLayout(form_layout)

        # Backstory text area with label
        backstory_label = QtWidgets.QLabel("Backstory:")
        container_layout.addWidget(backstory_label)
        self.backstory = AITextEdit(
            self.character.backstory if self.character else "",
            field_name="backstory",
            entity_type="Character",
            entity_context_func=self._get_entity_context,
            placeholder="Write the character's backstory...",
        )
        container_layout.addWidget(self.backstory, 1)

        # Attributes map
        attrs_label = QtWidgets.QLabel("Attributes:")
        container_layout.addWidget(attrs_label)
        self.attributes = MapEdit[str, int](self.character.attributes if self.character else {})
        container_layout.addWidget(self.attributes)

        # Skills map
        skills_label = QtWidgets.QLabel("Skills:")
        container_layout.addWidget(skills_label)
        self.skills = MapEdit[str, int](self.character.skills if self.character else {})
        container_layout.addWidget(self.skills)

        # Storylines
        storylines_label = QtWidgets.QLabel("Storylines:")
        container_layout.addWidget(storylines_label)
        self.storylines = IDListEdit(planning.Arc, self.character.storylines if self.character else [])
        container_layout.addWidget(self.storylines)

        # Inventory
        inventory_label = QtWidgets.QLabel("Inventory:")
        container_layout.addWidget(inventory_label)
        self.inventory = IDListEdit(planning.Item, self.character.inventory if self.character else [])
        container_layout.addWidget(self.inventory)

        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

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
        container_layout = QtWidgets.QVBoxLayout()

        # Short fields
        form_layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Location, self.location.obj_id if self.location else None)
        self.name = AILineEdit(
            self.location.name if self.location else "",
            field_name="name",
            entity_type="Location",
            entity_context_func=self._get_entity_context,
            placeholder="Location name",
        )
        self._latitude = QtWidgets.QLineEdit(
            str(self.location.coords[0]) if self.location and self.location.coords else ""
        )
        self._latitude.setPlaceholderText("e.g. 40.7128")
        self._longitude = QtWidgets.QLineEdit(
            str(self.location.coords[1]) if self.location and self.location.coords else ""
        )
        self._longitude.setPlaceholderText("e.g. -74.0060")
        self._altitude = QtWidgets.QLineEdit(
            str(self.location.coords[2])
            if self.location and self.location.coords and len(self.location.coords) == 3
            else ""
        )
        self._altitude.setPlaceholderText("e.g. 10.0")

        form_layout.addRow("ID:", self.obj_id)
        form_layout.addRow("Name:", self.name)
        form_layout.addRow("Latitude:", self._latitude)
        form_layout.addRow("Longitude:", self._longitude)
        form_layout.addRow("Altitude (optional):", self._altitude)
        container_layout.addLayout(form_layout)

        # Description text area with label
        desc_label = QtWidgets.QLabel("Description:")
        container_layout.addWidget(desc_label)
        self.description = AITextEdit(
            self.location.description if self.location else "",
            field_name="description",
            entity_type="Location",
            entity_context_func=self._get_entity_context,
            placeholder="Describe this location...",
        )
        container_layout.addWidget(self.description, 1)

        # Neighboring locations
        neighbors_label = QtWidgets.QLabel("Neighboring Locations:")
        container_layout.addWidget(neighbors_label)
        self.neighboring_locations = IDListEdit(
            planning.Location,
            self.location.neighboring_locations if self.location else [],
        )
        container_layout.addWidget(self.neighboring_locations)

        container.setLayout(container_layout)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

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
        self.title.setPlaceholderText("Campaign title")
        self.version = QtWidgets.QLineEdit(self.campaign_plan.version if self.campaign_plan else "")
        self.version.setPlaceholderText("e.g. 1.0")
        top_form_layout.addRow("ID:", self.obj_id)
        top_form_layout.addRow("Title:", self.title)
        top_form_layout.addRow("Version:", self.version)
        metadata_container_layout.addLayout(top_form_layout)

        # Splitter for resizable TextEdit fields
        text_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        text_splitter.setChildrenCollapsible(False)
        text_splitter.setHandleWidth(8)

        # Setting container
        self.setting = AITextEdit(
            self.campaign_plan.setting if self.campaign_plan else "",
            field_name="setting",
            entity_type="CampaignPlan",
            entity_context_func=self._get_entity_context,
            placeholder="Describe the campaign setting...",
        )
        self.setting.setMinimumHeight(30)
        text_splitter.addWidget(_make_labeled_text_widget("Setting:", self.setting))

        # Summary container
        self.summary = AITextEdit(
            self.campaign_plan.summary if self.campaign_plan else "",
            field_name="summary",
            entity_type="CampaignPlan",
            entity_context_func=self._get_entity_context,
            placeholder="Write a campaign summary...",
        )
        self.summary.setMinimumHeight(30)
        text_splitter.addWidget(_make_labeled_text_widget("Summary:", self.summary))

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
