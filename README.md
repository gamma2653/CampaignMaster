# CampaignMaster

A companion application for game masters of various TTRPG formats. This application allows a game master to plan, and then subsequently execute a game plan for player sessions. As development continues, support for additional game mechanics will be added, via a "Rules" framework, more to come later.

As far as game masters are concerned, running a TTRPG campaign is associated with two primary activities: preparation (planning), and execution (running the campaign with players).

This application breaks down this process into two clean steps. First, the user is able to plan out their campaign, or at least some overarching critical storypoints. Notably, the plan will be able to be modified on the fly, with new branches able to be spun off, and a notion of "executed" storypoints.

To fit this theme, the "installation" and "usage" instructions are outlined below, as "Preparation" and "Execution."

## Preparation

### Prerequisites

| Requirement | Version               | Notes                        |
| ----------- | --------------------- | ---------------------------- |
| Python      | 3.12 - 3.13           | Required for all modes       |
| Poetry      | Latest                | Python dependency management |
| Node.js     | Latest LTS            | Required only for web mode   |
| npm         | Included with Node.js | Required only for web mode   |

### Python Environment Setup

1. **Install Poetry** following the [official instructions](https://python-poetry.org/docs/#installing-with-the-official-installer).
   - Configure your preferred virtualenv defaults before proceeding.

2. **Install Python dependencies:**

   ```bash
   poetry install
   ```

3. **Activate the Poetry environment:**
   ```bash
   poetry shell
   ```
   See [Poetry's documentation](https://python-poetry.org/docs/managing-environments#powershell) for platform-specific instructions.

### Frontend Setup (Web Mode Only)

> **Note:** Complete the [Python setup](#python-environment-setup) first. This section is only required for web mode.

1. **Install Node.js** to get access to the `npm` command.
   - **Windows:** `winget install --id OpenJS.NodeJS --source winget`
   - **macOS:** `brew install node`
   - **Linux:** Use your distribution's package manager or [NodeSource](https://github.com/nodesource/distributions)

2. **Install frontend dependencies:**

   ```bash
   npm install
   ```

3. **Build the frontend (production):**

   ```bash
   npm run build
   ```

4. **Run the frontend development server (optional):**
   ```bash
   npm run dev
   ```
   This starts a hot-reloading development server separate from the Python backend.

## Execution

Run `python -m campaign_master -h` for full usage information.

The application can run in two modes: as a desktop GUI (Qt application) or as a web server.

### GUI Mode

> Node.js is not required for this mode.

```bash
python -m campaign_master --gui [--debug]
```

This launches a Qt desktop application where you can interface with your local file system to load relevant configuration files.

**Options:**

- `--debug`: Enable verbose logging

### Web Mode

```bash
python -m campaign_master --web [--debug] [--host 127.0.0.1] [--port 8000]
```

This builds the frontend (if needed) and starts the FastAPI server with uvicorn.

**Options:**

- `--debug`: Enable verbose logging and development server mode
- `--host`: Server host address (default: `127.0.0.1`)
- `--port`: Server port (default: `8000`)

## Testing

### Python Tests

```bash
# Run all tests
pytest

# Run a specific test file
pytest test/test_content_api.py

# Run with verbose output
pytest -v

# Skip slow tests
pytest -m "not slow"
```

### Frontend Tests

```bash
# Run tests once
npm run test:run

# Run tests in watch mode
npm run test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## Code Formatting & Linting

### Python

```bash
# Format code with Black
poetry run black .

# Sort imports with isort
poetry run isort .
```

### Frontend

```bash
# Format code with Prettier
npm run format

# Lint code with ESLint
npm run lint
```

## Building Standalone Executables

CampaignMaster can be packaged as standalone executables using PyInstaller. Two separate executables are created:

- **CampaignMasterGUI.exe** - Desktop GUI application (PySide6)
- **CampaignMasterWeb.exe** - Web server application (FastAPI + React)

### Prerequisites

Ensure PyInstaller is installed (included in the `build` dependency group):

```bash
poetry install --with build
```

### Build Commands

```bash
# Build both executables (onefolder mode - default)
python packaging/build.py

# Build both as single-file executables
python packaging/build.py --onefile

# Build only the GUI executable
python packaging/build.py --gui-only

# Build only the Web executable
python packaging/build.py --web-only

# Include debug information
python packaging/build.py --debug

# Skip frontend build (use existing dist/)
python packaging/build.py --skip-frontend

# Clean build artifacts before building
python packaging/build.py --clean
```

### Build Output

**Onefolder mode** (default, faster startup):

```
executables/CampaignMasterGUI/CampaignMasterGUI.exe
executables/CampaignMasterWeb/CampaignMasterWeb.exe
```

**Onefile mode** (single self-contained executable):

```
executables/CampaignMasterGUI.exe
executables/CampaignMasterWeb.exe
```

### Running the Executables

```bash
# GUI executable (onefolder)
.\executables\CampaignMasterGUI\CampaignMasterGUI.exe

# Web executable (onefolder)
.\executables\CampaignMasterWeb\CampaignMasterWeb.exe --port 8000

# GUI executable (onefile)
.\executables\CampaignMasterGUI.exe

# Web executable (onefile)
.\executables\CampaignMasterWeb.exe --port 8000
```

### Advanced: Direct PyInstaller Usage

You can also run PyInstaller directly with the spec file:

```bash
pyinstaller packaging/CampaignMaster.spec
```

## Environment Configuration

Configuration is managed via environment variables:

| Variable             | Default    | Description                                 |
| -------------------- | ---------- | ------------------------------------------- |
| `CM_LOG_LEVEL`       | `INFO`     | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DB_db_scheme`       | `:memory:` | Database connection string                  |
| `DB_db_connect_args` | -          | Additional database connection arguments    |

## Technologies Used

### Backend (Python)

| Technology                                    | Purpose                            |
| --------------------------------------------- | ---------------------------------- |
| [Pydantic](https://docs.pydantic.dev/latest/) | Data validation and business logic |
| [SQLAlchemy](https://www.sqlalchemy.org/)     | Database ORM                       |
| [FastAPI](https://fastapi.tiangolo.com/)      | Web API framework                  |
| [uvicorn](https://uvicorn.dev/)               | ASGI development server            |
| [PySide6](https://doc.qt.io/qtforpython-6/)   | Desktop GUI framework (Qt)         |
| [PyInstaller](https://pyinstaller.org/)       | Executable packaging               |
| [pytest](https://pytest.org/)                 | Testing framework                  |
| [Black](https://black.readthedocs.io/)        | Code formatting                    |
| [isort](https://pycqa.github.io/isort/)       | Import sorting                     |

### Frontend (React/TypeScript)

| Technology                                     | Purpose                      |
| ---------------------------------------------- | ---------------------------- |
| [Rsbuild](https://rsbuild.rs/)                 | Build tooling (Rspack-based) |
| [TypeScript](https://www.typescriptlang.org/)  | Type-safe JavaScript         |
| [React 19](https://react.dev/)                 | UI framework                 |
| [TanStack Router](https://tanstack.com/router) | File-based routing           |
| [TanStack Query](https://tanstack.com/query)   | Data fetching and caching    |
| [TanStack Form](https://tanstack.com/form)     | Form management              |
| [Tailwind CSS 4](https://tailwindcss.com/)     | Utility-first CSS            |
| [Zod](https://zod.dev/)                        | Schema validation            |
| [Vitest](https://vitest.dev/)                  | Testing framework            |
| [Prettier](https://prettier.io/)               | Code formatting              |
| [ESLint](https://eslint.org/)                  | Code linting                 |

### Infrastructure

| Technology                           | Purpose                      |
| ------------------------------------ | ---------------------------- |
| [nginx](https://nginx.org/)          | Production server (WIP)      |
| [Poetry](https://python-poetry.org/) | Python dependency management |
