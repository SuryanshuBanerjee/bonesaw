"""
Built-in steps for Bonesaw pipelines.

This module provides batteries-included steps for common automation tasks.
All steps are automatically registered when this module is imported.
"""

# Import all step modules to auto-register them
from skeleton_core.steps import file_ops, http_ops, text_ops, data_ops

__all__ = ['file_ops', 'http_ops', 'text_ops', 'data_ops']
