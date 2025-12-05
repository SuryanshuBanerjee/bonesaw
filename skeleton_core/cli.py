"""
CLI interface for Bonesaw pipeline framework.

Provides commands for listing available applications and running pipelines
from YAML configuration files.
"""

import importlib
import logging
import os
from pathlib import Path

import typer

from skeleton_core.config import build_pipeline_from_config, load_config

logger = logging.getLogger(__name__)

app = typer.Typer(help="🦴 Bonesaw - Pipeline automation framework 🦴")


def print_banner():
    """Print a spooky ASCII banner."""
    typer.echo("🦴 BONESAW CLI 🦴")
    typer.echo()


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


def _load_app_and_config(app_name: str, config_path: str):
    """
    Load app module and config, returning the config dict.
    
    Args:
        app_name: Name of the app
        config_path: Path to YAML config file
        
    Returns:
        Tuple of (config_dict, pipeline)
        
    Raises:
        typer.Exit on any error
    """
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
    app_name: str = typer.Option(..., "--app", "-a", help="Name of the app to inspect"),
    config: str = typer.Option(..., "--config", "-c", help="Path to YAML config file")
):
    """
    Inspect a pipeline configuration without executing it.
    
    Shows the pipeline structure and step descriptions.
    """
    print_banner()
    
    logger.info(f"Inspecting pipeline for app '{app_name}'")
    
    # Load app and config
    config_dict, pipeline = _load_app_and_config(app_name, config)
    
    # Print pipeline summary
    typer.echo(f"Pipeline: {pipeline.name}")
    typer.echo()
    
    for i, step in enumerate(pipeline.steps, start=1):
        step_type = step.__class__.__name__
        description = _get_step_description(step)
        typer.echo(f"{i}. {step_type}  → {description}")
    
    typer.echo()
    typer.echo(f"Total steps: {len(pipeline.steps)}")


@app.command()
def dry_run(
    app_name: str = typer.Option(..., "--app", "-a", help="Name of the app to simulate"),
    config: str = typer.Option(..., "--config", "-c", help="Path to YAML config file")
):
    """
    Perform a dry-run of a pipeline without executing steps.
    
    Shows detailed information about what would be executed.
    """
    print_banner()
    
    logger.info(f"Dry-run for app '{app_name}'")
    
    # Load app and config
    config_dict, pipeline = _load_app_and_config(app_name, config)
    
    # Print dry-run header
    typer.echo("⚠️  NOTE: This is a dry-run; no data will be processed or written.")
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
                typer.echo(f"  - Parameters: {params}")
        
        typer.echo()
    
    typer.echo(f"Total steps: {len(pipeline.steps)}")
    typer.echo()
    typer.echo("✅ Dry-run complete. Use 'run' command to execute the pipeline.")


@app.command()
def run(
    app_name: str = typer.Option(..., "--app", "-a", help="Name of the application to run"),
    config: str = typer.Option(..., "--config", "-c", help="Path to YAML config file"),
    use_llm: bool = typer.Option(False, "--use-llm", help="Enable LLM-enhanced summaries if BONESAW_LLM_* is configured")
):
    """
    Run a pipeline from a YAML configuration file.
    
    The specified app's pipelines.py module will be imported to register
    all step types, then the pipeline will be built and executed.
    """
    print_banner()
    
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
            typer.echo("⚠️  --use-llm specified but BONESAW_LLM_PROVIDER or BONESAW_LLM_API_KEY not set", err=True)
            typer.echo("    Falling back to deterministic summaries", err=True)
    
    # Run pipeline
    typer.echo(f"Running pipeline '{pipeline.name}' from app '{app_name}'...")
    typer.echo()
    
    try:
        # Pass context with use_llm flag
        context = {"app": app_name, "use_llm": use_llm}
        result = pipeline.run(context=context)
        typer.echo()
        typer.echo("✅ Pipeline completed successfully!")
        
        # Optionally display the result if it's a simple type
        if result is not None and not isinstance(result, (dict, list)):
            typer.echo(f"Final result: {result}")
        
    except Exception as e:
        typer.echo()
        typer.echo(f"❌ Pipeline failed: {e}", err=True)
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    # Configure logging for CLI usage
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )
    app()
