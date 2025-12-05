"""
Pytest configuration for Bonesaw tests.

Ensures the project root is on sys.path so imports work correctly.
"""

import os
import sys

# Add project root to sys.path so imports like "apps.*" and "skeleton_core.*" work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
