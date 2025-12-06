"""
File operation steps for Bonesaw.

Provides common file system operations like read, write, copy, move, delete.
"""

import logging
import shutil
from pathlib import Path
from typing import Any, Optional

from skeleton_core.config import register_step
from skeleton_core.utils import validate_file_path

logger = logging.getLogger(__name__)


@register_step("read_file")
class ReadFileStep:
    """
    Read a file and return its contents.

    Input: Ignored (or path can be passed via data)
    Output: str (file contents)
    Context: Writes 'file_size' and 'file_path'
    """

    def __init__(self, path: Optional[str] = None):
        """
        Args:
            path: Path to file (optional if passed via pipeline data)
        """
        self.path = path

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Read file contents."""
        file_path = self.path or data
        validated_path = validate_file_path(file_path)

        logger.info(f"Reading file: {validated_path}")

        with open(validated_path, 'r', encoding='utf-8') as f:
            contents = f.read()

        context['file_size'] = len(contents)
        context['file_path'] = str(validated_path)

        logger.info(f"Read {len(contents)} bytes from {validated_path}")
        return contents


@register_step("write_file")
class WriteFileStep:
    """
    Write data to a file.

    Input: str (contents to write)
    Output: str (path to written file)
    Context: Writes 'bytes_written'
    """

    def __init__(self, path: str, mode: str = 'w'):
        """
        Args:
            path: Path to output file
            mode: Write mode ('w' for overwrite, 'a' for append)
        """
        self.path = path
        self.mode = mode

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Write data to file."""
        output_path = Path(self.path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Writing to file: {output_path} (mode={self.mode})")

        with open(output_path, self.mode, encoding='utf-8') as f:
            f.write(str(data))

        bytes_written = output_path.stat().st_size
        context['bytes_written'] = bytes_written

        logger.info(f"Wrote {bytes_written} bytes to {output_path}")
        return str(output_path)


@register_step("copy_file")
class CopyFileStep:
    """
    Copy a file to a new location.

    Input: str (source path) or None if path provided
    Output: str (destination path)
    Context: Writes 'source_path' and 'dest_path'
    """

    def __init__(self, src: Optional[str] = None, dest: Optional[str] = None):
        """
        Args:
            src: Source file path (optional if passed via data)
            dest: Destination file path
        """
        self.src = src
        self.dest = dest

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Copy file."""
        src_path = validate_file_path(self.src or data)
        dest_path = Path(self.dest)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Copying {src_path} -> {dest_path}")

        shutil.copy2(src_path, dest_path)

        context['source_path'] = str(src_path)
        context['dest_path'] = str(dest_path)

        logger.info(f"Copied successfully")
        return str(dest_path)


@register_step("move_file")
class MoveFileStep:
    """
    Move/rename a file.

    Input: str (source path) or None if path provided
    Output: str (destination path)
    Context: Writes 'source_path' and 'dest_path'
    """

    def __init__(self, src: Optional[str] = None, dest: Optional[str] = None):
        """
        Args:
            src: Source file path (optional if passed via data)
            dest: Destination file path
        """
        self.src = src
        self.dest = dest

    def run(self, data: Any, context: dict[str, Any]) -> str:
        """Move file."""
        src_path = validate_file_path(self.src or data)
        dest_path = Path(self.dest)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Moving {src_path} -> {dest_path}")

        shutil.move(src_path, dest_path)

        context['source_path'] = str(src_path)
        context['dest_path'] = str(dest_path)

        logger.info(f"Moved successfully")
        return str(dest_path)


@register_step("delete_file")
class DeleteFileStep:
    """
    Delete a file.

    Input: str (file path) or None if path provided
    Output: bool (True if deleted)
    Context: Writes 'deleted_path'
    """

    def __init__(self, path: Optional[str] = None):
        """
        Args:
            path: File path to delete (optional if passed via data)
        """
        self.path = path

    def run(self, data: Any, context: dict[str, Any]) -> bool:
        """Delete file."""
        file_path = validate_file_path(self.path or data)

        logger.info(f"Deleting file: {file_path}")

        file_path.unlink()

        context['deleted_path'] = str(file_path)

        logger.info(f"Deleted successfully")
        return True


@register_step("list_files")
class ListFilesStep:
    """
    List files in a directory matching a pattern.

    Input: Ignored
    Output: list[str] (file paths)
    Context: Writes 'file_count'
    """

    def __init__(self, directory: str = ".", pattern: str = "*"):
        """
        Args:
            directory: Directory to search
            pattern: Glob pattern (e.g., "*.txt", "**/*.py")
        """
        self.directory = directory
        self.pattern = pattern

    def run(self, data: Any, context: dict[str, Any]) -> list[str]:
        """List files matching pattern."""
        dir_path = Path(self.directory)

        logger.info(f"Listing files in {dir_path} matching '{self.pattern}'")

        if "**" in self.pattern:
            files = list(dir_path.glob(self.pattern))
        else:
            files = list(dir_path.glob(self.pattern))

        file_paths = [str(f) for f in files if f.is_file()]

        context['file_count'] = len(file_paths)

        logger.info(f"Found {len(file_paths)} files")
        return file_paths
