"""
Configuration loading and pipeline building for Bonesaw.

This module provides the step registry mechanism and functions for loading
YAML configuration files and constructing Pipeline instances from them.
"""

import logging
from typing import Any

import yaml

from skeleton_core.pipeline import Pipeline, Step

logger = logging.getLogger(__name__)

# Global registry mapping step type names to Step classes
STEP_REGISTRY: dict[str, type[Step]] = {}


def register_step(name: str):
    """
    Decorator to register a Step class in the global registry.
    
    This allows steps to be referenced by name in YAML configuration files.
    Step names must be unique - attempting to register a duplicate name will
    raise a ValueError.
    
    Args:
        name: Unique string identifier for this step type
        
    Returns:
        Decorator function that registers the class
        
    Raises:
        ValueError: If a step with this name is already registered
        
    Example:
        @register_step("read_file")
        class ReadFileStep:
            def run(self, data, context):
                ...
    """
    def decorator(cls: type[Step]) -> type[Step]:
        if name in STEP_REGISTRY:
            raise ValueError(
                f"Step '{name}' is already registered. "
                f"Existing class: {STEP_REGISTRY[name].__name__}, "
                f"New class: {cls.__name__}"
            )
        STEP_REGISTRY[name] = cls
        logger.debug(f"Registered step '{name}' -> {cls.__name__}")
        return cls
    return decorator


def load_config(path: str) -> dict[str, Any]:
    """
    Load a YAML configuration file.
    
    Args:
        path: Filesystem path to the YAML configuration file
        
    Returns:
        Dictionary containing the parsed YAML configuration
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the file contains invalid YAML
    """
    logger.info(f"Loading configuration from {path}")
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    logger.debug(f"Configuration loaded successfully")
    return config


def build_pipeline_from_config(config: dict[str, Any]) -> Pipeline:
    """
    Build a Pipeline instance from a configuration dictionary.
    
    The config should have the structure:
        {
            "pipeline": {
                "name": "pipeline_name",
                "steps": [
                    {"type": "step_type", "param1": "value1", ...},
                    ...
                ]
            }
        }
    
    Args:
        config: Configuration dictionary (typically from load_config)
        
    Returns:
        Constructed Pipeline instance with all steps initialized
        
    Raises:
        KeyError: If required config keys are missing
        ValueError: If a step type is not found in STEP_REGISTRY
        TypeError: If a step is missing required constructor parameters
    """
    # Extract pipeline configuration
    if "pipeline" not in config:
        raise KeyError("Configuration must contain a 'pipeline' key")
        
    pipeline_config = config["pipeline"]
    pipeline_name = pipeline_config.get("name", "unnamed_pipeline")
    
    if "steps" not in pipeline_config:
        raise KeyError("Pipeline configuration must contain a 'steps' list")
        
    steps_config = pipeline_config["steps"]
    
    logger.info(f"Building pipeline '{pipeline_name}' with {len(steps_config)} steps")
    
    # Build step instances
    steps: list[Step] = []
    
    for i, step_config in enumerate(steps_config):
        if "type" not in step_config:
            raise KeyError(f"Step {i + 1} is missing required 'type' field")
            
        step_type = step_config["type"]
        
        # Look up step class in registry
        if step_type not in STEP_REGISTRY:
            available_types = ", ".join(sorted(STEP_REGISTRY.keys()))
            raise ValueError(
                f"Unknown step type '{step_type}' at position {i + 1}. "
                f"Available types: {available_types or '(none registered)'}"
            )
            
        step_class = STEP_REGISTRY[step_type]
        
        # Extract constructor parameters (all keys except 'type')
        step_params = {k: v for k, v in step_config.items() if k != "type"}
        
        # Instantiate the step
        try:
            step_instance = step_class(**step_params)
            steps.append(step_instance)
            logger.debug(f"Instantiated step {i + 1}: {step_type}")
        except TypeError as e:
            raise TypeError(
                f"Failed to instantiate step '{step_type}' at position {i + 1}: {e}"
            )
    
    # Create and return the pipeline
    pipeline = Pipeline(steps=steps, name=pipeline_name)
    logger.info(f"Pipeline '{pipeline_name}' built successfully")
    
    return pipeline
