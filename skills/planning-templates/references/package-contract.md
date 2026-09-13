# `docs/packages/<pkg>/contract.md` — the package contract

Written at package scope before designers are delegated; read by designers, implementer,
reviewer, `/project-workers:finalize-package`, and `/project-workers:plan-change` (its **Consumes** table). Budget 200 lines.

Where this contract needs a repo-contract shape to change, do not change it here — raise it
under **Repo contract deviations** in the integration doc.

1. **Purpose** — one paragraph, and which repo-contract shapes this package provides.

2. **Sections** — table: section | responsibility | path | owner doc | builds with |
   depends on | source. Paths are `packages/<pkg>/src/<pkg>/<section>/` (or `src/<pkg>/<section>/`
   in a single-package repo); owner docs are `docs/packages/<pkg>/design/<section>.md`.
   `Depends on` names sections in this package only, and must form a DAG — it becomes an
   import-linter contract and the order `/project-workers:implement-section` enforces. `source` is the
   external service the section consumes — one lowercase token, the name
   `docs/packages/<pkg>/sources/<source>.md` carries — or `—`. `/project-workers:plan-package` probes every
   source in this column before delegating designers; a service not named here is never
   probed.

3. **Section interfaces** — per section, what it returns to its dependents, as signatures.
   Reference repo shapes by name; never redefine them. This is where "what each section
   returns" is fixed, so designers of dependents have something concrete.

4. **Pipelines** — per pipeline: name, trigger, ordered section participation with what
   crosses at each step, failure behavior, and the CLI command that drives it. `download →
   clean → audit → store` is a pipeline; each arrow names a shape or a section interface.

5. **Public surface (intent)** — which repo shapes this package provides, which section
   realizes each, and which downstream package or CLI command consumes each. This is the
   list `surface.md` will be checked against: a name with no consumer here does not become
   public later. Keep it short; the surface is what consumers need, not what sections offer.

6. **Consumes** — table: upstream package | name | shape | status (`shipped` /
   `provisional` / `stale`). `/project-workers:plan-change` reads this to find planned consumers of a package,
   so list every upstream name this package will use.

7. **Package conventions** — only what goes beyond the repo contract.

8. **Open decisions** — `D<n>` numbers, one line each.

**Adopting an existing package** (`Mode: document`): every heading describes what the code
does today. Sections come from its directories, interfaces from its code, pipelines from what
its entry points actually run, Consumes from its actual imports. Where the code contradicts
its own conventions, say so under the relevant heading rather than tidying it.
