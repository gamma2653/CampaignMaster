import argparse
import sys

parser = argparse.ArgumentParser(description="Campaign Master - Manage your tabletop RPG campaigns")
parser.add_argument("--debug", action="store_true", help="Enable debug mode with verbose logging")
parser.add_argument("--gui", action="store_true", help="Launch the GUI application")
parser.add_argument("--web", action="store_true", help="Launch the web application")
parser.add_argument(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Host for the web application (default: 127.0.0.1)",
)
parser.add_argument(
    "--port",
    type=int,
    default=8000,
    help="Port for the web application (default: 8000)",
)

if __name__ == "__main__":
    known_args, _ = parser.parse_known_args()

    if known_args.web:
        from campaign_master.web import app as web_app
        from campaign_master.web import util

        util.build()
        if input("Would you like to run the web server in debug mode now? (y/n): ").strip().lower() not in ("y", "yes", "1"):
            sys.exit(0)
        web_app.run_dev(host=known_args.host, port=known_args.port, debug=known_args.debug)
        # else:
        # This case should be handled by an external service like nginx in production
        sys.exit(0)
    if known_args.gui:
        from PySide6 import QtWidgets

        from campaign_master.content.database import create_db_and_tables, create_example_data

        create_db_and_tables()
        create_example_data()
        from campaign_master.gui.main_window import CampaignMasterWindow
        from campaign_master.gui.themes import ThemeManager

        app = QtWidgets.QApplication(sys.argv)

        # Initialize dark theme
        theme_manager = ThemeManager(app)
        theme_manager.load_theme()

        window = CampaignMasterWindow()
        window.show()
        app.exec()

    print("Exiting Campaign Master")
    sys.exit(0)
