# Skeleton Core Framework Specification

## Overview

This specification defines the core framework for Bonesaw, a pipeline-based automation system. The framework provides a composable architecture where discrete processing steps can be chained together to form complete automation pipelines. Each pipeline is configured via YAML and executed through a simple, consistent interface.

## Core Abstractions

### Step Interface

A Step represents a single unit of work in a pipeline. All steps must conform to a common interface (protocol) that defines how they receive input, process data, and produce output.

**Interface Requirements:**

- Each Step must implement a single method: `run(self, data, context) -> Any`
- The `run` method accepts two parameters:
  - `data`: The output from the previous step (or initial input for the first step). Can be any Python object.
  - `context`: A mutable dictionary (`dict[str, Any]`) that is shared across all steps in the pipeline. Steps can read from and write to this context to share state or metadata.
- The `run` method returns a value of any type, which becomes the `data` input for the next step in the pipeline.

**Behavior:**

- Each step receives the previous step's output as its `data` parameter.
- Steps can store intermediate results, configuration, or metadata in the shared `context` dictionary.
- The return value from `run` is passed as `data` to the next step.
- Steps should be independent and composable - they should not make assumptions about what other steps exist in the pipeline.

### Pipeline Class

A Pipeline orchestrates the execution of an ordered sequence of steps.

**Constructor:**

- Takes a single parameter: an ordered list of Step instances.
- The order of steps in the list determines the execution order.

**Run Method:**

- Signature: `run(initial_data: Any | None = None, context: dict[str, Any] | None = None) -> Any`
- Parameters:
  - `initial_data`: The starting data passed to the first step. Defaults to `None` if not provided.
  - `context`: A dictionary for sharing state across steps. If `None`, an empty dictionary is initialized.
- Returns: The output from the final step in the pipeline.

**Behavior:**

- If `context` is `None`, initialize it as an empty dictionary before execution begins.
- Execute each step sequentially by calling `step.run(data, context)`.
- The `data` parameter for the first step is `initial_data`.
- For each subsequent step, the `data` parameter is the return value from the previous step.
- After all steps complete, return the output from the final step.

## Step Registry

The framework provides a global registry mechanism for discovering and instantiating steps by name.

**Registry Structure:**

- A global dictionary named `STEP_REGISTRY` with type `dict[str, type[Step]]`.
- Keys are string names that identify step types.
- Values are Step classes (not instances).

**Registration Decorator:**

- A decorator function `@register_step(name: str)` that registers Step classes into the registry.
- Usage: Applied to a Step class definition to make it available for lookup by name.
- The `name` parameter is the string key used to identify this step type in configuration files.

**Uniqueness Constraint:**

- Step names in the registry must be unique.
- If a step name is already registered, the decorator should overwrite the existing registration with the new class. This allows for step redefinition during development or testing.

## Configuration Format

Pipelines are defined using YAML configuration files with the following structure:

```yaml
pipeline:
  name: example_pipeline
  steps:
    - type: read_input
      source: input.txt
    - type: process_input
      mode: normalize
      threshold: 10
```

**Structure Details:**

- **`pipeline.name`**: An arbitrary string identifier for the pipeline. Used for logging and display purposes.
- **`pipeline.steps`**: An ordered list of step configurations. Each step configuration is a dictionary containing:
  - **`type`** (required): A string key that corresponds to a registered step name in `STEP_REGISTRY`.
  - **Additional keys**: Any other key-value pairs are treated as constructor parameters for the step. These are passed as keyword arguments when instantiating the step class.

**Loading Behavior:**

- The YAML file is loaded into a Python dictionary structure.
- A helper function `build_pipeline_from_config(config: dict) -> Pipeline` processes the configuration:
  1. Extracts the `pipeline.steps` list from the config dictionary.
  2. For each step configuration:
     - Looks up the step class in `STEP_REGISTRY` using the `type` value.
     - Extracts all configuration keys except `type`.
     - Instantiates the step class, passing the extracted keys as keyword arguments.
  3. Constructs and returns a Pipeline instance with all instantiated steps in order.

## Error Handling

The framework must provide clear, actionable error messages for common configuration and runtime issues.

**Unknown Step Types:**

- If a step's `type` value is not found in `STEP_REGISTRY`, raise a descriptive exception.
- The exception message should include:
  - The unknown step type name.
  - A list of available registered step types (for debugging).
  - The position in the pipeline where the error occurred.

**Missing Required Parameters:**

- If a step class requires constructor parameters that are not provided in the configuration, Python's standard `TypeError` will be raised.
- The framework should allow this exception to propagate with its default message, as it clearly indicates which parameters are missing.

**Step Execution Errors:**

- If a step's `run` method raises an exception during execution, the exception should propagate to the caller.
- The framework should not catch or suppress step execution errors, as they indicate problems with the step's logic or data.

**General Principle:**

- All errors should fail fast with clear messages that help developers identify and fix the issue quickly.

## Logging Guidelines

The framework must use Python's standard `logging` module for observability and debugging.

**Required Log Points:**

- **Pipeline Start**: Log when a pipeline begins execution, including the pipeline name (if available from config).
- **Pipeline End**: Log when a pipeline completes successfully, including execution time if feasible.
- **Step Start**: Log when each step begins execution, including the step's type or class name.
- **Step End**: Log when each step completes successfully.
- **Errors**: Log any exceptions or errors with full context, including which step failed and the error message.

**Log Levels:**

- Use `INFO` level for normal execution flow (pipeline start/end, step start/end).
- Use `ERROR` level for exceptions and failures.
- Use `DEBUG` level for detailed information like data shapes or context contents (optional).

**No External Frameworks:**

- Only use Python's built-in `logging` module.
- Do not introduce external logging libraries or frameworks.

## Example Configuration

Below is a complete example configuration demonstrating the YAML format:

```yaml
pipeline:
  name: simple_data_processor
  steps:
    - type: read_input
      filepath: data/input.txt
      encoding: utf-8
    - type: process_input
      operation: uppercase
      strip_whitespace: true
    - type: write_output
      filepath: data/output.txt
```

**Explanation:**

- The pipeline is named `simple_data_processor`.
- It consists of three steps executed in order:
  1. **read_input**: Reads data from a file. Receives `filepath` and `encoding` as constructor parameters.
  2. **process_input**: Processes the data. Receives `operation` and `strip_whitespace` as constructor parameters.
  3. **write_output**: Writes the processed data to a file. Receives `filepath` as a constructor parameter.

Each step's `type` must correspond to a registered step class in `STEP_REGISTRY`. The additional parameters are passed to the step's constructor when the pipeline is built.

## Design Principles

- **Simplicity**: The framework should be easy to understand and extend.
- **Composability**: Steps should be independent and reusable across different pipelines.
- **Declarative Configuration**: Pipelines are defined in YAML, separating configuration from code.
- **Extensibility**: New step types can be added by implementing the Step interface and registering them.
- **Observability**: Logging provides visibility into pipeline execution for debugging and monitoring.
