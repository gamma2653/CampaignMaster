from typing import Optional, cast

from PySide6 import QtWidgets

from ...content import api as content_api
from ...content import planning


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
            str(id_value)
            if id_value
            else str(content_api.generate_id(prefix=self.model_type._default_prefix))
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


class StrListEdit(QtWidgets.QWidget):
    """
    A widget to edit a list of strings.
    """

    def __init__(self, items: Optional[list[str]] = None, parent=None):
        super().__init__(parent)
        self.items = items if items else []
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.addItems(self.items)

        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        self.add_button.clicked.connect(self.add_item)
        self.remove_button.clicked.connect(self.remove_item)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)

        self.setLayout(layout)

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
        return [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]


class IDListEdit(QtWidgets.QWidget):
    """
    A widget to edit a list of IDs.
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
        layout = QtWidgets.QVBoxLayout()

        self.list_widget = QtWidgets.QListWidget()
        for id_value in self.ids:
            self.list_widget.addItem(str(id_value))

        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        self.add_button.clicked.connect(self.add_id)
        self.remove_button.clicked.connect(self.remove_id)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)

        self.setLayout(layout)

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
        return [
            planning.ID.from_str(self.list_widget.item(i).text())
            for i in range(self.list_widget.count())
        ]


class ListEdit[T: planning.Object](QtWidgets.QWidget):
    """
    A widget to edit a list of objects.
    """

    def __init__(
        self,
        model_type: type[T],
        objects: Optional[list[T]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.model_type = model_type
        self.objects = objects if objects else []
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.list_widget = QtWidgets.QListWidget()
        for object_ in self.objects:
            self.list_widget.addItem(str(object_.obj_id))

        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        self.add_button.clicked.connect(self.add_object)
        self.remove_button.clicked.connect(self.remove_object)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)

        self.setLayout(layout)

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
                QtWidgets.QDialogButtonBox.StandardButton.Ok
                | QtWidgets.QDialogButtonBox.StandardButton.Cancel
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
                self.objects.append(form_data)
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
                    self.objects.append(obj)

    def remove_object(self):
        selected_items_widgets = self.list_widget.selectedItems()
        if not selected_items_widgets:
            return
        for item_widget in selected_items_widgets:
            item = self.objects[self.list_widget.row(item_widget)]
            self.objects.remove(item)
            self.list_widget.takeItem(self.list_widget.row(item_widget))

    def get_objects(self) -> list[T]:
        """Return the list of objects."""
        return self.objects


class RuleEdit(QtWidgets.QWidget):
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
        layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Rule, self.rule.obj_id if self.rule else None)
        self.description = QtWidgets.QTextEdit(
            self.rule.description if self.rule else ""
        )
        self.effect = QtWidgets.QTextEdit(self.rule.effect if self.rule else "")
        self.components = StrListEdit(self.rule.components if self.rule else [])

        self.setLayout(layout)
        self.update_layout()

    def update_layout(self):
        layout = cast(QtWidgets.QFormLayout, self.layout())
        layout.addRow("ID:", self.obj_id)
        layout.addRow("Description:", self.description)
        layout.addRow("Effect:", self.effect)
        layout.addRow("Components:", self.components)

    def export_content(self) -> planning.Rule:
        """Export the form data as a Rule object."""
        return planning.Rule(
            obj_id=self.obj_id.get_id() if self.obj_id.get_id() else planning.ID(),
            description=self.description.toPlainText(),
            effect=self.effect.toPlainText(),
            components=self.components.get_items(),
        )


class ObjectiveEdit(QtWidgets.QWidget):
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
        layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(
            planning.Objective, self.objective.obj_id if self.objective else None
        )
        self.description = QtWidgets.QTextEdit(
            self.objective.description if self.objective else ""
        )
        self.components = StrListEdit(
            self.objective.components if self.objective else []
        )
        self.prerequisites = IDListEdit(
            planning.Objective, self.objective.prerequisites if self.objective else []
        )

        self.setLayout(layout)
        self.update_layout()

    def update_layout(self):
        layout = cast(QtWidgets.QFormLayout, self.layout())
        layout.addRow("ID:", self.obj_id)
        layout.addRow("Description:", self.description)
        layout.addRow("Components:", self.components)
        layout.addRow("Prerequisites:", self.prerequisites)

    def export_content(self) -> planning.Objective:
        """Export the form data as an Objective object."""
        return planning.Objective(
            obj_id=self.obj_id.get_id() if self.obj_id.get_id() else planning.ID(),
            description=self.description.toPlainText(),
            components=self.components.get_items(),
            prerequisites=self.prerequisites.get_ids(),
        )


class PointEdit(QtWidgets.QWidget):
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
        layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(
            planning.Point, self.point.obj_id if self.point else None
        )
        self.name = QtWidgets.QLineEdit(self.point.name if self.point else "")
        self.description = QtWidgets.QTextEdit(
            self.point.description if self.point else ""
        )
        self.objective = IDSelect(planning.Objective)
        self.setLayout(layout)
        self.update_layout()

    def update_layout(self):
        layout = cast(QtWidgets.QFormLayout, self.layout())
        layout.addRow("ID:", self.obj_id)
        layout.addRow("Name:", self.name)
        layout.addRow("Description:", self.description)
        layout.addRow("Objective ID:", self.objective)

    def export_content(self) -> planning.Point:
        """Export the form data as a Point object."""
        # Get objective ID, handling empty selection
        objective_id = None
        if self.objective.currentText():
            objective_id = self.objective.get_selected_object()

        return planning.Point(
            obj_id=self.obj_id.get_id() if self.obj_id.get_id() else planning.ID(),
            name=self.name.text(),
            description=self.description.toPlainText(),
            objective=objective_id,
        )


class SegmentEdit(QtWidgets.QWidget):
    """
    Contains a form to populate/edit a Segment object.

    Fields:
    name: str
    description: str
    start: Point
    end: Point
    """

    def __init__(self, segment: Optional[planning.Segment] = None, parent=None):
        super().__init__(parent)
        self.segment = segment
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(
            planning.Segment, self.segment.obj_id if self.segment else None
        )
        self.name = QtWidgets.QLineEdit(self.segment.name if self.segment else "")
        self.description = QtWidgets.QTextEdit(
            self.segment.description if self.segment else ""
        )
        self.start = PointEdit(self.segment.start if self.segment else None)
        self.end = PointEdit(self.segment.end if self.segment else None)
        self.setLayout(layout)
        self.update_layout()

    def update_layout(self):
        layout = cast(QtWidgets.QFormLayout, self.layout())
        layout.addRow("ID:", self.obj_id)
        layout.addRow("Name:", self.name)
        layout.addRow("Description:", self.description)
        layout.addRow("Start Point:", self.start)
        layout.addRow("End Point:", self.end)

    def export_content(self) -> planning.Segment:
        """Export the form data as a Segment object."""
        # Note: The GUI uses PointEdit widgets but the model expects ID references
        # For now, we'll export the Point objects and their IDs
        start_point = self.start.export_content()
        end_point = self.end.export_content()

        return planning.Segment(
            obj_id=self.obj_id.get_id() if self.obj_id.get_id() else planning.ID(),
            name=self.name.text(),
            description=self.description.toPlainText(),
            start=start_point.obj_id,
            end=end_point.obj_id,
        )


class ArcEdit(QtWidgets.QWidget):
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
        layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Arc, self.arc.obj_id if self.arc else None)
        self.name = QtWidgets.QLineEdit(self.arc.name if self.arc else "")
        self.description = QtWidgets.QTextEdit(self.arc.description if self.arc else "")
        self.segments = QtWidgets.QListWidget()
        if self.arc:
            for segment in self.arc.segments:
                item = QtWidgets.QListWidgetItem(segment.name)
                self.segments.addItem(item)
        self.setLayout(layout)
        self.update_layout()

    def update_layout(self):
        layout = cast(QtWidgets.QFormLayout, self.layout())
        layout.addRow("ID:", self.obj_id)
        layout.addRow("Name:", self.name)
        layout.addRow("Description:", self.description)
        layout.addRow("Segments:", self.segments)

    def export_content(self) -> planning.Arc:
        """Export the form data as an Arc object."""
        # Note: The GUI uses a simple QListWidget which doesn't properly manage segments
        # For now, we'll export with an empty segments list
        # A proper implementation would need a ListEdit widget for segments
        return planning.Arc(
            obj_id=self.obj_id.get_id() if self.obj_id.get_id() else planning.ID(),
            name=self.name.text(),
            description=self.description.toPlainText(),
            segments=[],  # TODO: Properly handle segments list
        )


class MapEdit[K, V](QtWidgets.QWidget):
    """
    A widget to edit a mapping of strings to strings.
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
        layout = QtWidgets.QVBoxLayout()
        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(self.k_v_labels)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.populate_table()

        self.add_button = QtWidgets.QPushButton("Add")
        self.remove_button = QtWidgets.QPushButton("Remove")

        self.add_button.clicked.connect(self.add_entry)
        self.remove_button.clicked.connect(self.remove_entry)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)

        layout.addWidget(self.table_widget)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def populate_table(self):
        self.table_widget.setRowCount(0)
        for key, value in self.map_.items():
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            self.table_widget.setItem(
                row_position, 0, QtWidgets.QTableWidgetItem(str(key))
            )
            self.table_widget.setItem(
                row_position, 1, QtWidgets.QTableWidgetItem(str(value))
            )

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


