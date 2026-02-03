#!/usr/bin/env python
"""
Build orchestration script for CampaignMaster executable packaging.

This script creates TWO separate executables:
1. CampaignMasterGUI.exe - Desktop GUI application (PySide6)
2. CampaignMasterWeb.exe - Web server application (FastAPI + React)

Usage:
    python packaging/build.py              # Build both executables
    python packaging/build.py --gui-only   # Build GUI executable only
    python packaging/build.py --web-only   # Build Web executable only
    python packaging/build.py --onefile    # Build as single-file executables
    python packaging/build.py --debug      # Include debug info
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.resolve()


def run_command(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=check)
    return result


def build_frontend(project_root: Path) -> bool:
    """Build the React frontend."""
    print("\n" + "=" * 60)
    print("Building React frontend...")
    print("=" * 60 + "\n")

    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    try:
        run_command([npm_cmd, "install"], cwd=project_root)
        run_command([npm_cmd, "run", "build"], cwd=project_root)

        dist_dir = project_root / "dist"
        if not dist_dir.exists():
            print("ERROR: Frontend build failed - dist directory not created")
            return False

        print("\nFrontend build completed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Frontend build failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("ERROR: npm not found. Please install Node.js and npm.")
        return False


def create_onefile_spec(project_root: Path, base_spec: Path, target: str) -> Path:
    """
    Create a modified spec file for onefile mode.

    Args:
        project_root: Project root directory
        base_spec: Path to the base spec file
        target: 'gui', 'web', or 'both'

    Returns:
        Path to the temporary onefile spec
    """
    onefile_spec_path = project_root / "packaging" / f"CampaignMaster_onefile_{target}.spec"
    spec_content = base_spec.read_text()

    # For onefile mode, we need to modify the EXE and remove COLLECT
    lines = spec_content.split("\n")
    new_lines = []

    skip_until_next_section = False
    in_exe_block = None  # Track which EXE block we're in

    for i, line in enumerate(lines):
        # Skip COLLECT sections entirely for onefile
        if "gui_coll = COLLECT(" in line or "web_coll = COLLECT(" in line:
            skip_until_next_section = True
            continue

        if skip_until_next_section:
            if line.strip() == ")":
                skip_until_next_section = False
            continue

        # Track EXE blocks
        if "gui_exe = EXE(" in line:
            in_exe_block = "gui"
        elif "web_exe = EXE(" in line:
            in_exe_block = "web"
        elif in_exe_block and line.strip() == ")":
            in_exe_block = None

        # Modify EXE configuration for onefile
        if in_exe_block:
            if "exclude_binaries=True" in line:
                line = line.replace("exclude_binaries=True", "exclude_binaries=False")
            elif "[]," in line and "scripts" in lines[i - 1]:
                # Change empty list to include binaries and datas
                if in_exe_block == "gui":
                    line = line.replace("[]", "gui_a.binaries + gui_a.datas")
                else:
                    line = line.replace("[]", "web_a.binaries + web_a.datas")

        new_lines.append(line)

    onefile_spec_path.write_text("\n".join(new_lines))
    return onefile_spec_path


def create_single_target_spec(project_root: Path, base_spec: Path, target: str, onefile: bool) -> Path:
    """
    Create a spec file for building only GUI or only Web.

    Args:
        project_root: Project root directory
        base_spec: Path to the base spec file
        target: 'gui' or 'web'
        onefile: Whether to create onefile build

    Returns:
        Path to the temporary spec file
    """
    spec_path = project_root / "packaging" / f"CampaignMaster_{target}_only.spec"
    spec_content = base_spec.read_text()

    lines = spec_content.split("\n")
    new_lines = []

    # Determine which sections to skip
    skip_prefix = "web_" if target == "gui" else "gui_"
    skip_section = False
    paren_depth = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check if we're starting a section to skip
        if stripped.startswith(skip_prefix) and "=" in stripped:
            skip_section = True
            paren_depth = 0

        if skip_section:
            paren_depth += line.count("(") - line.count(")")
            if paren_depth <= 0 and stripped.endswith(")"):
                skip_section = False
            continue

        # For onefile mode, modify EXE blocks
        if onefile:
            target_prefix = "gui_" if target == "gui" else "web_"
            if f"{target_prefix}exe = EXE(" in line:
                pass  # Keep the line
            elif "exclude_binaries=True" in line:
                line = line.replace("exclude_binaries=True", "exclude_binaries=False")
            elif "[]," in line and i > 0 and "scripts" in lines[i - 1]:
                if target == "gui":
                    line = line.replace("[]", "gui_a.binaries + gui_a.datas")
                else:
                    line = line.replace("[]", "web_a.binaries + web_a.datas")
            # Skip COLLECT for onefile
            elif f"{target_prefix}coll = COLLECT(" in line:
                skip_section = True
                paren_depth = 1
                continue

        new_lines.append(line)

    spec_path.write_text("\n".join(new_lines))
    return spec_path


def build_executables(
    project_root: Path,
    build_gui: bool = True,
    build_web: bool = True,
    onefile: bool = False,
    debug: bool = False,
) -> bool:
    """Build the executable(s) using PyInstaller."""

    targets = []
    if build_gui:
        targets.append("GUI")
    if build_web:
        targets.append("Web")

    mode = "onefile" if onefile else "onefolder"
    print("\n" + "=" * 60)
    print(f"Building {' and '.join(targets)} executable(s) ({mode} mode)...")
    print("=" * 60 + "\n")

    base_spec = project_root / "packaging" / "CampaignMaster.spec"
    if not base_spec.exists():
        print(f"ERROR: Spec file not found: {base_spec}")
        return False

    # Determine which spec to use
    if build_gui and build_web:
        if onefile:
            spec_file = create_onefile_spec(project_root, base_spec, "both")
        else:
            spec_file = base_spec
    elif build_gui:
        spec_file = create_single_target_spec(project_root, base_spec, "gui", onefile)
    else:
        spec_file = create_single_target_spec(project_root, base_spec, "web", onefile)

    cmd = ["pyinstaller", "--noconfirm", "--clean", "--distpath", str(project_root / "executables")]
    if debug:
        cmd.append("--log-level=DEBUG")
    cmd.append(str(spec_file))

    try:
        run_command(cmd, cwd=project_root)

        # Clean up temporary spec files
        for temp_spec in project_root.glob("packaging/CampaignMaster_*_only.spec"):
            temp_spec.unlink(missing_ok=True)
        for temp_spec in project_root.glob("packaging/CampaignMaster_onefile_*.spec"):
            temp_spec.unlink(missing_ok=True)

        # Verify outputs
        success = True

        if build_gui:
            if onefile:
                gui_path = project_root / "executables" / "CampaignMasterGUI.exe"
            else:
                gui_path = project_root / "executables" / "CampaignMasterGUI" / "CampaignMasterGUI.exe"

            if gui_path.exists():
                print(f"\nGUI executable created: {gui_path}")
                print(f"  Size: {gui_path.stat().st_size / (1024 * 1024):.2f} MB")
            else:
                print("ERROR: GUI executable was not created")
                success = False

        if build_web:
            if onefile:
                web_path = project_root / "executables" / "CampaignMasterWeb.exe"
            else:
                web_path = project_root / "executables" / "CampaignMasterWeb" / "CampaignMasterWeb.exe"

            if web_path.exists():
                print(f"\nWeb executable created: {web_path}")
                print(f"  Size: {web_path.stat().st_size / (1024 * 1024):.2f} MB")
            else:
                print("ERROR: Web executable was not created")
                success = False

        return success

    except subprocess.CalledProcessError as e:
        print(f"ERROR: PyInstaller failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("ERROR: PyInstaller not found. Install with: poetry add --group build pyinstaller")
        return False


def clean_build_artifacts(project_root: Path):
    """Clean previous build artifacts."""
    print("\nCleaning previous build artifacts...")

    dirs_to_clean = [
        project_root / "build",
        project_root / "executables" / "CampaignMasterGUI",
        project_root / "executables" / "CampaignMasterWeb",
    ]

    files_to_clean = [
        project_root / "executables" / "CampaignMasterGUI.exe",
        project_root / "executables" / "CampaignMasterWeb.exe",
    ]

    # Add temporary spec files
    files_to_clean.extend(project_root.glob("packaging/CampaignMaster_*_only.spec"))
    files_to_clean.extend(project_root.glob("packaging/CampaignMaster_onefile_*.spec"))

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"  Removing: {dir_path}")
            shutil.rmtree(dir_path)

    for file_path in files_to_clean:
        if isinstance(file_path, Path) and file_path.exists():
            print(f"  Removing: {file_path}")
            file_path.unlink()


def main():
    parser = argparse.ArgumentParser(
        description="Build CampaignMaster executables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python packaging/build.py                    # Build both GUI and Web (onefolder)
    python packaging/build.py --onefile          # Build both as single executables
    python packaging/build.py --gui-only         # Build only GUI executable
    python packaging/build.py --web-only         # Build only Web executable
    python packaging/build.py --skip-frontend    # Skip frontend build (for GUI-only)
    python packaging/build.py --debug            # Include debug information
    python packaging/build.py --clean            # Clean and rebuild

Output:
    Onefolder mode:
        executables/CampaignMasterGUI/CampaignMasterGUI.exe
        executables/CampaignMasterWeb/CampaignMasterWeb.exe

    Onefile mode:
        executables/CampaignMasterGUI.exe
        executables/CampaignMasterWeb.exe
        """,
    )

    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "--gui-only",
        action="store_true",
        help="Build only the GUI executable (excludes web dependencies)",
    )
    target_group.add_argument(
        "--web-only",
        action="store_true",
        help="Build only the Web executable (excludes GUI dependencies)",
    )

    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Build single-file executables (larger but self-contained)",
    )
    parser.add_argument(
        "--onefolder",
        action="store_true",
        default=True,
        help="Build folder distributions (default, faster builds)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Include debug information in build",
    )
    parser.add_argument(
        "--skip-frontend",
        action="store_true",
        help="Skip frontend build (use existing dist/)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building",
    )

    args = parser.parse_args()

    project_root = get_project_root()
    print(f"Project root: {project_root}")

    # Determine what to build
    build_gui = not args.web_only
    build_web = not args.gui_only
    onefile = args.onefile

    # Clean if requested
    if args.clean:
        clean_build_artifacts(project_root)

    # Build frontend if building web and not skipped
    if build_web and not args.skip_frontend:
        if not build_frontend(project_root):
            print("\nFrontend build failed. Use --skip-frontend to skip this step.")
            sys.exit(1)
    elif build_web:
        print("\nSkipping frontend build (using existing dist/)")
        dist_dir = project_root / "dist"
        if not dist_dir.exists():
            print("WARNING: dist/ directory does not exist. Frontend assets will be missing.")
    elif args.gui_only:
        print("\nSkipping frontend build (GUI-only mode)")

    # Build executables
    if not build_executables(project_root, build_gui=build_gui, build_web=build_web, onefile=onefile, debug=args.debug):
        print("\nExecutable build failed.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)

    if onefile:
        if build_gui:
            print(f"\nGUI: executables/CampaignMasterGUI.exe")
        if build_web:
            print(f"Web: executables/CampaignMasterWeb.exe")
    else:
        if build_gui:
            print(f"\nGUI: executables/CampaignMasterGUI/CampaignMasterGUI.exe")
        if build_web:
            print(f"Web: executables/CampaignMasterWeb/CampaignMasterWeb.exe")

    print("\nUsage:")
    if build_gui:
        if onefile:
            print("  GUI: .\\executables\\CampaignMasterGUI.exe")
        else:
            print("  GUI: .\\executables\\CampaignMasterGUI\\CampaignMasterGUI.exe")
    if build_web:
        if onefile:
            print("  Web: .\\executables\\CampaignMasterWeb.exe --port 8000")
        else:
            print("  Web: .\\executables\\CampaignMasterWeb\\CampaignMasterWeb.exe --port 8000")


if __name__ == "__main__":
    main()
