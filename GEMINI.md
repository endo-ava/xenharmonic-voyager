# Project Overview

This project, "Xenharmonic Voyager," is an experimental web application designed to explore the concept of xenharmonic consonance. It utilizes Sethares' acoustic roughness model to calculate and visualize consonance scores for musical chords in various equal divisions of the octave (N-EDO). The application is built with Python and Streamlit, leveraging NumPy for scientific computing and Pydantic for data validation.

The primary goal of this project is to serve as a portfolio piece, demonstrating skills in Python, scientific computing, and web application development.

# Building and Running

The project uses `uv` for package and environment management.

**Installation:**

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    uv sync
    ```
3.  Install pre-commit hooks:
    ```bash
    uv run pre-commit install
    ```

**Running the Application:**

To start the Streamlit development server, run:
```bash
uv run streamlit run app.py
```
The application will be available at `http://localhost:8501`.

**Running Tests:**

To execute the test suite, run:
```bash
uv run pytest
```

# Development Conventions

*   **Code Style:** The project uses `Ruff` for linting and formatting. The configuration is in `ruff.toml`.
*   **Testing:** Unit tests are written using `Pytest` and are located in the `tests/` directory. The configuration is in `pytest.ini`.
*   **Git Hooks:** `pre-commit` is used to enforce code quality checks before committing. The configuration is in `.pre-commit-config.yaml`.
*   **Dependencies:** Project dependencies are managed in `pyproject.toml`.



# 主要な開発コマンド

```bash
# 依存関係のインストール（開発依存含む）
uv sync

# Streamlitアプリケーションの起動（開発サーバー）
uv run streamlit run app.py

# Lintとフォーマットのチェック
uv run ruff check .
uv run ruff format --check .

# 自動フォーマット適用
uv run ruff format .

# テストの実行
uv run pytest

# カバレッジ付きテスト実行
uv run pytest --cov=src --cov-report=html

# pre-commitフックのインストール
uv run pre-commit install

# pre-commitフックの手動実行
uv run pre-commit run --all-files
```
