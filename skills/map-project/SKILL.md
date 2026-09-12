---
name: map-project
description: Adopt an existing codebase into the planning system, at repo scope - reverse-engineers docs/architecture.md, the decision ledger, and the follow-up queue from the code as it stands, then hands each package to /project-workers:plan-package for its own document-mode run. Run once on a repo with code but no docs/, and again when the canonical docs have drifted from the code.
argument-hint: "[scope — a directory or a note on what to focus on; optional]"
context: fork
agent: architect
background: false
disable-model-invocation: true
---

Map this existing repository into canonical planning documents — **repo scope, document mode**.

Scope hint (may be empty — map the whole repo if so):

$ARGUMENTS

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `architect` subagent — the agent is not
> registered, usually because the project-workers plugin was installed or updated after Claude
> Code started. Stop, tell the user to run `/reload-plugins` (or restart Claude Code),
> verify with `/agents`, and re-run. Do not plan in the main thread.

Run this on a repo that has code but no `docs/` — and again, later, when the canonical docs have
drifted far enough from the code that they mislead. This run writes the **repo-level** documents
only. Each package is then adopted by `/project-workers:plan-package <pkg>`, which on existing code runs in
document mode and writes the package contract, section designs, integration, and surface. One
run per level keeps each run small enough to finish, and makes a re-run after the interview
rule cheap.

## What you are producing

You are writing **what the code already does**, not what it should do. Nothing here proposes a
change. Where the code is wrong, record it as a risk or a follow-up; do not design the fix.

Four files at most: `docs/assessment.md`, `docs/decisions.md`, `docs/followups.md`, and —
only after the interview rule proceeds — `docs/architecture.md`. If you stop for questions,
the first three exist and the contract does not.

## If canonical docs already exist

You are re-mapping a repo whose docs have drifted. Do not blindly overwrite them — they hold
intent that source code does not, and losing it is expensive.

Read every existing canonical doc first, and treat each as a claim to check against the code.
Where the code agrees, keep the existing wording; the phrasing may encode a distinction you
cannot see. Where the code contradicts it, rewrite that part to match the code and record the
contradiction — those are the interesting findings, because each one is either a doc that went
stale or a bug that has been shipping quietly. Where a doc describes something that no longer
exists at all, remove it and say so.

Report every change you made to an existing doc in your return, grouped as *stale doc corrected*
versus *code looks wrong, filed as a follow-up*. A re-map that silently rewrites half the
architecture doc is indistinguishable from one that hallucinated it.

## Steps

1. **Assess.** Spawn an `Explore` subagent (thoroughness: very thorough) to map the repo:
   packages (workspace members, or the one package), the imports between them, each package's
   top-level directories and entry points, the top-level `__init__.py` exports, the data types
   and schemas that cross package boundaries, config and env vars, error and logging patterns,
   test layout, the toolchain in use, and anything fragile. `Explore` is read-only and cannot
   write files, so take its report, verify the paths and signatures it cites with your own
   `Read`/`Grep`, and write the result yourself to `docs/assessment.md`. Section-level detail
   belongs to the package runs; do not go deeper than the package boundary here.

2. **Survey skills.** Enumerate the project skills per your instructions. Map each skill to the
   package it would build; a skill with no match usually means an area you have not identified
   yet, or one someone intends to add.

3. **Interview rule.** This is where the package decomposition gets settled, and it is worth
   stopping for: you are naming things that become permanent directory names and shell
   arguments. Also worth asking: which conventions you found are intentional versus accidental,
   and whether any area is deliberately out of scope. Check the ledger; stub anything unasked
   tagged `Raised by: /project-workers:map-project (interview)` and **stop** with the stop message — before
   the contract is written, and with the questions in `docs/decisions.md` and nowhere else.
   Otherwise proceed.

4. **Repo contract.** Invoke `planning-templates`, read `references/repo-contract.md`, and
   write `docs/architecture.md` describing the repo as it is: the packages found, the import
   graph between them as the Dependency graph (if it is cyclic, say so — the import-linter
   block records the order that *should* hold, marked as not yet true), the shapes actually
   crossing each boundary, the conventions actually in use even when inconsistent (note the
   inconsistency), and the toolchain actually in use. Where the code has no convention at all,
   say that explicitly rather than inventing one. Its Open decisions heading lists `D<n>`
   numbers only.

5. **Seed the ledger and the queue.** Append a `D<n>` stub for every open question that
   survived — including the "there is no convention for X" gaps from step 4 and any cyclic
   dependency. Create `docs/followups.md` if absent, and file an item for each concrete defect
   the mapping surfaced, addressed to `<pkg>/<section>` where the section is obvious from the
   directory and to `<pkg>` otherwise.

6. **Return** your standard summary plus one line per package: path, whether its top-level
   `__init__.py` re-exports anything, and whether a `docs/packages/<pkg>/` already exists. End
   with the next command: `/project-workers:plan-package <lowest package in dependency order>` — the
   package runs go bottom-up so each one's dependencies are documented first.

## Constraints

- Documentation only. No code, no config, no tests, no fixes.
- Do not spawn designers and do not write package documents; `/project-workers:plan-package` does both, in
  document mode, one package at a time.
- Do not design improvements. If the code does something badly, that is a follow-up — the
  change that fixes it is a separate `/project-workers:plan-change` run.
- Be honest about what you could not determine. A contract that guesses at a shape is worse
  than one with a gap marked, because the next run will plan against your guess.
