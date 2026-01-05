# Branch Protection Setup

To make tests required before merging, configure branch protection rules on GitHub:

## Steps to Enable Required Tests

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Branches**
3. Click **Add branch protection rule**
4. Configure the following:
   - **Branch name pattern**: `main` (or your default branch)
   - Enable: **Require status checks to pass before merging**
   - Search for and select:
     - `test (ubuntu-latest, 3.10)`
     - `test (ubuntu-latest, 3.11)`
     - `test (ubuntu-latest, 3.12)`
     - `test (ubuntu-latest, 3.13)`
     - `test (windows-latest, 3.10)`
     - `test (windows-latest, 3.11)`
     - `test (windows-latest, 3.12)`
     - `test (windows-latest, 3.13)`
     - `test (macos-latest, 3.10)`
     - `test (macos-latest, 3.11)`
     - `test (macos-latest, 3.12)`
     - `test (macos-latest, 3.13)`
     - `lint`
   - Enable: **Require branches to be up to date before merging**
   - Optional: Enable **Require a pull request before merging**
   - Optional: Enable **Include administrators** (applies rules to admin users too)

5. Click **Create** or **Save changes**

## Quick Setup (Minimal)

For a simpler setup, you can require just the Ubuntu tests:
- `test (ubuntu-latest, 3.12)`
- `lint`

This will still ensure tests pass on the most common platform.

## Running Tests Locally

Before pushing, always run tests locally:

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest test/test_content_api.py -v
```

## Current Test Status

⚠️ **Note**: Tests are currently failing due to implementation issues:
- ID generation not implemented in some models
- Validation errors in Segment and Location models

These issues need to be fixed before branch protection can effectively block merges.
