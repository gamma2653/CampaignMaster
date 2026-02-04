"""Tests for PyInstaller packaging and build process."""

import ast
import subprocess
import sys
from pathlib import Path

import pytest


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.resolve()


PROJECT_ROOT = get_project_root()
PACKAGING_DIR = PROJECT_ROOT / "packaging"
SPEC_FILE = PACKAGING_DIR / "CampaignMaster.spec"


class TestBuildModuleImport:
    """Tests for importing the build module."""

    def test_build_module_imports(self):
        """The build module should import without errors."""
        sys.path.insert(0, str(PACKAGING_DIR))
        try:
            import build

            assert hasattr(build, "main")
            assert hasattr(build, "build_executables")
            assert hasattr(build, "build_frontend")
            assert hasattr(build, "get_project_root")
        finally:
            sys.path.remove(str(PACKAGING_DIR))

    def test_entry_gui_imports(self):
        """The GUI entry point should import without errors."""
        sys.path.insert(0, str(PACKAGING_DIR))
        try:
            import entry_gui

            assert hasattr(entry_gui, "main")
        finally:
            sys.path.remove(str(PACKAGING_DIR))

    def test_entry_web_imports(self):
        """The web entry point should import without errors."""
        sys.path.insert(0, str(PACKAGING_DIR))
        try:
            import entry_web

            assert hasattr(entry_web, "main")
        finally:
            sys.path.remove(str(PACKAGING_DIR))


class TestSpecFile:
    """Tests for the PyInstaller spec file."""

    def test_spec_file_exists(self):
        """The spec file should exist."""
        assert SPEC_FILE.exists(), f"Spec file not found: {SPEC_FILE}"

    def test_spec_file_is_valid_python(self):
        """The spec file should be valid Python syntax."""
        spec_content = SPEC_FILE.read_text()
        try:
            ast.parse(spec_content)
        except SyntaxError as e:
            pytest.fail(f"Spec file has invalid Python syntax: {e}")

    def test_spec_defines_gui_executable(self):
        """The spec file should define a GUI executable."""
        spec_content = SPEC_FILE.read_text()
        assert "gui_exe = EXE(" in spec_content
        assert 'name="CampaignMasterGUI"' in spec_content

    def test_spec_defines_web_executable(self):
        """The spec file should define a Web executable."""
        spec_content = SPEC_FILE.read_text()
        assert "web_exe = EXE(" in spec_content
        assert 'name="CampaignMasterWeb"' in spec_content

    def test_spec_defines_required_hidden_imports(self):
        """The spec file should include critical hidden imports."""
        spec_content = SPEC_FILE.read_text()
        required_imports = [
            "pydantic",
            "sqlalchemy",
            "campaign_master",
            "campaign_master.content",
            "campaign_master.content.api",
        ]
        for import_name in required_imports:
            assert f'"{import_name}"' in spec_content, f"Missing hidden import: {import_name}"

    def test_spec_gui_includes_pyside(self):
        """The GUI spec should include PySide6 imports."""
        spec_content = SPEC_FILE.read_text()
        assert '"PySide6"' in spec_content
        assert '"PySide6.QtCore"' in spec_content
        assert '"PySide6.QtWidgets"' in spec_content

    def test_spec_web_includes_fastapi(self):
        """The Web spec should include FastAPI imports."""
        spec_content = SPEC_FILE.read_text()
        assert '"fastapi"' in spec_content
        assert '"uvicorn"' in spec_content
        assert '"starlette"' in spec_content

    def test_spec_entry_points_exist(self):
        """The entry point files referenced in the spec should exist."""
        assert (PACKAGING_DIR / "entry_gui.py").exists()
        assert (PACKAGING_DIR / "entry_web.py").exists()


