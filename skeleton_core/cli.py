"""
CLI interface for Bonesaw pipeline framework.

Provides commands for listing available applications and running pipelines
from YAML configuration files.
"""

import importlib
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

import typer

from skeleton_core.cache import cache_stats, clear_cache
from skeleton_core.config import build_pipeline_from_config, load_config
from skeleton_core.scaffold import generate_app_files
# Import built-in steps to auto-register them
import skeleton_core.steps  # noqa: F401

logger = logging.getLogger(__name__)

app = typer.Typer(help="Bonesaw - Pipeline automation framework")


def safe_echo(text: str, **kwargs):
    """
    Echo text to console, falling back to ASCII if Unicode fails.

    Handles Windows console encoding issues by stripping emojis/Unicode
    characters when the console doesn't support them.
    """
    try:
        typer.echo(text, **kwargs)
    except UnicodeEncodeError:
        # Remove emoji and special Unicode characters for Windows consoles
        import re
        ascii_text = re.sub(r'[\u2600-\u27BF\U0001F300-\U0001F9FF\u2192\u26A0\uFE0F]+', '', text)
        ascii_text = ascii_text.replace('→', '->').replace('⚠', 'WARNING:').replace('✅', '[OK]').replace('❌', '[FAIL]')
        typer.echo(ascii_text.strip(), **kwargs)


def print_banner():
    """Print a spooky ASCII banner."""
    safe_echo("🦴 BONESAW CLI 🦴")
    typer.echo()


