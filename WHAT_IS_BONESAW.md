# What Is Bonesaw?

**Bonesaw is a declarative pipeline automation framework** - think of it as "Make for data workflows" or "GitHub Actions for automation pipelines."

## What Does It Do?

Bonesaw lets you build automation workflows by chaining together reusable "steps" defined in simple YAML files. Each step does one thing well (fetch data, transform it, write files, etc.), and you connect them like LEGO blocks.

### Example: Daily News Digest

Instead of writing a Python script to:
1. Fetch an RSS feed
2. Parse the XML
3. Format it as markdown
4. Save to a file

You write a **5-step YAML pipeline**:

```yaml
pipeline:
  name: daily_news_digest
  steps:
    - type: http_get
      url: https://news.ycombinator.com/rss

    - type: parse_rss
      limit: 15

    - type: format_entries_markdown
      numbered: true

    - type: template
      template: |
        # Daily News Digest
        Generated: {context[timestamp]}
        {data}

    - type: write_file
      path: digest.md
```

Run it with: `python main.py run --config pipeline.yml`

## What Have We Built?

### Core Framework
- **Pipeline Engine** - Executes steps in order, passes data between them
- **Step Registry** - Auto-discovers and registers step types
- **Context System** - Shared state between steps
- **Error Handling** - Detailed error messages with step context
- **Type Safety** - Full Python type hints throughout

### 30+ Built-In Steps
- **HTTP Operations** - GET/POST requests, downloads, webhooks
- **File Operations** - Read, write, copy, move, delete, list files
- **Text Processing** - Grep, replace, split, join, templates, case conversion
- **Data Formats** - JSON, CSV, YAML, RSS/Atom parsing and serialization
- **Data Transformation** - Filtering, mapping, aggregation

### Smart Caching
- **TTL-based caching** - Cache expensive HTTP requests or computations
- **@cache_step decorator** - Add caching to any step with one line
- **CLI cache management** - View stats, clear old entries

### CLI Interface
- **Inspect pipelines** - See structure without running
- **Dry-run mode** - Preview execution with parameters
- **App scaffolding** - Generate new apps with `create-app`
- **Cache commands** - Manage cached data

### MCP Server
- **Model Context Protocol server** - Programmatic access to Bonesaw
- **Run pipelines via API** - Trigger pipelines remotely
- **List apps/pipelines** - Query available resources
- **Create/delete apps** - Manage apps programmatically

### Optional LLM Integration
- **Deterministic summaries** - Always works, no API required
- **LLM-enhanced summaries** - Optional AI-powered insights
- **Graceful fallbacks** - Never fails if LLM unavailable
- **OpenRouter support** - Works with Claude, GPT, etc.

## How to Use LLM Features

Set these environment variables:

```bash
export BONESAW_LLM_PROVIDER=openrouter
export BONESAW_LLM_API_KEY=sk-or-...
export BONESAW_LLM_MODEL=anthropic/claude-3-sonnet
```

Then run with `--use-llm` flag:

```bash
python main.py run --config pipeline.yml --use-llm
```

**What it does:**
- Adds AI-generated summaries to reports
- Works for logs, feeds, and text processing
- Falls back to deterministic summaries if not configured
- Costs ~$0.001-0.01 per summary (depending on model)

## What Makes Bonesaw Special?

### 1. **Declarative, Not Imperative**
Write WHAT you want, not HOW to do it:
```yaml
- type: http_get
  url: https://api.example.com
```
Instead of:
```python
import requests
response = requests.get("https://api.example.com")
if response.status_code != 200:
    raise Exception(...)
data = response.text
```

### 2. **Composable & Reusable**
Build complex workflows from simple, tested pieces. Share step configurations across projects.

### 3. **Type-Safe & Testable**
Full Python type hints. Each step has clear input/output contracts. Easy to unit test.

