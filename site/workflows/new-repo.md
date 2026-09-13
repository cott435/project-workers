# New repo, package by package

```
/project-workers:plan-repo docs/brief.md
```

Forks into the **architect** at repo scope. It reads your brief and your project skills and
writes `docs/architecture.md` — the **repo contract**: the package list with responsibilities,
the dependency graph as an import-linter block, the **shapes** that cross each boundary (a
DataFrame of bars with these columns, a `Lot` record — not function signatures), the shared
conventions (error format, log keys, config prefixes, timezone, ID types), and the toolchain
(workspace tool, test and lint commands, docs renderer). It never spawns designers: packages
are planned one at a time, below.

If it has questions it cannot settle, it **stops** — see **Questions** on the home page — and you
re-run.

```
/project-workers:plan-package data
```

Forks into the architect at package scope. It reads the repo contract and, for every package
`data` depends on, that package's `docs/packages/<dep>/interface.md` — the surface as shipped.
Then:

1. Writes `docs/packages/data/contract.md` — the **package contract**: the section list, what
   each section returns to its siblings (signatures now, not shapes), the pipelines that run
   the sections in order (`download → clean → audit → store`), what the package will expose,
   and a `Consumes` table of every upstream name it uses. Its Sections table names the
   external `source` each section consumes.
2. Spawns one **researcher** per source, in parallel. Each checks the credential (env or a
   root `.env`), reads the vendor's docs, calls the real endpoints plus one bad request each,
   and writes `docs/packages/data/sources/<source>.md` — the **observed** schema, pagination,
   limits, error shapes — with a scrubbed sample and a re-runnable probe script. A key that is
   unset or rejected **stops** the run here, naming the variable, before any design exists.
3. Spawns one **designer** per section, in parallel, each given its section's probe doc. Each
   writes `docs/packages/data/design/<section>.md` and returns ten lines.
4. Reads every design and writes `docs/packages/data/integration.md`: deviations, mismatches,
   dependency order, shared work, risks, decisions needed — and **Repo contract deviations**,
   which it may resolve by editing the repo contract only when no shipped package is bound by
   the shape.
5. Writes `docs/packages/data/surface.md` — the design of the public surface, now that the
   section interfaces are concrete: the `__all__` names (only those a downstream package or a
   CLI command consumes, each with its consumer named), the pipeline signatures, the CLI
   commands with every argument, the import-linter contracts for this package.
6. Appends `D<n>` stubs to `docs/decisions.md`.

Then answer the decisions, and implement in the order `integration.md` gives, reviewing as you
go:

```
/project-workers:implement-section data/ingest
/project-workers:review-section data/ingest
/project-workers:implement-section data/clean
/project-workers:review-section data/clean
…
```

Sections go in that order and cannot be built out of it: `/project-workers:implement-section data/clean`
refuses while `data/ingest` has no README. Each implementer reads the **READMEs** of the
sections it depends on — what actually shipped — ranked above those sections' design docs. `integration.md` is a plan-time document; it stops
being true the moment the first implementer deviates, and implementers deviate. The README is
where a deviation is recorded, so the README is what the next section codes against.

When every section has a README *and a review newer than it*, publish the package:

```
/project-workers:status data --gate
/project-workers:finalize-package data
/project-workers:review-package data
```

`/project-workers:finalize-package` refuses until every section is built and reviewed since its last build and
no review-sourced follow-up is open — `/project-workers:status data --gate` shows the same check. Then it forks
into the implementer in **surface mode**: it writes the top-level `src/data/__init__.py`
(lazy re-exports — importing `data` loads nothing until a name is used — of only the names a
consumer needs), the `pipelines/` that compose the sections, `cli.py` with one function per
command (its docstring is the `--help` text), the package's `docs/api/data.md` page so the
docs site builds strict from here on, `Applied:` lines any section implementer missed, and
`docs/packages/data/interface.md` — the public surface **as shipped**. `/project-workers:review-package` is
the gate: `__all__`, `interface.md`, and the section READMEs agree; every public name has a
consumer; every shape the repo contract promised is realized; `lint-imports` and `mkdocs
build --strict` pass; the pipelines and commands run.

Next week:

```
/project-workers:plan-package analysis
```

reads `docs/packages/data/interface.md` as its upstream, and its designers reference those
names exactly. Planning against a package that has no `interface.md` yet is allowed — every
consumed name is marked `provisional` and the return says so.

```
/project-workers:finalize-project
```

writes a README per package and the root README from the shipped documents, plus the docs-site
API pages. Safe to run early and often.
