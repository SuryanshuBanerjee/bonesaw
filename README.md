# 🎃 Bonesaw

A Kiro-powered Skeleton Crew framework for building automation pipelines.

## Overview

Bonesaw provides a reusable Python skeleton for creating CLI automation pipelines ("jobs"). Define your pipeline steps in YAML, implement step logic, and let Bonesaw orchestrate the execution.

## Features

- **Pipeline Framework**: Composable step-based architecture
- **YAML Configuration**: Define pipelines declaratively
- **CLI Interface**: Easy command-line execution
- **Extensible**: Add custom steps for any automation task

## Example Applications

This repository includes two example applications built on the Bonesaw skeleton:

1. **Haunted Log Cleaner**: Parses messy logs, anonymizes data, aggregates errors, and generates markdown reports
2. **Graveyard Feed Reviver**: Fetches old RSS/Atom feeds, normalizes entries, and outputs structured data

## Quick Start

```bash
pip install -r requirements.txt
python main.py --help
```

## Built with Kiro

This project demonstrates spec-driven development, steering docs, hooks, and automation best practices using Kiro.

## License

MPL 2.0
