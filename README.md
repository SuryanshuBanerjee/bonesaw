# 🦴🪚 Bonesaw

**The missing link between bash scripts and Airflow.**

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](.github/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MPL--2.0-orange.svg)](LICENSE)

> YAML-powered automation that doesn't suck.

Bonesaw is a lightweight, declarative pipeline framework for building composable automation workflows. Think GitHub Actions for your local machine, or Make for data pipelines.

```yaml
pipeline:
  name: morning_digest
  steps:
    - type: http_get
      url: https://news.ycombinator.com/rss
    - type: grep
      pattern: "<title>"
    - type: write_file
      path: digest.txt
```

```bash
python main.py run --config pipeline.yml
```

That's it. No framework magic. No hidden complexity. Just simple, composable steps.

---

## Why Bonesaw?

**Too Simple** → Bash scripts (messy, unmaintainable)
**👉 Perfect** → Bonesaw (declarative, testable, composable)
**Too Complex** → Airflow (overkill unless you're Netflix)

### What Makes Bonesaw Different

- **🎯 Declarative**: YAML configuration, not imperative code
- **🔧 Hackable**: ~3,000 LOC, readable in one sitting
- **🔋 Batteries Included**: 30+ built-in steps for common tasks
- **⚡ Smart Caching**: Automatic result caching for fast iteration
- **🪨 Rock Solid**: Type-safe Python with comprehensive tests
- **🎃 Fun**: Spooky theme (haunted_log_cleaner, graveyard_feed_reviver)

---

## Quick Start

### Install

```bash
git clone https://github.com/yourusername/bonesaw
cd bonesaw
pip install -r requirements.txt
```

### Run an Example

```bash
# Fetch today's top tech news
python main.py run --config examples/daily_news_digest/pipeline.yml

# Process CSV data
python main.py run --config examples/csv_processor/pipeline.yml

# Monitor websites
python main.py run --config examples/website_monitor/pipeline.yml
```

### Create Your Own

```bash
# Generate a new pipeline app
python main.py create-app my_automation

# Edit the generated files
cd apps/my_automation
# - pipelines.py: Define your custom steps
# - config.example.yml: Configure your pipeline

# Run it
python main.py run --app my_automation --config apps/my_automation/config.example.yml
```

---

## Features

### Batteries-Included Steps

Bonesaw ships with 30+ built-in steps for common tasks:

#### 📁 File Operations
- `read_file` / `write_file` - File I/O
- `copy_file` / `move_file` / `delete_file` - File management
- `list_files` - Find files with glob patterns

#### 🌐 HTTP Operations
- `http_get` / `http_post` - Make API requests
- `download_file` - Download from URLs
- `webhook` - Send data to webhooks

#### 📝 Text Operations
- `grep` - Filter lines (like Unix grep)
- `replace` - Regex find/replace
- `split_lines` / `join_lines` - Line manipulation
- `template` - String templating
- `to_uppercase` / `to_lowercase` - Case conversion

#### 📊 Data Operations
- `parse_json` / `to_json` - JSON parsing/serialization
- `parse_csv` / `to_csv` - CSV parsing/serialization
- `parse_yaml` / `to_yaml` - YAML parsing/serialization
- `filter_data` - Filter lists with conditions

### Smart Caching

Expensive operations are automatically cached:

```python
from skeleton_core.cache import cache_step

@register_step("expensive_api_call")
@cache_step(ttl=3600)  # Cache for 1 hour
class ExpensiveAPIStep:
    def run(self, data, context):
        # This only runs once per hour
        return fetch_from_slow_api()
```

Manage cache from CLI:

```bash
python main.py cache-info    # Show cache stats
python main.py cache-clear   # Clear cache
```

### Custom Steps

Build your own steps in minutes:

```python
from skeleton_core.config import register_step

@register_step("my_step")
class MyCustomStep:
    def __init__(self, param: str):
        self.param = param

    def run(self, data, context):
        # Process data
        result = transform(data, self.param)

        # Share state via context
        context['my_key'] = 'my_value'

        return result
```

Use in YAML:

```yaml
pipeline:
  name: my_pipeline
  steps:
    - type: my_step
      param: "value"
```

---

## Example Pipelines

### 📰 Daily News Digest

Fetch top stories from Hacker News:

```yaml
pipeline:
  name: news_digest
  steps:
    - type: http_get
      url: https://news.ycombinator.com/rss
    - type: grep
      pattern: "<title>"
    - type: replace
      pattern: "<[^>]+>"
      replacement: ""
    - type: write_file
      path: digest.md
```

### 📊 CSV Data Pipeline

Download, filter, and transform CSV data:

```yaml
pipeline:
  name: csv_pipeline
  steps:
    - type: download_file
      url: https://example.com/data.csv
    - type: read_file
    - type: parse_csv
    - type: filter_data
      field: country
      value: US
    - type: to_json
    - type: write_file
      path: filtered.json
```

### 🔌 API Integration

Fetch from API, transform, save:

```yaml
pipeline:
  name: api_integration
  steps:
    - type: http_get
      url: https://api.example.com/data
    - type: parse_json
    - type: to_yaml
    - type: write_file
      path: data.yml
```

[See more examples →](examples/)

---

## How It Works

### Pipeline Execution

Pipelines execute steps sequentially:

1. Load YAML configuration
2. Instantiate step classes from registry
3. Execute steps in order, passing data between them
4. Share state via context dictionary

```
initial_data → Step1 → Step2 → Step3 → final_result
                ↓       ↓       ↓
              context (shared state)
```

### Step Interface

Every step implements the same simple interface:

```python
class Step:
    def run(self, data: Any, context: dict[str, Any]) -> Any:
        """
        Args:
            data: Output from previous step
            context: Shared dictionary for state

        Returns:
            Data for next step
        """
```

### Context Sharing

Steps communicate via a shared context:

```python
# Step 1: Store data
context['user_count'] = 100

# Step 2: Read data
if context['user_count'] > 50:
    send_alert()
```

---

## CLI Commands

```bash
# List available apps
python main.py list-apps

# Inspect pipeline without running
python main.py inspect --config pipeline.yml

# Dry-run (show what would happen)
python main.py dry-run --config pipeline.yml

# Run pipeline
python main.py run --config pipeline.yml

# Create new app
python main.py create-app my_app

# Delete app
python main.py delete-app my_app

# Cache management
python main.py cache-info
python main.py cache-clear
```

---

## Comparison to Alternatives

| Feature | Bash Scripts | Bonesaw | Airflow | Prefect |
|---------|-------------|---------|---------|---------|
| **Setup Time** | 0 min | 5 min | 30+ min | 20+ min |
| **Learning Curve** | Low | Low | High | Medium |
| **Declarative Config** | ❌ | ✅ | ❌ | ❌ |
| **Type Safety** | ❌ | ✅ | ✅ | ✅ |
| **Built-in Steps** | ❌ | ✅ 30+ | ✅ Many | ✅ Many |
| **Caching** | Manual | ✅ Auto | ✅ | ✅ |
| **Web UI** | ❌ | ❌ | ✅ | ✅ |
| **Parallel Execution** | Manual | 🚧 | ✅ | ✅ |
| **Local First** | ✅ | ✅ | ❌ | ❌ |
| **Lines of Code** | Varies | ~3,000 | ~500,000 | ~200,000 |

**Bonesaw is for you if:**
- You outgrew bash scripts
- Airflow feels like overkill
- You want local-first automation
- You value simplicity and hackability

---

## Architecture

### Project Structure

```
bonesaw/
├── skeleton_core/          # Core framework
│   ├── pipeline.py         # Pipeline execution engine
│   ├── config.py          # Step registry & config loader
│   ├── cache.py           # Caching system
│   ├── cli.py             # CLI interface
│   ├── utils.py           # Utilities (path validation, etc.)
│   └── steps/             # Built-in steps
│       ├── file_ops.py    # File operations
│       ├── http_ops.py    # HTTP operations
│       ├── text_ops.py    # Text manipulation
│       └── data_ops.py    # Data transformation
├── apps/                  # Your custom pipelines
├── examples/              # Example pipelines
├── tests/                 # Test suite
└── main.py               # CLI entry point
```

### Core Components

- **Pipeline**: Orchestrates step execution
- **Step Registry**: Auto-discovers steps via decorators
- **Context**: Shared state dictionary
- **Cache**: Automatic result caching with TTL
- **CLI**: Typer-based command interface

---

## Advanced Usage

### Environment Variables

```bash
# LLM integration (optional)
export BONESAW_LLM_PROVIDER=openrouter
export BONESAW_LLM_MODEL=deepseek/deepseek-r1
export BONESAW_LLM_API_KEY=your_api_key
```

### Programmatic Usage

```python
from skeleton_core.config import build_pipeline_from_config, load_config

# Load pipeline from YAML
config = load_config('pipeline.yml')
pipeline = build_pipeline_from_config(config)

# Run it
result = pipeline.run(initial_data="Hello")
print(result)
```

### Testing Your Steps

```python
import pytest
from your_app.pipelines import YourStep

def test_your_step():
    step = YourStep(param="value")
    context = {}

    result = step.run(input_data, context)

    assert result == expected_output
    assert context['key'] == expected_value
```

---

## Roadmap

### ✅ Completed
- Core pipeline framework
- 30+ built-in steps
- Smart caching
- CLI commands
- Example pipelines

### 🚧 In Progress
- Async/parallel execution
- Watch mode (auto-rerun on changes)
- Web UI for visualization

### 💡 Planned
- Plugin marketplace
- More LLM providers
- Conditional steps
- Error retry policies
- Prometheus metrics
- Docker support

---

## Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass: `pytest`
5. Ensure code quality: `ruff check .`
6. Submit a pull request

### Adding New Built-in Steps

1. Create step in `skeleton_core/steps/`
2. Use `@register_step` decorator
3. Implement `run(data, context)` method
4. Add tests
5. Update documentation

---

## FAQ

**Q: Why "Bonesaw"?**
A: It cuts through complexity like a saw through bone. Also, spooky vibes.

**Q: Is this production-ready?**
A: Getting there! It's stable for personal use. We're hardening it for production.

**Q: Can I use this in production?**
A: Sure, but test thoroughly first. We recommend starting with non-critical workflows.

**Q: How does this compare to Luigi/Dagster/etc?**
A: Bonesaw is simpler and more hackable. Those tools are more feature-rich but heavier.

**Q: Can I contribute?**
A: Yes! See [CONTRIBUTING.md](CONTRIBUTING.md)

**Q: Why not just use Airflow?**
A: Airflow is amazing for large-scale orchestration. Bonesaw is for when you need something simpler.

---

## License

Mozilla Public License 2.0 (MPL-2.0)

### MPL-2.0 Summary
- **Permissions**: Commercial use, modification, distribution, patent use
- **Conditions**: Disclose source, include license, state changes
- **Limitations**: Liability, warranty

See [LICENSE](LICENSE) for full text.

---

## Acknowledgments

Built with:
- Python 3.11+
- Typer (CLI framework)
- PyYAML (configuration)
- Feedparser (RSS/Atom support)
- Pytest (testing)
- Ruff (code quality)

---

## Support

- 🐛 [Report bugs](https://github.com/yourusername/bonesaw/issues)
- 💬 [Discussions](https://github.com/yourusername/bonesaw/discussions)
- 📖 [Documentation](docs/)
- ⭐ [Star on GitHub](https://github.com/yourusername/bonesaw)

---

**Bonesaw** - YAML-powered automation that doesn't suck. 🦴🪚

*Made with ❤️ (and a bit of 💀) for developers who hate complexity*
