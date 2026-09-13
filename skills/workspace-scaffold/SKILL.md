---
name: workspace-scaffold
description: The skeleton files a new repository or package starts from — root and package pyproject.toml for a uv workspace, the import-linter contracts that enforce dependency direction, mkdocs.yml, and the CI commands. Invoke when planning a repo's Toolchain section or when scaffolding the first section of a repo or package. Values come from docs/architecture.md; this skill supplies the shapes.
---

# Workspace scaffold

The shapes a repo starts from. Kept out of the always-loaded path because only two runs ever
need them: the architect writing the repo contract's **Toolchain** section, and the implementer
scaffolding the first section of a repo or a package. Everything repo-specific — package names,
dependency order, env prefixes — comes from `docs/architecture.md`; copy shapes from here and
values from there.

The lint thresholds are **not** here. They live in `${CLAUDE_PLUGIN_ROOT}/pyproject-lint-config.toml`, which
is merged into the root `pyproject.toml` verbatim; a second copy would drift.

## 1. Root `pyproject.toml` (workspace)

```toml
[project]
name = "<repo>"
version = "0.0.0"
requires-python = ">=3.12"
dependencies = []

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
# one line per package, so members resolve each other from the workspace, not PyPI
data = { workspace = true }
analysis = { workspace = true }

[dependency-groups]
dev = ["pytest", "pytest-mock", "ruff", "pylint", "import-linter", "mkdocs-material", "mkdocstrings[python]"]

# --- merge ${CLAUDE_PLUGIN_ROOT}/pyproject-lint-config.toml here: [tool.ruff*], [tool.pylint*] ---

# --- import-linter: copy the block from docs/architecture.md § Dependency graph ---
[tool.importlinter]
root_packages = []          # grown by the scaffold step as packages are first built
```

The root is itself a workspace member (uv requires it), so it needs a `[project]` table even
though it holds no code. One lockfile, one virtual environment, shared by every package.

## 2. Package `pyproject.toml`

```toml
[project]
name = "<pkg>"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2",
    "pydantic-settings>=2",
    "loguru",
    # upstream packages by name; resolved from the workspace via the root's [tool.uv.sources]
]

[project.scripts]
# <pkg>-<verb> = "<pkg>.cli:<function>"   — added by /project-workers:finalize-package; the module must live
#                                          inside src/<pkg>/ or the entry point cannot resolve

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/<pkg>"]
```

Nothing about lint, import-linter, or docs goes here — the root owns those.

## 3. import-linter contracts

Three kinds of contract, all in the root `pyproject.toml`. `layers` lists **highest first**;
indirect import chains count; a layer that does not exist yet fails the check unless it is
wrapped `(pkg)`, which is why the scaffold step adds packages as they are built rather than
listing the whole target up front. Packages must be importable — run inside the workspace
environment.

```toml
[tool.importlinter]
root_packages = ["analysis", "data"]            # every package built so far

# 1. Package dependency direction — from docs/architecture.md, highest first.
[[tool.importlinter.contracts]]
name = "package dependency direction"
type = "layers"
layers = ["ml", "analysis", "data"]

# 2. Consumers use the public surface only — one per shipped package, listing its sections.
#    Written by /project-workers:finalize-package from the package contract's Sections table.
[[tool.importlinter.contracts]]
name = "data: consumers import the top level only"
type = "forbidden"
source_modules = ["analysis", "ml"]
forbidden_modules = ["data.ingest", "data.clean", "data.audit", "data.storage"]

# 3. Section layering inside a package — from surface.md §5, derived from the Sections
#    table's Depends on column. `|` separates sections that may not import each other.
[[tool.importlinter.contracts]]
name = "data: section layering"
type = "layers"
containers = ["data"]
layers = ["storage", "audit | clean", "ingest"]
```

`pipelines` and `configs` are container-level modules, not layers, so a pipeline that imports
every section is legal. `lint-imports` is the command; it exits non-zero on any broken contract.

**Growing the block.** The first `/project-workers:implement-section` of a package adds the package to
`root_packages` and to contract 1 in the position `docs/architecture.md` gives, and adds
contract 3 for that package. `/project-workers:finalize-package` adds contract 2. Never list a package that
has no code yet.

## 4. `mkdocs.yml`

```yaml
site_name: <repo>
docs_dir: docs                       # the planning docs; API pages go under docs/api/
exclude_docs: |
  plans/**                           # proposal history stays out of the site
  packages/*/sources/*.json          # probe samples and scripts are data, not pages
  packages/*/sources/*.py
theme:
  name: material
plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [packages/*/src]     # uv workspace layout
          options:
            docstring_style: google
            merge_init_into_class: true
            show_source: false
nav:
  - Home: index.md                    # stub written at scaffold; regenerated by /project-workers:finalize-project
  - Architecture: architecture.md
  - Decisions: decisions.md
  - API: []                           # /project-workers:finalize-package appends "- <pkg>: api/<pkg>.md" per package
```

The site must build strict from the first scaffold onward, so the `nav` only ever names
files that exist: the scaffold step writes a stub `docs/index.md` (repo name, the Goal
paragraph, links to `architecture.md` and `decisions.md`) and a nav with `Home`,
`Architecture`, and `Decisions`; each `/project-workers:finalize-package` adds `docs/api/<pkg>.md` (one
`::: <module>` block per providing module in `interface.md`, plus `::: <pkg>.cli` and the
pipeline modules) and its `API` nav entry; `/project-workers:finalize-project` regenerates `index.md` and
keeps the nav in sync. Cross-references in docstrings use `` [`name`][pkg.module.name] ``;
`mkdocs build --strict` turns an unresolved one, or a nav entry with no file, into a build
failure — which is the point.

## 5. CI commands

Run in the workspace environment, from the root:

```
uv sync --all-packages
uv run ruff check && uv run ruff format --check
uv run pylint --disable=all --enable=C0302,R0904 packages/*/src
uv run lint-imports
uv run --package <pkg> pytest packages/<pkg>/tests          # one package
uv run pytest packages/*/tests                              # everything
uv run mkdocs build --strict
```

These are the commands the repo contract's Toolchain section states, and the ones every
implementer and reviewer copies rather than guesses.
