# 🩸 Haunted Log Cleaner

A Bonesaw application for processing, anonymizing, and analyzing log files.

## What It Does

Haunted Log Cleaner demonstrates the power of the Bonesaw pipeline framework by processing messy log files through a series of composable steps:

1. **Load Logs**: Reads raw log file contents
2. **Parse Logs**: Extracts structured data (timestamp, level, message) from log lines
3. **Anonymize Logs**: Redacts sensitive information (emails, IP addresses)
4. **Aggregate Errors**: Computes statistics by log level
5. **Write Markdown Report**: Generates a formatted report with summary tables
6. **LLM Summary**: Adds a spooky AI-generated summary (stubbed for demo)

## How It Uses Bonesaw

This app showcases the Bonesaw skeleton framework:

- **Step Registration**: Each processing step is a class decorated with `@register_step()`
- **Composable Pipeline**: Steps are chained together via YAML configuration
- **Shared Context**: Steps communicate through a shared context dictionary
- **Data Flow**: Each step receives the previous step's output and returns data for the next

All step implementations live in `pipelines.py`, keeping the core framework generic and reusable.

## Running the Application

### Prerequisites

```bash
pip install -r requirements.txt
```

### Execute the Pipeline

```bash
python main.py run --app haunted_log_cleaner --config apps/haunted_log_cleaner/config.example.yml
```

### Output

The pipeline generates a markdown report at:
```
apps/haunted_log_cleaner/output_report.md
```

The report includes:
- Total log entry count
- Breakdown by log level (INFO, WARNING, ERROR)
- Sample log messages
- AI-generated summary (spooky! 👻)

## Sample Data

The `sample_logs.log` file contains 15 log entries with:
- Mixed log levels (INFO, WARNING, ERROR)
- Sensitive data (emails, IP addresses) that get anonymized
- Multiple ERROR entries to make the report interesting

## Customization

To process your own logs:

1. Update the `path` in `config.example.yml` to point to your log file
2. Modify the `output_path` if you want a different report location
3. Run the pipeline!

The log parser expects this format:
```
YYYY-MM-DD HH:MM:SS [LEVEL] message text
```

## Architecture

```
Load → Parse → Anonymize → Aggregate → Report → Summary
```

Each arrow represents data flowing from one step to the next, with the shared context available to all steps for metadata and statistics.
