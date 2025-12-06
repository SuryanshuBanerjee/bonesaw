"""
Utility functions for Bonesaw.

Provides common helper functions used across the framework.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def validate_file_path(path: str, must_exist: bool = True, base_dir: Optional[str] = None) -> Path:
    """
    Validate and resolve a file path to prevent path traversal attacks.

    Args:
        path: The file path to validate
        must_exist: If True, raise an error if the file doesn't exist
        base_dir: Optional base directory to restrict access to

    Returns:
        Resolved Path object

    Raises:
        ValueError: If path is outside the allowed base directory
        FileNotFoundError: If must_exist=True and file doesn't exist
    """
    resolved = Path(path).resolve()

    # Check if path is within allowed base directory
    if base_dir:
        base = Path(base_dir).resolve()
        try:
            resolved.relative_to(base)
        except ValueError:
            raise ValueError(
                f"Path '{path}' is outside allowed directory '{base_dir}'. "
                f"Resolved to: {resolved}"
            )

    # Check if file exists (if required)
    if must_exist and not resolved.exists():
        raise FileNotFoundError(f"File not found: {path} (resolved to: {resolved})")

    logger.debug(f"Validated path: {path} -> {resolved}")
    return resolved