class ItemEdit(QtWidgets.QWidget):
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
        layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(planning.Item, self.item.obj_id if self.item else None)
        self.name = QtWidgets.QLineEdit(self.item.name if self.item else "")
        self.type_ = QtWidgets.QLineEdit(self.item.type_ if self.item else "")
        self.description = QtWidgets.QTextEdit(
            self.item.description if self.item else ""
        )
        self.properties = MapEdit[str, str](self.item.properties if self.item else {})

        self.setLayout(layout)
        self.update_layout()

    def update_layout(self):
        layout = cast(QtWidgets.QFormLayout, self.layout())
        layout.addRow("ID:", self.obj_id)
        layout.addRow("Name:", self.name)
        layout.addRow("Type:", self.type_)
        layout.addRow("Description:", self.description)
        layout.addRow("Properties:", self.properties)

    def export_content(self) -> planning.Item:
        """Export the form data as an Item object."""
        return planning.Item(
            obj_id=self.obj_id.get_id() if self.obj_id.get_id() else planning.ID(),
            name=self.name.text(),
            type_=self.type_.text(),
            description=self.description.toPlainText(),
            properties=self.properties.get_map(),
        )


class CharacterEdit(QtWidgets.QWidget):
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
        layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(
            planning.Character, self.character.obj_id if self.character else None
        )
        self.name = QtWidgets.QLineEdit(self.character.name if self.character else "")
        self.role = QtWidgets.QLineEdit(self.character.role if self.character else "")
        self.backstory = QtWidgets.QTextEdit(
            self.character.backstory if self.character else ""
        )
        self.attributes = MapEdit[str, int](
            self.character.attributes if self.character else {}
        )
        self.skills = MapEdit[str, int](self.character.skills if self.character else {})
        self.storylines = IDListEdit(
            planning.Arc, self.character.storylines if self.character else []
        )
        self.inventory = IDListEdit(
            planning.Item, self.character.inventory if self.character else []
        )

        self.setLayout(layout)
        self.update_layout()

    def update_layout(self):
        layout = cast(QtWidgets.QFormLayout, self.layout())
        layout.addRow("ID:", self.obj_id)
        layout.addRow("Name:", self.name)
        layout.addRow("Role:", self.role)
        layout.addRow("Backstory:", self.backstory)
        layout.addRow("Attributes:", self.attributes)
        layout.addRow("Skills:", self.skills)
        layout.addRow("Storylines:", self.storylines)
        layout.addRow("Inventory:", self.inventory)

    def export_content(self) -> planning.Character:
        """Export the form data as a Character object."""
        # Note: MapEdit.get_map() returns dict[str, str], but we need dict[str, int] for attributes and skills
        # Converting the values to int
        attributes_dict = {
            k: int(v) if v.isdigit() else 0
            for k, v in self.attributes.get_map().items()
        }
        skills_dict = {
            k: int(v) if v.isdigit() else 0 for k, v in self.skills.get_map().items()
        }

        return planning.Character(
            obj_id=self.obj_id.get_id() if self.obj_id.get_id() else planning.ID(),
            name=self.name.text(),
            role=self.role.text(),
            backstory=self.backstory.toPlainText(),
            attributes=attributes_dict,
            skills=skills_dict,
            storylines=self.storylines.get_ids(),
            inventory=self.inventory.get_ids(),
        )


