# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a template repository for Python projects that use uv for their dependency management.

This project uses:
- **uv** for dependency management
- **Ruff** for linting and formatting
- **pyright** for type checking
- **pytest** for testing
- **MkDocs** for documentation

## Common Commands

```bash
# Install dependencies
uv sync

# Run all quality checks (lint, format, type check, deptry)
make check

# Run tests
make test

# Run a single test
uv run pytest tests/test_file.py::test_function -v

# Serve documentation locally
make docs
```

## Project Structure

```
src/idfkit/    # Main package
tests/              # Test files (mirror source structure)
docs/               # MkDocs documentation
pyproject.toml      # Project configuration and dependencies
```

## Code Style

- **Line length**: 120 characters
- **Imports**: Always include `from __future__ import annotations`
- **Type hints**: Required on all functions (parameters and return types)
- **Docstrings**: Google or NumPy style for public APIs
- **Data models**: Use dataclasses or Pydantic instead of raw dicts

## Testing

Tests live in `tests/` and mirror the source structure. When adding new functionality:

1. Create test file: `tests/test_<module_name>.py`
2. Write tests before or alongside implementation
3. Run tests: `uv run pytest tests/test_<module_name>.py -v`
4. Verify all tests pass: `make test`

Use pytest fixtures (in `conftest.py`) for shared test setup.

## Type Checking

This project uses **pyright** for static type analysis. **ALWAYS** try to fix the typing issues with a proper solution rather than adding an ignore statement.

```bash
uv run pyright
```

Ensure all new code is fully typed. The configuration is in `pyproject.toml`.

## Before Committing

Always run the full quality gate before proposing changes:

```bash
make check && make test
```

This runs: lock file validation, pre-commit hooks (ruff format/lint), pyright, deptry, and pytest.
