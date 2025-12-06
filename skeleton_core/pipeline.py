"""
Core pipeline execution framework for Bonesaw.

This module defines the Step protocol and Pipeline class that form the foundation
of the Bonesaw automation framework. Steps are composable units of work that can
be chained together into pipelines.
"""

import logging
from typing import Any, Protocol, Optional

logger = logging.getLogger(__name__)


class Step(Protocol):
    """
    Protocol defining the interface for pipeline steps.
    
    All steps must implement a `run` method that accepts data from the previous
    step and a shared context dictionary, then returns data for the next step.
    """
    
    def run(self, data: Any, context: dict[str, Any]) -> Any:
        """
        Execute this step's processing logic.
        
        Args:
            data: Input data from the previous step (or initial_data for first step)
            context: Shared mutable dictionary for passing state between steps
            
        Returns:
            Output data to be passed to the next step
        """
        ...


class Pipeline:
    """
    Orchestrates execution of an ordered sequence of steps.
    
    A Pipeline takes a list of Step instances and executes them sequentially,
    passing the output of each step as input to the next. All steps share a
    common context dictionary for storing metadata and intermediate state.
    """
    
    def __init__(self, steps: list[Step], name: Optional[str] = None):
        """
        Initialize a pipeline with an ordered list of steps.
        
        Args:
            steps: Ordered list of Step instances to execute
            name: Optional name for the pipeline (used in logging)
        """
        self.steps = steps
        self.name = name or "unnamed_pipeline"
        
    def run(self, initial_data: Optional[Any] = None, context: Optional[dict[str, Any]] = None) -> Any:
        """
        Execute all steps in the pipeline sequentially.
        
        Args:
            initial_data: Starting data passed to the first step (defaults to None)
            context: Shared context dictionary (initialized as empty dict if None)
            
        Returns:
            The output from the final step in the pipeline
            
        Raises:
            Any exception raised by a step's run method will propagate to the caller
        """
        # Initialize context if not provided
        if context is None:
            context = {}
            
        logger.info(f"Pipeline '{self.name}' starting with {len(self.steps)} steps")
        
        # Start with initial data
        data = initial_data

        # Execute each step sequentially
        for i, step in enumerate(self.steps):
            step_name = step.__class__.__name__
            try:
                logger.info(f"Step {i + 1}/{len(self.steps)}: {step_name} starting")

                # Run the step and capture its output
                data = step.run(data, context)

                logger.info(f"Step {i + 1}/{len(self.steps)}: {step_name} completed")

            except Exception as e:
                logger.error(
                    f"Pipeline '{self.name}' failed at step {i + 1}/{len(self.steps)} "
                    f"({step_name}): {e}",
                    exc_info=True
                )
                raise RuntimeError(
                    f"Pipeline '{self.name}' failed at step {i + 1}/{len(self.steps)} "
                    f"({step_name}): {e}"
                ) from e

        logger.info(f"Pipeline '{self.name}' completed successfully")
        return data
