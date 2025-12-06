# Daily News Digest 🗞️

Automatically fetch and compile top tech news from Hacker News.

## What it does

1. Fetches HN RSS feed
2. Extracts story titles
3. Formats as markdown
4. Saves daily digest

## Run it

```bash
python main.py run --config examples/daily_news_digest/pipeline.yml
```

## Automate it

Add to cron (Linux/Mac):
```bash
# Run every morning at 8am
0 8 * * * cd /path/to/bonesaw && python main.py run --config examples/daily_news_digest/pipeline.yml
```

Windows Task Scheduler:
```bash
schtasks /create /tn "Daily News" /tr "python C:\path\to\main.py run --config examples/daily_news_digest/pipeline.yml" /sc daily /st 08:00
```

## Customize

Edit `pipeline.yml`:
- Change RSS feed URL
- Adjust number of stories
- Add email notification step
- Customize markdown template
