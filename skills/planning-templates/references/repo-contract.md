# `docs/architecture.md` — the repo contract

Written at repo scope (`/project-workers:plan-repo`, `/project-workers:map-project`); read by every skill; edited later only
for parts no shipped package provides or consumes, or by `/project-workers:sync-plan` after a change ships.

Budget 250 lines. A contract complete enough that a package could be planned from it plus the
shipped surfaces below it is the requirement; the line count is a hint that you are writing
prose where a table would do.

1. **Goal** — one paragraph.

2. **Packages** — table: package | responsibility | path | depends on | candidate skills.
   Dependency-ordered, lowest first. A single-package repo has one row with path `.`.

3. **Dependency graph** — the import-linter block, verbatim TOML: contract 1 from
   `workspace-scaffold` §3 with this repo's packages, highest first. This *is* the graph;
   prose about it is optional. On a mapped repo whose real imports are cyclic, write the
   order that should hold and say in one line that it does not yet.

4. **Boundaries** — one subsection per edge *provider → consumer*, listing each **shape** that
   crosses it: name, kind (DataFrame / record / artifact / event / file), columns or fields
   with types and nullability, invariants (sorted by, unique on, timezone, units). Shapes,
   not signatures: `Bars — DataFrame, index (symbol, ts: UTC tz-aware), columns
   open/high/low/close: float64 non-null, volume: int64` — not `load_bars(start, end)`. The
   providing package fixes the signature in its `surface.md`.

5. **Shared conventions** — everything more than one package touches: error format and
   exception base; log keys and levels; config env prefix per package (`<PKG>_`); time and
   timezone handling; ID types and how they are generated; DataFrame index and dtype
   conventions; serialization formats; auth model if any. Where the repo has no convention
   for something, say so — "no convention" is a decision waiting to be made and "the
   convention is X" is not.

6. **Toolchain** — workspace tool; the one-package test command; lint, import-lint, and docs
   build commands; where each config lives; the docs renderer and its cross-reference syntax;
   the skeleton blocks the scaffold step copies. Invoke `workspace-scaffold` and copy its
   shapes with this repo's values — do not paraphrase commands from memory.

7. **Non-goals** — explicitly out of scope.

8. **Open decisions** — the `D<n>` numbers currently `open` or `deferred`, one line each.
   Numbers and questions only. The entries themselves live in `docs/decisions.md`; nothing
   about a decision beyond its number belongs in this file.
