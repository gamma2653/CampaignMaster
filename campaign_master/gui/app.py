# GUI application for managing tabletop RPG campaigns

from PySide6 import QtWidgets, QtCore


class CampaignMasterApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Campaign Master")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(layout)

        self.label = QtWidgets.QLabel("Welcome to Campaign Master!")
        layout.addWidget(self.label)

        self.new_btn = QtWidgets.QPushButton("Start New Campaign")
        layout.addWidget(self.new_btn)

        self.load_btn = QtWidgets.QPushButton("Load Existing Campaign")
        layout.addWidget(self.load_btn)

        self.new_btn.clicked.connect(self.start_new_campaign)
        self.load_btn.clicked.connect(self.load_existing_campaign)

    def start_new_campaign(self):
        self.label.setText("Starting a new campaign...")

    def load_existing_campaign(self):
        self.label.setText("Loading an existing campaign...")