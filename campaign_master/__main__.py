import sys
import argparse
import pathlib

import uvicorn
from PySide6 import QtCore, QtWidgets

from campaign_master.gui.app import CampaignMasterPlanApp
from campaign_master.web import app

parser = argparse.ArgumentParser(description="Campaign Master - Manage your tabletop RPG campaigns")
parser.add_argument('--debug', action='store_true', help='Enable debug mode with verbose logging')
parser.add_argument('--gui', action='store_true', help='Launch the GUI application')
parser.add_argument('--web', action='store_true', help='Launch the web application')
parser.add_argument('--host', type=str, default='127.0.0.1', help='Host for the web application (default: 127.0.0.1)')
parser.add_argument('--port', type=int, default=8000, help='Port for the web application (default: 8000)')

if __name__ == "__main__":
    known_args, _ = parser.parse_known_args()   

    if known_args.debug and known_args.gui:
        QtCore.qDebug("Debug mode is enabled")
    if known_args.web:
        app.build()
        if input("Would you like to run the web server now? (y/n): ").strip().lower() not in ('y', 'yes', '1'):
            print("Exiting after build.")
            sys.exit(0)
        if known_args.debug:
            app.run_dev()
            # from fastapi.staticfiles import StaticFiles
            # static_path = pathlib.Path(__file__).parent.parent / "dist" / "static"
            # print(f"Serving static files from: {static_path.resolve(strict=True)}")
            # app.app.mount("/static", StaticFiles(directory=static_path), name="static")
            # print("Debug mode is enabled.")
        # uvicorn.run(app.app, host=known_args.host, port=known_args.port, log_level="debug" if known_args.debug else "info")
        sys.exit(0)
    if known_args.gui:
        app = QtWidgets.QApplication(sys.argv)
        window = CampaignMasterPlanApp()
        window.show()
        app.exec()
    
    print("Exiting Campaign Master")
    sys.exit(0)