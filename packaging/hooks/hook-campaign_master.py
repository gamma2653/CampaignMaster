"""
PyInstaller hook for campaign_master package.

This hook ensures that all campaign_master submodules and data files
are properly collected when building the executable.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules of campaign_master
# This ensures dynamically imported modules are included
hiddenimports = collect_submodules("campaign_master")

# Collect data files (assets, templates, etc.)
datas = collect_data_files("campaign_master")
