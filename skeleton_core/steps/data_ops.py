"""
Data operation steps for Bonesaw.

Provides steps for working with structured data (JSON, CSV, YAML, RSS/Atom).
"""

import csv
import json
import logging
from io import StringIO
from typing import Any, Optional

import feedparser
import yaml

from skeleton_core.config import register_step

logger = logging.getLogger(__name__)


@register_step("parse_json")
class ParseJSONStep:
    """
    Parse JSON string to Python object.

    Input: str (JSON text)
    Output: dict or list (parsed JSON)
    Context: None
    """

    def run(self, data: Any, context: dict[str, Any]) -> Any:
        """Parse JSON."""
        json_text = str(data)

        logger.info(f"Parsing JSON ({len(json_text)} chars)")

        result = json.loads(json_text)

        logger.info("Parsed successfully")
        return result


@register_step("to_json")
class ToJSONStep:
    """
    Convert Python object to JSON string.

    Input: Any (Python object)
    Output: str (JSON text)
    Context: Writes 'output_size'
    """

    def __init__(self, indent: Optional[int] = 2, ensure_ascii: bool = False):
        """
        Args:
            indent: JSON indentation (None for compact)
            ensure_ascii: Whether to escape non-ASCII characters
        """
        self.indent = indent
        self.ensure_ascii = ensure_ascii

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Convert to JSON."""
        logger.info("Converting to JSON")

        result = json.dumps(data, indent=self.indent, ensure_ascii=self.ensure_ascii)

        context['output_size'] = len(result)

        logger.info(f"Generated {len(result)} chars")
        return result


@register_step("parse_yaml")
class ParseYAMLStep:
    """
    Parse YAML string to Python object.

    Input: str (YAML text)
    Output: dict or list (parsed YAML)
    Context: None
    """

    def run(self, data: Any, context: dict[str, Any]) -> Any:
        """Parse YAML."""
        yaml_text = str(data)

        logger.info(f"Parsing YAML ({len(yaml_text)} chars)")

        result = yaml.safe_load(yaml_text)

        logger.info("Parsed successfully")
        return result


@register_step("to_yaml")
class ToYAMLStep:
    """
    Convert Python object to YAML string.

    Input: Any (Python object)
    Output: str (YAML text)
    Context: Writes 'output_size'
    """

    def __init__(self, default_flow_style: bool = False):
        """
        Args:
            default_flow_style: Use flow style (inline) formatting
        """
        self.default_flow_style = default_flow_style

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Convert to YAML."""
        logger.info("Converting to YAML")

        result = yaml.dump(data, default_flow_style=self.default_flow_style)

        context['output_size'] = len(result)

        logger.info(f"Generated {len(result)} chars")
        return result


@register_step("parse_csv")
class ParseCSVStep:
    """
    Parse CSV string to list of dicts.

    Input: str (CSV text)
    Output: list[dict] (rows)
    Context: Writes 'row_count', 'column_count'
    """

    def __init__(self, has_header: bool = True, delimiter: str = ','):
        """
        Args:
            has_header: Whether first row is header
            delimiter: CSV delimiter
        """
        self.has_header = has_header
        self.delimiter = delimiter

    def run(self, data: Any, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse CSV."""
        csv_text = str(data)

        logger.info(f"Parsing CSV ({len(csv_text)} chars)")

        reader = csv.DictReader(
            StringIO(csv_text),
            delimiter=self.delimiter
        ) if self.has_header else csv.reader(StringIO(csv_text), delimiter=self.delimiter)

        rows = list(reader)

        context['row_count'] = len(rows)
        if rows and isinstance(rows[0], dict):
            context['column_count'] = len(rows[0])

        logger.info(f"Parsed {len(rows)} rows")
        return rows


@register_step("to_csv")
class ToCSVStep:
    """
    Convert list of dicts to CSV string.

    Input: list[dict] (rows)
    Output: str (CSV text)
    Context: Writes 'row_count', 'output_size'
    """

    def __init__(self, delimiter: str = ','):
        """
        Args:
            delimiter: CSV delimiter
        """
        self.delimiter = delimiter

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Convert to CSV."""
        rows = list(data)

        logger.info(f"Converting {len(rows)} rows to CSV")

        if not rows:
            return ""

        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=rows[0].keys(),
            delimiter=self.delimiter
        )

        writer.writeheader()
        writer.writerows(rows)

        result = output.getvalue()

        context['row_count'] = len(rows)
        context['output_size'] = len(result)

        logger.info(f"Generated {len(result)} chars")
        return result


