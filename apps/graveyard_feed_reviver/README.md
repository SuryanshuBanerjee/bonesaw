# ☠️ Graveyard Feed Reviver

A Bonesaw application for resurrecting old RSS/Atom feeds into structured JSON and markdown grimoires.

## What It Does

Graveyard Feed Reviver demonstrates the versatility of the Bonesaw pipeline framework by fetching external data sources and transforming them through a series of steps:

1. **Load Feed URLs**: Reads a list of RSS/Atom feed URLs from a text file
2. **Fetch Feeds**: Uses `feedparser` to retrieve feed contents from the web
3. **Normalize Entries**: Ensures all entries have consistent structure and fields
4. **Write JSON**: Outputs structured data as JSON for programmatic access
5. **Write Markdown**: Generates a human-readable markdown grimoire
6. **LLM Summary**: Adds a necromancer's overview (stubbed for demo)

## How It Uses Bonesaw

This app showcases the same Bonesaw skeleton framework as Haunted Log Cleaner, but for a completely different domain:

- **Step Registration**: Each processing step is registered with `@register_step()`
- **External Data**: Demonstrates fetching data from external sources (RSS feeds)
- **Multiple Outputs**: Shows how one pipeline can generate multiple output formats (JSON + Markdown)
- **Shared Context**: Steps communicate statistics through the context dictionary
- **Composability**: The same core framework handles both log processing and feed aggregation

All step implementations live in `pipelines.py`, keeping the core framework domain-agnostic.

## Running the Application

### Prerequisites

```bash
pip install -r requirements.txt
```

The `feedparser` library is required for RSS/Atom parsing.

### Execute the Pipeline

```bash
python main.py run --app graveyard_feed_reviver --config apps/graveyard_feed_reviver/config.example.yml
```

### Output

The pipeline generates two files:

1. **JSON output**: `apps/graveyard_feed_reviver/output_feeds.json`
   - Structured data for programmatic access
   - Array of normalized feed entries

2. **Markdown grimoire**: `apps/graveyard_feed_reviver/output_feeds.md`
   - Human-readable format
   - Organized by feed source
   - Includes necromancer's overview 💀

## Sample Data

The `sample_feeds.txt` file contains three public RSS feeds:
- Hacker News (top stories)
- Reddit r/programming
- Python.org blog

You can add your own feeds by adding URLs (one per line) to this file.

## Customization

To resurrect your own feeds:

1. Edit `sample_feeds.txt` to include your feed URLs
2. Update the `path` in `config.example.yml` if using a different file
3. Modify `output_path` values for JSON and markdown outputs
4. Run the pipeline!

The app handles both RSS and Atom formats automatically via `feedparser`.

## Architecture

```
Load URLs → Fetch Feeds → Normalize → Write JSON → Write Markdown → Summary
```

Each arrow represents data flowing from one step to the next. The pipeline fetches live data from the web and transforms it into multiple output formats, all orchestrated by the Bonesaw framework.

## Use Cases

- Archiving old or dying feeds
- Aggregating multiple feeds into a single document
- Converting RSS/Atom to JSON for further processing
- Creating readable summaries of feed content
- Monitoring feed changes over time (with scheduled runs)
