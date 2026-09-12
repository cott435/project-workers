---
name: finalize-package
description: Build a package's public surface once every section has shipped — the top-level __init__.py re-exports with __all__, the pipelines that cross sections, the scripts that drive them — and write docs/packages/pkg/interface.md, the shipped surface that downstream packages are planned and built against.
argument-hint: "<pkg>"
arguments: [pkg]
context: fork
agent: implementer
background: false
disable-model-invocation: true
---

Build the public surface of package **$pkg** — **surface mode**.

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `implementer` subagent — the agent is not
> registered, usually because the project-workers plugin was installed or updated after Claude
> Code started. Stop, tell the user to run `/reload-plugins` (or restart Claude Code),
> verify with `/agents`, and re-run. Do not build in the main thread.

If `$pkg` reached you unsubstituted, take the first token of `$ARGUMENTS`.

## Why this is a separate step

Sections are built one at a time and each publishes only to its siblings. The package as a
whole publishes once, here, after every section exists: what consumers may import, the
pipelines that run the sections in order, and the scripts that drive those pipelines. The
document this step writes, `interface.md`, is what `/project-workers:plan-package` hands the next package's
designers and what `/project-workers:implement-section` in that package codes against. Until it exists, the
package is not shipped.

## Preconditions

Return a blocker naming what is missing if any of these fails. Run the check script first —
it prints the table your **Surface mode** preconditions describe:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/status/scripts/status.py $pkg
```

Then confirm: `contract.md` and `surface.md` exist; every section in the Sections table has
a `README.md`; every section has a review dated on or after its README's last change; no
unchecked review-sourced follow-up (`review <date>` in its text) is addressed to any
`$pkg/<section>`. No partial mode — a consumer cannot be built against half a surface, and
the surface must not re-export code with an open CRITICAL finding. Other open follow-ups
are listed in your return, not blockers.

## Paths

| Document | Path |
|---|---|
| Surface (your design doc) | `docs/packages/$pkg/surface.md` |
| Package contract | `docs/packages/$pkg/contract.md` |
| Repo contract | `docs/architecture.md` — the shapes `$pkg` provides, the Toolchain |
| Integration | `docs/packages/$pkg/integration.md` |
| Section READMEs | at each section's path; item 3 is what exists |
| Decisions | `docs/decisions.md` — entries scoped `$pkg` or `repo` |
| Follow-ups | `docs/followups.md` — entries addressed to `$pkg/surface` |
| Review findings | `docs/reviews/` — the most recent `<date>-<pkg>-package.md` for this package |
| Existing interface | `docs/packages/$pkg/interface.md` if this is a re-run after changes |
| **Write** | `packages/$pkg/src/$pkg/__init__.py`, `…/pipelines/`, `…/cli.py` (or `cli/`), `packages/$pkg/pyproject.toml` (`[project.scripts]`), the root `pyproject.toml` (the `forbidden` import contract), `packages/$pkg/tests/`, `docs/api/$pkg.md` and the `nav` list in `mkdocs.yml`, `docs/packages/$pkg/interface.md`, and `Applied:` lines in `docs/decisions.md` |

On a single-package repo the code paths drop the `packages/$pkg/` prefix.

## Steps

1. Check the preconditions; if any fails, return the blocker and stop.
2. Read every document above. Apply your blocking rules; the decision sweep applies to the
   surface code too.
3. Build per your **Surface mode** section: the lazy `__init__.py`, pipelines, `cli.py`,
   config composition, the `forbidden` contract, the docs page and nav entry, tests. Run the
   package suite, `lint-imports`, and `mkdocs build --strict`; all three pass or you are not
   done. Then the ledger sweep.
4. Write `docs/packages/$pkg/interface.md` per your template, including the computed
   **Consumers** snapshot.
5. Tick off the `$pkg/surface` follow-ups you addressed; file follow-ups to sections for any
   name `surface.md` expected that no README provides.
6. Return your surface-mode summary, ending with the next command: `/project-workers:review-package $pkg`.

## Constraints

- You may edit only the paths in the **Write** row. Section code is not yours: a defect there
  is a follow-up to that section, and if it stops a pipeline from running, a blocker.
- `interface.md` describes what shipped, not what `surface.md` intended. Where they differ,
  write what shipped and list the difference under **Deviations**.
- Do not write a section README; `interface.md` is the package-level equivalent.
