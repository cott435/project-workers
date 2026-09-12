---
name: review-package
description: Review a finalized package - its public surface against surface.md, plus the package-level checks nothing else runs - import contracts pass, __all__ and interface.md and the section READMEs agree, every repo-contract shape the package provides is realized, pipelines run. Writes docs/reviews/date-pkg-package.md and files critical findings into docs/followups.md. Run after /project-workers:finalize-package and before planning the next package against this one.
argument-hint: "<pkg>"
arguments: [pkg]
context: fork
agent: reviewer
background: false
disable-model-invocation: true
---

Review package: **$pkg** — the surface `/project-workers:finalize-package` built, and the package as a whole.

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `reviewer` subagent — the agent is not
> registered, usually because the project-workers plugin was installed or updated after Claude
> Code started. Stop, tell the user to run `/reload-plugins` (or restart Claude Code),
> verify with `/agents`, and re-run.

If `$pkg` reached you unsubstituted, take the first token of `$ARGUMENTS`.

## Why this exists

`/project-workers:review-section` sees one section. Nothing else checks the things that are only true or
false of the package: that the three descriptions of its public surface agree, that every
shape the repo contract promised is actually there, that the import contracts are in place
and pass, that the pipelines run end to end. This is the gate before the next package is
planned against `interface.md`.

## Paths

| Document | Path |
|---|---|
| Surface (the spec) | `docs/packages/$pkg/surface.md` |
| Interface (as shipped) | `docs/packages/$pkg/interface.md` — missing means `/project-workers:finalize-package` has not run; return that as the blocker |
| Package contract | `docs/packages/$pkg/contract.md` |
| Repo contract | `docs/architecture.md` — Boundaries where `$pkg` is the provider; Toolchain commands |
| Integration | `docs/packages/$pkg/integration.md` |
| Section READMEs | at each section's path from the Sections table |
| Section reviews | `docs/reviews/<date>-<pkg>-<section>.md` for this package — which sections were ever reviewed |
| Decisions | `docs/decisions.md` — entries scoped `$pkg`, `repo`, or any `$pkg/<section>` |
| Follow-ups | `docs/followups.md` — entries addressed to `$pkg/*` |
| Code | `packages/$pkg/src/$pkg/__init__.py`, `…/pipelines/`, `…/cli.py`, `packages/$pkg/pyproject.toml`, `docs/api/$pkg.md`, `mkdocs.yml`, the root `pyproject.toml` |
| **Write your report to** | `docs/reviews/<today's date, YYYY-MM-DD>-<pkg>-package.md`, with `$pkg` in place of `<pkg>` |

## Steps

1. Read the documents above, then the surface code and tests.
2. Run, from the repo root with the Toolchain's commands: the package test suite,
   `lint-imports`, and the strict docs build if one is configured. Record results.
3. Work your **package review checklist** in order.
4. Write your report to the path above.
5. Append every CRITICAL finding to `docs/followups.md` — addressed to `$pkg/surface` for
   surface findings and to `$pkg/<section>` for section findings — so `/project-workers:finalize-package $pkg`
   or `/project-workers:implement-section` picks them up.
6. Return your summary. If the verdict is `request changes`, end with the command that fixes
   the worst finding; otherwise end with `/project-workers:plan-package <next package>` or
   `/project-workers:finalize-project`.

Change nothing but your report and `docs/followups.md`.
