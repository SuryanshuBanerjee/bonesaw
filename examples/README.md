# 🦴 Bonesaw Example Pipelines 🦴

Real-world examples showcasing Bonesaw's capabilities.

## Examples

### 📰 [Daily News Digest](daily_news_digest/)
Fetch and compile top tech news from Hacker News.
```bash
python main.py run --config examples/daily_news_digest/pipeline.yml
```

### 📊 [CSV Data Pipeline](csv_processor/)
Download, process, and transform CSV data automatically.
```bash
python main.py run --config examples/csv_processor/pipeline.yml
```

### 💾 [Backup Automation](backup_automation/)
Find and catalog files for backup.
```bash
python main.py run --config examples/backup_automation/pipeline.yml
```

### 🌐 [Website Monitor](website_monitor/)
Check website status and generate reports.
```bash
python main.py run --config examples/website_monitor/pipeline.yml
```

### 🔌 [API Integration](api_integration/)
Fetch from API, transform between JSON/YAML formats.
```bash
python main.py run --config examples/api_integration/pipeline.yml
```

## Built-in Steps Used

All examples use Bonesaw's batteries-included steps:

**File Operations**: `read_file`, `write_file`, `list_files`
**HTTP Operations**: `http_get`, `download_file`
**Text Operations**: `grep`, `replace`, `template`
**Data Operations**: `parse_json`, `parse_csv`, `parse_yaml`, `to_json`, `to_csv`, `to_yaml`, `filter_data`

## Create Your Own

```bash
python main.py create-app my_pipeline
```

Then edit the generated files in `apps/my_pipeline/`
