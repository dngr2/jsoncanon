# Contributing

Thanks for considering contributing to jsoncanon!

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```
uv sync
```

## Running tests

```
uv run pytest
```

## Code style

The project uses `yapf` for formatting, `isort` for import sorting, and `flake8` for linting.

```
uv run yapf -ir src tests
uv run isort src tests
uv run flake8 src tests
```

## Submitting changes

1. Fork the repository and create a branch for your change.
2. Make your changes, ensuring tests pass and code is formatted/linted.
3. Add or update tests to cover your change.
4. Open a pull request describing the change and the motivation behind it.

