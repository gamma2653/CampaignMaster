# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CampaignMaster is a companion application for TTRPG game masters, supporting campaign planning and execution. The application operates in two modes: a desktop GUI (PySide6) and a web interface (FastAPI + React). Both modes share the same core business logic layer.

## Development Setup

### Python Environment

```bash
# Install dependencies using Poetry
poetry install

# Activate the Poetry environment
poetry shell
```

### Frontend (Web Mode Only)

```bash
# Install Node dependencies
npm install
```

## Running the Application

### GUI Mode

```bash
python -m campaign_master --gui [--debug]
```

### Web Mode

```bash
python -m campaign_master --web [--debug] [--host 127.0.0.1] [--port 8000]
```

Note: Web mode builds the frontend first, then prompts before starting the server.

## Testing

```bash
# Run all tests
pytest

# Run a specific test file
pytest test/test_content_api.py

# Run with verbose output
pytest -v
```

## Code Formatting

```bash
# Format Python code
poetry run black .

# Sort imports
poetry run isort .

# Format frontend code
npm run format
```

## Linting

```bash
# Lint frontend code
npm run lint
```

## Architecture Overview

### Three-Layer Architecture

```
Entry Point (__main__.py)
    ├── GUI Mode (PySide6)
    └── Web Mode (FastAPI + React)
           ↓
    Content API (content/api.py)
           ↓
    ┌──────────────┴──────────────┐
    ↓                             ↓
Pydantic Models            SQLAlchemy Models
(planning.py)                 (models.py)
Business Logic              Database Layer
```

### Dual-Model Pattern

**Critical Design Decision:** The codebase uses separate Pydantic and SQLAlchemy models rather than a unified ORM like SQLModel.

- **Pydantic Models** (`content/planning.py`): Business logic, validation, serialization
- **SQLAlchemy Models** (`content/models.py`): Database persistence, relationships
- **Bridging**: `to_pydantic()` and `from_pydantic()` methods convert between layers
- **Mapping**: `PydanticToSQLModel` dict in `models.py` links types

**Why this matters:** When adding new entity types, you must create both models and implement conversion methods.

### Custom ID System

All domain objects use a custom ID format: `PREFIX-NUMERIC` (e.g., "R-000001", "C-000042")

- IDs are stored in the `ObjectID` table with separate `prefix` and `numeric` fields
- `proto_user_id` scopes IDs to users (0 = global, used by GUI)
- ID generation is centralized in `content/api.py` via `generate_id()`
- Each object type has a `_default_prefix` class variable (e.g., "R" for Rule, "C" for Character)
- `PREFIX_TO_OBJECT_TYPE` dict in `planning.py` enables prefix-based dispatch — `retrieve_object(id)` uses this to resolve the correct type without any `isinstance` checks

### Domain Model Hierarchy

All business objects inherit from `planning.Object`:

- **Rule**: Game rules (components, effects)
- **Objective**: Campaign goals (with prerequisites)
- **Point**: Story points (linked to objectives)
- **Segment**: Story segments (start/end points)
- **Arc**: Story arcs (collection of segments)
- **Item**: Game items (properties dict)
- **Character**: NPCs/PCs (attributes, skills, inventory, storylines)
- **Location**: Places (coordinates, neighboring locations)
- **CampaignPlan**: Top-level campaign container
- **AgentConfig** (prefix `AG`): AI provider configuration — provider, model, API key, base URL (`content/planning.py`)
- **CampaignExecution** (prefix `EX`): Campaign execution state with session entries (`content/executing.py`)

**Reference Pattern:** Objects reference each other by ID (string), not by embedding full objects. This avoids circular dependencies. Database models handle actual relationships via SQLAlchemy `relationship()` definitions.

**Exception:** `Arc.segments` embeds `Segment` objects directly (`list[Segment]`). This is the only intentional deviation from the ID-reference pattern.

**`ExecutionEntry`** is a plain `BaseModel` (not `Object`, no ID) stored within `CampaignExecution.entries`. It holds an `entity_id: ID`, `entity_type`, `status: ExecutionStatus` enum, and raw/refined notes.

### Session Management

- Database sessions are passed explicitly as parameters (not scoped sessions)
- `@perform_w_session` decorator in `api.py` provides automatic session handling
- Functions work with or without an explicit `session` parameter
- Always use `SessionLocal()` from `database.py` to create sessions

### ProtoUser System

- Lightweight user representation for multi-tenancy
- GUI typically uses global scope (proto_user_id=0)
- Web mode associates objects with specific users
- Required parameter when calling most `content/api.py` functions

### AI Provider Architecture

