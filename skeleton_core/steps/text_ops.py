"""
Text operation steps for Bonesaw.

Provides steps for text manipulation like grep, replace, split, template.
"""

import logging
import re
from typing import Any

from skeleton_core.config import register_step

logger = logging.getLogger(__name__)


@register_step("grep")
class GrepStep:
    """
    Filter lines matching a pattern (like Unix grep).

    Input: str or list[str] (text or lines)
    Output: list[str] (matching lines)
    Context: Writes 'match_count', 'total_lines'
    """

    def __init__(self, pattern: str, case_sensitive: bool = True, invert: bool = False):
        """
        Args:
            pattern: Regex pattern to match
            case_sensitive: Whether matching is case-sensitive
            invert: If True, return non-matching lines
        """
        self.pattern = pattern
        self.case_sensitive = case_sensitive
        self.invert = invert

    def run(self, data: Any, context: dict[str, Any]) -> list[str]:
        """Grep for pattern."""
        # Convert input to lines
        if isinstance(data, str):
            lines = data.splitlines()
        else:
            lines = list(data)

        flags = 0 if self.case_sensitive else re.IGNORECASE
        regex = re.compile(self.pattern, flags)

        logger.info(f"Grepping for '{self.pattern}' in {len(lines)} lines")

        matches = []
        for line in lines:
            is_match = regex.search(line) is not None
            if is_match != self.invert:  # XOR logic for invert
                matches.append(line)

        context['match_count'] = len(matches)
        context['total_lines'] = len(lines)

        logger.info(f"Found {len(matches)} matches")
        return matches


@register_step("replace")
class ReplaceStep:
    """
    Replace text using regex (like sed).

    Input: str (text to process)
    Output: str (transformed text)
    Context: Writes 'replacement_count'
    """

    def __init__(self, pattern: str, replacement: str, count: int = 0):
        """
        Args:
            pattern: Regex pattern to find
            replacement: Replacement text (can use regex groups like \\1)
            count: Max replacements (0 = all)
        """
        self.pattern = pattern
        self.replacement = replacement
        self.count = count

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Replace pattern."""
        text = str(data)

        logger.info(f"Replacing '{self.pattern}' with '{self.replacement}'")

        result, num_replacements = re.subn(
            self.pattern,
            self.replacement,
            text,
            count=self.count
        )

        context['replacement_count'] = num_replacements

        logger.info(f"Made {num_replacements} replacements")
        return result


@register_step("split_lines")
class SplitLinesStep:
    """
    Split text into lines.

    Input: str (text)
    Output: list[str] (lines)
    Context: Writes 'line_count'
    """

    def __init__(self, strip: bool = True, skip_empty: bool = False):
        """
        Args:
            strip: Strip whitespace from each line
            skip_empty: Skip empty lines
        """
        self.strip = strip
        self.skip_empty = skip_empty

    def run(self, data: Any, context: dict[str, Any]) -> list[str]:
        """Split into lines."""
        text = str(data)
        lines = text.splitlines()

        if self.strip:
            lines = [line.strip() for line in lines]

        if self.skip_empty:
            lines = [line for line in lines if line]

        context['line_count'] = len(lines)

        logger.info(f"Split into {len(lines)} lines")
        return lines


@register_step("join_lines")
class JoinLinesStep:
    """
    Join lines into a single string.

    Input: list[str] (lines)
    Output: str (joined text)
    Context: Writes 'line_count', 'output_length'
    """

    def __init__(self, separator: str = "\n"):
        """
        Args:
            separator: String to join lines with
        """
        self.separator = separator

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Join lines."""
        lines = list(data)
        result = self.separator.join(lines)

        context['line_count'] = len(lines)
        context['output_length'] = len(result)

        logger.info(f"Joined {len(lines)} lines ({len(result)} chars)")
        return result


@register_step("template")
class TemplateStep:
    """
    Apply a template using Python f-string style formatting.

    Input: dict[str, Any] (template variables)
    Output: str (rendered template)
    Context: None
    """

    def __init__(self, template: str):
        """
        Args:
            template: Template string with {variable} placeholders
        """
        self.template = template

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Render template."""
        variables = dict(data) if isinstance(data, dict) else {'data': data}

        # Also make context available
        variables['context'] = context

        logger.info(f"Rendering template with {len(variables)} variables")

        result = self.template.format(**variables)

        logger.info(f"Rendered {len(result)} chars")
        return result


@register_step("to_uppercase")
class ToUppercaseStep:
    """
    Convert text to uppercase.

    Input: str (text)
    Output: str (uppercase text)
    """

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Convert to uppercase."""
        return str(data).upper()


@register_step("to_lowercase")
class ToLowercaseStep:
    """
    Convert text to lowercase.

    Input: str (text)
    Output: str (lowercase text)
    """

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Convert to lowercase."""
        return str(data).lower()
