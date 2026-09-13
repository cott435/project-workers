---
name: extract-legacy
description: Mine an old codebase for resources worth carrying into a rebuild - API clients, schemas, parsers, validators, algorithms - and turn each one the user keeps into a project skill under .claude/skills/ that the architect assigns and designers and implementers invoke. The first run drafts docs/legacy/inventory.md and stops; mark keep on each row and re-run to extract. Run before /project-workers:plan-repo so the architect sees the skills.
argument-hint: "<path to the old repo - required on the first run, ignored afterwards>"
context: fork
agent: curator
background: false
disable-model-invocation: true
---

Curate the legacy repo at:

$ARGUMENTS

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `curator` subagent — the agent is not
> registered, usually because the project-workers plugin was installed or updated after Claude
> Code started. Stop, tell the user to run `/reload-plugins` (or restart Claude Code),
> verify with `/agents`, and re-run. Do not survey in the main thread.

## Two modes, decided by what exists

- **Survey** — no `docs/legacy/inventory.md`. The argument is required: the path to the old
  repo, absolute or relative to this repo's root. It must be outside this repo's `packages/`
  directory — a sibling directory or a path elsewhere on disk are both fine. With no argument,
  return a blocker asking for the path. Draft the inventory per your instructions and stop.
- **Extract** — `docs/legacy/inventory.md` exists. Ignore the argument; the old repo path and
  commit are in the inventory's heading. Act on every row with `keep: yes` and
  `status: pending`.

## Before extracting

- Create `.claude/skills/` if it does not exist; create nothing else outside it.
- A row whose `skill` collides with a skill this plugin provides is `failed: name reserved`,
  never extracted: `plan-repo`, `plan-package`, `plan-change`, `map-project`,
  `implement-section`, `review-section`, `finalize-package`, `review-package`, `sync-plan`,
  `finalize-project`, `extract-legacy`, `probe-source`, `status`, `project-structure`,
  `python-implementation`, `python-style-guide`, `security-review`, `workspace-scaffold`,
  `planning-templates`.
- A row whose `skill` directory already exists is `failed: skill exists`, unless the user
  reset its `status` to `pending` — then the researcher overwrites it.

## Steps

Survey: your **Survey** steps 1–5, ending with the stop message.

Extract: your **Extract** steps 1–4 — spawn every researcher in one message, wait for all of
them, update the inventory, return.

## Constraints

- `docs/legacy/inventory.md` is the only file you write; skills are written by researchers.
- If `docs/architecture.md` already exists, this repo has been planned: say in your return that
  the architect will pick up the new skills on its next `/project-workers:plan-package` run, and that a package
  already planned needs `/project-workers:plan-package <pkg>` re-run for its designers to see them.
