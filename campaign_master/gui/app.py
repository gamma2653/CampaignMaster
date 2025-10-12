# GUI application for managing tabletop RPG campaigns

from typing import Optional, cast
from ..content.planning import (
    ID,
    AbstractObject,
    Object,
    CampaignPlan,
    RuleID
)

from PySide6 import QtWidgets, QtCore


class BaseModelView(QtWidgets.QGroupBox):
    """
    A base view for displaying and editing Pydantic models.
    """
    is_model_view = True

    @staticmethod
    def is_model_view_widget(widget: QtWidgets.QWidget) -> bool:
        """
        Check if a given widget is a model view.
        """
        return bool(getattr(widget, "is_model_view", False))


class ModelListView(BaseModelView):
    item_added = QtCore.Signal(AbstractObject)
    item_removed = QtCore.Signal(AbstractObject)

    """
    A list view to display and manage a list of Pydantic model instances.
    """

    def __init__(
        self, model: type[Object], parent: "Optional[PydanticForm]" = None
    ):
        # TODO: localize and pluralize the title
        super().__init__(f"{model.__name__}s", parent)
        self.model = model
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.list_widget = QtWidgets.QListWidget(self)
        layout.addWidget(self.list_widget)

        self.forms: dict[ID, PydanticForm] = {}

        self.add_button = QtWidgets.QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_item)
        layout.addWidget(self.add_button)

        self.remove_button = QtWidgets.QPushButton("Remove", self)
        self.remove_button.clicked.connect(self.remove_item)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

    def add_item(self):
        # Create a form to add a new item
        form = PydanticForm(self.model, self.parent())
        form.setWindowTitle("Add New Item")
        form.show()
        self.forms[ID("new")] = form

    def remove_item(self):
        # Logic to remove the selected item
        pass


class PydanticForm(QtWidgets.QWidget):
    """
    A form to display and edit Pydantic model fields.
    """

    def __init__(self, model: type[Object], parent=None):
        super().__init__(parent)
        self.is_subform = isinstance(parent, PydanticForm)
        # After some internal debate, I've decided that subforms will act in a slightly funky way-
        # To pop out, they will reset their parent, while keeping track of the original parent.
        self.parent_form: Optional["PydanticForm"]
        if self.is_subform:
            self.parent_form = cast("PydanticForm", parent)
            self.setParent(None)
        else:
            self.parent_form = None
        self.model = model
        self.init_ui()

    @property
    def annotations(self):
        return self.model.__annotations__
    
    @property
    def type_name(self) -> str:
        return self.model.__name__.lower()

    def init_ui(self):
        """
        Precondition: self.fields is a list of field names in the Pydantic model.
        """
        print(f"Initializing UI with fields: {self.annotations.keys()}")
        layout = QtWidgets.QVBoxLayout(self)
        for field in self.annotations.keys():
            input_field = self.create_field_item(field, self.annotations[field])
            layout.addWidget(input_field)
        self.setLayout(layout)

    def create_field_item(self, field_name, field_type):
        """
        Create an input field widget based on the field type.

        If the field type is iterable,
        """
        print(f"Creating input field for {field_name} of type {field_type}")
        try:
            iter(field_type)
        except TypeError:
            # Not iterable
            pass
        else:
            # Iterable
            return ModelListView(field_type.__args__[0], self)
        # Handle special "id" case
        line_edit = QtWidgets.QLineEdit(self)
        if field_name == "id":
            # line_edit.setText(str(ID_FACTORY.from_field_name(self.type_name)))
            line_edit.setReadOnly(True)
        return line_edit

    @classmethod
    def from_existing(
        cls, obj_type: type[Object], obj_instance: Object, parent: Optional[QtWidgets.QWidget] = None
    ) -> "PydanticForm":
        """
        Create a PydanticForm from an existing Pydantic model instance.
        """
        form_instance = cls(obj_type, parent)
        # Populate fields with existing data
        for field in form_instance.annotations.keys():
            value = getattr(obj_instance, field, "")
            input_field = form_instance.findChild(QtWidgets.QLineEdit, field)
            if input_field:
                input_field.setText(str(value))
        return form_instance

    def save(self):
        """
        Save the current form data back to the Pydantic model instance.
        """
        data = {}
        for field in self.annotations.keys():
            input_field = self.findChild(QtWidgets.QLineEdit, field)
            if input_field:
                data[field] = input_field.text()
        self.save_requested.emit(self.model.model_validate(data))


class CampaignMasterPlanApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Campaign Master")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.setup_ui()

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
        self.form = PydanticForm(CampaignPlan, self)
        self.central_widget.addWidget(self.form)
        self.central_widget.setCurrentWidget(self.form)

    def load_existing_campaign(self):
        self.label.setText("Loading an existing campaign...")
        file_dialog = QtWidgets.QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open Campaign Plan", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            # Load the campaign plan from the selected file
            # self.form = PydanticForm.from_existing(
            #     _CampaignPlan, load_obj(_CampaignPlan, file_path), self
            # )
            self.central_widget.addWidget(self.form)
            self.central_widget.setCurrentWidget(self.form)
        else:
            self.label.setText("No file selected.")
