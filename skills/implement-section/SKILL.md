---
name: implement-section
description: Implement one section of one package from its design doc, applying decided decisions, review findings, and follow-ups, coding against the shipped documents of what it consumes. Use after the package plan is reviewed and open questions are answered in docs/decisions.md.
argument-hint: "<pkg>/<section> [plan-slug]"
arguments: [section, plan]
context: fork
agent: implementer
background: false
disable-model-invocation: true
---

Implement section: **$section**
Plan slug (empty for canonical work): **$plan**

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `implementer` subagent — the agent is not
> registered, usually because the project-workers plugin was installed or updated after Claude
> Code started. Stop, tell the user to run `/reload-plugins` (or restart Claude Code),
> verify with `/agents`, and re-run. Do not build in the main thread.

If `$section` reached you unsubstituted — literally the text `$section` — parse the section
and optional plan slug from `$ARGUMENTS` instead, first token and second token.

## Resolve the identity

`$section` is `<pkg>/<name>`. Split on the `/`: `$pkg` is the part before it, `$name` the part
after. If there is no `/`, read the Packages table in `docs/architecture.md`: with exactly one
row, that is `$pkg`; with more, return a blocker asking for the qualified name — there is more
than one package that could own a section called `$name`.

If `$name` is `surface`, stop: the public surface is built by `/project-workers:finalize-package $pkg`, not by
this skill.

## Paths

Read all of these that exist. Absence is meaningful in each case, so note which were missing.

| Document | Path | If absent |
|---|---|---|
| Repo contract | `docs/architecture.md` | Fall back to the contract delta. If neither exists, that is a blocker — return it and name `/project-workers:plan-repo` or `/project-workers:map-project` as the fix. |
| Package contract | `docs/packages/$pkg/contract.md` | Blocker unless a contract delta names this section as new. Name `/project-workers:plan-package $pkg`. |
| Contract delta | `docs/plans/$plan/contract-delta.md` *(only when a slug is set)* | The change added no contracts; the canonical contracts stand. |
| Design | `docs/plans/$plan/$pkg/$name.md` if a slug is set, else `docs/packages/$pkg/design/$name.md` | Blocker. There is nothing to build from. |
| Integration | `docs/plans/$plan/integration.md` if a slug is set, else `docs/packages/$pkg/integration.md` | Proceed, but you have no cross-section resolutions or dependency order — say so in your return. |
| Surface | `docs/packages/$pkg/surface.md` | Proceed; mark every entry point `Public: no` and say so. |
| Interface (shipped) | `docs/packages/$pkg/interface.md` | Not shipped; the shipped-surface blocking rule does not apply. |
| Assessment | `docs/plans/$plan/assessment.md` *(only when a slug is set)* | Proceed. |
| Decisions | `docs/decisions.md` | Every open question is unanswered; your blocking rules apply. |
| Follow-ups | `docs/followups.md` | Nothing queued for you. |
| Review findings | `docs/reviews/` — the most recent `<date>-<pkg>-<section>.md` for this section | No prior review. |
| Dependency READMEs | the `README.md` at the path of each section in the package contract's `Depends on` for `$name` | **Blocker.** Sections are built in the integration doc's order; name the unbuilt dependency and `/project-workers:implement-section $pkg/<dep>` as the fix. |
| Upstream interfaces | `docs/packages/<dep>/interface.md` for each package in the repo contract's `Depends on` for `$pkg` | That package is unshipped: if it has code, use its `contract.md` and treat every consumed name as provisional; if it has no code, blocker naming `/project-workers:plan-package <dep>` and its build. |
| Source probe | `docs/packages/$pkg/sources/<source>.md` and `<source>.sample.json`, for the `source` in this section's row of the package contract's Sections table | Proceed; your step 5 probes the source yourself, and your return says so. |

The contract delta outranks the canonical contracts for anything it names: it is newer by
construction, and `/project-workers:plan-change` deliberately does not fold it back until the code ships.

## Steps

1. Read every document above. Apply your blocking rules — the unbuilt-dependency rule first
   (it is the cheapest to check and the one that keeps sections in order), then the
   shipped-surface rule when `interface.md` exists and no slug is set; if blocked, return the
   blocker and stop.
2. Implement per your procedure — the scaffold step on a first run, the stale `TODO(decision)`
   sweep, and the `Applied:` write-back are the steps nothing else in this system will do for
   you.
3. Return your summary in your standard format.

Implement only this section. Under `docs/`, you may append to `followups.md` and fill in
`Applied:` fields in `decisions.md`; everything else under `docs/` is read-only. Never touch
your package's top-level `__init__.py` beyond its scaffold docstring, and never touch another
package.
