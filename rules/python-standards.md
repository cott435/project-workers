---
paths:
  - "**/*.py"
  - "pyproject.toml"
---

# Python code standards

Match the conventions of the code around you. Consistency with this repo beats any external
guide.

Two skills carry the detail. Invoke the relevant one before writing or reviewing Python:

- **`project-structure`** — where files go, how big they get before splitting, config
  placement, module and package naming, workspace layout.
- **`python-style-guide`** — what goes inside a file: imports, exceptions, type annotations,
  docstrings on everything, function shape, identifier naming, `__init__.py` policy.

Three rules worth having here because getting them wrong is expensive to undo:

- A package's **top-level `__init__.py` re-exports the public API with `__all__`**; every
  nested one is empty. Inside a package import from the defining module; from another package
  import from its top level only. import-linter enforces the second.
- On an existing repo, **its layout wins.** Never create `src/<pkg>/` beside an existing
  top-level package — two import roots is a silent, expensive failure.
- Every module, class, function, and method gets a docstring; the docs build runs strict, so a
  missing or malformed one fails CI.
