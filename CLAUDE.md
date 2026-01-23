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

**Reference Pattern:** Objects reference each other by ID (string), not by embedding full objects. This avoids circular dependencies. Database models handle actual relationships via SQLAlchemy `relationship()` definitions.

### Session Management

- Database sessions are passed explicitly as parameters (not scoped sessions)
- `@perform_w_session` decorator in `api.py` provides automatic session handling
- Functions work with or without explicit `_session` parameter
- Always use `SessionLocal()` from `database.py` to create sessions

### ProtoUser System

- Lightweight user representation for multi-tenancy
- GUI typically uses global scope (proto_user_id=0)
- Web mode associates objects with specific users
- Required parameter when calling most `content/api.py` functions

## Frontend Architecture (Web Mode)

### Tech Stack

- **Build Tool**: Rsbuild (faster alternative to Webpack)
- **Framework**: React 19 with TypeScript
- **Routing**: TanStack Router (file-based routing in `web/react/routes/`)
- **Data Fetching**: TanStack Query
- **Forms**: TanStack Form
- **Styling**: Tailwind CSS 4
- **Validation**: Zod

### Frontend Build Process

```bash
# Development server (separate from Python backend)
npm run dev

# Production build (creates static files)
npm run build
```

## Database Configuration

- Default: In-memory SQLite (`:memory:`) - data lost on restart
- Override via environment variable: `DB_db_scheme`
- Connection args via: `DB_db_connect_args`
- Settings defined in `content/settings.py` using Pydantic Settings
- Prefix: `CM_` for general settings, `DB_` for database settings

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

### GUI Widget Generation

GUI widgets (`gui/widgets/planning.py`) dynamically generate forms from Pydantic models. Field types and validation rules are introspected from the model definitions.

## Recent Major Changes

The codebase recently migrated from SQLModel to separate SQLAlchemy + Pydantic models. Key commits:

- "Not using sqlmodel, sqlalchemy + pydantic all the way" - Architectural decision
- "Massive DB changes, working through cyclic references" - Complex relationship modeling
- "Fix pydantic-sqlalchemy issues" - Integration stabilization

**Files affected:**

- `content/database.py` (NEW): Database initialization and session management
- `content/models.py` (NEW): SQLAlchemy ORM models
- `content/db.py`: May be deprecated/duplicate - check before modifying
- `content/planning.py`: Pydantic business logic models

## Logging

Centralized logger factory in `util.py`:

```python
from campaign_master.util import get_basic_logger
logger = get_basic_logger(__name__)
```

Control log level via `CM_LOG_LEVEL` environment variable.

## Technologies Used

### Backend

- **Pydantic**: Business logic validation
- **FastAPI**: Web API framework
- **SQLAlchemy**: Database ORM
- **PySide6**: Desktop GUI framework
- **uvicorn**: Development web server

### Frontend

- **Rsbuild**: Build tooling
- **TypeScript**: Type-safe React
- **TanStack**: Router, Query, Form libraries
- **Tailwind CSS**: Utility-first styling
