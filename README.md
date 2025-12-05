# Bonesaw

A modular Python automation framework for building composable data processing pipelines.

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](.github/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MPL--2.0-orange.svg)](LICENSE)

## Overview

Bonesaw is a lightweight, extensible framework for creating automation pipelines. It provides a step-based architecture where each step performs a discrete operation, and pipelines are defined declaratively using YAML configuration files.

The framework is designed for:
- Data processing workflows
- Log analysis and transformation
- Feed aggregation and normalization
- Report generation
- Any sequential automation task

## Key Features

- **Declarative Configuration**: Define pipelines using YAML files
- **Step Registry**: Automatic step discovery via decorator-based registration
- **Context Sharing**: Pass state between steps using a shared context dictionary
- **CLI Tools**: Built-in commands for running, inspecting, and managing pipelines
- **App Scaffolding**: Generate new pipeline applications with a single command
- **Optional LLM Integration**: Enhance output with AI-powered summaries via OpenRouter
- **Testing**: Comprehensive test suite with pytest
- **Code Quality**: Enforced linting with Ruff
- **CI/CD**: GitHub Actions workflow included

## Installation

### Prerequisites

- Python 3.11 or higher
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### List Available Applications

```bash
python main.py list-apps
```

### Inspect a Pipeline

View pipeline structure without executing:

```bash
python main.py inspect --app log_cleaner --config apps/log_cleaner/config.example.yml
```


### Dry-Run a Pipeline

See detailed step information without side effects:

```bash
python main.py dry-run --app feed_processor --config apps/feed_processor/config.example.yml
```

### Run a Pipeline

Execute a complete pipeline:

```bash
python main.py run --app log_cleaner --config apps/log_cleaner/config.example.yml
```

## Directory Structure

```
bonesaw/
├── skeleton_core/          # Core framework
│   ├── pipeline.py         # Pipeline execution engine
│   ├── config.py           # Step registry and configuration loader
│   ├── cli.py              # Command-line interface
│   ├── scaffold.py         # App generator
│   └── summarization.py    # Optional LLM integration
├── apps/                   # Pipeline applications
│   ├── log_cleaner/        # Example: Log processing pipeline
│   └── feed_processor/     # Example: RSS/Atom feed pipeline
├── tests/                  # Test suite
├── main.py                 # CLI entry point
└── requirements.txt        # Python dependencies
```

### Core Components

- **`skeleton_core/`**: Contains the reusable framework code
- **`apps/`**: Individual pipeline applications, each with its own steps and configuration
- **`tests/`**: Pytest test files for framework and applications
- **`main.py`**: Entry point for the CLI

## Usage Examples

### Creating a New Application

Generate a new pipeline application with scaffolding:

```bash
python main.py create-app my_processor
```

This creates:
- `apps/my_processor/pipelines.py` - Step implementations
- `apps/my_processor/config.example.yml` - Pipeline configuration
- `apps/my_processor/sample_input.txt` - Sample data
- `apps/my_processor/README.md` - Documentation

### Running with LLM Enhancement

Enable optional AI-powered summaries:

```bash
set BONESAW_LLM_PROVIDER=openrouter
set BONESAW_LLM_MODEL=deepseek/deepseek-r1-0528-qwen3-8b
set BONESAW_LLM_API_KEY=your_api_key

python main.py run --app my_processor --config apps/my_processor/config.example.yml --use-llm
```

### Deleting an Application

Remove an application and its files:

```bash
python main.py delete-app my_processor
```


## Creating Custom Pipeline Steps

Steps are the building blocks of pipelines. Each step implements a `run` method that processes data and optionally updates shared context.

### Step Implementation

