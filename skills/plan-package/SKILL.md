---
name: plan-package
description: Plan one package of a repo that /plan-repo has already contracted. Writes the package contract - sections, section interfaces, pipelines - runs parallel section designs, reconciles them into integration.md, and designs the public surface in surface.md. Reads the shipped interface.md of every package this one depends on.
argument-hint: "<pkg> [package brief, or path to a file containing it]"
arguments: [pkg]
context: fork
agent: architect
background: false
disable-model-invocation: true
---

Plan package **$pkg** at **package scope**.

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `architect` subagent — the agent is not
> registered, usually because `.claude/agents/` was added after Claude Code started. Stop, tell the
> user to restart Claude Code (verify with `/agents`) and re-run. Do not plan in the main thread.

If `$pkg` reached you unsubstituted — literally the text `$pkg` — take the first token of
`$ARGUMENTS` as the package. Everything after the first token is the package brief: inline
text, or a path to a file holding it. It may be empty.

## Preconditions

`docs/architecture.md` must exist and its Packages table must have a row for `$pkg`. If not,
return a blocker naming `/plan-repo` — a package planned without the repo contract will
invent its own shapes and conventions, and the next package will invent them differently.

## What you read before anything else

- `docs/architecture.md` — the repo contract. Your package's row, its `Depends on`, the
  Boundaries subsections for every edge into and out of it, Shared conventions, Toolchain.
- For each package in `Depends on`: `docs/packages/<dep>/interface.md` if it exists — that
  package is **shipped** and those signatures are what your designers build against. If it
  does not, `docs/packages/<dep>/contract.md` if that exists, else only the repo contract's
  Boundaries; in both of those cases every name you consume is **provisional**.
- `docs/packages/$pkg/` if it exists — a re-run after the interview rule stopped, or a
  package with a brief already persisted.
- The package's code directory if it exists (an existing repo being adopted package by
  package).

## Steps

1. **Persist the brief** to `docs/packages/$pkg/brief.md` if one was given — inline text
   verbatim, a path's contents copied — so a re-run as `/plan-package $pkg` with no brief
   finds it. Survey the package directory if it exists and write
   `docs/packages/$pkg/assessment.md`; on a greenfield package there is nothing to assess.

2. **Survey skills.** Enumerate the project skills per your instructions; the repo contract's
   `candidate skills` column for `$pkg` is the starting point.

3. **Interview rule.** Section boundaries the brief and contract do not settle, a candidate
   skill with no section, a section with no skill, a pipeline whose ordering is ambiguous, a
   provisional upstream name you need settled. Check the ledger; stub anything unasked tagged
   `Raised by: /plan-package $pkg (interview)` and **stop** with the stop message. Otherwise
   proceed.

4. **Package contract.** Invoke `planning-templates`, read `references/package-contract.md`,
   and write `docs/packages/$pkg/contract.md` to it. **Public surface (intent)** is the
   filter `surface.md` will be checked against: every entry names the downstream package or
   CLI command that consumes it, and nothing without a consumer is listed.

5. **Delegate.** One `designer` per section, all in parallel, using your delegation template:
   - `Section: $pkg/<section>`
   - `Mode: new` (or `document` for a section that already has code and is being adopted)
   - `Contracts (highest first): docs/packages/$pkg/contract.md, docs/architecture.md`
   - `Upstream interfaces:` the shipped `interface.md` paths, or `provisional:` paths, or `none`
   - `Existing design: none` · `Assessment:` the package assessment if you wrote one
   - `Skills to invoke:` that section's project skills
   - `Write your design to: docs/packages/$pkg/design/<section>.md`
   - `Constraints:` what the section must not import — including every sibling section it
     does not depend on, and every upstream package's internals
   
   If every section already has a current design on disk, no designer is spawned this run —
   proceed straight to step 6 with those files. Otherwise, once the last spawned designer has
   returned, continue immediately, in that same turn, to step 6 — do not end your turn
   reporting that unification will happen next; nothing else will trigger it.

6. **Unify.** Read the design docs you delegated, read `references/integration.md`, and write
   `docs/packages/$pkg/integration.md` to it, including **Repo contract deviations** with its
   shipped-package rule.
   Update `docs/packages/$pkg/contract.md` where you accept a deviation into the package
   contract; update `docs/architecture.md` only where the resolution is `update repo contract`.

7. **Surface.** Read `references/surface.md` and write `docs/packages/$pkg/surface.md` to it.
   Apply its selection rule strictly: a name is public only when the contract's **Public
   surface (intent)** names a consumer for it — a downstream package or a CLI command. The
   designs' `Public: yes` rows are candidates, not the answer; most section entry points are
   for siblings and stay internal. Pipelines as concrete signatures and ordered section calls;
   CLI commands with every argument spelled out; the end-to-end tests; the two import-linter
   contracts.

8. **Record decisions.** Append a `D<n>` stub for every open question that survived — from
   the designs' **Open questions**, your **Contract deviations**, **Repo contract deviations**
   with `needs plan-change`, and `surface.md`'s open questions. `Scope:` the sections it
   binds, or `$pkg` when it is package-wide.

9. **Return** your standard summary — implementation order, provisional upstreams named —
   ending with the next command: `/implement-section $pkg/<first section in dependency order>`

## Adopting an existing package

When the package directory already has code (a repo mapped by `/map-project`, or a package
someone wrote by hand), this run documents rather than designs: the assessment in step 1 is
the survey of that code; the contract is written *as it is* (the template says how); every
designer runs `Mode: document`; the integration doc gains its **Coverage** heading; and
`surface.md` is *transcribed* from the top-level `__init__.py`, entry points, and CLI as they
exist — or *inferred* and marked so when the top-level `__init__.py` is empty. If it was
transcribed, also write `docs/packages/$pkg/interface.md` in the same as-is spirit: it is a
transcription of shipped code, which is what that file always is. If inferred, write no
`interface.md` — the package is not shipped in this system's sense until `/finalize-package`
runs — and say so in your return. Nothing in an adoption run proposes a change; what looks
wrong becomes a followup addressed to its section.

## Constraints

- Planning documents only. No code, no config, no tests.
- Never edit another package's documents. A change you need from a shipped package is a
  stub recommending `/plan-change`; from an unshipped one, a stub scoped to that package that
  its `/plan-package` run will find.
- Do not implement anything. The user reviews the plan and answers decisions first.
