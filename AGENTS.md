# Repository Guidelines

## Project Structure & Module Organization

- The repository is currently flat, with seed files in the root: `readme.txt`, `b.txt`, and `test.txt`.
- There are no `src/`, `tests/`, or `docs/` directories yet. If you add code, create clear top-level folders (for example, `src/` for implementation, `tests/` for automated tests, and `docs/` for documentation) and keep the root minimal.

## Build, Test, and Development Commands

- No build or test tooling is configured yet.
- When adding tooling, document the exact commands here. Example layout (replace with real commands once they exist):
  - `./scripts/build.ps1` - build or package the project.
  - `./scripts/test.ps1` - run the automated test suite.
  - `./scripts/dev.ps1` - run the project locally or start a dev server.

## Coding Style & Naming Conventions

- Indentation: 4 spaces, no tabs.
- File names: lowercase with underscores (for example, `data_loader.cpp`).
- C++ (if added): `UpperCamelCase` for types, `lower_snake_case` for functions/variables, `kConstant` for constants.
- Add a formatter or linter config (for example, `.editorconfig` or `.clang-format`) in the repo root and keep it consistent across files.

## Testing Guidelines

- No test framework is configured yet.
- If you add tests, prefer a standard framework for the language and keep tests next to code (`tests/`) with clear naming (`*_test` or `test_*`).
- Require tests for new behavior and bug fixes, and document the exact test command in the section above.

## Commit & Pull Request Guidelines

- Existing commit history uses short, lowercase summaries (for example, "hotfix", "conflict fixed"). Keep messages concise and action-oriented.
- Pull requests should include: a brief description, linked issue or context, steps to verify, and screenshots for UI changes.

## Security & Configuration Tips

- Keep secrets out of the repository. Use local environment files (for example, `.env.local`) and add them to `.gitignore` if introduced.