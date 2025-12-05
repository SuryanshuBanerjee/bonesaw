"""
Graveyard Feed Reviver - Pipeline steps for fetching and processing RSS/Atom feeds.

This module defines all the steps needed to resurrect old feeds, normalize their
entries, and output them as JSON and markdown grimoires.
"""

import json
import logging
from typing import Any

import feedparser

from skeleton_core.config import register_step
from skeleton_core.summarization import summarize_feeds

logger = logging.getLogger(__name__)


@register_step("load_feed_urls")
class LoadFeedURLsStep:
    """
    Load feed URLs from a text file.
    
    Input: None (or ignored)
    Output: list[str] of feed URLs
    Context: Writes 'url_count' with number of URLs loaded
    """
    
    def __init__(self, path: str):
        """
        Initialize the URL loader.
        
        Args:
            path: Filesystem path to text file containing URLs (one per line)
        """
        self.path = path
    
    def run(self, data: Any, context: dict[str, Any]) -> list[str]:
        """Load feed URLs from file."""
        logger.info(f"Loading feed URLs from {self.path}")
        
        urls = []
        with open(self.path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    urls.append(line)
        
        context['url_count'] = len(urls)
        logger.info(f"Loaded {len(urls)} feed URLs")
        
        return urls


@register_step("fetch_feeds")
class FetchFeedsStep:
    """
    Fetch RSS/Atom feeds from URLs and extract entries.
    
    Input: list[str] of feed URLs
    Output: list[dict] of feed entries with metadata
    Context: Writes 'feeds_fetched' and 'total_entries'
    """
    
    def run(self, data: Any, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch feeds and extract entries."""
        urls = data
        all_entries = []
        feeds_fetched = 0
        
        logger.info(f"Fetching {len(urls)} feeds")
        
        for url in urls:
            logger.info(f"Fetching feed: {url}")
            
            try:
                feed = feedparser.parse(url)
                
                # Get feed-level metadata
                feed_title = feed.feed.get('title', 'Unknown Feed')
                
                # Extract entries
                for entry in feed.entries:
                    all_entries.append({
                        'feed_title': feed_title,
                        'entry_title': entry.get('title', 'Untitled'),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', None),
                        'summary': entry.get('summary', None)
                    })
                
                feeds_fetched += 1
                logger.info(f"Extracted {len(feed.entries)} entries from {feed_title}")
                
            except Exception as e:
                logger.error(f"Failed to fetch feed {url}: {e}")
        
        context['feeds_fetched'] = feeds_fetched
        context['total_entries'] = len(all_entries)
        
        logger.info(f"Fetched {feeds_fetched} feeds with {len(all_entries)} total entries")
        
        return all_entries


@register_step("normalize_entries")
class NormalizeEntriesStep:
    """
    Normalize feed entries to ensure consistent structure.
    
    Ensures all entries have the required fields with proper defaults.
    
    Input: list[dict] of raw feed entries
    Output: list[dict] of normalized entries
    Context: Writes 'normalized_count'
    """
    
    def run(self, data: Any, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Normalize feed entries."""
        entries = data
        
        logger.info(f"Normalizing {len(entries)} entries")
        
        normalized = []
        for entry in entries:
            normalized.append({
                'feed_title': entry.get('feed_title', 'Unknown Feed'),
                'entry_title': entry.get('entry_title', 'Untitled'),
                'link': entry.get('link', ''),
                'published': entry.get('published', None),
                'summary': entry.get('summary', None)
            })
        
        context['normalized_count'] = len(normalized)
        logger.info(f"Normalized {len(normalized)} entries")
        
        return normalized


@register_step("write_json")
class WriteJSONStep:
    """
    Write feed entries to a JSON file.
    
    Input: list[dict] of normalized entries
    Output: Same list (pass-through)
    Context: Writes 'json_path' with output file path
    """
    
    def __init__(self, output_path: str):
        """
        Initialize the JSON writer.
        
        Args:
            output_path: Path where JSON file will be written
        """
        self.output_path = output_path
    
    def run(self, data: Any, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Write entries to JSON file."""
        entries = data
        
        logger.info(f"Writing {len(entries)} entries to JSON: {self.output_path}")
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        
        context['json_path'] = self.output_path
        logger.info("JSON file written successfully")
        
        return entries


@register_step("write_markdown")
class WriteMarkdownStep:
    """
    Generate a markdown grimoire from feed entries.
    
    Input: list[dict] of normalized entries
    Output: Same list (pass-through)
    Context: Writes 'markdown_path' with output file path
    """
    
    def __init__(self, output_path: str):
        """
        Initialize the markdown writer.
        
        Args:
            output_path: Path where markdown file will be written
        """
        self.output_path = output_path
    
    def run(self, data: Any, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate and write markdown grimoire."""
        entries = data
        
        logger.info(f"Writing {len(entries)} entries to markdown: {self.output_path}")
        
        lines = [
            "# ☠️ Graveyard Feed Reviver",
            "",
            f"Resurrected {len(entries)} entries from the digital graveyard.",
            ""
        ]
        
        # Group entries by feed for better organization
        by_feed: dict[str, list[dict[str, Any]]] = {}
        for entry in entries:
            feed_title = entry['feed_title']
            if feed_title not in by_feed:
                by_feed[feed_title] = []
            by_feed[feed_title].append(entry)
        
        # Write entries grouped by feed
        for feed_title, feed_entries in by_feed.items():
            lines.append(f"## 📡 {feed_title}")
            lines.append("")
            
            for entry in feed_entries:
                lines.append(f"### 🧟 {entry['entry_title']}")
                lines.append("")
                
                if entry['link']:
                    lines.append(f"**Link:** {entry['link']}")
                    lines.append("")
                
                if entry['published']:
                    lines.append(f"**Published:** {entry['published']}")
                    lines.append("")
                
                if entry['summary']:
                    # Truncate long summaries
                    summary = entry['summary']
                    if len(summary) > 300:
                        summary = summary[:297] + "..."
                    lines.append(f"{summary}")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        # Write to file
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        context['markdown_path'] = self.output_path
        logger.info("Markdown grimoire written successfully")
        
        return entries


@register_step("feed_llm_summary")
class FeedLLMSummaryStep:
    """
    Generate an LLM-style overview of resurrected feeds (stubbed).
    
    This step demonstrates where an LLM API call would go. For now,
    it generates a fake necromancer's overview based on the entries.
    
    Input: list[dict] of normalized entries
    Output: Same list (pass-through)
    Context: Writes 'llm_overview' with generated text
    """
    
    def __init__(self, output_path: str):
        """
        Initialize the LLM summary generator.
        
        Args:
            output_path: Path to append the overview to
        """
        self.output_path = output_path
    
    def run(self, data: Any, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate and append necromancer's overview."""
        entries = data
        
        logger.info("Generating feed summary")
        
        # Use the robust summarization system
        summary_text = summarize_feeds(entries, context)
        
        # Append to the existing markdown file
        with open(self.output_path, 'a', encoding='utf-8') as f:
            f.write("\n## 🧙 Necromancer's Overview\n\n")
            f.write(summary_text)
            f.write("\n")
        
        context['llm_overview'] = summary_text
        logger.info("Summary appended to grimoire")
        
        return entries
