# Contributing to SEIM

Thank you for your interest in contributing to the Student Exchange Information Manager (SEIM) project!

## Getting Started

1. **Fork the repository** and clone your fork locally.
2. **Set up the development environment** (see [installation guide](documentation/installation.md)).
3. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Branching & Pull Requests

- Use descriptive branch names: `feature/`, `bugfix/`, `docs/`, etc.
- Keep your branch up to date with `main`.
- Open a Pull Request (PR) against the `main` branch.
- Reference related issues in your PR description.
- Ensure your PR passes all CI checks and code reviews.

## Code Style & Linting

- Follow PEP8 and Django best practices.
- Use type annotations where possible.
- Run linters and formatters before committing:
  ```bash
  make quality-check  # Run all quality checks
  # Or individually:
  ruff check .        # Linting
  ruff format .       # Formatting
  flake8             # Additional linting
  isort .            # Import sorting
  mypy .             # Type checking
  ```

## Commit Messages

- Use clear, descriptive commit messages.
- Example: `fix: correct document upload validation`

## Issues & Feature Requests

- Use GitHub Issues to report bugs or request features.
- Provide clear steps to reproduce bugs or describe feature needs.

## Code Review Process

- All code must be reviewed before merging.
- Address all reviewer comments and suggestions.
- Be respectful and constructive in feedback.

## Security & Conduct

- Report security issues privately to the project maintainer.
- Follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/).

## 📚 Documentation Standards & Generation

- All documentation (API, code, Sphinx HTML) must be generated using Docker containers for consistency.
- Use the Makefile targets for all documentation tasks:
  - `make docs-api` for API docs
  - `make docs-sphinx-docker` for Sphinx HTML docs
  - `make docs-workflow` for the full workflow
- Always update docstrings and run the full documentation workflow before submitting a PR.
- See the [developer guide](documentation/developer_guide.md) and [README](README.md) for details.

## Questions?

See the [Support & Contact](README.md#support--contact) section or open an issue on GitHub. 