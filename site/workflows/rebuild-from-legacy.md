# Rebuilding from a legacy repo

For a rebuild: you have an old, messy repo with working pieces in it — API clients, schemas,
parsers, validators, algorithms — and you want a fresh repo whose contracts come from a brief,
not from the old shape. The old code reaches the new build as **project skills**, never as a
map the architect reads. The architect only ever sees skill names and descriptions.

## 1. Mine the old repo

```
/project-workers:extract-legacy ../old-repo
```

Forks into the **curator**. It spawns `Explore` over the old repo, verifies what it cites,
and drafts `docs/legacy/inventory.md`: one row per resource worth carrying — named as a
capability (`polygon-aggregates`, `bars-schema`), never as a file — with `suggested: yes/no`
from the brief and `keep: ?` on every row. Then it **stops**.

You edit the inventory: set `keep` to `yes` or `no`, merge rows that belong in one skill by
listing their paths under one id, name the skills, and put instructions for the extractor in
`notes` ("the pagination has an off-by-one — do not port it"). The row is the unit: one row
becomes one skill, so granularity is your call, made here.

```
/project-workers:extract-legacy
```

The curator spawns one **researcher** per kept row, in parallel. Each cuts the resource out of
the old code into `.claude/skills/<name>/references/`, rewrites its imports to stdlib and
third-party only, checks it imports cleanly in a scratch venv, copies the old fixtures
(scrubbed, 200 KB cap), and writes a `SKILL.md` whose first paragraph says the contracts
govern where the code lives and what it is called. The curator marks each row `extracted` or
`failed: <reason>`. Re-running is idempotent; reset a row to `pending` to redo it.

The old repo can live anywhere — a sibling directory, another disk — and is not needed
after this step.

## 2. Plan the new repo

```
/project-workers:plan-repo docs/brief.md
```

The architect enumerates `.claude/skills/`, finds the extracted skills beside any you wrote by
hand, and lists them as candidate skills per package. It never opens the old repo.

## 3. Plan each package, probing its sources

```
/project-workers:plan-package data
```

Same as the new-repo workflow, with one step you will notice: after the package contract is
written — its Sections table names the external `source` each section consumes — the
architect spawns one **researcher** per source, in parallel, before any designer. Each
researcher checks the credential (env or a root `.env`), reads the vendor's docs, calls the
real endpoints plus one deliberately bad request each, and writes
`docs/packages/data/sources/<source>.md`: the **observed** schema, pagination, limits, and
error shapes, with a scrubbed sample and a re-runnable probe script. When an extracted skill
exists for that source, the probe also diffs the old fixtures against today's responses.

A key that is unset or rejected **stops** the run there:

```
Stopped for credentials: POLYGON_API_KEY unset
Set them and re-run `/project-workers:plan-package data`.
```

Nothing is designed until every source has answered. Designers then get `Source probes:` and
design the parser against the observed schema; implementers test against the recorded sample
(and re-probe themselves if the doc is missing or older than the design); the reviewer flags
a parser whose fixture is a hand-written dict shaped like the design.

From here it is the new-repo loop: `/project-workers:implement-section`, `/project-workers:review-section`,
`/project-workers:finalize-package`, `/project-workers:review-package`, package by package.

## Later

```
/project-workers:probe-source data polygon
```

Re-probes one source on its own — after an API changes, or when a follow-up from an
implementer says the design assumed one shape and the wire returned another. The doc is
rewritten with a new date and a **Changes since last probe** section.
