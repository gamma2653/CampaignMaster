"""
Entry point for CampaignMaster Web executable.

This script is used by PyInstaller to create the Web-only executable.
It excludes all GUI-related dependencies (PySide6).
The React frontend is bundled with the executable.
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="CampaignMaster Web - Browser-based campaign management")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with verbose logging")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for the web server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the web server (default: 8000)",
    )
    args = parser.parse_args()

    from campaign_master.web import app as web_app

    print(f"Starting CampaignMaster Web on http://{args.host}:{args.port}")
    web_app.run_dev(host=args.host, port=args.port, debug=args.debug)
    sys.exit(0)


if __name__ == "__main__":
    main()
