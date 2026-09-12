---
name: plan-repo
description: Plan a repository at the package level — new or extending. Produces docs/architecture.md, the repo contract - packages, dependency graph, the shapes crossing each boundary, shared conventions, toolchain - plus decision stubs. Does not plan sections; run /project-workers:plan-package for each package afterwards.
argument-hint: "<repo brief, or path to a file containing it>"
context: fork
agent: architect
background: false
disable-model-invocation: true
---

Plan this repository at **repo scope** from the brief below:

$ARGUMENTS

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `architect` subagent — the agent is not
> registered, usually because the project-workers plugin was installed or updated after Claude
> Code started. Stop, tell the user to run `/reload-plugins` (or restart Claude Code),
> verify with `/agents`, and re-run. Do not plan in the main thread.

If the argument is a file path, read it and treat its contents as the brief. If it is empty and
`docs/brief.md` exists, that is the brief (a re-run after the interview rule stopped).

## Two modes, decided by what exists

- **New repo** — no `docs/architecture.md`. You are writing the repo contract from the brief.
- **Extending** — `docs/architecture.md` exists. The brief describes packages to add or
  boundaries to change. Read the contract, every `docs/packages/*/interface.md` (those
  packages are **shipped** and their shapes are frozen to you), and every
  `docs/packages/*/contract.md` (planned, not shipped). Persist what you find to
  `docs/assessment.md`.

## Steps

1. **Persist the brief.** Whether it came in as inline text or as a path, make sure its
   contents are in `docs/brief.md`: write them verbatim on a new repo, or append them under a
   dated heading when extending (skip this when the argument *is* `docs/brief.md`). It is the
   only statement of original intent, every document downstream is a paraphrase of it, and it
   is what a re-run with no argument reads — so this happens before anything that could stop.

2. **Survey.** Enumerate the project skills per your instructions. Read `CLAUDE.md` and any
   existing repo structure. Invoke `workspace-scaffold` so the Toolchain section copies real
   shapes rather than remembered ones.

3. **Interview rule.** Decide what you would ask — package boundaries the brief does not
   settle, dependency direction where two orders are defensible, a shared convention with no
   implied default (timezone, ID type, error envelope, config prefix scheme), a project skill
   with no package. Check the ledger; if anything is unasked, stub it tagged
   `Raised by: /project-workers:plan-repo (interview)` and **stop** with the stop message. Otherwise proceed.

4. **Repo contract.** Invoke `planning-templates` and read `references/repo-contract.md`, then
   write `docs/architecture.md` to it. Only now — a contract written before the interview rule
   proceeds is a contract written on guesses, and decisions never go inside it (its Open
   decisions heading lists `D<n>` numbers; the entries live in `docs/decisions.md`).

   When extending: edit only parts no shipped package provides or consumes. Anything else
   becomes a stub scoped `repo` recommending `/project-workers:plan-change`, and the contract stays as it is.

5. **Record decisions.** Append a `D<n>` stub for every open question that survived — the
   conventions you had to pick without a basis, boundary shapes you are unsure of. Each gets a
   recommendation and an assumption, `Scope: repo` unless it belongs to one package.

6. **Return** your standard summary, ending with the next command:
   `/project-workers:plan-package <first package in dependency order that has no docs/packages/<pkg>/contract.md>`

## Constraints

- Planning documents only. No code, no config, no tests.
- Do not spawn designers and do not plan sections. Packages are planned one at a time by
  `/project-workers:plan-package`, each against the shipped surface of the packages below it.
- Shapes, not signatures, at every boundary. A signature belongs to the providing package's
  `surface.md`, which does not exist yet.
