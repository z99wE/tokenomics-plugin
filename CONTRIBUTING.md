# Contributing to Tokenomics

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/z99wE/tokenomics-plugin.git
cd tokenomics
pip install -e .
pip install ruff
```

## Running Tests

```bash
python -m unittest tokenomics.tests.test_core tokenomics.tests.test_hermes tokenomics.tests.test_cli -v
```

## Linting

```bash
ruff check .
```

## Commit Conventions

Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, `test:`.

## Pull Requests

- Include tests for new functionality.
- Keep changes focused and minimal.
- Update documentation when behavior changes.
- Ensure CI passes before requesting review.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
