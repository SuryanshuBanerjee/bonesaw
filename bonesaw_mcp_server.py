"""
Bonesaw MCP Server

Provides Model Context Protocol tools for introspecting and controlling
Bonesaw pipelines programmatically.
"""

import importlib
import logging
import shutil
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from skeleton_core.config import build_pipeline_from_config, load_config
from skeleton_core.scaffold import generate_app_files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="Bonesaw MCP",
    stateless_http=True,
    json_response=True
)


def _get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).parent


def _get_step_description(step) -> str:
    """Extract first line of docstring from a step instance."""
    docstring = step.__class__.__doc__
    if docstring:
        lines = [line.strip() for line in docstring.split('\n') if line.strip()]
        if lines:
            return lines[0]
    return "No description provided."


@mcp.tool()
def bonesaw_list_pipelines() -> list[dict[str, str]]:
    """
    List all available Bonesaw pipeline applications.
    
    Scans the apps/ directory and returns metadata about each app including
    whether it has a default config and README.
    
    Returns:
        List of dictionaries with app metadata
    """
    logger.info("MCP: Listing pipelines")
    
    root = _get_repo_root()
    apps_dir = root / "apps"
    
    if not apps_dir.exists():
        return []
    
    results = []
    for app_path in apps_dir.iterdir():
        if not app_path.is_dir():
            continue
        
        # Check if it looks like an app (has at least one .py file)
        py_files = list(app_path.glob("*.py"))
        if not py_files:
            continue
        
        app_name = app_path.name
        config_path = app_path / "config.example.yml"
        readme_path = app_path / "README.md"
        
        results.append({
            "app": app_name,
            "default_config": str(config_path.relative_to(root)) if config_path.exists() else "",
            "has_readme": "true" if readme_path.exists() else "false"
        })
    
    logger.info(f"MCP: Found {len(results)} pipelines")
    return results


@mcp.tool()
def bonesaw_inspect_pipeline(app: str, config: str | None = None) -> dict:
    """
    Inspect a Bonesaw pipeline configuration without executing it.
    
    Loads the pipeline configuration and returns detailed information about
    each step including class names, types, and descriptions.
    
    Args:
        app: Name of the application
        config: Optional path to config file (defaults to apps/<app>/config.example.yml)
        
    Returns:
        Dictionary with pipeline metadata and step details
    """
    logger.info(f"MCP: Inspecting pipeline for app '{app}'")
    
    root = _get_repo_root()
    
    # Resolve config path
    if config is None:
        config_path = root / "apps" / app / "config.example.yml"
    else:
        config_path = root / config
    
    if not config_path.exists():
        return {
            "app": app,
            "error": f"Config file not found: {config_path}"
        }
    
    try:
        # Import app's pipelines module to register steps
        module_name = f"apps.{app}.pipelines"
        importlib.import_module(module_name)
        
        # Load config and build pipeline
        config_dict = load_config(str(config_path))
        pipeline = build_pipeline_from_config(config_dict)
        
        # Extract step information
        steps = []
        for i, step in enumerate(pipeline.steps, start=1):
            step_class = step.__class__.__name__
            description = _get_step_description(step)
            
            # Try to find the step type from registry
            # (This is a best-effort lookup)
            step_type = "unknown"
            from skeleton_core.config import STEP_REGISTRY
            for name, cls in STEP_REGISTRY.items():
                if cls == step.__class__:
                    step_type = name
                    break
            
            steps.append({
                "index": i,
                "step_class": step_class,
                "step_type": step_type,
                "description": description
            })
        
        return {
            "app": app,
            "config_path": str(config_path.relative_to(root)),
            "step_count": len(steps),
            "steps": steps
        }
        
    except Exception as e:
        logger.error(f"MCP: Failed to inspect pipeline: {e}", exc_info=True)
        return {
            "app": app,
            "error": f"Failed to inspect pipeline: {type(e).__name__}: {str(e)}"
        }