- **Protocol**: `ai/protocol.py` defines `AIProvider` (runtime-checkable protocol)
- **Providers**: `ai/providers/` contains `AnthropicProvider`, `OpenAIProvider`, `OllamaProvider` (all extend `BaseProvider`)
- **Registry**: `PROVIDER_REGISTRY` dict and `get_provider(provider_type, api_key, base_url, model)` factory function in `ai/providers/__init__.py`
- **GUI Service**: `AICompletionService` in `ai/service.py` — singleton, lazy-imported to avoid PySide6 dependency in web mode
- **Web Endpoints**: `web/ai_api.py` exposes AI completion endpoints for the web frontend — stateless, provider credentials are passed in every request body
- **Configuration**: `AgentConfig` objects stored in DB provide per-user provider settings

### Web Authentication

- UUID token-based auth with bcrypt password hashing (`web/auth.py`)
- Endpoints: `/api/auth` — login, register, logout, profile
- Default admin user auto-created on startup (username: `admin`, password: `admin`, proto_user_id=0)
- Protected routes require Bearer token in Authorization header

### File Upload / Storage

- `web/storage.py` provides `LocalStorage` and `S3Storage` backends
- Factory function `get_storage()` selects backend based on config
- Profile pictures stored in `uploads/profile_pictures/`
- S3 configurable via `CM_s3_*` environment variables

## Frontend Architecture (Web Mode)

### Tech Stack

- **Build Tool**: Rsbuild (faster alternative to Webpack)
- **Framework**: React 19 with TypeScript
- **Routing**: TanStack Router (file-based routing in `web/react/routes/`)
- **Data Fetching**: TanStack Query
- **Forms**: TanStack Form
- **Styling**: Tailwind CSS 4
- **Validation**: Zod

### Route Structure

File-based routing in `web/react/routes/`:

- `__root.tsx` — Root layout with auth guard (redirects to `/login` if no Bearer token)
- `index.tsx` — Home page
- `login.tsx` — Login page
- `profile.tsx` — User profile
- `campaign/` — Campaign planning routes (nested: `plan/$camp_id/...`)
- `settings/` — Settings routes

### AI Integration

- `features/ai/` — AIContext provider, completion hooks, AI-enhanced form components
- `features/shared/components/fields.tsx` — Reusable field components
- `query.tsx` — Query hook factory pattern for TanStack Query

### Query Factory Pattern

`web/react/query.tsx` uses factory functions to generate all CRUD hooks for every entity type, keeping the code DRY with full TypeScript types:

- `generateShallowQueries<ID, Ret>(prefixes)` → `[useData, useDataByID]` tuple
- `generateCreateMutation`, `generateUpdateMutation`, `generateDeleteMutation` — typed mutation hooks
- All 11 entity types have pre-generated hooks exported from this file

### Frontend Build & Test

```bash
# Development server (separate from Python backend)
npm run dev

# Production build (creates static files)
npm run build

# Run frontend tests (Vitest)
npm run test:run
```

## Configuration / Environment Variables

### Database

- Default: `sqlite:///campaignmaster.db` (file-based, persistent)
- Override via environment variable: `DB_db_scheme`
- Connection args via: `DB_db_connect_args`
- Settings defined in `content/settings.py` using Pydantic Settings
- Prefix: `DB_` for database settings

### Web & General Settings

- Prefix: `CM_` for general settings
- `CM_web_host`, `CM_web_port`: Web server bind address (default `127.0.0.1:8000`)
- `CM_debug_mode`: Enable debug logging/features
- `CM_upload_dir`: Local upload directory (default `uploads/`)
- `CM_s3_bucket`, `CM_s3_region`, `CM_s3_access_key`, `CM_s3_secret_key`: S3 storage config
- `CM_LOG_LEVEL`: Control log verbosity

## Adding a New Entity Type

1. Define Pydantic model in `content/planning.py`
   - Inherit from `planning.Object`
   - Set `_default_prefix` class variable (unique single letter or two-letter code)
   - Define all business logic fields with Pydantic types

2. Create SQLAlchemy model in `content/models.py`
   - Mirror the Pydantic model structure
   - Add `__tablename__` and `__pydantic_model__` attributes
   - Define database relationships using SQLAlchemy `relationship()`
   - Implement `to_pydantic()` and `from_pydantic()` methods

3. Register in `models.py`
   - Add mapping to `PydanticToSQLModel` dict

4. Add to type registry
   - Add to `ALL_OBJECT_TYPES` list in `planning.py`

## Important Patterns

### ID References Over Object Embedding

Objects store references to other objects using the `ID` type, not embedded objects. This prevents circular dependencies and allows lazy loading.

