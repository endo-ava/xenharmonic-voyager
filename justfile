# Xenharmonic Voyager - Development Commands
# Run `just --list` to see all available commands

# Default recipe (show help)
default:
    @just --list

# Install dependencies (including dev dependencies)
install:
    uv sync

# Run the Streamlit application
dev:
    uv run streamlit run app.py

# Run all tests
test:
    uv run pytest

# Run lint checks (without fixing)
lint:
    uv run ruff check .

# Run format checks (without fixing)
format-check:
    uv run ruff format --check .

# Run type checks
typecheck:
    uv run mypy src --strict --ignore-missing-imports

# Auto-fix lint issues
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Run pre-commit hooks on all files (auto-fixes issues)
pre:
    uv run pre-commit run --all-files

# Install pre-commit hooks
pre-install:
    uv run pre-commit install

# Prepare for commit: auto-fix everything
prepare:
    @echo "🔧 Auto-fixing lint and format issues..."
    uv run ruff check --fix .
    uv run ruff format .
    @echo "🔍 Running type checks..."
    uv run mypy src --strict --ignore-missing-imports
    @echo "✨ Running pre-commit hooks..."
    uv run pre-commit run --all-files || uv run pre-commit run --all-files
    @echo "✅ Ready to commit!"

# Clean generated files
clean:
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf .coverage
    rm -rf .ruff_cache
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
