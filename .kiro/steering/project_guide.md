# Bonesaw Project Guide

This document provides guidance for working with the Bonesaw codebase. It describes the repository structure, coding conventions, and expectations for how Kiro should assist with development.

## Repository Structure

### Core Framework (`skeleton_core/`)

The `skeleton_core/` directory contains the generic pipeline framework. This is the reusable foundation that all applications build upon.

- **`pipeline.py`**: Defines the `Step` protocol and `Pipeline` class for orchestrating step execution.
- **`config.py`**: Provides the step registry (`STEP_REGISTRY`), `@register_step` decorator, and configuration loading functions.
- **`cli.py`**: CLI interface using Typer for running pipelines and managing apps.
- **`logging_utils.py`**: Optional logging configuration helpers.
- **`__init__.py`**: Package initialization.

**Important**: The core framework should contain NO application-specific logic. It provides only the generic abstractions for building pipelines.

### Applications (`apps/`)

Each application lives in its own subdirectory under `apps/`. Applications use the core framework to implement domain-specific automation pipelines.

**Required files for each app:**

- **`pipelines.py`**: Defines all Step classes specific to this application. Each step must be registered using `@register_step("step_name")`.
- **`config.example.yml`**: Example pipeline configuration demonstrating how to use the app's steps.
- **`README.md`**: Brief description of what the app does and how to use it.
- **`__init__.py`**: Package initialization.

**Optional files:**

- **`sample_*.{log,txt,json}`**: Test data files for demonstrating or testing the app.

**Current applications:**

1. **`apps/haunted_log_cleaner/`**: Parses messy logs, anonymizes data, aggregates errors, and generates markdown reports.
2. **`apps/graveyard_feed_reviver/`**: Fetches old RSS/Atom feeds, normalizes entries, and outputs structured data.

### Tests (`tests/`)

The `tests/` directory contains pytest test files for both the core framework and applications.

- **`test_pipeline_core.py`**: Tests for `skeleton_core/pipeline.py` and `skeleton_core/config.py`.
- **`test_logs.py`**: Tests for the Haunted Log Cleaner app.
- **`test_feeds.py`**: Tests for the Graveyard Feed Reviver app.

### Entry Point

- **`main.py`**: Main entry point that imports and runs the CLI from `skeleton_core/cli.py`.

### Kiro Configuration (`.kiro/`)

- **`.kiro/specs/`**: Specification documents for features (spec-driven development).
- **`.kiro/steering/`**: Steering documents that guide Kiro's behavior (like this file).
- **`.kiro/hooks/`**: Automation hooks for running tests and linters on file changes.

## Coding Style and Conventions

### Python Version and Type Hints

- Use **Python 3.11+** features and syntax.
- Use type hints consistently for all function signatures and class attributes.
- Prefer modern type hint syntax: `list[str]` over `List[str]`, `dict[str, Any]` over `Dict[str, Any]`.
- Use `Any` from `typing` when a value can truly be any type.

### Code Organization

- Prefer **small, single-responsibility functions and classes**.
- Keep functions focused on one task.
- Extract complex logic into helper functions with clear names.
- Avoid deeply nested code; use early returns and guard clauses.

### Logging

- Use Python's standard **`logging` module** for all logging.
- **Never use `print()` statements** in library code (`skeleton_core/` or `apps/`).
- Configure a module-level logger: `logger = logging.getLogger(__name__)`.
- Use appropriate log levels:
  - `DEBUG`: Detailed diagnostic information.
  - `INFO`: Normal execution flow (pipeline start/end, step execution).
  - `WARNING`: Unexpected but recoverable situations.
  - `ERROR`: Errors and exceptions.

### Step Classes

Every Step class must follow these conventions:

1. **Registration**: Use the `@register_step("step_name")` decorator to register the step in the global registry.
2. **Interface**: Implement the `run(self, data: Any, context: dict[str, Any]) -> Any` method.
3. **Docstring**: Include a clear docstring that describes:
   - What the step does.
   - Expected input (`data` parameter).
   - What it returns (output `data`).
   - Any context keys it reads or writes.