```python
# Good: Reference by ID
class Character(Object):
    inventory: list[ID]  # List of Item IDs (using ID type from planning.py)

# Bad: Embedded objects (causes circular references)
class Character(Object):
    inventory: list[Item]  # Don't do this!
```

**Exception:** `Arc.segments` embeds `Segment` objects directly (`list[Segment]`). This is the only intentional deviation from the ID-reference pattern.

### `from_pydantic` Idempotency

Every SQLAlchemy `from_pydantic` first checks if the object already exists before inserting. This makes it safe to call multiple times and simplifies upsert-style flows. `to_pydantic()` requires an explicit `session` because `obj_id()` on `ObjectBase` performs a manual `select(ObjectID)` query rather than relying on SQLAlchemy lazy-loading.

### Session Management

**Critical Pattern**: All database operations use proper session management with automatic error handling and transaction control.

#### Basic Principles

1. **Automatic Sessions**: All API functions create sessions automatically via the `@perform_w_session` decorator
2. **Error Handling**: Database errors trigger automatic rollback of the transaction
3. **Transaction Boundaries**: Top-level API functions commit by default, internal helpers don't
4. **Manual Transactions**: Use the `transaction()` context manager for multi-step operations
5. **Parameter Name**: All functions use `session` (not `_session`) for consistency

#### Usage Patterns

**Simple Operation (Automatic Session)**

```python
from campaign_master.content import api as content_api

# Session created, committed, and closed automatically
rule = content_api.create_object(planning.Rule, proto_user_id=0)
```

**Manual Transaction (Multiple Operations)**

```python
from campaign_master.content.database import transaction

with transaction() as session:
    # All operations in same transaction
    rule = content_api.create_object(
        planning.Rule, session=session, auto_commit=False
    )
    character = content_api.create_object(
        planning.Character, session=session, auto_commit=False
    )
    # Both committed together at end of with block
```

**Error Handling**

```python
from sqlalchemy.exc import SQLAlchemyError

try:
    obj = content_api.create_object(planning.Rule)
except SQLAlchemyError as e:
    # Error automatically rolled back by decorator
    logger.error(f"Database error: {e}")
```

#### When Adding New API Functions

1. Use `@perform_w_session` decorator
2. Accept optional `session` parameter (NOT `_session`)
3. Set `auto_commit=False` for internal helpers (prefix with `_`)
4. Set `auto_commit=True` (default) for public API functions
5. Don't call `session.commit()` directly - let decorator handle it
6. Let decorator handle rollback on errors

**Example: Internal Helper**

```python
@perform_w_session
def _internal_helper(
    obj_id: str, session: Session | None = None,
    auto_commit: bool = False  # Default False for helpers
) -> SomeType:
    # Do work, no manual commit
    return result
```

**Example: Public API Function**

```python
@perform_w_session
def public_function(
    obj_id: str, session: Session | None = None,
    auto_commit: bool = True  # Default True for public API
) -> SomeType:
    # Call helpers with auto_commit=False
    result = _internal_helper(obj_id, session=session, auto_commit=False)
    # Decorator handles commit
    return result
```

### Test Database Isolation

`content/database.py` supports an engine registry with `"default"` and `"test"` keys. Use `configure_test_database()` to switch the active engine in tests, ensuring test operations don't touch the production database.

### GUI Widget Generation

GUI widgets (`gui/widgets/planning.py`) dynamically generate forms from Pydantic models. Field types and validation rules are introspected from the model definitions.

## Build & Packaging

- Two separate executables: `CampaignMasterGUI` (no console window) and `CampaignMasterWeb` (console)
- Build script: `packaging/build.py`
  - Flags: `--gui-only`, `--web-only`, `--onefile`, `--onefolder`, `--clean`, `--debug`, `--skip-frontend`
- PyInstaller spec: `packaging/CampaignMaster.spec`
- Entry points: `packaging/entry_gui.py`, `packaging/entry_web.py`

## CI/CD

- `.github/workflows/test.yml`: **test** (multi-platform Python tests: Ubuntu/Windows/macOS, Python 3.12 + 3.13) and **frontend-test** (frontend tests and linting)
- `.github/workflows/lint.yml`: **lint** (auto-formatting with black + isort, commits fixes automatically)
- `.github/workflows/release.yml`: **create-release** (GitHub release creation, triggered after both Test and Lint succeed on main) and **package** (cross-platform executable packaging)

## Logging

Centralized logger factory in `util.py`:

```python
from campaign_master.util import get_basic_logger
logger = get_basic_logger(__name__)
```

Control log level via `CM_LOG_LEVEL` environment variable.
