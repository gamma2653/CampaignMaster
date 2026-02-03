"""
Entry point for CampaignMaster GUI executable.

This script is used by PyInstaller to create the GUI-only executable.
It excludes all web-related dependencies (FastAPI, uvicorn, React frontend).
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="CampaignMaster GUI - Desktop campaign management")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with verbose logging")
    args = parser.parse_args()

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
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