class TestBuildHelpers:
    """Tests for build.py helper functions."""

    def test_get_project_root(self):
        """get_project_root should return the correct directory."""
        sys.path.insert(0, str(PACKAGING_DIR))
        try:
            from build import get_project_root as build_get_project_root

            root = build_get_project_root()
            assert root.exists()
            assert (root / "pyproject.toml").exists()
            assert (root / "campaign_master").exists()
        finally:
            sys.path.remove(str(PACKAGING_DIR))

    def test_create_single_target_spec_gui(self, tmp_path):
        """create_single_target_spec should create a GUI-only spec."""
        sys.path.insert(0, str(PACKAGING_DIR))
        try:
            from build import create_single_target_spec

            spec_path = create_single_target_spec(PROJECT_ROOT, SPEC_FILE, "gui", onefile=False)
            try:
                assert spec_path.exists()
                spec_content = spec_path.read_text()
                # GUI sections should be present
                assert "gui_a = Analysis(" in spec_content
                assert "gui_exe = EXE(" in spec_content
                # Web sections should be removed
                assert "web_a = Analysis(" not in spec_content
                assert "web_exe = EXE(" not in spec_content
            finally:
                spec_path.unlink(missing_ok=True)
        finally:
            sys.path.remove(str(PACKAGING_DIR))

    def test_create_single_target_spec_web(self, tmp_path):
        """create_single_target_spec should create a Web-only spec."""
        sys.path.insert(0, str(PACKAGING_DIR))
        try:
            from build import create_single_target_spec

            spec_path = create_single_target_spec(PROJECT_ROOT, SPEC_FILE, "web", onefile=False)
            try:
                assert spec_path.exists()
                spec_content = spec_path.read_text()
                # Web sections should be present
                assert "web_a = Analysis(" in spec_content
                assert "web_exe = EXE(" in spec_content
                # GUI sections should be removed
                assert "gui_a = Analysis(" not in spec_content
                assert "gui_exe = EXE(" not in spec_content
            finally:
                spec_path.unlink(missing_ok=True)
        finally:
            sys.path.remove(str(PACKAGING_DIR))


class TestPyInstallerAvailability:
    """Tests for PyInstaller availability."""

    def test_pyinstaller_is_installed(self):
        """PyInstaller should be installed."""
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"PyInstaller not available: {result.stderr}"

    def test_pyinstaller_version(self):
        """PyInstaller should be version 6.x or higher."""
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True,
            text=True,
        )
        version_str = result.stdout.strip()
        major_version = int(version_str.split(".")[0])
        assert major_version >= 6, f"PyInstaller version too old: {version_str}"


@pytest.mark.slow
class TestActualBuild:
    """
    Tests that actually run PyInstaller builds.

    These tests are marked as slow and can be skipped with: pytest -m "not slow"
    """

    def test_full_build_completes(self):
        """Both GUI and Web builds should complete using the preexisting spec file."""
        import shutil

        # Clean previous build artifacts
        build_dir = PROJECT_ROOT / "build"
        executables_dir = PROJECT_ROOT / "executables"
        if build_dir.exists():
            shutil.rmtree(build_dir)
        if executables_dir.exists():
            shutil.rmtree(executables_dir)

        # Ensure frontend is built for web executable
        dist_dir = PROJECT_ROOT / "dist"
        if not dist_dir.exists():
            npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
            subprocess.run([npm_cmd, "install"], cwd=PROJECT_ROOT, check=True, timeout=120)
            subprocess.run([npm_cmd, "run", "build"], cwd=PROJECT_ROOT, check=True, timeout=120)

        # Run PyInstaller directly with the preexisting spec file
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "PyInstaller",
                "--noconfirm",
                "--clean",
                "--distpath",
                str(executables_dir),
                str(SPEC_FILE),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        assert result.returncode == 0, f"Build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

        # Check both executables were created
        gui_exe = executables_dir / "CampaignMasterGUI" / "CampaignMasterGUI.exe"
        web_exe = executables_dir / "CampaignMasterWeb" / "CampaignMasterWeb.exe"

        assert gui_exe.exists(), f"GUI executable not found: {gui_exe}"
        assert web_exe.exists(), f"Web executable not found: {web_exe}"


@pytest.mark.slow
class TestExecutableExecution:
    """
    Tests that verify the built executables can start.

    These tests are marked as slow and require the executables to be built first.
    """

    @pytest.fixture
    def gui_executable(self):
        """Get the path to the GUI executable if it exists."""
        exe_path = PROJECT_ROOT / "executables" / "CampaignMasterGUI" / "CampaignMasterGUI.exe"
        if not exe_path.exists():
            pytest.skip("GUI executable not built")
        return exe_path

    @pytest.fixture
    def web_executable(self):
        """Get the path to the Web executable if it exists."""
        exe_path = PROJECT_ROOT / "executables" / "CampaignMasterWeb" / "CampaignMasterWeb.exe"
        if not exe_path.exists():
            pytest.skip("Web executable not built")
        return exe_path

    def test_gui_executable_starts(self, gui_executable):
        """The GUI executable should start without immediate crash."""
        # Run with --help to check it starts without actually running the GUI
        result = subprocess.run(
            [str(gui_executable), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # --help should work and show usage
        assert result.returncode == 0 or "usage" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_web_executable_starts(self, web_executable):
        """The Web executable should start without immediate crash."""
        # Run with --help to check it starts without actually running the server
        result = subprocess.run(
            [str(web_executable), "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # --help should work and show usage
        assert result.returncode == 0 or "usage" in result.stdout.lower() or "help" in result.stdout.lower()