4. **Constructor**: Accept configuration parameters as keyword arguments in `__init__`.
5. **Independence**: Steps should be composable and not make assumptions about other steps in the pipeline.

**Example:**

```python
from skeleton_core.config import register_step

@register_step("example_step")
class ExampleStep:
    """
    Does something useful with the input data.
    
    Input: A string to process
    Output: A processed string
    Context: Writes 'example_count' with the number of operations performed
    """
    
    def __init__(self, mode: str = "default"):
        self.mode = mode
    
    def run(self, data: Any, context: dict[str, Any]) -> Any:
        # Implementation here
        context['example_count'] = 1
        return processed_data
```

### Documentation

- Every module should have a docstring explaining its purpose.
- Every public class and function should have a docstring.
- Use clear, concise language.
- For complex logic, add inline comments explaining the "why", not the "what".

## Kiro-Specific Guidance

### Adding New Pipelines or Apps

When asked to add new pipelines or applications:

1. **Create app-specific Steps in `apps/<app_name>/pipelines.py`**, not in `skeleton_core/`.
2. **Import and use** `@register_step` from `skeleton_core.config`.
3. **Create a `config.example.yml`** showing how to configure the pipeline.
4. **Add a `README.md`** explaining what the app does.
5. **Keep the core framework generic** - no app-specific logic in `skeleton_core/`.

### Modifying Core Behavior

When asked to modify core framework behavior:

1. **Update the spec first**: Modify `.kiro/specs/skeleton_core.md` to reflect the desired behavior.
2. **Align code to the spec**: Update the implementation in `skeleton_core/` to match the spec.
3. **Document the change**: Update docstrings and comments as needed.

This ensures the spec remains the source of truth for the framework's design.

### Testing

- Assume **`pytest`** is the test runner.
- Write tests in the `tests/` directory.
- Test files should be named `test_*.py`.
- Use descriptive test function names: `test_pipeline_executes_steps_in_order()`.
- Keep tests focused and independent.

### CLI Expectations

The CLI is implemented in `skeleton_core/cli.py` using **Typer**.

**Expected commands:**

- `bonesaw list-apps`: List all available applications.
- `bonesaw run --app <name> --config <path>`: Run a pipeline from a config file.

When implementing or modifying CLI behavior:

- Use Typer's decorators and type hints for argument parsing.
- Provide helpful error messages for invalid inputs.
- Keep CLI code thin - delegate to core framework functions.

## Hackathon Constraints

This is a **hackathon project** built to demonstrate Kiro's capabilities. Keep these principles in mind:

1. **Don't over-engineer**: Prefer simple, clear solutions over complex abstractions.
2. **Focus on clarity**: Code should be easy to read and understand.
3. **Show Kiro integration**: Demonstrate spec-driven development, steering docs, hooks, and vibe coding.
4. **Prioritize working features**: Get things working first, then polish if time allows.
5. **Document as you go**: Clear docstrings and comments help judges understand the code.

## File Placement Quick Reference

| What | Where |
|------|-------|
| Generic pipeline framework | `skeleton_core/` |
| App-specific Step classes | `apps/<app_name>/pipelines.py` |
| Pipeline configurations | `apps/<app_name>/config.example.yml` |
| Tests | `tests/test_*.py` |
| CLI commands | `skeleton_core/cli.py` |
| Specs | `.kiro/specs/` |
| Steering docs | `.kiro/steering/` |
| Hooks | `.kiro/hooks/hooks.yaml` |

## Summary

- **Core framework** (`skeleton_core/`) is generic and reusable.
- **Applications** (`apps/`) contain domain-specific Steps and configurations.
- **Steps** must be registered, implement `run()`, and have clear docstrings.
- **Use logging**, not print statements.
- **Type hints** are required.
- **Keep it simple** - this is a hackathon project.
- **Spec-driven development** - update specs before changing core behavior.