@app.command()
def create_app(
    app_name: str = typer.Argument(..., help="Name of the new app (folder under apps/)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing app directory if it exists")
):
    """
    Create a new Bonesaw application with a working text processing pipeline.
    
    Generates a complete app skeleton with pipelines, config, sample data, and README.
    """
    print_banner()
    
    # Compute target directory
    target_dir = Path("apps") / app_name
    
    # Check if directory exists
    if target_dir.exists():
        if not force:
            typer.echo(f"Error: App directory already exists: {target_dir}", err=True)
            typer.echo("Use --force to overwrite the existing app.", err=True)
            raise typer.Exit(code=1)
        else:
            safe_echo(f"⚠️  Overwriting existing app at {target_dir}")
    
    # Create the app
    logger.info(f"Creating new app '{app_name}' at {target_dir}")
    
    try:
        generate_app_files(app_name, target_dir)
    except Exception as e:
        typer.echo(f"Error: Failed to create app: {e}", err=True)
        logger.error(f"App creation failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
    
    # Success message
    safe_echo(f"✅ Successfully created app '{app_name}' at {target_dir}")
    typer.echo()
    typer.echo("Next steps:")
    typer.echo(f"  1. Inspect:  python main.py inspect --app {app_name} --config apps/{app_name}/config.example.yml")
    typer.echo(f"  2. Dry-run:  python main.py dry-run --app {app_name} --config apps/{app_name}/config.example.yml")
    typer.echo(f"  3. Run:      python main.py run --app {app_name} --config apps/{app_name}/config.example.yml")


@app.command()
def delete_app(
    app_name: str = typer.Argument(..., help="Name of the app (folder under apps/) to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Delete without confirmation")
):
    """
    Delete an application and all its files.
    
    Removes the app directory under apps/. Use with caution!
    """
    print_banner()
    
    # Resolve target directory
    target_dir = Path("apps") / app_name
    
    # Check if directory exists
    if not target_dir.exists():
        typer.echo(f"Error: App '{app_name}' does not exist under 'apps/'.", err=True)
        raise typer.Exit(code=1)
    
    # Confirm deletion unless force is set
    if not force:
        confirm = typer.confirm(
            f"Are you sure you want to delete app '{app_name}' and all its files?"
        )
        if not confirm:
            typer.echo("Deletion cancelled.")
            return
    
    # Delete the directory
    logger.info(f"Deleting app '{app_name}' at {target_dir}")
    
    try:
        shutil.rmtree(target_dir)
        safe_echo(f"✅ Successfully deleted app '{app_name}'")
    except Exception as e:
        typer.echo(f"Error: Failed to delete app: {e}", err=True)
        logger.error(f"App deletion failed: {e}", exc_info=True)
        raise typer.Exit(code=1)


@app.command()
def list_apps():
    """
    List all available applications in the apps/ directory.
    
    Scans for subdirectories containing a pipelines.py file.
    """
    print_banner()
    
    apps_dir = Path("apps")
    
    if not apps_dir.exists():
        typer.echo("No apps/ directory found.", err=True)
        raise typer.Exit(code=1)
    
    # Find all subdirectories with a pipelines.py file
    available_apps = []
    for app_path in apps_dir.iterdir():
        if app_path.is_dir() and (app_path / "pipelines.py").exists():
            available_apps.append(app_path.name)
    
    if not available_apps:
        typer.echo("No applications found in apps/")
        return
    
    typer.echo("Available applications:")
    for app_name in sorted(available_apps):
        typer.echo(f"  - {app_name}")


def _get_step_description(step) -> str:
    """
    Extract a short description from a step instance.
    
    Args:
        step: Step instance
        
    Returns:
        First non-empty line of docstring, or fallback message
    """
    docstring = step.__class__.__doc__
    if docstring:
        lines = [line.strip() for line in docstring.split('\n') if line.strip()]
        if lines:
            return lines[0]
    return "No description provided."


def _load_app_and_config(app_name: Optional[str], config_path: str):
    """
    Load app module and config, returning the config dict.

    Args:
        app_name: Name of the app (None for standalone configs)
        config_path: Path to YAML config file

    Returns:
        Tuple of (config_dict, pipeline)

    Raises:
        typer.Exit on any error
    """
    # If app is specified, import its pipelines module
    if app_name:
        # Validate that the app exists
        app_pipelines_path = Path("apps") / app_name / "pipelines.py"
        if not app_pipelines_path.exists():
            typer.echo(f"Error: Application '{app_name}' not found.", err=True)
            typer.echo(f"Expected to find: {app_pipelines_path}", err=True)
            raise typer.Exit(code=1)

        # Import the app's pipelines module to register steps
        try:
            module_name = f"apps.{app_name}.pipelines"
            logger.debug(f"Importing {module_name} to register steps")
            importlib.import_module(module_name)
        except ImportError as e:
            typer.echo(f"Error: Failed to import {module_name}: {e}", err=True)
            raise typer.Exit(code=1)
    else:
        logger.debug("Using built-in steps only (no app specified)")
    
    # Load configuration
    try:
        config_dict = load_config(config_path)
    except FileNotFoundError:
        typer.echo(f"Error: Config file not found: {config_path}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: Failed to load config: {e}", err=True)
        raise typer.Exit(code=1)
    
    # Build pipeline
    try:
        pipeline = build_pipeline_from_config(config_dict)
    except Exception as e:
        typer.echo(f"Error: Failed to build pipeline: {e}", err=True)
        logger.error(f"Pipeline build failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
    
    return config_dict, pipeline


@app.command()
def inspect(
    config: str = typer.Option(..., "--config", "-c", help="Path to YAML config file"),
    app_name: Optional[str] = typer.Option(None, "--app", "-a", help="Name of the app to inspect (optional for standalone configs)")
):
    """
    Inspect a pipeline configuration without executing it.

    Shows the pipeline structure and step descriptions.
    """
    print_banner()

    if app_name:
        logger.info(f"Inspecting pipeline for app '{app_name}'")
    else:
        logger.info(f"Inspecting standalone pipeline")

    # Load app and config
    config_dict, pipeline = _load_app_and_config(app_name, config)

    # Print pipeline summary
    typer.echo(f"Pipeline: {pipeline.name}")
    typer.echo()

    for i, step in enumerate(pipeline.steps, start=1):
        step_type = step.__class__.__name__
        description = _get_step_description(step)
        safe_echo(f"{i}. {step_type}  → {description}")

    typer.echo()
    typer.echo(f"Total steps: {len(pipeline.steps)}")


@app.command()
def dry_run(
    config: str = typer.Option(..., "--config", "-c", help="Path to YAML config file"),
    app_name: Optional[str] = typer.Option(None, "--app", "-a", help="Name of the app to simulate (optional for standalone configs)")
):
    """
    Perform a dry-run of a pipeline without executing steps.

    Shows detailed information about what would be executed.
    """
    print_banner()

    if app_name:
        logger.info(f"Dry-run for app '{app_name}'")
    else:
        logger.info(f"Dry-run for standalone pipeline")
    
    # Load app and config
    config_dict, pipeline = _load_app_and_config(app_name, config)
    
    # Print dry-run header
    safe_echo("⚠️  NOTE: This is a dry-run; no data will be processed or written.")
    typer.echo()
    typer.echo(f"Dry run: {pipeline.name}")
    typer.echo()
    
    # Print detailed step information
    for i, step in enumerate(pipeline.steps, start=1):
        step_type = step.__class__.__name__
        description = _get_step_description(step)
        
        typer.echo(f"Step {i}: {step_type}")
        typer.echo(f"  - Description: {description}")
        
        # Show step parameters if available
        if hasattr(step, '__dict__'):
            params = {k: v for k, v in step.__dict__.items() if not k.startswith('_')}
            if params:
                safe_echo(f"  - Parameters: {params}")

        typer.echo()
    
    typer.echo(f"Total steps: {len(pipeline.steps)}")
    typer.echo()
    safe_echo("✅ Dry-run complete. Use 'run' command to execute the pipeline.")


@app.command()
def run(
    config: str = typer.Option(..., "--config", "-c", help="Path to YAML config file"),
    app_name: Optional[str] = typer.Option(None, "--app", "-a", help="Name of the application to run (optional for standalone configs)"),
    use_llm: bool = typer.Option(False, "--use-llm", help="Enable LLM-enhanced summaries if BONESAW_LLM_* is configured")
):
    """
    Run a pipeline from a YAML configuration file.

    If --app is specified, the app's pipelines.py module will be imported to register
    custom step types. Otherwise, only built-in steps will be available.
    """
    print_banner()

    # If app is specified, import its pipelines module
    if app_name:
        # Validate that the app exists
        app_pipelines_path = Path("apps") / app_name / "pipelines.py"
        if not app_pipelines_path.exists():
            typer.echo(f"Error: Application '{app_name}' not found.", err=True)
            typer.echo(f"Expected to find: {app_pipelines_path}", err=True)
            raise typer.Exit(code=1)

        # Import the app's pipelines module to register steps
        try:
            module_name = f"apps.{app_name}.pipelines"
            logger.info(f"Importing {module_name} to register steps")
            importlib.import_module(module_name)
        except ImportError as e:
            typer.echo(f"Error: Failed to import {module_name}: {e}", err=True)
            raise typer.Exit(code=1)
    else:
        logger.info("Running with built-in steps only (no app specified)")
    
    # Load configuration
    try:
        config_dict = load_config(config)
    except FileNotFoundError:
        typer.echo(f"Error: Config file not found: {config}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: Failed to load config: {e}", err=True)
        raise typer.Exit(code=1)
    
    # Build pipeline
    try:
        pipeline = build_pipeline_from_config(config_dict)
    except Exception as e:
        typer.echo(f"Error: Failed to build pipeline: {e}", err=True)
        logger.error(f"Pipeline build failed: {e}", exc_info=True)
        raise typer.Exit(code=1)
    
    # Check LLM configuration
    llm_provider = os.getenv("BONESAW_LLM_PROVIDER")
    llm_api_key = os.getenv("BONESAW_LLM_API_KEY")
    
    if use_llm:
        if llm_provider and llm_api_key:
            logger.info(f"LLM enhancement enabled with provider: {llm_provider}")
        else:
            safe_echo("⚠️  --use-llm specified but BONESAW_LLM_PROVIDER or BONESAW_LLM_API_KEY not set", err=True)
            typer.echo("    Falling back to deterministic summaries", err=True)
    
    # Run pipeline
    typer.echo(f"Running pipeline '{pipeline.name}' from app '{app_name}'...")
    typer.echo()

    try:
        # Pass context with use_llm flag and timestamp
        from datetime import datetime
        context = {
            "app": app_name,
            "use_llm": use_llm,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        result = pipeline.run(context=context)
        typer.echo()
        safe_echo("✅ Pipeline completed successfully!")

        # Optionally display the result if it's a simple type
        if result is not None and not isinstance(result, (dict, list)):
            typer.echo(f"Final result: {result}")

    except Exception as e:
        typer.echo()
        safe_echo(f"❌ Pipeline failed: {e}", err=True)
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        raise typer.Exit(code=1)


@app.command()
def cache_info():
    """
    Show cache statistics.
    """
    print_banner()

    stats = cache_stats()

    if stats['file_count'] == 0:
        typer.echo("Cache is empty")
        return

    safe_echo(f"📊 Cache Statistics:")
    typer.echo(f"  Files: {stats['file_count']}")
    typer.echo(f"  Total size: {stats['total_size_mb']} MB")
    typer.echo(f"  Oldest entry: {stats['oldest_age']}s ago")
    typer.echo(f"  Newest entry: {stats['newest_age']}s ago")


@app.command()
def cache_clear(
    older_than: int = typer.Option(
        0,
        help="Only clear cache entries older than N seconds (0 = clear all)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt"
    )
):
    """
    Clear the pipeline cache.
    """
    print_banner()

    stats = cache_stats()

    if stats['file_count'] == 0:
        typer.echo("Cache is already empty")
        return

    if not force:
        if older_than > 0:
            typer.echo(f"This will clear cache entries older than {older_than}s")
        else:
            typer.echo(f"This will clear ALL {stats['file_count']} cache entries ({stats['total_size_mb']} MB)")

        confirm = typer.confirm("Continue?")
        if not confirm:
            typer.echo("Cancelled")
            raise typer.Exit()

    clear_cache(older_than=older_than if older_than > 0 else None)

    safe_echo("✅ Cache cleared")


if __name__ == "__main__":
    # Configure logging for CLI usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )
    app()
