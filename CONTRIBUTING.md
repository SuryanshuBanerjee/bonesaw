# Contributing to Bonesaw

Thanks for your interest in contributing to Bonesaw! This guide will help you get started.

## Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/bonesaw.git
cd bonesaw
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
# Run tests
python -m pytest -v

# Check code quality
python -m ruff check .

# Try the CLI
python main.py --help
```

## Project Structure

```
bonesaw/
├── skeleton_core/          # Core framework
│   ├── pipeline.py         # Pipeline execution engine
│   ├── config.py           # YAML config loading & step registry
│   ├── cache.py            # Caching system
│   ├── cli.py              # Command-line interface
│   ├── summarization.py    # LLM integration
│   ├── scaffold.py         # App generation
│   └── steps/              # Built-in steps
│       ├── file_ops.py     # File operations
│       ├── http_ops.py     # HTTP requests
│       ├── text_ops.py     # Text processing
│       └── data_ops.py     # Data formats (JSON, CSV, YAML, RSS)
├── apps/                   # User applications
├── examples/               # Example pipelines
├── tests/                  # Test suite
├── main.py                 # CLI entry point
└── bonesaw_mcp_server.py  # MCP server
```

## How to Contribute

### 1. Create a New Step

Steps are the building blocks of Bonesaw pipelines. Here's how to create one:

```python
# In skeleton_core/steps/your_category.py
from skeleton_core.config import register_step
from typing import Any

@register_step("your_step_name")
class YourStep:
    """
    Brief description of what this step does.

    Input: Description of expected input type
    Output: Description of output type
    Context: What this step writes to context (if anything)
    """

    def __init__(self, param1: str, param2: int = 42):
        """
        Initialize the step.

        Args:
            param1: Description
            param2: Description with default
        """
        self.param1 = param1
        self.param2 = param2

    def run(self, data: Any, context: dict[str, Any]) -> Any:
        """Execute the step logic."""
        # Your implementation here
        # - Read from `data` (output of previous step)
        # - Optionally write to `context` for sharing state
        # - Return result for next step

        result = f"Processed: {data} with {self.param1}"
        context['your_step_executed'] = True
        return result
```

**Guidelines:**
- Keep steps focused on one task
- Use type hints throughout
- Write clear docstrings
- Log important operations
- Handle errors gracefully
- Add tests for your step

### 2. Write Tests

Add tests to `tests/test_your_feature.py`:

```python
def test_your_step():
    """Test YourStep basic functionality."""
    from skeleton_core.steps.your_category import YourStep

    step = YourStep(param1="test")
    context = {}
    result = step.run("input data", context)

    assert result == "Processed: input data with test"
    assert context['your_step_executed'] is True
```

Run tests with:
```bash
python -m pytest -v
python -m pytest tests/test_your_feature.py -v  # Run specific test
```

### 3. Code Quality

Before submitting, ensure code passes linting:

```bash
# Check for issues
python -m ruff check .

# Auto-fix what's possible
python -m ruff check . --fix

# Format code (if using ruff format)
python -m ruff format .
```

**Code standards:**
- Follow PEP 8
- Use type hints
- Write docstrings for all public functions/classes
- Keep functions small and focused
- No unused imports or variables

### 4. Submit Pull Request

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Add your code
   - Write tests
   - Update documentation

4. **Commit with clear messages**
   ```bash
   git add .
   git commit -m "Add feature: brief description

   - Detailed point 1
   - Detailed point 2

   Closes #123"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub

## Common Contribution Types

### Adding a Built-in Step

1. Choose the right category:
   - `file_ops.py` - File system operations
   - `http_ops.py` - Network/HTTP operations
   - `text_ops.py` - String/text manipulation
   - `data_ops.py` - Structured data (JSON, CSV, etc.)

2. Add your step class with `@register_step` decorator
3. Write tests in `tests/`
4. Add example usage to README or create example pipeline

### Creating Example Pipelines

1. Create directory: `examples/your_example/`
2. Add files:
   - `pipeline.yml` - The pipeline configuration
   - `README.md` - Explanation and usage
   - Any sample input files

3. Test your example:
   ```bash
   python main.py inspect --config examples/your_example/pipeline.yml
   python main.py dry-run --config examples/your_example/pipeline.yml
   python main.py run --config examples/your_example/pipeline.yml
   ```

### Improving Documentation

- Update README.md with new features
- Add docstrings to undocumented code
- Create tutorials or guides
- Fix typos or clarify confusing sections

### Reporting Bugs

Open an issue with:
- **Title**: Brief description
- **Description**: What happened vs. what you expected
- **Reproduction**: Step-by-step instructions
- **Environment**: OS, Python version, Bonesaw version
- **Logs**: Relevant error messages or stack traces

## Development Tips

### Testing Locally

```bash
# Run specific test
python -m pytest tests/test_pipeline_core.py::test_pipeline_executes_steps_in_order -v

# Run with coverage
python -m pytest --cov=skeleton_core --cov-report=html

# Test a pipeline you're working on
python main.py dry-run --config your_pipeline.yml
python main.py run --config your_pipeline.yml
```

### Debugging Steps

Add logging to your steps:
```python
import logging
logger = logging.getLogger(__name__)

def run(self, data, context):
    logger.debug(f"Input data: {data}")
    logger.info(f"Processing with param: {self.param}")
    # ...
    logger.debug(f"Output: {result}")
    return result
```

Run with debug logging:
```bash
# Set log level to DEBUG in main.py or use environment variable
LOGLEVEL=DEBUG python main.py run --config pipeline.yml
```

### Working with MCP Server

Test the MCP server:
```bash
# Start server
python bonesaw_mcp_server.py

# In another terminal, test with curl
curl http://localhost:8000/mcp/tools/list
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "list_pipelines", "arguments": {}}'
```

## Questions?

- **Documentation**: Check README.md and WHAT_IS_BONESAW.md
- **Examples**: Look at `examples/` directory
- **Issues**: Search existing issues or open a new one
- **Discussions**: Start a discussion for ideas or questions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for making Bonesaw better! 🦴
