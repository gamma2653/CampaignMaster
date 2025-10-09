import sys
import argparse

from PySide6 import QtCore, QtWidgets

from campaign_master.gui.app import CampaignMasterPlanApp
from campaign_master.web import app as web_app
from campaign_master.web import build as web_build

parser = argparse.ArgumentParser(description="Campaign Master - Manage your tabletop RPG campaigns")
parser.add_argument('--debug', action='store_true', help='Enable debug mode with verbose logging')
parser.add_argument('--gui', action='store_true', help='Launch the GUI application')
parser.add_argument('--web', action='store_true', help='Launch the web application')

if __name__ == "__main__":
    known_args, _ = parser.parse_known_args()   

    if known_args.debug and known_args.gui:
        QtCore.qDebug("Debug mode is enabled")
    if known_args.web:
        web_build.initialize_web_app()
        print("Web app is ready. Please run the FastAPI server to access it.")
        sys.exit(0)
    if known_args.gui:
        app = QtWidgets.QApplication(sys.argv)
        window = CampaignMasterPlanApp()
        window.show()
        app.exec()
    
    print("Exiting Campaign Master")
    sys.exit(0)