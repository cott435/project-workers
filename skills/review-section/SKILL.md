---
name: review-section
description: Review an implemented section of a package against its design doc, the contracts, and the shipped documents it consumes. Writes findings to docs/reviews/date-pkg-section.md and files critical ones into docs/followups.md so the next implement-section run picks them up.
argument-hint: "<pkg>/<section> [plan-slug]"
arguments: [section, plan]
context: fork
agent: reviewer
background: false
disable-model-invocation: true
---

Review section: **$section**
Plan slug (empty for canonical work): **$plan**

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `reviewer` subagent — the agent is not
> registered, usually because the project-workers plugin was installed or updated after Claude
> Code started. Stop, tell the user to run `/reload-plugins` (or restart Claude Code),
> verify with `/agents`, and re-run.

If `$section` reached you unsubstituted, parse the section and optional plan slug from
`$ARGUMENTS` — first token and second token.

## Resolve the identity

`$section` is `<pkg>/<name>`; split on the `/` into `$pkg` and `$name`. With no `/`, use the
sole row of the Packages table in `docs/architecture.md` as `$pkg`, or return a blocker asking
for the qualified name if there is more than one. If `$name` is `surface`, stop and name
`/project-workers:review-package $pkg`.

## Paths

| Document | Path |
|---|---|
| Repo contract | `docs/architecture.md` |
| Package contract | `docs/packages/$pkg/contract.md` |
| Contract delta | `docs/plans/$plan/contract-delta.md` *(when a slug is set)* |
| Design | `docs/plans/$plan/$pkg/$name.md` if a slug is set, else `docs/packages/$pkg/design/$name.md` |
| Integration | `docs/plans/$plan/integration.md` if a slug is set, else `docs/packages/$pkg/integration.md` |
| Surface | `docs/packages/$pkg/surface.md` — which entry points should be `Public: yes` |
| Decisions | `docs/decisions.md` |
| Section README | the README at the section's path in the package contract's Sections table |
| Dependency READMEs | the README of each section in `Depends on` for `$name` |
| Upstream interfaces | `docs/packages/<dep>/interface.md` for each package `$pkg` depends on |
| Source probe | `docs/packages/$pkg/sources/<source>.md` and `<source>.sample.json`, for the `source` in the section's row of the Sections table |
| **Write your report to** | `docs/reviews/<today's date, YYYY-MM-DD>-<pkg>-<section>.md`, with `$pkg` and `$name` in place of the placeholders |

If the design doc is missing there is no spec to conform to — review for correctness,
security, tests, and documentation only, and say in the report that spec conformance was not
checked and why.

## Steps

1. Read the documents above, then the section's code and tests.
2. Work your **section review checklist** in priority order. Spec conformance first, including
   the seams: the point of this system is that the code matches the documents, and a section
   that works but diverges is the failure mode that only surfaces when another section — or
   another package — trusts the contract.
3. Write your report to the path above.
4. Append every CRITICAL finding to `docs/followups.md` addressed to `$pkg/$name`, so the next
   `/project-workers:implement-section $pkg/$name` picks them up without anything passing through chat.
5. Return your summary.

Change nothing but your report and `docs/followups.md`.