@mcp.tool()
def bonesaw_run_pipeline(
    app: str,
    config: str | None = None,
    use_llm: bool = False
) -> dict:
    """
    Execute a Bonesaw pipeline and return execution results.
    
    Runs the specified pipeline with optional LLM enhancement and captures
    execution metadata including success status, duration, and outputs.
    
    Args:
        app: Name of the application
        config: Optional path to config file (defaults to apps/<app>/config.example.yml)
        use_llm: Whether to enable LLM-enhanced summaries
        
    Returns:
        Dictionary with execution results and metadata
    """
    logger.info(f"MCP: Running pipeline for app '{app}' (use_llm={use_llm})")
    
    root = _get_repo_root()
    
    # Resolve config path
    if config is None:
        config_path = root / "apps" / app / "config.example.yml"
    else:
        config_path = root / config
    
    if not config_path.exists():
        return {
            "app": app,
            "success": False,
            "error": f"Config file not found: {config_path}"
        }
    
    start_time = time.time()
    
    try:
        # Import app's pipelines module to register steps
        module_name = f"apps.{app}.pipelines"
        importlib.import_module(module_name)
        
        # Load config and build pipeline
        config_dict = load_config(str(config_path))
        pipeline = build_pipeline_from_config(config_dict)
        
        # Run pipeline with context
        context = {"app": app, "use_llm": use_llm}
        _ = pipeline.run(context=context)
        
        duration = time.time() - start_time
        
        # Extract outputs from context
        outputs = {}
        if 'report_path' in context:
            outputs['report_path'] = context['report_path']
        if 'json_path' in context:
            outputs['json_path'] = context['json_path']
        if 'markdown_path' in context:
            outputs['markdown_path'] = context['markdown_path']
        
        return {
            "app": app,
            "config_path": str(config_path.relative_to(root)),
            "success": True,
            "error": "",
            "step_count": len(pipeline.steps),
            "used_llm": use_llm,
            "duration_seconds": round(duration, 3),
            "outputs": outputs
        }
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"MCP: Pipeline execution failed: {e}", exc_info=True)
        
        return {
            "app": app,
            "config_path": str(config_path.relative_to(root)) if config_path.exists() else config or "",
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
            "step_count": 0,
            "used_llm": use_llm,
            "duration_seconds": round(duration, 3),
            "outputs": {}
        }


@mcp.tool()
def bonesaw_create_app(app: str) -> dict:
    """
    Create a new Bonesaw application with scaffolded files.
    
    Generates a complete app skeleton including pipelines, config, sample data,
    and documentation. The app will be immediately runnable.
    
    Args:
        app: Name of the new application
        
    Returns:
        Dictionary with creation results and file paths
    """
    logger.info(f"MCP: Creating app '{app}'")
    
    root = _get_repo_root()
    target_dir = root / "apps" / app
    
    # Check if app already exists
    if target_dir.exists():
        return {
            "app": app,
            "error": f"App already exists at {target_dir.relative_to(root)}."
        }
    
    try:
        # Generate app files
        generate_app_files(app, target_dir)
        
        return {
            "app": app,
            "app_dir": str(target_dir.relative_to(root)),
            "config_path": str((target_dir / "config.example.yml").relative_to(root)),
            "readme_path": str((target_dir / "README.md").relative_to(root)),
            "message": f"App scaffolded successfully. Run via: python main.py run --app {app} --config apps/{app}/config.example.yml"
        }
        
    except Exception as e:
        logger.error(f"MCP: Failed to create app: {e}", exc_info=True)
        return {
            "app": app,
            "error": f"Failed to create app: {type(e).__name__}: {str(e)}"
        }


@mcp.tool()
def bonesaw_delete_app(app: str, force: bool = False) -> dict:
    """
    Delete a Bonesaw application and all its files.
    
    Removes the app directory under apps/. This operation cannot be undone.
    
    Args:
        app: Name of the application to delete
        force: If True, delete without confirmation (programmatic use)
        
    Returns:
        Dictionary with deletion results
    """
    logger.info(f"MCP: Deleting app '{app}' (force={force})")
    
    root = _get_repo_root()
    target_dir = root / "apps" / app
    
    # Check if app exists
    if not target_dir.exists():
        return {
            "app": app,
            "deleted": False,
            "error": f"App does not exist at {target_dir.relative_to(root)}."
        }
    
    try:
        # Delete the directory
        shutil.rmtree(target_dir)
        
        return {
            "app": app,
            "deleted": True,
            "app_dir": str(target_dir.relative_to(root))
        }
        
    except Exception as e:
        logger.error(f"MCP: Failed to delete app: {e}", exc_info=True)
        return {
            "app": app,
            "deleted": False,
            "error": f"Failed to delete app: {type(e).__name__}: {str(e)}"
        }


if __name__ == "__main__":
    # Run HTTP server on localhost:8001, path /mcp
    logger.info("Starting Bonesaw MCP server on http://localhost:8001/mcp")
    mcp.run(transport="streamable-http")