class LocationEdit(QtWidgets.QWidget):
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
        layout = QtWidgets.QFormLayout()
        self.obj_id = IDDisplay(
            planning.Location, self.location.obj_id if self.location else None
        )
        self.name = QtWidgets.QLineEdit(self.location.name if self.location else "")
        self.description = QtWidgets.QTextEdit(
            self.location.description if self.location else ""
        )
        self.neighboring_locations = IDListEdit(
            planning.Location,
            self.location.neighboring_locations if self.location else [],
        )
        self._latitude = QtWidgets.QLineEdit(
            str(self.location.coords[0])
            if self.location and self.location.coords
            else ""
        )
        self._longitude = QtWidgets.QLineEdit(
            str(self.location.coords[1])
            if self.location and self.location.coords
            else ""
        )
        self._altitude = QtWidgets.QLineEdit(
            str(self.location.coords[2])
            if self.location and self.location.coords and len(self.location.coords) == 3
            else ""
        )

        self.setLayout(layout)
        self.update_layout()

    def update_layout(self):
        layout = cast(QtWidgets.QFormLayout, self.layout())
        layout.addRow("ID:", self.obj_id)
        layout.addRow("Name:", self.name)
        layout.addRow("Description:", self.description)
        layout.addRow("Neighboring Locations:", self.neighboring_locations)
        layout.addRow("Latitude:", self._latitude)
        layout.addRow("Longitude:", self._longitude)
        layout.addRow("Altitude (optional):", self._altitude)

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
            obj_id=self.obj_id.get_id() if self.obj_id.get_id() else planning.ID(),
            name=self.name.text(),
            description=self.description.toPlainText(),
            neighboring_locations=self.neighboring_locations.get_ids(),
            coords=coords,
        )


