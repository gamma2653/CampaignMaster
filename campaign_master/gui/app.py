# GUI application for managing tabletop RPG campaigns

from typing import Optional, cast
from ..content.planning import TypeAdapter, ObjectType, Object, _CampaignPlan

from PySide6 import QtWidgets


class ModelListView(QtWidgets.QWidget):
    """
    A list view to display and manage a list of Pydantic model instances.
    """

    def __init__(self, model: TypeAdapter[Object], parent=None):
        super().__init__(parent)
        self.model = model
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.list_widget = QtWidgets.QListWidget(self)
        layout.addWidget(self.list_widget)

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
        # form.connect(form.save, self.on_item_added)

    def on_item_added(self, object: ObjectType):
        self.list_widget.addItem(str(object))

    def remove_item(self):
        # Logic to remove the selected item
        pass
    

class PydanticForm(QtWidgets.QWidget):
    """
    A form to display and edit Pydantic model fields.
    """

    def __init__(self, model: TypeAdapter[Object], parent=None):
        super().__init__(parent)
        self.is_subform = isinstance(parent, PydanticForm)
        self.model = model
        self.init_ui()

    @property
    def annotations(self):
        return self.model._type.__annotations__
    
    @property
    def parent_form(self) -> Optional["PydanticForm"]:
        if self.is_subform:
            return cast("PydanticForm", self.parent())
        return None


    def init_ui(self):
        """
        Precondition: self.fields is a list of field names in the Pydantic model.
        """
        print(f"Initializing UI with fields: {self.annotations.keys()}")
        layout = QtWidgets.QFormLayout(self)
        for field in self.annotations.keys():

            label = QtWidgets.QLabel(field.title(), self)
            input_field = self.create_input_field(field, self.annotations[field])
            layout.addRow(label, input_field)
        self.setLayout(layout)


    def create_input_field(self, field_name, field_type):
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
            return ModelListView(TypeAdapter(field_type.__args__[0]), self)
            
        return QtWidgets.QLineEdit(self)
    
    @classmethod
    def from_existing(cls, model_instance, parent=None):
        """
        Create a PydanticForm from an existing Pydantic model instance.
        """
        instance = cls(TypeAdapter(model_instance), parent)
        # Populate fields with existing data
        for field in instance.annotations.keys():
            value = getattr(model_instance, field, "")
            input_field = instance.findChild(QtWidgets.QLineEdit, field)
            if input_field:
                input_field.setText(str(value))
        return instance
    
    def save(self):
        """
        Save the current form data back to the Pydantic model instance.
        """
        data = {}
        for field in self.annotations.keys():
            input_field = self.findChild(QtWidgets.QLineEdit, field)
            if input_field:
                data[field] = input_field.text()
        return self.model.validate_python(data)
    

    
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
        self.form = PydanticForm(_CampaignPlan, self)
        self.central_widget.addWidget(self.form)
        self.central_widget.setCurrentWidget(self.form)

    def load_existing_campaign(self):
        self.label.setText("Loading an existing campaign...")
        file_dialog = QtWidgets.QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Open Campaign Plan", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                data = file.read()
            campaign_plan = _CampaignPlan.validate_python(data)
            self.form = PydanticForm.from_existing(campaign_plan, self)
            self.central_widget.addWidget(self.form)
            self.central_widget.setCurrentWidget(self.form)
        else:
            self.label.setText("No file selected.")
