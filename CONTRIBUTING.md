# Contributing

Thanks for considering contributing to jsoncanon!

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```
uv sync --group dev
uv run prek install
```

To manually run all pre-commit hooks against all files:

```
uv run prek run --all-files
```

Hooks are split into two groups: `watch` (fast checks suitable for running on
every file save, e.g. from an editor or file watcher) and `commit` (the full
set run on `git commit`, including `mypy`). Run a specific group with:

```
uv run prek run --all-files --group watch
```

## Running tests

```
uv run pytest
```

## Code style

The project uses [ruff](https://docs.astral.sh/ruff/) for formatting and linting.

```
uv run ruff format
uv run ruff check
```

TOML files (`pyproject.toml`, `prek.toml`) are formatted with
[taplo](https://taplo.tamasfe.dev/), configured in `.taplo.toml`.

```
uv run taplo fmt
```

## Type checking

The project uses [pyright](https://microsoft.github.io/pyright/) (strict mode)
and [mypy](https://mypy-lang.org/) (strict mode) for static type checking.

```
uv run pyright src
uv run mypy src
```

## IDE setup

Run `uv sync --group dev` first so the `.venv` and development tools used below exist.

### VS Code

1. Install the extensions: **Python** (`ms-python.python`), **Pylance**
   (`ms-python.vscode-pylance`), **Ruff** (`charliermarsh.ruff`),
   **Mypy Type Checker** (`ms-python.mypy-type-checker`), and
   **Even Better TOML** (`tamasfe.even-better-toml`).
2. Select the interpreter: Command Palette → "Python: Select Interpreter" →
   choose `.venv/bin/python` (created by `uv sync`).
3. Set Ruff as the default formatter for Python and enable format-on-save:
   Settings → search "Default Formatter" → set to **Ruff** for the Python
   language, then enable "Editor: Format On Save".
4. Enable Ruff's fix-all and import-organizing on save: Settings → search
   "Code Actions On Save" → add `source.fixAll.ruff` and
   `source.organizeImports.ruff`, both set to `explicit`.
5. Pylance automatically picks up strict mode from `[tool.pyright]` in
   `pyproject.toml` — no extra configuration needed.
6. The Mypy extension picks up `[tool.mypy]` from `pyproject.toml`
   automatically once the interpreter is set.
7. Even Better TOML formats `.toml` files using `.taplo.toml`
   automatically. Enable format-on-save for TOML the same way as step 3.
8. Optionally, run the rest of the prek `watch` group (the checks not
   already covered by the Ruff extension or Even Better TOML above)
   automatically on save. VS Code has no built-in file watcher equivalent to
   PyCharm's, but the **Run on Save** extension (`emeraldwalk.runonsave`)
   provides the same behavior. Install it, then add to your `settings.json`
   (user or workspace, not committed):
   ```
   "emeraldwalk.runonsave": {
     "commands": [
       {
         "match": ".*",
         "cmd": "uv run prek run --group watch --files ${file}"
       }
     ]
   }
   ```

### PyCharm

1. Set the project interpreter to `.venv` (created by `uv sync`):
   Settings → Project → Python Interpreter → Add → select `.venv/bin/python`.
2. PyCharm includes Ruff support. Enable the bundled Ruff external tool under
   Settings → Python → Tools → **External Tools**;
   it picks up the config from `pyproject.toml` automatically. To format on
   save, go to Settings → Tools → **Actions on Save**, select **Reformat code**,
   and configure its file types to include **Python**.
3. Enable Pyright as the type checker: Settings → Languages & Frameworks →
   Python → Type Checker → select **Pyright**. It picks up strict mode from
   `[tool.pyright]` in `pyproject.toml`.
4. For mypy, either install the **Mypy** plugin or rely on `uv run mypy src`
   / the `commit` prek group.
5. Optionally, run the prek `watch` group (the checks not already covered by
   Ruff above — trailing whitespace/EOF fixers and taplo)
   automatically on save via a File Watcher: Settings → Tools →
   File Watchers → **+** → **Custom**:
   - Name: `prek watch`
   - File type: `Any`
   - Program: `uv` (or the full path from `which uv`)
   - Arguments: `run prek run --group watch --files $FilePath$`
   - Working directory: `$ProjectFileDir$`
   - Under **Advanced Options**, uncheck "Auto-save edited files to trigger
     the watcher" if you only want it to run on explicit save (Cmd/Ctrl+S).

## Submitting changes

1. Fork the repository and create a branch for your change.
2. Make your changes, ensuring tests pass and code is formatted/linted.
3. Add or update tests to cover your change.
4. Open a pull request describing the change and the motivation behind it.

## Releasing

Release versions are derived from Git tags. A tag `vX.Y.Z` produces a package
with version `X.Y.Z`. Release notes are reviewed as a draft GitHub Release,
then the approved release assets are published to PyPI using
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (no API tokens
stored as secrets).

### One-time setup

On the [PyPI publishing settings](https://pypi.org/manage/project/jsoncanon/settings/publishing/)
page, add a trusted publisher with:

- Owner: `sveinugu`
- Repository: `jsoncanon`
- Workflow filename: `release.yml`
- Environment name: `pypi`

### Preparing and reviewing a release

1. On GitHub, open **Actions → Prepare release → Run workflow** and select
   `main`.
2. Enter the new tag as `vX.Y.Z` (for example, `v0.2.4`) and run the workflow.
3. The workflow runs CI, creates the tag locally, builds the tagged version,
   then pushes the tag and creates a draft GitHub Release with generated notes
   and the wheel and source distribution attached.
4. Open the draft under **Releases**, review and edit its notes, then click
   **Publish release**.
5. Publishing the GitHub Release runs `.github/workflows/release.yml`, which
   uploads the previously validated release assets to PyPI.

If preparation fails before the draft release is created, no remote tag or
PyPI release is created. Fix the issue on `main` and run **Prepare release**
again with the same version. If PyPI publishing fails without uploading any
files, rerun the failed publish job.
