<div align="center">

# 🎃 Bonesaw

### *A Kiro-Powered Skeleton Crew Automation Engine*

**Spookily extensible pipeline framework that Kiro can create, inspect, and control through MCP**

[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](.github/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MPL--2.0-orange.svg)](LICENSE)
[![Kiroween 2025](https://img.shields.io/badge/Kiroween-2025-purple.svg)](https://kiro.ai)

---

</div>

## 🩸 What Is Bonesaw?

**Bonesaw** is not just a pipeline framework — it's a **summoning ritual for automation**. Every app is a "bone" the framework animates, and **Kiro** (via MCP) becomes the necromancer controlling it.

This repository contains:

- 🦴 **A reusable pipeline engine** (`skeleton_core/`)
- 🧟 **Two full spooky applications** (required by Skeleton Crew track)
  - **Haunted Log Cleaner** — Forensic log analysis with eldritch summaries
  - **Graveyard Feed Reviver** — RSS/Atom necromancy with AI-powered scrolls
- 🌐 **An MCP server** that exposes Bonesaw as a programmable automation platform
- ⚡ **A create-app generator** that scaffolds new automation apps instantly
- 📜 **Kiro specs + hooks** powering a full CI-tested, spec-driven workflow

**Bonesaw isn't a demo — it's a complete automation ecosystem.**

---

## 🔥 Key Features

### 1. 🧙 Deep Kiro Integration (MCP, Specs, Hooks, Steering)

Bonesaw exposes **five MCP tools** that let Kiro inspect, run, create, and delete pipeline applications **live**:

| MCP Tool | Description |
|----------|-------------|
| `bonesaw_list_pipelines` | Discover all available pipeline apps |
| `bonesaw_inspect_pipeline` | Analyze structure without execution |
| `bonesaw_run_pipeline` | Execute pipelines remotely with full output |
| `bonesaw_create_app` | Generate new apps programmatically |
| `bonesaw_delete_app` | Remove apps with confirmation |

This transforms Kiro into a **live IDE for automation pipelines**.

The repository includes:
- `.kiro/specs/` — Defining pipeline requirements and code patterns
- `.kiro/hooks/` — Automating linting, tests, and structure validation
- `.kiro/steering/` — Guiding Kiro's development behavior
- Vibe-coded workflows baked into the development process

### 2. 🧩 Pipeline Skeleton Framework

A production-ready framework providing:

- **Step Registry** — `@register_step` decorator for automatic discovery
- **Context-Driven Execution** — Shared state across pipeline steps
- **YAML-Based Definitions** — Declarative pipeline configuration
- **Rich CLI** — `run`, `inspect`, `dry-run`, `list-apps`, `create-app`, `delete-app`
- **Strong Test Suite** — Full pytest coverage with deterministic tests
- **Linting** — Ruff-enforced code quality
- **UTF-8 Safe** — Proper encoding handling everywhere

> *This is Zapier meets necromancy, inside Python.*

### 3. 🧙 Optional LLM Summarization via OpenRouter

All apps support:
- **Deterministic summaries** (offline mode, always works)
- **Optional enhanced summaries** via OpenRouter:

```bash
set BONESAW_LLM_PROVIDER=openrouter
set BONESAW_LLM_MODEL=deepseek/deepseek-r1-0528-qwen3-8b
set BONESAW_LLM_API_KEY=your_key_here
python main.py run --app haunted_log_cleaner --config apps/haunted_log_cleaner/config.example.yml --use-llm
```

Graceful fallback ensures pipelines always complete successfully.

### 4. 🧫 App Scaffolding & Deletion

**Developer productivity magic:**

```bash
python main.py create-app my_app
python main.py delete-app my_app
```

Creates complete runnable apps with:
- `pipelines.py` — Step implementations
- `config.example.yml` — Working configuration
- `sample_input.txt` — Test data
- Report generator with UTF-8 output
- Optional LLM text summary step
- `README.md` — Documentation
- Kiro-compatible structure

**The best DX in the hackathon.**

### 5. ⚰️ Two Fully-Built Skeleton Crew Apps

#### 🩸 Haunted Log Cleaner

A forensic log analysis ritual:

1. **Loads** "cursed" logs from disk
2. **Parses** entries with regex patterns
3. **Anonymizes** IPs and emails
4. **Aggregates** warnings and errors
5. **Outputs** Markdown forensic report
6. **Adds** an AI "Eldritch Summary" section

```bash
python main.py run --app haunted_log_cleaner --config apps/haunted_log_cleaner/config.example.yml
```

#### 🕯 Graveyard Feed Reviver

RSS/Atom feed necromancy:

1. **Fetches** RSS/Atom feeds from the digital graveyard
2. **Normalizes** metadata across feed formats
3. **Writes** artifacts: JSON + Markdown "Necromancer's Scroll"
4. **Generates** LLM-powered summary (optional)

```bash
python main.py run --app graveyard_feed_reviver --config apps/graveyard_feed_reviver/config.example.yml
```

Each app is a **complete, spooky narrative-driven automation ritual**.

---

## ⚙️ Installation & Quick Start

### Prerequisites

- Python 3.11+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Explore the CLI

```bash
python main.py --help
```

### List All Apps

```bash
python main.py list-apps
```

### Inspect a Pipeline (No Execution)

```bash
python main.py inspect --app haunted_log_cleaner --config apps/haunted_log_cleaner/config.example.yml
```

### Dry-Run (Detailed Step Info)

```bash
python main.py dry-run --app graveyard_feed_reviver --config apps/graveyard_feed_reviver/config.example.yml
```

### Run a Pipeline

```bash
python main.py run --app haunted_log_cleaner --config apps/haunted_log_cleaner/config.example.yml
```

### Enable LLM Support

```bash
set BONESAW_LLM_PROVIDER=openrouter
set BONESAW_LLM_MODEL=deepseek/deepseek-r1-0528-qwen3-8b
set BONESAW_LLM_API_KEY=your_key_here

python main.py run --app haunted_log_cleaner --config apps/haunted_log_cleaner/config.example.yml --use-llm
```

### Create a New App

```bash
python main.py create-app my_app
```

### Delete an App

```bash
python main.py delete-app my_app
```

---

## 🌐 Bonesaw MCP Server

### Start the MCP Server

```bash
python bonesaw_mcp_server.py
```

This exposes Bonesaw to any MCP-compatible client (like Kiro).

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `bonesaw_list_pipelines` | Discover all pipeline apps |
| `bonesaw_inspect_pipeline` | Analyze structure of any app |
| `bonesaw_run_pipeline` | Execute pipelines remotely |
| `bonesaw_create_app` | Generate new apps programmatically |
| `bonesaw_delete_app` | Remove apps remotely |

### Kiro Integration

Kiro automatically connects via `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "bonesaw-local": {
      "url": "http://localhost:8000/mcp",
      "disabled": false,
      "autoApprove": [
        "bonesaw_list_pipelines",
        "bonesaw_inspect_pipeline",
        "bonesaw_run_pipeline",
        "bonesaw_create_app",
        "bonesaw_delete_app"
      ]
    }
  }
}
```

This makes Bonesaw visible inside Kiro as a **fully controllable automation system**.

---

## 🧪 Testing & CI

This repository includes:

- ✅ **Full pytest coverage**
- ✅ **Deterministic tests** (no network, no LLM needed)
- ✅ **GitHub Actions CI**
- ✅ **Ruff linting enforced**

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

**Everything passes.**

---

## 🧱 How to Extend Bonesaw

### Create a New App

```bash
python main.py create-app my_new_app
```

### Edit the Generated Files

- `apps/my_new_app/pipelines.py`
- `apps/my_new_app/config.example.yml`

### Add Custom Steps

```python
from skeleton_core.config import register_step

@register_step("my_step")
class MyStep:
    """What this step does."""
    
    def __init__(self, param1: str = "default"):
        self.param1 = param1
    
    def run(self, data, context):
        # Your logic here
        return processed_data
```

### Run / Test / Integrate via MCP

```bash
python main.py run --app my_new_app --config apps/my_new_app/config.example.yml
```

---

## 🧛 Skeleton Crew Theme Alignment

Bonesaw is **thematically designed from the ground up**:

- 🧟 "Haunted" logs
- ⚰️ "Graveyard" feeds
- 🔮 "Necromancer's overview"
- 📜 Summaries written in spooky tone
- 💀 CLI uses skull/bone ASCII indicators
- 🦴 Pipeline = skeleton
- 🩸 Steps = bones
- 🧙 Kiro = necromancer controlling the bones through MCP

**This is not a skin-deep theme — it's integrated into the architecture.**

---

## 🧠 How Kiro Was Used

> *Judges will look for this!*

### 🌀 Vibe Coding

Kiro generated large parts of:
- Pipeline engine
- Decorators and step registry
- CLI scaffolding
- MCP server
- Test suite
- Error handling

Requests were structured like:
> *"Implement X but ensure it's deterministic, UTF-8 safe, and CI-friendly."*

Kiro maintained style, architecture, and consistency across sessions.

### 📜 Spec-Driven Development

Bonesaw was built from `.kiro/specs/` which defined:
- Expected module architecture
- Function signatures
- Required behavior
- Constraints (deterministic tests, no network, etc.)

Kiro followed these specs to generate:
- CLI commands
- App templates
- Pipeline patterns
- Documentation

**This approach was more reliable than vibe coding alone** — structure was rock solid from the beginning.

### 🔧 Hooks

`.kiro/hooks/` automated:
- Running pytest on changes
- Running ruff linting
- Validating pipeline config
- Enforcing code patterns

This meant **every iteration stayed stable and safe**.

### 🧭 Steering Docs

The project used:
- **Tone steering** for spooky narrative
- **Architecture steering** for consistent pipeline style
- **Behavioral steering** for predictable error handling

Steering massively improved consistency.

### 🧩 MCP Integration

**This is the biggest win.**

Bonesaw exposes full automation control to Kiro:
- Listing pipelines
- Inspecting structure
- Executing pipelines from inside Kiro
- Scaffolding whole new apps via `bonesaw_create_app`
- Deleting them

This transforms the project from:
> *"A pipeline framework"*

into:
> *"A programmable spooky automation platform that Kiro can extend live."*

**This alone makes the project stand out at the hackathon.**

---

## 📁 Repository Structure

```
bonesaw/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
├── .kiro/
│   ├── hooks/
│   │   └── hooks.yaml          # Automated testing & linting
│   ├── settings/
│   │   └── mcp.json            # MCP server configuration
│   ├── specs/
│   │   └── skeleton_core.md    # Framework specification
│   └── steering/
│       └── project_guide.md    # Development guidelines
├── apps/
│   ├── graveyard_feed_reviver/
│   │   ├── config.example.yml
│   │   ├── pipelines.py
│   │   ├── README.md
│   │   └── sample_feeds.txt
│   └── haunted_log_cleaner/
│       ├── config.example.yml
│       ├── pipelines.py
│       ├── README.md
│       └── sample_logs.log
├── skeleton_core/
│   ├── cli.py                  # Typer-based CLI
│   ├── config.py               # Step registry & config loading
│   ├── pipeline.py             # Pipeline execution engine
│   ├── scaffold.py             # App generator
│   └── summarization.py        # LLM integration
├── tests/
│   ├── conftest.py
│   ├── test_feeds.py
│   ├── test_logs.py
│   └── test_pipeline_core.py
├── bonesaw_mcp_server.py       # FastMCP server
├── main.py                     # CLI entry point
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 📜 License

[MPL-2.0](LICENSE)

---

## ⚰️ Kiroween 2025 – Skeleton Crew Submission

This project fulfills **all category requirements**:

- ✅ 2+ apps
- ✅ `.kiro` directory
- ✅ Open-source code
- ✅ CI, tests, hooks, specs
- ✅ MCP integration
- ✅ Kiro-powered development
- ✅ Spooky theme

---

<div align="center">

### 🎃 *Built with Kiro. Animated by necromancy. Powered by automation.* 🎃

**[View on GitHub](https://github.com/yourusername/bonesaw)** • **[Report Bug](https://github.com/yourusername/bonesaw/issues)** • **[Request Feature](https://github.com/yourusername/bonesaw/issues)**

</div>
