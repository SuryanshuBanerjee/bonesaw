"""
Bonesaw - Pipeline automation framework.

Main entry point for the CLI application.
"""

import logging

from skeleton_core.cli import app

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )
    
    # Run the Typer CLI app
    app()
