import sys
import argparse

from PySide6 import QtCore, QtWidgets

from campaign_master.gui.app import CampaignMasterApp


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Campaign Master - Manage your tabletop RPG campaigns")
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with verbose logging')
    known_args, _ = parser.parse_known_args()

    if known_args.debug:
        QtCore.qDebug("Debug mode is enabled")

    app = QtWidgets.QApplication(sys.argv)
    window = CampaignMasterApp()
    window.show()
    app.exec()