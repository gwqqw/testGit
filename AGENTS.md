# Repository Guidelines

## Project Structure & Module Organization

- Source lives in `src/rag_mcp/` (FastMCP server, indexing, embeddings).
- Tests live in `tests/` and import from `src/` via `tests/conftest.py`.
- Reference documents for indexing are in `docs/`. The vector index persists under `data/` (runtime output; keep untracked).

## Build, Test, and Development Commands

- Install dependencies: `pip install -r requirements.txt`
- Install test tooling: `pip install -r requirements-dev.txt`
- Run the MCP server (PowerShell): `$env:PYTHONPATH=\"src\"; python -m rag_mcp.server`
- Run tests: `python -m pytest`

## Coding Style & Naming Conventions

- Indentation: 4 spaces, no tabs.
- File names: lowercase with underscores (for example, `data_loader.cpp`).
- C++ (if added): `UpperCamelCase` for types, `lower_snake_case` for functions/variables, `kConstant` for constants.
- Add a formatter or linter config (for example, `.editorconfig` or `.clang-format`) in the repo root and keep it consistent across files.

## Testing Guidelines

- Use `pytest`. New behavior and bug fixes should include tests in `tests/`.
- Keep tests deterministic; unit tests use the simple embedding backend to avoid network/model downloads.

## Commit & Pull Request Guidelines

- Existing commit history uses short, lowercase summaries (for example, "hotfix", "conflict fixed"). Keep messages concise and action-oriented.
- Pull requests should include: a brief description, linked issue or context, steps to verify, and screenshots for UI changes.

## Security & Configuration Tips

- Keep secrets out of the repository. Use local environment files (for example, `.env.local`) and add them to `.gitignore` if introduced.