### 4. **Security-First**
- Path traversal protection
- Timeout on HTTP requests
- No arbitrary code execution from YAML
- Dependency pinning

### 5. **Spooky Themed** 🦴
Because automation should be fun. Halloween project roots show through!

## Common Use Cases

### Data Pipeline Automation
- Fetch data from APIs on schedule
- Transform and normalize data
- Generate reports
- Send notifications

### RSS/Feed Aggregation
- Collect posts from multiple feeds
- Filter by keywords
- Generate daily digests
- Archive to files or databases

### Log Processing
- Parse log files
- Filter errors
- Anonymize sensitive data
- Generate incident reports

### Backup & Maintenance
- List files matching patterns
- Copy to backup locations
- Clean old files
- Generate manifests

### API Integration
- Call multiple APIs in sequence
- Transform between formats (JSON ↔ YAML ↔ CSV)
- Combine data sources
- Cache responses

## Architecture

```
┌─────────────────────────────────────────┐
│  YAML Config                             │
│  ├─ pipeline: name                       │
│  └─ steps: [...]                         │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Config Loader                           │
│  ├─ Parse YAML                           │
│  ├─ Look up step types in registry       │
│  └─ Instantiate step classes             │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Pipeline Engine                         │
│  ├─ Initialize context {}                │
│  ├─ For each step:                       │
│  │   ├─ Log progress                     │
│  │   ├─ data = step.run(data, context)   │
│  │   └─ Handle errors                    │
│  └─ Return final result                  │
└─────────────────────────────────────────┘
```

Each step is a Python class with a `run(data, context)` method. Steps read from `data`, write to `context`, and return new data for the next step.

## Project Status

✅ **Core framework complete** - Stable and tested (11/11 tests passing)
✅ **30+ built-in steps** - Cover most common use cases
✅ **CLI interface** - Full-featured command line tool
✅ **MCP server** - Programmatic access
✅ **LLM integration** - Optional AI enhancement
✅ **Caching system** - Smart performance optimization
✅ **Example pipelines** - 5 working examples
✅ **Documentation** - README, docstrings, examples

## Future Possibilities

### Core Features
- **Parallel execution** - Run independent steps concurrently
- **Conditional steps** - If/else logic in pipelines
- **Loop steps** - Iterate over data
- **Sub-pipelines** - Call pipelines from pipelines
- **Step dependencies** - Define execution order constraints

### Integration
- **Database steps** - SQLite, PostgreSQL, MongoDB
- **Email steps** - Send/receive emails
- **Cloud steps** - S3, GCS, Azure blob storage
- **Notification steps** - Slack, Discord, Telegram
- **Git steps** - Clone, commit, push

### Developer Experience
- **VS Code extension** - Syntax highlighting, validation
- **Step generator CLI** - Scaffold new steps
- **Pipeline visualizer** - See data flow graphically
- **Hot reload** - Auto-restart on config changes
- **Step marketplace** - Share custom steps

### Production Features
- **Scheduling** - Cron-like execution
- **Retries & circuit breakers** - Fault tolerance
- **Metrics & monitoring** - Prometheus integration
- **Secrets management** - Vault/KMS integration
- **Multi-tenancy** - Run pipelines for different users

## Bottom Line

**Bonesaw is a Python framework for building automation pipelines declaratively.**

It's like Make, GitHub Actions, or Airflow - but focused on **simplicity and composability** for individual developers and small teams who want to automate repetitive tasks without writing boilerplate code.

Instead of writing 50 lines of Python to fetch an API, parse JSON, filter data, and save to a file... you write 10 lines of YAML.

It's **production-ready for personal use**, **extensible for custom steps**, and **has room to grow** into a full workflow orchestration platform.

---

**TL;DR:** Bonesaw = Automation workflows as YAML files. Chain together 30+ built-in steps (HTTP, files, text, data formats) to build pipelines. Optional LLM integration for smart summaries. Think "Make for data workflows."