```python
from skeleton_core.config import register_step
from typing import Any

@register_step("transform_data")
class TransformDataStep:
    """
    Transforms input data according to specified rules.
    
    Input: Raw data dictionary
    Output: Transformed data dictionary
    Context: Writes 'transform_count' with number of transformations
    """
    
    def __init__(self, mode: str = "default", multiplier: int = 1):
        """
        Initialize the step with configuration parameters.
        
        Args:
            mode: Transformation mode
            multiplier: Scaling factor for numeric values
        """
        self.mode = mode
        self.multiplier = multiplier
    
    def run(self, data: Any, context: dict[str, Any]) -> Any:
        """
        Execute the transformation step.
        
        Args:
            data: Input data from previous step
            context: Shared context dictionary
            
        Returns:
            Transformed data for next step
        """
        # Implement transformation logic
        transformed = self._transform(data)
        
        # Update context
        context['transform_count'] = len(transformed)
        
        return transformed
    
    def _transform(self, data: Any) -> Any:
        # Transformation implementation
        return data
```

### Pipeline Configuration

Define pipelines in YAML:

```yaml
pipeline:
  name: data_processor
  steps:
    - type: load_data
      source: input.txt
    
    - type: transform_data
      mode: advanced
      multiplier: 2
    
    - type: write_output
      destination: output.txt
```

### Step Registration

The `@register_step` decorator automatically registers steps in the global registry. The framework uses the step type from the configuration to instantiate the correct class.


## Example Applications

The repository includes two complete example applications demonstrating different use cases.

### Log Cleaner

A log processing pipeline that:
1. Loads log files from disk
2. Parses log entries using regex patterns
3. Anonymizes sensitive data (IP addresses, email addresses)
4. Aggregates errors and warnings
5. Generates a formatted Markdown report
6. Optionally adds an AI-generated summary

**Usage:**
```bash
python main.py run --app log_cleaner --config apps/log_cleaner/config.example.yml
```

### Feed Processor

An RSS/Atom feed aggregation pipeline that:
1. Loads feed URLs from a text file
2. Fetches and parses feeds using feedparser
3. Normalizes entry metadata across different feed formats
4. Outputs structured JSON data
5. Generates a formatted Markdown report
6. Optionally adds an AI-generated summary

**Usage:**
```bash
python main.py run --app feed_processor --config apps/feed_processor/config.example.yml
```

## Optional LLM Integration

Bonesaw supports optional AI-powered text summarization via OpenRouter.

### Configuration

Set environment variables:

```bash
set BONESAW_LLM_PROVIDER=openrouter
set BONESAW_LLM_MODEL=deepseek/deepseek-r1-0528-qwen3-8b
set BONESAW_LLM_API_KEY=your_api_key_here
```

### Behavior

- **Without LLM**: Pipelines generate deterministic, template-based summaries
- **With LLM**: Summaries are enhanced with AI-generated insights
- **Fallback**: If LLM calls fail, the system gracefully falls back to deterministic summaries

### Supported Providers

Currently supports OpenRouter. The framework can be extended to support additional providers by modifying `skeleton_core/summarization.py`.


## Testing

The project includes a comprehensive test suite using pytest.

### Running Tests

```bash
pytest
```

### Test Coverage

- **`tests/test_pipeline_core.py`**: Core framework functionality
- **`tests/test_logs.py`**: Log cleaner application
- **`tests/test_feeds.py`**: Feed processor application

All tests are deterministic and do not require network access or external API calls.

### Code Quality

Linting is enforced using Ruff:

```bash
ruff check .
```

## Continuous Integration

The repository includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:
- Runs on push and pull requests to main/master branches
- Tests against Python 3.11 on Ubuntu
- Installs dependencies
- Runs Ruff linting
- Executes the full test suite

## Extending the Framework

### Adding New Step Types

1. Create a new class in your app's `pipelines.py`
2. Decorate with `@register_step("step_name")`
3. Implement the `run(self, data, context)` method
4. Add the step to your pipeline configuration

### Creating Reusable Steps

Steps can be shared across applications by:
- Placing them in a common module
- Importing them in application-specific `pipelines.py` files
- Ensuring they are registered before pipeline execution

### Custom Context Keys

Steps can read and write arbitrary keys to the shared context dictionary. Common patterns:
- Store metadata: `context['record_count'] = 100`
- Share configuration: `context['output_format'] = 'json'`
- Pass intermediate results: `context['parsed_data'] = data`


## Architecture

### Pipeline Execution Flow

