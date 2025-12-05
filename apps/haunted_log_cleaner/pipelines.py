"""
Haunted Log Cleaner - Pipeline steps for processing and anonymizing log files.

This module defines all the steps needed to read messy logs, parse them,
anonymize sensitive data, aggregate statistics, and generate reports.
"""

import logging
import re
from typing import Any

from skeleton_core.config import register_step
from skeleton_core.summarization import summarize_logs

logger = logging.getLogger(__name__)


@register_step("load_logs")
class LoadLogsStep:
    """
    Load log file contents into memory.
    
    Input: None (or ignored)
    Output: list[str] of raw log lines
    Context: Writes 'source_file' with the path that was loaded
    """
    
    def __init__(self, path: str):
        """
        Initialize the log loader.
        
        Args:
            path: Filesystem path to the log file
        """
        self.path = path
    
    def run(self, data: Any, context: dict[str, Any]) -> list[str]:
        """Load log file and return lines."""
        logger.info(f"Loading logs from {self.path}")
        
        with open(self.path, 'r') as f:
            lines = f.readlines()
        
        context['source_file'] = self.path
        logger.info(f"Loaded {len(lines)} log lines")
        
        return lines


@register_step("parse_logs")
class ParseLogsStep:
    """
    Parse raw log lines into structured dictionaries.
    
    Expected format: YYYY-MM-DD HH:MM:SS [LEVEL] message text
    
    Input: list[str] of raw log lines
    Output: list[dict] with keys: timestamp, level, message
    Context: Writes 'parsed_count' and 'skipped_count'
    """
    
    # Pattern: YYYY-MM-DD HH:MM:SS [LEVEL] message
    LOG_PATTERN = re.compile(
        r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+(.+)$'
    )
    
    def run(self, data: Any, context: dict[str, Any]) -> list[dict[str, str]]:
        """Parse log lines into structured format."""
        lines = data
        parsed_logs = []
        skipped = 0
        
        logger.info(f"Parsing {len(lines)} log lines")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            match = self.LOG_PATTERN.match(line)
            if match:
                parsed_logs.append({
                    'timestamp': match.group(1),
                    'level': match.group(2),
                    'message': match.group(3)
                })
            else:
                skipped += 1
                logger.debug(f"Skipped unparseable line: {line[:50]}")
        
        context['parsed_count'] = len(parsed_logs)
        context['skipped_count'] = skipped
        
        logger.info(f"Parsed {len(parsed_logs)} logs, skipped {skipped}")
        
        return parsed_logs


@register_step("anonymize_logs")
class AnonymizeLogsStep:
    """
    Anonymize sensitive data in log messages.
    
    Replaces email addresses and IPv4 addresses with [REDACTED].
    
    Input: list[dict] of parsed logs
    Output: list[dict] with anonymized messages
    Context: Writes 'anonymized_count' with number of redactions
    """
    
    EMAIL_PATTERN = re.compile(r'\S+@\S+')
    IPV4_PATTERN = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
    
    def run(self, data: Any, context: dict[str, Any]) -> list[dict[str, str]]:
        """Anonymize sensitive data in log messages."""
        logs = data
        redaction_count = 0
        
        logger.info(f"Anonymizing {len(logs)} log entries")
        
        for log_entry in logs:
            original_message = log_entry['message']
            
            # Replace emails
            message = self.EMAIL_PATTERN.sub('[REDACTED]', original_message)
            
            # Replace IP addresses
            message = self.IPV4_PATTERN.sub('[REDACTED]', message)
            
            if message != original_message:
                redaction_count += 1
            
            log_entry['message'] = message
        
        context['anonymized_count'] = redaction_count
        logger.info(f"Anonymized {redaction_count} log entries")
        
        return logs


@register_step("aggregate_errors")
class AggregateErrorsStep:
    """
    Aggregate log statistics by level.
    
    Input: list[dict] of parsed logs
    Output: dict with 'total', 'by_level', and 'logs' keys
    Context: Writes 'error_count' with number of ERROR-level logs
    """
    
    def run(self, data: Any, context: dict[str, Any]) -> dict[str, Any]:
        """Compute statistics from parsed logs."""
        logs = data
        
        logger.info(f"Aggregating statistics for {len(logs)} logs")
        
        # Count by level
        by_level: dict[str, int] = {}
        for log_entry in logs:
            level = log_entry['level']
            by_level[level] = by_level.get(level, 0) + 1
        
        result = {
            'total': len(logs),
            'by_level': by_level,
            'logs': logs
        }
        
        context['error_count'] = by_level.get('ERROR', 0)
        
        logger.info(f"Statistics: {result['total']} total, {len(by_level)} levels")
        
        return result


@register_step("write_markdown_report")
class WriteMarkdownReportStep:
    """
    Generate a markdown report from aggregated log statistics.
    
    Input: dict with 'total', 'by_level', and 'logs' keys
    Output: Same dict (pass-through)
    Context: Writes 'report_path' with the output file path
    """
    
    def __init__(self, output_path: str):
        """
        Initialize the report writer.
        
        Args:
            output_path: Path where the markdown report will be written
        """
        self.output_path = output_path
    
    def run(self, data: Any, context: dict[str, Any]) -> dict[str, Any]:
        """Generate and write markdown report."""
        stats = data
        
        logger.info(f"Writing markdown report to {self.output_path}")
        
        # Build markdown content
        lines = [
            "# 🩸 Haunted Log Report",
            "",
            "## Summary",
            "",
            f"**Total log entries:** {stats['total']}",
            "",
            "## Counts by Level",
            ""
        ]
        
        # Add level counts as a table
        lines.append("| Level | Count |")
        lines.append("|-------|-------|")
        for level in sorted(stats['by_level'].keys()):
            count = stats['by_level'][level]
            lines.append(f"| {level} | {count} |")
        
        lines.append("")
        lines.append("## Sample Messages")
        lines.append("")
        
        # Show up to 5 sample messages
        sample_logs = stats['logs'][:5]
        for log_entry in sample_logs:
            lines.append(f"- **[{log_entry['level']}]** {log_entry['timestamp']}: {log_entry['message']}")
        
        lines.append("")
        
        # Write to file
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        context['report_path'] = self.output_path
        logger.info(f"Report written successfully")
        
        return stats


@register_step("log_llm_summary")
class LogLLMSummaryStep:
    """
    Generate an LLM-style summary of log statistics (stubbed).
    
    This step demonstrates where an LLM API call would go. For now,
    it generates a fake spooky summary based on the statistics.
    
    Input: dict with 'total', 'by_level', and 'logs' keys
    Output: Same dict (pass-through)
    Context: Writes 'llm_summary' with the generated text
    """
    
    def __init__(self, output_path: str):
        """
        Initialize the LLM summary generator.
        
        Args:
            output_path: Path to append the summary to (or write separately)
        """
        self.output_path = output_path
    
    def run(self, data: Any, context: dict[str, Any]) -> dict[str, Any]:
        """Generate and append LLM summary."""
        stats = data
        
        logger.info("Generating log summary")
        
        # Use the robust summarization system
        summary_text = summarize_logs(stats, context)
        
        # Append to the existing report
        with open(self.output_path, 'a', encoding='utf-8') as f:
            f.write("\n## 🔮 AI Summary\n\n")
            f.write(summary_text)
            f.write("\n")
        
        context['llm_summary'] = summary_text
        logger.info("Summary appended to report")
        
        return stats
