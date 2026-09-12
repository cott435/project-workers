# `docs/packages/<pkg>/surface.md` — the design of the public surface

Written at package scope **after** unification, because only then are the section interfaces
concrete. It is the design doc `/project-workers:finalize-package` builds from, and the plan-time twin of
`interface.md`. Under 150 lines; tables over prose.

**The selection rule.** A name goes on the surface when something outside the package needs
it — a downstream package (a Boundaries edge in the repo contract where this package is the
provider) or a CLI command — and not otherwise. Each row names its consumer. Sections offer
many entry points to their siblings; consumers need a few of them. The designs' `Public: yes`
rows are candidates, the contract's **Public surface (intent)** is the filter, and "a
downstream might want it someday" is not a consumer. A small surface is the point: it is what
consumers are built against and what a change has to preserve.

1. **Public names** — table: name | kind (function / class / constant) | providing section |
   module path | consumer (package or CLI command) | one-line purpose. Exactly the names the
   top-level `__init__.py` will expose in `__all__`, lazily (see `python-style-guide`,
   "Package `__init__.py` Files").

2. **Pipelines** — per pipeline from the contract: function name and signature; ordered
   steps as calls to section entry points, each with what it passes on; failure behavior;
   config it reads. These become `src/<pkg>/pipelines/`.

3. **CLI commands** — table: command name | entry point (`<pkg>.cli:<function>`) | arguments
   (name, type, default, one-line help — every one; this table is what the implementer turns
   into the command's docstring, and the docstring is what `--help` and the docs site show) |
   pipeline it runs. Commands live in `src/<pkg>/cli.py` (or `cli/` when there are many) and
   are registered under `[project.scripts]`; there is no `scripts/` directory.

4. **Tests** — one end-to-end test per pipeline, with the fixtures it needs, named; one
   invocation test per CLI command (`--help` parses, a minimal run succeeds against fixtures).

5. **Import contracts** — the `forbidden` contract (contract 2 in `workspace-scaffold` §3)
   listing this package's sections, and the intra-package `layers` contract (contract 3)
   derived from the Sections table's `Depends on` column, sections that do not depend on each
   other separated with `|`.

6. **Open questions** — `OQ-<pkg>-surface-<k>`, each with the assumption you designed against.

**On an adopted package** (existing code): transcribe what the top-level `__init__.py`,
entry points, and CLI actually expose, and mark the file *transcribed*; if the top-level
`__init__.py` is empty, list what the code appears to intend as public, mark the file
*inferred*, and note that the package is not shipped until `/project-workers:finalize-package` runs.