1. **Configuration Loading**: YAML file is parsed into a dictionary
2. **Step Instantiation**: Each step type is looked up in the registry and instantiated with its parameters
3. **Pipeline Creation**: Steps are assembled into a Pipeline object
4. **Execution**: Pipeline runs each step sequentially, passing data and context
5. **Output**: Final step returns the processed result

### Step Protocol

Steps must implement:
```python
def run(self, data: Any, context: dict[str, Any]) -> Any:
    """
    Process data and return result for next step.
    
    Args:
        data: Output from previous step (or initial_data for first step)
        context: Shared dictionary for passing state between steps
        
    Returns:
        Processed data for next step
    """
```

### Context Dictionary

The context is a mutable dictionary shared across all steps in a pipeline execution. It enables:
- Passing metadata between steps
- Accumulating statistics
- Sharing configuration
- Storing intermediate results

## CLI Reference

### Commands

- **`list-apps`**: Display all available pipeline applications
- **`inspect`**: Show pipeline structure without execution
- **`dry-run`**: Display detailed step information without side effects
- **`run`**: Execute a complete pipeline
- **`create-app`**: Generate a new pipeline application
- **`delete-app`**: Remove a pipeline application

### Common Options

- **`--app`**: Application name (required for most commands)
- **`--config`**: Path to YAML configuration file (required for pipeline operations)
- **`--use-llm`**: Enable LLM-enhanced summaries (optional, requires environment variables)
- **`--force`**: Skip confirmation prompts (for delete-app)

### Examples

```bash
# List all applications
python main.py list-apps

# Inspect pipeline structure
python main.py inspect --app my_app --config apps/my_app/config.example.yml

# Run with detailed output
python main.py run --app my_app --config apps/my_app/config.example.yml

# Create new application
python main.py create-app new_processor

# Delete application (with confirmation)
python main.py delete-app old_processor

# Delete application (skip confirmation)
python main.py delete-app old_processor --force
```


## Requirements

### Python Dependencies

- **pyyaml**: YAML configuration parsing
- **typer**: CLI framework
- **feedparser**: RSS/Atom feed parsing (for feed processor example)
- **requests**: HTTP client (for LLM integration)
- **pytest**: Testing framework
- **ruff**: Code linting and formatting

See `requirements.txt` for complete dependency list with versions.

### System Requirements

- Python 3.11 or higher
- pip package manager
- Operating System: Windows, macOS, or Linux

## Configuration File Format

Pipeline configurations use YAML format:

```yaml
pipeline:
  name: my_pipeline
  steps:
    - type: step_type_1
      param1: value1
      param2: value2
    
    - type: step_type_2
      param1: value1
    
    - type: step_type_3
      param1: value1
      param2: value2
      param3: value3
```

### Configuration Rules

- **`pipeline.name`**: Arbitrary string for identification and logging
- **`pipeline.steps`**: Ordered list of step definitions
- **`type`**: Step type name (must match a registered step)
- Additional keys are passed as keyword arguments to the step constructor

## Error Handling

The framework provides clear error messages for common issues:

- **Unknown step type**: Raised when a step type is not found in the registry
- **Missing configuration**: Raised when required parameters are not provided
- **File not found**: Raised when configuration or input files cannot be located
- **Step execution errors**: Logged with full context and re-raised for debugging

All errors include descriptive messages to aid in troubleshooting.

## Contributing

Contributions are welcome. Please ensure:
- All tests pass (`pytest`)
- Code passes linting (`ruff check .`)
- New features include tests
- Documentation is updated


## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0).

See the [LICENSE](LICENSE) file for full license text.

### MPL-2.0 Summary

- **Permissions**: Commercial use, modification, distribution, patent use, private use
- **Conditions**: Disclose source, include license and copyright notice, state changes
- **Limitations**: Liability, warranty

## Project Status

This project is actively maintained and suitable for production use. The framework is stable and the API is considered mature.

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review example applications for usage patterns

## Acknowledgments

Built with:
- Python 3.11+
- Typer for CLI
- PyYAML for configuration
- Feedparser for RSS/Atom support
- Pytest for testing
- Ruff for code quality

---

**Bonesaw** - A modular Python automation framework for composable data processing pipelines.
