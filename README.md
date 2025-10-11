# 🎵 Xenharmonic Voyager

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://xenharmonic-voyager.streamlit.app/)
[![CI](https://github.com/endo-ava/xenharmonic-voyager/actions/workflows/ci.yml/badge.svg)](https://github.com/endo-ava/xenharmonic-voyager/actions/workflows/ci.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

An experimental web application to explore xenharmonic consonance using Sethares' acoustic roughness model.

## Overview

Xenharmonic Voyager is an interactive visualization tool that calculates and displays consonance scores for chords in various equal divisions of the octave (N-EDO). Unlike traditional music theory apps that focus on 12-tone equal temperament (12-EDO), this application allows you to explore the acoustic properties of alternative tuning systems.

The application implements Sethares' acoustic roughness model to provide objective, physics-based consonance measurements rather than relying on cultural conventions or subjective judgments.

## Features

- **N-EDO Support**: Analyze chords in 12-EDO, 19-EDO, and potentially other equal divisions
- **Consonance Calculation**: Uses Sethares' (1993) acoustic roughness model
- **Interactive UI**: Built with Streamlit for rapid prototyping and experimentation
- **Scientific Computing**: Leverages NumPy for efficient harmonic series calculations

## Technology Stack

### Core Dependencies
- **Python 3.13+**: Modern Python features and performance
- **Streamlit**: Interactive web application framework
- **NumPy**: Numerical computing for frequency and harmonic calculations
- **Pydantic**: Runtime type checking and data validation

### Development Tools
- **uv**: Fast Python package and project manager
- **Ruff**: Lightning-fast linting and formatting
- **Pytest**: Comprehensive testing framework with coverage reporting
- **pre-commit**: Git hooks for code quality enforcement

## Getting Started

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/endo-ava/xenharmonic-voyager.git
cd xenharmonic-voyager
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Install pre-commit hooks:
```bash
uv run pre-commit install
```

### Running the Application

Start the Streamlit development server:
```bash
uv run streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Running Tests

Execute the test suite with coverage:
```bash
uv run pytest
```

### Code Quality

Run linting and formatting:
```bash
# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

## Project Structure

```
xenharmonic-voyager/
├── app.py                  # Streamlit main application
├── src/
│   ├── __init__.py
│   └── calculator.py       # Consonance calculation logic
├── tests/
│   ├── __init__.py
│   └── test_calculator.py  # Unit tests
├── docs/                   # Project documentation
├── .pre-commit-config.yaml # Pre-commit hooks
├── ruff.toml              # Ruff configuration
├── pytest.ini             # Pytest configuration
└── pyproject.toml         # Project metadata and dependencies
```

## Acknowledgments

- William Sethares for the acoustic roughness model
- The Xenharmonic community for inspiration and resources