@register_step("filter_data")
class FilterDataStep:
    """
    Filter list items using a simple condition.

    Input: list[dict] (items)
    Output: list[dict] (filtered items)
    Context: Writes 'input_count', 'output_count'
    """

    def __init__(self, field: str, value: Any = None, condition: str = 'equals'):
        """
        Args:
            field: Field name to check
            value: Value to compare against
            condition: Comparison type ('equals', 'contains', 'gt', 'lt', 'exists')
        """
        self.field = field
        self.value = value
        self.condition = condition

    def run(self, data: Any, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Filter data."""
        items = list(data)

        logger.info(f"Filtering {len(items)} items by {self.field} {self.condition} {self.value}")

        filtered = []
        for item in items:
            field_value = item.get(self.field)

            keep = False
            if self.condition == 'equals':
                keep = field_value == self.value
            elif self.condition == 'contains':
                keep = self.value in str(field_value)
            elif self.condition == 'gt':
                keep = field_value > self.value
            elif self.condition == 'lt':
                keep = field_value < self.value
            elif self.condition == 'exists':
                keep = self.field in item

            if keep:
                filtered.append(item)

        context['input_count'] = len(items)
        context['output_count'] = len(filtered)

        logger.info(f"Kept {len(filtered)} items")
        return filtered


@register_step("parse_rss")
class ParseRSSStep:
    """
    Parse RSS/Atom feed from XML string.

    Input: str (RSS/Atom XML)
    Output: list[dict] (parsed entries with title, link, published, summary)
    Context: Writes 'feed_title', 'entry_count'
    """

    def __init__(self, limit: Optional[int] = None):
        """
        Args:
            limit: Maximum number of entries to return (None for all)
        """
        self.limit = limit

    def run(self, data: Any, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse RSS/Atom feed."""
        xml_text = str(data)

        logger.info(f"Parsing RSS/Atom feed ({len(xml_text)} chars)")

        feed = feedparser.parse(xml_text)

        # Extract feed metadata
        feed_title = feed.feed.get('title', 'Unknown Feed')
        context['feed_title'] = feed_title

        # Extract entries
        entries = []
        for entry in feed.entries[:self.limit] if self.limit else feed.entries:
            entries.append({
                'title': entry.get('title', 'Untitled'),
                'link': entry.get('link', ''),
                'published': entry.get('published', entry.get('updated', '')),
                'summary': entry.get('summary', entry.get('description', ''))[:200]
            })

        context['entry_count'] = len(entries)

        logger.info(f"Parsed {len(entries)} entries from '{feed_title}'")
        return entries


@register_step("format_entries_markdown")
class FormatEntriesMarkdownStep:
    """
    Format parsed feed entries as markdown list.

    Input: list[dict] (entries with title, link, published, summary keys)
    Output: str (markdown-formatted text)
    Context: None
    """

    def __init__(self, include_summary: bool = False, numbered: bool = False):
        """
        Args:
            include_summary: Include entry summaries
            numbered: Use numbered list instead of bullets
        """
        self.include_summary = include_summary
        self.numbered = numbered

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Format entries as markdown."""
        entries = list(data)

        logger.info(f"Formatting {len(entries)} entries as markdown")

        lines = []
        for i, entry in enumerate(entries, 1):
            title = entry.get('title', 'Untitled')
            link = entry.get('link', '')
            published = entry.get('published', '')
            summary = entry.get('summary', '')

            if self.numbered:
                prefix = f"{i}. "
            else:
                prefix = "- "

            if link:
                lines.append(f"{prefix}[{title}]({link})")
            else:
                lines.append(f"{prefix}{title}")

            if published and not self.include_summary:
                lines.append(f"  _{published}_")

            if self.include_summary and summary:
                lines.append(f"  {summary}")
                if published:
                    lines.append(f"  _{published}_")

            lines.append("")  # Blank line between entries

        result = "\n".join(lines)

        logger.info(f"Generated {len(result)} chars of markdown")
        return result
