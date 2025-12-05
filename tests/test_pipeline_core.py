"""
Tests for core pipeline functionality.

Tests the Pipeline class and configuration loading.
"""

from typing import Any

import pytest

from skeleton_core.config import build_pipeline_from_config
from skeleton_core.pipeline import Pipeline


class AddOneStep:
    """Test step that adds 1 to the input."""
    
    def run(self, data: Any, context: dict[str, Any]) -> Any:
        return data + 1


class MultiplyByTwoStep:
    """Test step that multiplies input by 2."""
    
    def run(self, data: Any, context: dict[str, Any]) -> Any:
        return data * 2


def test_pipeline_executes_steps_in_order():
    """Test that pipeline executes steps sequentially with correct data flow."""
    pipeline = Pipeline(
        [AddOneStep(), MultiplyByTwoStep()],
        name="test_pipeline"
    )
    
    # (3 + 1) * 2 = 8
    result = pipeline.run(initial_data=3, context={})
    
    assert result == 8


def test_pipeline_with_empty_context():
    """Test that pipeline initializes empty context if None provided."""
    pipeline = Pipeline([AddOneStep()], name="test_empty_context")
    
    result = pipeline.run(initial_data=5)
    
    assert result == 6


def test_build_pipeline_with_unknown_step_type():
    """Test that building a pipeline with unknown step type raises ValueError."""
    bad_config = {
        "pipeline": {
            "name": "bad_pipeline",
            "steps": [
                {"type": "this_step_does_not_exist"}
            ]
        }
    }
    
    with pytest.raises(ValueError) as exc_info:
        build_pipeline_from_config(bad_config)
    
    assert "Unknown step type" in str(exc_info.value)
    assert "this_step_does_not_exist" in str(exc_info.value)


def test_build_pipeline_missing_steps_key():
    """Test that config without 'steps' key raises KeyError."""
    bad_config = {
        "pipeline": {
            "name": "no_steps"
        }
    }
    
    with pytest.raises(KeyError) as exc_info:
        build_pipeline_from_config(bad_config)
    
    assert "steps" in str(exc_info.value)
