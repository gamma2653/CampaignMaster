# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for CampaignMaster.

This spec file creates TWO separate executables:
1. CampaignMasterGUI.exe - Desktop GUI application (PySide6)
2. CampaignMasterWeb.exe - Web server application (FastAPI + React)

Each executable only includes dependencies needed for its mode,
resulting in smaller, more focused distributions.

Usage:
    pyinstaller packaging/CampaignMaster.spec

Or use the build script:
    python packaging/build.py
    python packaging/build.py --gui-only
    python packaging/build.py --web-only
"""

import sys
from pathlib import Path

# Project root directory (SPECPATH is a string in PyInstaller)
SPEC_DIR = Path(SPECPATH)
PROJECT_ROOT = SPEC_DIR.parent.resolve()

# Entry points
GUI_ENTRY_POINT = str(SPEC_DIR / "entry_gui.py")
WEB_ENTRY_POINT = str(SPEC_DIR / "entry_web.py")

# ============================================================================
# SHARED CONFIGURATION
# ============================================================================

# Common hidden imports (shared between both executables)
common_hiddenimports = [
    # Pydantic and related
    "pydantic",
    "pydantic_settings",
    "pydantic_core",
    "pydantic.deprecated.decorator",
    "pydantic.v1",
    # SQLAlchemy
    "sqlalchemy",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.ext.asyncio",
    "aiosqlite",
    # Standard library modules sometimes missed
    "multiprocessing",
    "asyncio",
    "concurrent.futures",
    "json",
    "logging.config",
    # Campaign master core modules
    "campaign_master",
    "campaign_master.content",
    "campaign_master.content.api",
    "campaign_master.content.database",
    "campaign_master.content.models",
    "campaign_master.content.planning",
    "campaign_master.content.settings",
    "campaign_master.util",
]

# Common exclusions
common_excludes = [
    "tkinter",
    "matplotlib",
    "numpy",
    "scipy",
    "pandas",
    "PIL",
    "cv2",
    "tensorflow",
    "torch",
    "pytest",
    "black",
    "isort",
    "_pytest",
]

# ============================================================================
# GUI EXECUTABLE CONFIGURATION
# ============================================================================

gui_datas = [
    # GUI assets (icons, images)
    (str(PROJECT_ROOT / "campaign_master" / "assets"), "campaign_master/assets"),
]

gui_hiddenimports = common_hiddenimports + [
    # PySide6 / Qt
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    # Campaign master GUI modules
    "campaign_master.gui",
    "campaign_master.gui.main_window",
    "campaign_master.gui.themes",
    "campaign_master.gui.widgets",
]

gui_excludes = common_excludes + [
    # Exclude web-related packages for GUI build
    "uvicorn",
    "fastapi",
    "starlette",
    "httptools",
    "websockets",
    "python_multipart",
    "email_validator",
    "anthropic",
    "openai",
    "httpx",
]

# GUI Analysis
gui_a = Analysis(
    [GUI_ENTRY_POINT],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=gui_datas,
    hiddenimports=gui_hiddenimports,
    hookspath=[str(PROJECT_ROOT / "packaging" / "hooks")],
    hooksconfig={},
    runtime_hooks=[],
    excludes=gui_excludes,
    noarchive=False,
    optimize=0,
)

gui_pyz = PYZ(gui_a.pure)

gui_exe = EXE(
    gui_pyz,
    gui_a.scripts,
    [],
    exclude_binaries=True,
    name="CampaignMasterGUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_ROOT / "campaign_master" / "assets" / "images" / "icons" / "book2.ico")
    if (PROJECT_ROOT / "campaign_master" / "assets" / "images" / "icons" / "book2.ico").exists()
    else None,
)

gui_coll = COLLECT(
    gui_exe,
    gui_a.binaries,
    gui_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CampaignMasterGUI",
)

# ============================================================================
# WEB EXECUTABLE CONFIGURATION
# ============================================================================

web_datas = [
    # React frontend build output
    (str(PROJECT_ROOT / "dist"), "dist"),
]

web_hiddenimports = common_hiddenimports + [
    # FastAPI / Uvicorn / Starlette
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.protocols.websockets.wsproto_impl",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
    "starlette",
    "starlette.middleware",
    "starlette.middleware.cors",
    "starlette.responses",
    "starlette.routing",
    "fastapi",
    "fastapi.responses",
    "fastapi.staticfiles",
    # Form handling
    "python_multipart",
    "email_validator",
    # AI providers (dynamically imported based on config)
    "anthropic",
    "openai",
    "httpx",
    "httpx._transports",
    "httpx._transports.default",
    # Authentication
    "bcrypt",
    # Campaign master web modules
    "campaign_master.web",
    "campaign_master.web.app",
    "campaign_master.web.api",
    "campaign_master.web.ai_api",
    "campaign_master.web.auth",
    "campaign_master.web.settings",
]

web_excludes = common_excludes + [
    # Exclude GUI-related packages for Web build
    "PySide6",
    "PySide6_Addons",
    "PySide6_Essentials",
    "shiboken6",
]

# Web Analysis
web_a = Analysis(
    [WEB_ENTRY_POINT],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=web_datas,
    hiddenimports=web_hiddenimports,
    hookspath=[str(PROJECT_ROOT / "packaging" / "hooks")],
    hooksconfig={},
    runtime_hooks=[],
    excludes=web_excludes,
    noarchive=False,
    optimize=0,
)

web_pyz = PYZ(web_a.pure)

web_exe = EXE(
    web_pyz,
    web_a.scripts,
    [],
    exclude_binaries=True,
    name="CampaignMasterWeb",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console needed for web server output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(PROJECT_ROOT / "campaign_master" / "assets" / "images" / "icons" / "book2.ico")
    if (PROJECT_ROOT / "campaign_master" / "assets" / "images" / "icons" / "book2.ico").exists()
    else None,
)

web_coll = COLLECT(
    web_exe,
    web_a.binaries,
    web_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CampaignMasterWeb",
)
