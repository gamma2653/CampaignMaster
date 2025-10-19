# GUI application for managing tabletop RPG campaigns

from typing import Optional, cast, Any, NamedTuple

from ..content.planning import (
    ID,
    AbstractObject,
    CampaignPlan,
    release_id,
)
from pydantic.fields import FieldInfo

from PySide6 import QtWidgets, QtCore, QtGui


FieldPair = NamedTuple("FieldPair", [("field_name", str), ("field", QtWidgets.QWidget)])

class ObjectListWidget(QtWidgets.QGroupBox):
    """
    A list view to display and manage a list of Pydantic model instances.

    Spawns instances of PydanticForm to add/edit items.
    """

    def __init__(
        self, model: type[AbstractObject], parent: "Optional[ObjectForm]" = None
    ):
        # TODO: localize and pluralize the title
        print(model)
        super().__init__(f"{model.__name__}s", parent)
        self.model = model
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.list_widget = QtWidgets.QListWidget(self)
        layout.addWidget(self.list_widget)

        # Track open forms for editing items, keyed by str(obj_id)
        self.forms: dict[str, ObjectForm] = {}

        self.add_button = QtWidgets.QPushButton("Add", self)
        self.edit_button = QtWidgets.QPushButton("Edit", self)
        self.remove_button = QtWidgets.QPushButton("Remove", self)

        self.add_button.clicked.connect(self.open_add_item)
        self.edit_button.clicked.connect(
            lambda: self.edit_item(
                self.list_widget.currentItem().data(QtCore.Qt.ItemDataRole.UserRole)
            )
        )
        self.remove_button.clicked.connect(self.remove_item)

        layout.addWidget(self.add_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

    def open_add_item(self):
        # Create a pop-out form to add a new item, and connect its save event
        form = ObjectForm(self.model, self.parent())
        # On subform save, add item to the list view
        form.save_event.connect(lambda: self.add_item(form.export_content()))
        form.show()
        # HACK: Sneak-peak the ID from the newly created form.
        obj_id = form.raw_content.get("obj_id", None)
        if obj_id:
            self.forms[obj_id] = form
        else:
            print(
                f"Warning: Could not retrieve obj_id from new form of model {form.model_name}."
            )

    def add_item(self, item: AbstractObject):
        # Add the item to the list view
        if str(item.obj_id) not in self.forms:
            print(
                f"Warning: Item with obj_id {item.obj_id} not in forms dict. Cannot add."
            )
        else:
            item_widget = QtWidgets.QListWidgetItem(str(item))
            item_widget.setData(QtCore.Qt.ItemDataRole.UserRole, item.obj_id)
            self.list_widget.addItem(item_widget)

    def edit_item(self, item_id: ID):
        # Create a form to edit the selected item
        if str(item_id) not in self.forms:
            print(f"Warning: No form found for item ID {item_id}. Opening new form.")
            self.forms[str(item_id)] = ObjectForm(self.model, self.parent())
        self.forms[str(item_id)].show()

    def remove_item(self):
        # Logic to remove the selected item
        selected_items = self.list_widget.selectedItems()
        for item in selected_items:
            item_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if item_id and str(item_id) in self.forms:
                form = self.forms[str(item_id)]
                form.hide()
                # del self.forms[str(item_id)]
                self.list_widget.takeItem(self.list_widget.row(item))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        # Close any open forms
        for form in self.forms.values():
            form.prompt_for_save = False
            form.close()
        return super().closeEvent(event)
    
    def close_form(self) -> None:
        self.close()


class ObjectCreateWidget(QtWidgets.QWidget):
    """
    A widget to create a new Pydantic model instance.
    """

    def __init__(self, model: type[AbstractObject], parent=None):
        super().__init__(parent)
        self.model = model
        self.form = ObjectForm(self.model, self.parent())
        self.label = QtWidgets.QLabel(f"<Empty>", self)
        self.button = QtWidgets.QPushButton(f"Create {self.model.__name__}", self)
        self.button.clicked.connect(self.form.show)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def close_form(self) -> None:
        self.form.prompt_for_save = False
        self.form.close()


class ObjectForm(QtWidgets.QWidget):
    """
    A form to display and edit Pydantic model fields.
    """

    save_event = QtCore.Signal()
    prompt_for_save = True

    def __init__(self, model: type[AbstractObject], parent=None):
        super().__init__(parent)
        self.is_subform = isinstance(parent, ObjectForm)
        self.model = model
        self.exists = False
        # After some internal debate, I've decided that subforms will act in a slightly funky way-
        # To pop out, they will reset their parent, while keeping track of the original parent.
        self.parent_form: Optional["ObjectForm"] = None
        self.fields: dict[str, QtWidgets.QWidget] = {}
        if self.is_subform:
            self.parent_form = cast("ObjectForm", parent)
            self.setParent(None)
        # Internal data tracking
        self.dirty_fields: set[FieldPair] = set()
        self._raw_content: dict[str, Any] = {}
        self.obj_id = self.export_content().obj_id
        self.init_ui()
        self.setWindowTitle(f"{self.model_name} Form")
    
    @staticmethod
    def get_line_content(field: QtWidgets.QLineEdit) -> str:
        """
        Retrieve the current content of a QLineEdit field.
        """
        return field.text()
    
    @staticmethod
    def get_object_content(field: ObjectCreateWidget) -> AbstractObject:
        """
        Retrieve the current content of a subform as a Pydantic model instance.
        """
        return field.form.export_content()

    @staticmethod
    def get_list_content(field: ObjectListWidget) -> list[AbstractObject]:
        """
        Retrieve the current content of a list widget as a list of Pydantic model instances.
        """
        # Compile list content
        items = []
        for i in range(field.list_widget.count()):
            item_widget = field.list_widget.item(i)
            item_id = item_widget.data(QtCore.Qt.ItemDataRole.UserRole)
            if item_id and item_id in field.forms:
                item_form = field.forms[item_id]
                items.append(item_form.export_content())
        return items

    TYPE_TO_RETRIEVER = {
        ObjectCreateWidget: get_object_content,
        ObjectListWidget: get_list_content,
    }

    @property
    def raw_content(self) -> dict[str, Any]:
        """
        Retrieve the current content of the form as a validated Pydantic model instance.
        """
        raw_content = {}
        for field_name, field in self.dirty_fields:
            retriever = self.TYPE_TO_RETRIEVER.get(type(field), ObjectForm.get_line_content)
            raw_content[field_name] = retriever(field)
        # Compile w/ existing content
        return self._raw_content | raw_content

    def export_content(self) -> AbstractObject:
        # Validate and return the content as a Pydantic model instance
        return self.model.model_validate(self.raw_content)
        # TODO: On validation error, highlight the offending fields

    @raw_content.setter
    def raw_content(self, content: AbstractObject):
        # Validate and set the content of the form
        content = self.model.model_validate(content)
        # Reflect the content in the form fields
        for field in self.model_fields.keys():
            value = getattr(content, field, "")
            input_field = self.findChild(
                QtWidgets.QLineEdit,
                field,
                QtCore.Qt.FindChildOption.FindDirectChildrenOnly,
            )
            if input_field:
                input_field.setText(str(value))

    @property
    def model_fields(self) -> dict[str, FieldInfo]:
        return self.model.model_fields

    @property
    def model_name(self) -> str:
        return self.model.__name__

    def save_content(self):
        """
        Save the current content of the form.
        Validate and store the content, emitting the save_event signal.
        """
        try:
            self._raw_content = self.export_content().model_dump()
        except Exception as e:
            print(f"Error saving content: {e}")
        self.dirty_fields.clear()
        if self.exists:
            # Update existing content
            pass
        else:
            self.exists = True
            self.save_event.emit()

    def save_and_close(self):
        """
        Save the current content and close the form.
        """
        self.save_content()
        self.close()

    def init_ui(self):
        """
        Precondition: self.fields is a list of field names in the Pydantic model.
        """
        layout = QtWidgets.QVBoxLayout(self)
        for field in self.model_fields.keys():
            self.fields[field] = self.create_field_item(
                field, self.model_fields[field].annotation
            )
            layout.addWidget(self.fields[field])
        # Special handling for "obj_id" field to make it read-only
        obj_id_field: Optional[QtWidgets.QWidget] = self.fields.get("obj_id", None)
        try:
            obj_id_field = cast(QtWidgets.QLineEdit, obj_id_field)
            obj_id_field.setReadOnly(True)
            obj_id_field.setText(str(self.obj_id))
        except Exception as e:
            print(f"Error setting obj_id field to read-only: {e}?")
        # Add save and save_and_close buttons
        self.save_button = QtWidgets.QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_content)
        layout.addWidget(self.save_button)
        self.save_and_close_button = QtWidgets.QPushButton("Save and Close", self)
        self.save_and_close_button.clicked.connect(self.save_and_close)
        layout.addWidget(self.save_and_close_button)
        self.setLayout(layout)

    def mark_field_dirty(self, field_name: str):
        """
        Mark a field as dirty (aka modified, unsynced).
        """
        self.dirty_fields.add(FieldPair(field_name, self.fields[field_name]))

    def create_field_item(self, field_name, field_type):
        """
        Create an input field widget based on the field type.

        If the field type is iterable,
        """
        try:
            iter(field_type)
        except TypeError:
            # Not iterable
            if issubclass(field_type, AbstractObject):
                # Subform
                return ObjectCreateWidget(field_type, self)
        else:
            # Iterable
            return ObjectListWidget(field_type.__args__[0], self)

        # Default to QLineEdit for simple types
        line_edit = QtWidgets.QLineEdit(self)
        line_edit.textChanged.connect(lambda: self.mark_field_dirty(field_name))
        line_edit.setPlaceholderText(field_name)
        return line_edit

    @classmethod
    def from_existing(
        cls,
        obj_instance: AbstractObject,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> "ObjectForm":
        """
        Create a PydanticForm from an existing Pydantic model instance.
        """
        form_instance = cls(type(obj_instance), parent=parent)
        form_instance.raw_content = obj_instance
        return form_instance

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        # Request confirmation if there are unsaved changes
        if self.dirty_fields and self.prompt_for_save:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No
                | QtWidgets.QMessageBox.StandardButton.Cancel,
            )
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.save_content()
            elif reply == QtWidgets.QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        # Close any subforms
        for field in self.fields.values():
            if isinstance(field, ObjectCreateWidget) or isinstance(field, ObjectListWidget):
                field = cast(ObjectCreateWidget | ObjectListWidget, field)
                field.close_form()
        # Release ID
        if not self.exists:
            release_id(self.obj_id)
        # Execute normal close event
        return super().closeEvent(event)


class CampaignMasterPlanApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Campaign Master")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.main_form: Optional[ObjectForm] = None

        self.setup_ui()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        # Close any open forms or dialogs
        for i in range(self.central_widget.count()):
            widget = self.central_widget.widget(i)
            widget.close()
        return super().closeEvent(event)

    def setup_ui(self):
        """
        Setup the user interface for `CampaignMasterPlanApp`.
        """
        self.info_panel = QtWidgets.QWidget()
        self.central_widget.addWidget(self.info_panel)

        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("Welcome to Campaign Master!")
        layout.addWidget(self.label)

        self.info_panel.setLayout(layout)

        self.new_btn = QtWidgets.QPushButton("Create New Campaign Plan")
        layout.addWidget(self.new_btn)

        self.load_btn = QtWidgets.QPushButton("Load Existing Campaign Plan")
        layout.addWidget(self.load_btn)

        self.new_btn.clicked.connect(self.start_new_campaign)
        self.load_btn.clicked.connect(self.load_existing_campaign)

    def start_new_campaign(self):
        """
        Spawn a Pydantic form to create a new campaign plan.
        """
        self.label.setText("Starting a new campaign...")
        self.main_form = ObjectForm(CampaignPlan, self)
        self.central_widget.addWidget(self.main_form)
        self.central_widget.setCurrentWidget(self.main_form)

    def load_existing_campaign(self):
        self.label.setText("Loading an existing campaign...")
        file_dialog = QtWidgets.QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open Campaign Plan", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            # Load the campaign plan from the selected file
            with open(file_path, "rb") as f:
                self.main_form = ObjectForm.from_existing(
                    CampaignPlan.model_validate_json(f.read()),
                    self,
                )
            self.central_widget.addWidget(self.main_form)
            self.central_widget.setCurrentWidget(self.main_form)
