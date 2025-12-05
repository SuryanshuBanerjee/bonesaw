"""
App scaffolding utilities for Bonesaw.

Provides functions to generate new application skeletons with working pipelines.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_app_files(app_name: str, target_dir: Path) -> None:
    """
    Generate all files for a new Bonesaw app.
    
    Args:
        app_name: Name of the app
        target_dir: Target directory (apps/<app_name>/)
    """
    # Ensure target directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate each file
    _write_init_py(target_dir)
    _write_pipelines_py(app_name, target_dir)
    _write_config_yml(app_name, target_dir)
    _write_sample_input(app_name, target_dir)
    _write_readme(app_name, target_dir)
    
    logger.info(f"Generated all files for app '{app_name}'")


def _write_init_py(target_dir: Path) -> None:
    """Write __init__.py file."""
    content = f'"""{target_dir.name.replace("_", " ").title()} application."""\n'
    (target_dir / "__init__.py").write_text(content, encoding="utf-8")


def _write_pipelines_py(app_name: str, target_dir: Path) -> None:
    """Write pipelines.py with four working steps including LLM summary."""
    content = f'''"""
{app_name.replace("_", " ").title()} - Pipeline steps for text processing.

This module defines steps for loading, transforming, and reporting on text files.
"""

import logging
from typing import Any

from skeleton_core.config import register_step
from skeleton_core.summarization import summarize_text

logger = logging.getLogger(__name__)


@register_step("load_text")
class LoadTextStep:
    """
    Load a text file and return a list of lines.
    
    Input: None (or ignored)
    Output: list[str] of text lines
    Context: Writes 'source_file' with the loaded file path
    """
    
    def __init__(self, input_path: str):
        """
        Initialize the text loader.
        
        Args:
            input_path: Path to the text file to load
        """
        self.input_path = input_path
    
    def run(self, data: Any, context: dict[str, Any]) -> list[str]:
        """Load text file and return lines."""
        logger.info(f"Loading text from {{self.input_path}}")
        
        with open(self.input_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\\n') for line in f]
        
        context['source_file'] = self.input_path
        logger.info(f"Loaded {{len(lines)}} lines")
        
        return lines


@register_step("transform_text")
class TransformTextStep:
    """
    Apply simple transformations to each line (uppercase, line numbers).
    
    Input: list[str] of text lines
    Output: list[str] of transformed lines
    Context: Writes 'transformations_applied' with list of transformation names
    """
    
    def __init__(self, uppercase: bool = True, prefix_line_numbers: bool = True):
        """
        Initialize the text transformer.
        
        Args:
            uppercase: Convert lines to uppercase
            prefix_line_numbers: Prefix each line with line number
        """
        self.uppercase = uppercase
        self.prefix_line_numbers = prefix_line_numbers
    
    def run(self, data: Any, context: dict[str, Any]) -> list[str]:
        """Transform text lines."""
        lines = data
        transformations = []
        
        logger.info(f"Transforming {{len(lines)}} lines")
        
        result = []
        for i, line in enumerate(lines):
            transformed = line
            
            if self.uppercase:
                transformed = transformed.upper()
                if 'uppercase' not in transformations:
                    transformations.append('uppercase')
            
            if self.prefix_line_numbers:
                transformed = f"{{i + 1}}: {{transformed}}"
                if 'line_numbers' not in transformations:
                    transformations.append('line_numbers')
            
            result.append(transformed)
        
        context['transformations_applied'] = transformations
        logger.info(f"Applied transformations: {{', '.join(transformations)}}")
        
        return result


@register_step("write_text_report")
class WriteTextReportStep:
    """
    Write a markdown report summarizing the processed text.
    
    Input: list[str] of processed text lines
    Output: Same list (pass-through)
    Context: Writes 'report_path' with the output file path
    """
    
    def __init__(self, output_path: str):
        """
        Initialize the report writer.
        
        Args:
            output_path: Path where the markdown report will be written
        """
        self.output_path = output_path
    
    def run(self, data: Any, context: dict[str, Any]) -> list[str]:
        """Generate and write markdown report."""
        lines = data
        
        logger.info(f"Writing report to {{self.output_path}}")
        
        # Build markdown content
        report_lines = [
            "# 🩸 Bonesaw Text Report",
            "",
            "## Summary",
            "",
            f"**Total lines processed:** {{len(lines)}}",
            ""
        ]
        
        # Show transformations if available
        if 'transformations_applied' in context:
            transformations = context['transformations_applied']
            report_lines.append(f"**Transformations applied:** {{', '.join(transformations)}}")
            report_lines.append("")
        
        # Show first few lines as preview
        preview_count = min(3, len(lines))
        if preview_count > 0:
            report_lines.append("## Preview (first {{}} lines)".format(preview_count))
            report_lines.append("")
            for line in lines[:preview_count]:
                report_lines.append(f"- {{line}}")
            report_lines.append("")
        
        # Include full transformed text
        report_lines.append("## Full Transformed Text")
        report_lines.append("")
        report_lines.append("```")
        report_lines.extend(lines)
        report_lines.append("```")
        report_lines.append("")
        
        # Write to file
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write('\\n'.join(report_lines))
        
        context['report_path'] = self.output_path
        logger.info("Report written successfully")
        
        return lines


@register_step("text_llm_summary")
class TextLLMSummaryStep:
    """
    Append a deterministic + optional LLM-powered summary of the transformed text to the report.
    
    Input: list[str] of transformed text lines
    Output: Same list (pass-through)
    Context: Writes 'llm_summary' with the generated summary text
    """
    
    def __init__(self, report_path: str):
        """
        Initialize the text summary generator.
        
        Args:
            report_path: Path to the markdown report to append summary to
        """
        self.report_path = report_path
    
    def run(self, data: Any, context: dict[str, Any]) -> list[str]:
        """Generate and append text summary."""
        lines = data
        
        logger.info("Generating text summary")
        
        # Use the robust summarization system
        summary_text = summarize_text(lines, context)
        
        # Append to the existing report
        with open(self.report_path, 'a', encoding='utf-8') as f:
            f.write("\\n## 🔮 AI Summary\\n\\n")
            f.write(summary_text)
            f.write("\\n")
        
        context['llm_summary'] = summary_text
        logger.info("Summary appended to report")
        
        return lines
'''
    (target_dir / "pipelines.py").write_text(content, encoding="utf-8")


def _write_config_yml(app_name: str, target_dir: Path) -> None:
    """Write config.example.yml with LLM summary step."""
    content = f'''pipeline:
  name: {app_name}
  steps:
    - type: load_text
      input_path: "apps/{app_name}/sample_input.txt"
    
    - type: transform_text
      uppercase: true
      prefix_line_numbers: true
    
    - type: write_text_report
      output_path: "apps/{app_name}/output_report.md"
    
    - type: text_llm_summary
      report_path: "apps/{app_name}/output_report.md"
'''
    (target_dir / "config.example.yml").write_text(content, encoding="utf-8")


def _write_sample_input(app_name: str, target_dir: Path) -> None:
    """Write sample_input.txt."""
    content = f'''Welcome to the Bonesaw pipeline.
This file was generated for app "{app_name}".
Each line will be transformed and reported.
The framework makes it easy to build automation pipelines.
Try modifying the config to change transformations!
'''
    (target_dir / "sample_input.txt").write_text(content, encoding="utf-8")


def _write_readme(app_name: str, target_dir: Path) -> None:
    """Write README.md."""
    content = f'''# {app_name.replace("_", " ").title()}

A Bonesaw application for text processing and transformation.

## What It Does

This app demonstrates the Bonesaw pipeline framework with a simple text processing workflow:

1. **Load Text**: Reads a text file line by line
2. **Transform Text**: Applies transformations (uppercase, line numbering)
3. **Write Report**: Generates a markdown report with the processed text

## Running the Application

### Inspect the Pipeline

See the pipeline structure without executing:

```bash
python main.py inspect --app {app_name} --config apps/{app_name}/config.example.yml
```

### Dry Run

Preview what would be executed:

```bash
python main.py dry-run --app {app_name} --config apps/{app_name}/config.example.yml
```

### Execute the Pipeline

Run the full pipeline:

```bash
python main.py run --app {app_name} --config apps/{app_name}/config.example.yml
```

## Output

The pipeline generates a markdown report at:
```
apps/{app_name}/output_report.md
```

The report includes:
- Summary statistics (line count, transformations)
- Preview of first few lines
- Full transformed text

## Customization

Edit `config.example.yml` to customize the pipeline:

- Change `uppercase` to `false` to preserve original case
- Change `prefix_line_numbers` to `false` to skip line numbering
- Modify `input_path` to process different text files
- Adjust `output_path` for different report locations

## Architecture

```
Load Text → Transform Text → Write Report
```

Each step is independent and composable, following the Bonesaw framework patterns.
'''
    (target_dir / "README.md").write_text(content, encoding="utf-8")