class CampaignPlanEdit(QtWidgets.QWidget):
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

    def __init__(
        self, campaign_plan: Optional[planning.CampaignPlan] = None, parent=None
    ):
        super().__init__(parent)
        self.campaign_plan = campaign_plan
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QFormLayout()

        self.obj_id = IDDisplay(
            planning.CampaignPlan,
            self.campaign_plan.obj_id if self.campaign_plan else None,
        )
        self.title = QtWidgets.QLineEdit(
            self.campaign_plan.title if self.campaign_plan else ""
        )
        self.version = QtWidgets.QTextEdit(
            self.campaign_plan.version if self.campaign_plan else ""
        )
        self.setting = QtWidgets.QTextEdit(
            self.campaign_plan.setting if self.campaign_plan else ""
        )
        self.summary = QtWidgets.QTextEdit(
            self.campaign_plan.summary if self.campaign_plan else ""
        )
        self.storypoints = ListEdit(
            planning.Point, self.campaign_plan.storypoints if self.campaign_plan else []
        )
        self.storyline = ListEdit(
            planning.Arc, self.campaign_plan.storyline if self.campaign_plan else []
        )
        self.items = ListEdit(
            planning.Item, self.campaign_plan.items if self.campaign_plan else []
        )
        self.rules = ListEdit(
            planning.Rule, self.campaign_plan.rules if self.campaign_plan else []
        )
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
        # Further widgets for objectives, arcs, items, characters, locations can be added here.

        self.setLayout(layout)
        self.update_layout()

    def update_layout(self):
        layout = cast(QtWidgets.QFormLayout, self.layout())
        layout.addRow("ID:", self.obj_id)
        layout.addRow("Title:", self.title)
        layout.addRow("Version:", self.version)
        layout.addRow("Setting:", self.setting)
        layout.addRow("Summary:", self.summary)
        layout.addRow("Story Points:", self.storypoints)
        layout.addRow("Storyline Arcs:", self.storyline)
        layout.addRow("Items:", self.items)
        layout.addRow("Rules:", self.rules)
        layout.addRow("Objectives:", self.objectives)
        layout.addRow("Characters:", self.characters)
        layout.addRow("Locations:", self.locations)
