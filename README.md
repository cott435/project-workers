# project_workers

A Claude Code **plugin** of **agents** (roles with fixed tools, model, and permissions) and
**skills** (procedures you invoke with `/name`). Skills fork into agents; agents hand work to
other agents; every hand-off goes through a file under `docs/`, never through chat.

You drive it. Every workflow skill is `disable-model-invocation: true`, so Claude never
triggers one on its own — you type them.

v4 plans a **repo of packages** — `data` → `analysis` → `ml`, say — one package at a time,
where each finished package publishes an `interface.md` that the next one is planned and built
against. A single-package repo is the same thing with one row in the Packages table.

## Contents

```
project-workers/
├── .claude-plugin/
│   ├── plugin.json           the plugin manifest
│   └── marketplace.json      lets this repo serve as its own marketplace
├── agents/
│   ├── architect.md      plans at repo, package, or change scope; delegates; unifies  (opus)
│   ├── designer.md       designs one section against the contracts + upstream interfaces
│   ├── implementer.md    builds one section — or, in surface mode, a package's public surface
│   ├── reviewer.md       reviews one section, or one package
│   └── documenter.md     package READMEs, API pages, root README from shipped docs
├── rules/
│   └── python-standards.md   thin pointer; loads on *.py for your own interactive work
├── pyproject-lint-config.toml  merge into the root pyproject.toml; enforces the hard limits
└── skills/
    ├── plan-repo/          → architect     repo contract: packages, graph, shapes, conventions
    ├── plan-package/       → architect     one package: sections, designs, integration, surface
    ├── plan-change/        → architect     change to shipped code, with downstream impact
    ├── map-project/        → architect     adopt an existing repo (repo level; then plan-package per package)
    ├── implement-section/  → implementer   <pkg>/<section> [slug]
    ├── review-section/     → reviewer      <pkg>/<section> [slug]
    ├── finalize-package/   → implementer   <pkg>: lazy __init__, pipelines, cli.py, docs page, interface.md
    ├── review-package/     → reviewer      <pkg>: surface + package-level checks
    ├── sync-plan/          → architect     fold a shipped change into canonical docs
    ├── finalize-project/   → documenter    package READMEs, index.md, root README
    ├── status/             (inline)        the checklist: planned / built / reviewed / open, derived
    ├── project-structure/    layout, size limits, config placement        (preloaded: 4 agents)
    ├── python-style-guide/   inside a file: docstrings, function shape, … (preloaded: impl, review)
    ├── planning-templates/   headings for every planning document          (invoked by architect)
    ├── python-implementation/ splitting mechanics, config code            (invoked on demand)
    ├── workspace-scaffold/   pyproject / import-linter / mkdocs skeletons  (invoked on demand)
    └── security-review/      checklist                                    (invoked on triggers)

site/                         the reading site — see site/README.md
```

**Agents are roles; skills are entry points.** The line between them is what stops the two
from drifting apart:

- The **agent** holds what is true every time it runs: its tools, its discipline, its return
  format, and the templates only it writes — the delegation prompt, the design template, the
  section README template, the `interface.md` template. The architect's five document
  templates live in `planning-templates` instead, one reference file each, because a run
  writes one or two of them and should not carry all five.
- The **skill** holds what varies per invocation: which scope, which paths, which order of
  steps, what to do when a file is missing.
- Nothing is stated in both. If you find yourself editing the same sentence in two files, one
  of them is in the wrong place.

Domain knowledge — how *you* want a Postgres schema designed, how your vendor clients are
built — belongs in your own skills (`db-design/`, `vendor-clients/`, `feature-pipeline/`). The
architect discovers them, assigns each to a section, and passes the names down to the designer
and then the implementer, so the same conventions apply at design time and at build time.

## One-time setup

1. Add this repo as a marketplace and install the plugin:
   `/plugin marketplace add <owner>/project-workers` then
   `/plugin install project-workers@connor-plugins`. In Cowork: Customize -> Plugins ->
   Add marketplace, then Install.
2. **Verify with `/agents`** before the first run: the five agents must be listed. If they are
   not, run `/reload-plugins` (or restart Claude Code). Until they are registered a workflow
   skill runs in your main conversation instead of forking — you get a question widget instead
   of a stop message, and the run writes the wrong files. Every workflow skill checks for this
   and refuses, but the check is an instruction, not a guarantee.
   Note: user-level definitions in `~/.claude/agents/` override same-named plugin agents, so
   those must not exist for the plugin's versions to take effect.
3. Run in **auto** or **acceptEdits** mode. Not plan mode: subagents inherit your mode, plan
   mode is read-only, and nothing would reach `docs/`.
4. Every agent inherits your session model, so set `/model` before you start a run.
5. `/project-workers:status` at any time prints where everything stands; `/project-workers:status <pkg> --gate` runs the exact
   preconditions `/project-workers:finalize-package` will check.

## Which skill to run

```
new repo, nothing exists yet                → /project-workers:plan-repo, then /project-workers:plan-package <pkg> per package
existing repo, no docs/ yet                 → /project-workers:map-project (repo level), then /project-workers:plan-package <pkg> per package (document mode)
existing repo, docs/ already there          → /project-workers:plan-change
docs/ exist but have drifted from the code  → /project-workers:map-project (re-map), then /project-workers:plan-package <pkg> as needed
adding a package to a planned repo          → /project-workers:plan-repo "<what to add>", then /project-workers:plan-package <pkg>
lost track                                  → /project-workers:status
```

## Workflow A — new repo, package by package

```
/project-workers:plan-repo docs/brief.md
```

Forks into the **architect** at repo scope. It reads your brief and your project skills and
writes `docs/architecture.md` — the **repo contract**: the package list with responsibilities,
the dependency graph as an import-linter block, the **shapes** that cross each boundary (a
DataFrame of bars with these columns, a `Lot` record — not function signatures), the shared
conventions (error format, log keys, config prefixes, timezone, ID types), and the toolchain
(workspace tool, test and lint commands, docs renderer). It never spawns designers: packages
are planned one at a time, below.

If it has questions it cannot settle, it **stops** — see [Questions](#questions) — and you
re-run.

```
/project-workers:plan-package data
```

Forks into the architect at package scope. It reads the repo contract and, for every package
`data` depends on, that package's `docs/packages/<dep>/interface.md` — the surface as shipped.
Then:

1. Writes `docs/packages/data/contract.md` — the **package contract**: the section list, what
   each section returns to its siblings (signatures now, not shapes), the pipelines that run
   the sections in order (`download → clean → audit → store`), what the package will expose,
   and a `Consumes` table of every upstream name it uses.
2. Spawns one **designer** per section, in parallel. Each writes
   `docs/packages/data/design/<section>.md` and returns ten lines.
3. Reads every design and writes `docs/packages/data/integration.md`: deviations, mismatches,
   dependency order, shared work, risks, decisions needed — and **Repo contract deviations**,
   which it may resolve by editing the repo contract only when no shipped package is bound by
   the shape.
4. Writes `docs/packages/data/surface.md` — the design of the public surface, now that the
   section interfaces are concrete: the `__all__` names (only those a downstream package or a
   CLI command consumes, each with its consumer named), the pipeline signatures, the CLI
   commands with every argument, the import-linter contracts for this package.
5. Appends `D<n>` stubs to `docs/decisions.md`.

Then answer the decisions, and implement in the order `integration.md` gives, reviewing as you
go:

```
/project-workers:implement-section data/ingest
/project-workers:review-section data/ingest
/project-workers:implement-section data/clean
/project-workers:review-section data/clean
…
```

Sections go in that order and cannot be built out of it: `/project-workers:implement-section data/clean`
refuses while `data/ingest` has no README. Each implementer reads the **READMEs** of the
sections it depends on — what actually shipped — ranked above those sections' design docs. `integration.md` is a plan-time document; it stops
being true the moment the first implementer deviates, and implementers deviate. The README is
where a deviation is recorded, so the README is what the next section codes against.

When every section has a README *and a review newer than it*, publish the package:

```
/project-workers:status data --gate
/project-workers:finalize-package data
/project-workers:review-package data
```

`/project-workers:finalize-package` refuses until every section is built and reviewed since its last build and
no review-sourced follow-up is open — `/project-workers:status data --gate` shows the same check. Then it forks
into the implementer in **surface mode**: it writes the top-level `src/data/__init__.py`
(lazy re-exports — importing `data` loads nothing until a name is used — of only the names a
consumer needs), the `pipelines/` that compose the sections, `cli.py` with one function per
command (its docstring is the `--help` text), the package's `docs/api/data.md` page so the
docs site builds strict from here on, `Applied:` lines any section implementer missed, and
`docs/packages/data/interface.md` — the public surface **as shipped**. `/project-workers:review-package` is
the gate: `__all__`, `interface.md`, and the section READMEs agree; every public name has a
consumer; every shape the repo contract promised is realized; `lint-imports` and `mkdocs
build --strict` pass; the pipelines and commands run.

Next week:

```
/project-workers:plan-package analysis
```

reads `docs/packages/data/interface.md` as its upstream, and its designers reference those
names exactly. Planning against a package that has no `interface.md` yet is allowed — every
consumed name is marked `provisional` and the return says so.

```
/project-workers:finalize-project
```

writes a README per package and the root README from the shipped documents, plus the docs-site
API pages. Safe to run early and often.

## Workflow B — changing shipped code

```
/project-workers:plan-change "Add volume-weighted bars"
```

1. Forks into the architect at change scope, which spawns **Explore** to assess what the change
   touches and writes `docs/plans/<slug>/assessment.md`.
2. **Downstream impact.** For every affected package with an `interface.md`, it computes the
   consumers — `grep` over `packages/*/src` for shipped ones, the `Consumes` tables in other
   packages' contracts for planned ones — and lists which public names each uses that the
   change alters. Nothing maintains a consumers list; it is derived every time.
3. Seeds anything canonical that is missing (see `/project-workers:map-project` for the full version).
4. Writes `docs/plans/<slug>/contract-delta.md`: only the contracts added, changed, or removed,
   grouped by **Repo contract**, **Package contract: <pkg>**, and **Interface: <pkg>**.
5. Spawns designers in `Mode: change` (or `new`) — including downstream consumer sections it is
   adapting — writing to `docs/plans/<slug>/<pkg>/<section>.md`.
6. Writes `docs/plans/<slug>/integration.md`, including **Canonical doc updates**.

Then implement with the slug, and fold the plan back when it ships:

```
/project-workers:implement-section data/clean add-vwap
/project-workers:implement-section analysis/features add-vwap
/project-workers:review-section data/clean add-vwap
/project-workers:sync-plan add-vwap
```

**A change to a shipped package's public surface must go through `/project-workers:plan-change`.** If you run
`/project-workers:implement-section data/clean` without a slug and the work would alter a name in
`docs/packages/data/interface.md`, the implementer refuses: consumers were built against that
file. Internal changes proceed.

**`/project-workers:sync-plan` is not optional.** Until it runs, the design docs, contracts, and `interface.md`
describe pre-change behavior — and those stale files are what the next `/project-workers:plan-change` hands its
designers and what `/project-workers:plan-package` hands the next package as its upstream. It folds in only the
sections it can verify shipped, records them in `docs/plans/synced.md`, recomputes consumers
for any `interface.md` it changed, and files follow-ups for consumers the plan did not adapt.

## Questions

Subagents cannot ask you anything — Claude Code removes `AskUserQuestion` from every subagent,
whatever its `tools:` field says. So the architect does the only thing it can: when it has a
question that would change the shape of the plan, it writes a stub to `docs/decisions.md`
tagged `Raised by: /project-workers:plan-package data (interview)`, writes nothing else, and **stops**:

```
Stopped for decisions: D12, D13
- D12 — Bars: store timestamps as UTC or exchange-local? (assumption: UTC)
- D13 — Is audit its own section or part of clean? (assumption: its own)
Answer in docs/decisions.md, or re-run `/project-workers:plan-package data` as-is to accept the assumptions.
```

Fill in `Decision:` and set `Status: decided`, or do nothing — either way, re-run the same
command. The tag is how it knows not to ask twice: on the re-run, every entry carrying that
tag counts as asked, and it proceeds on your answer or on its assumption (leaving a marker in
the code, below). There is no fixed number of questions per stop — v3's "at most four" was
the batch limit of the `AskUserQuestion` widget, which is gone; the cost test is the only
gate, and the architect is told that a page of stubs means it should have settled more
itself.

## Decisions

Subagents start with a fresh context and never see your conversation. Anything you decide has
to be in a file. `docs/decisions.md` is that file, and it is the highest-authority document in
the system. One ledger for the whole repo, one `D<n>` sequence — decisions cross packages
routinely ("what timezone do we store?"), and per-package ledgers would split them in half.

The architect writes the stubs. It is the only allocator of `D` numbers. You fill in
`Decision:` and `Status:`.

```markdown
## D7 — Session store: Redis or Postgres?
Scope: data/storage, analysis/cache
Raised by: OQ-data-storage-2, docs/packages/data/integration.md
Recommendation: Postgres. One dependency instead of two.
Assumption if unanswered: Postgres.
Decision: Postgres.
Status: decided
Applied: data/storage, 2026-09-09, packages/data/src/data/storage/session.py
```

`Scope:` is `repo`, a package name, or a list of `<pkg>/<section>`. An implementer working on
`analysis/cache` is bound by entries scoped `repo`, `analysis`, or any list containing
`analysis/cache` — one prefix rule.

- `decided` — the implementer builds it and adds an `Applied:` line, one per section.
- `deferred`, or `open` with an assumption — the implementer builds the assumption and leaves
  `# TODO(decision D7)` at the affected line.
- `open` with **no** `Assumption if unanswered:` — **blocks** the implementer if the section
  cannot be built without it; otherwise a marker and a note.
- `superseded` — the question is moot. Only the architect sets this.

**The loop closes on re-run.** Change a decision to `decided`, run `/project-workers:implement-section` again,
and the implementer greps its section for `TODO(decision D*)`, re-reads each one's status,
implements the ones now decided, and deletes their markers.

**Adopting an older ledger.** A `decisions.md` from v3 says `Sections:` instead of `Scope:`
and has unqualified section names. Nothing breaks: every agent reads `Sections:` as a `Scope:`
over the only package, numbers continue above the highest `D<n>` found, and `Applied:` lines
are added as decisions are applied.

## Follow-ups and reviews

The implementer only touches its own section. When it needs something elsewhere, it appends to
`docs/followups.md` with the qualified target:

```
- [ ] data/storage: add index on bars(symbol, ts) — needed by analysis/features, 2026-09-04
- [ ] data/surface: load_bars now takes a DateRange, surface.md said (start, end) — 2026-09-05
```

`<pkg>/surface` is a reserved target: it is what `/project-workers:finalize-package` picks up, and where an
implementer files any drift between what it shipped and what `surface.md` planned.

`/project-workers:review-section` and `/project-workers:review-package` feed the same queue: a full report to
`docs/reviews/<date>-<pkg>-<section>.md` (or `<date>-<pkg>-package.md`), every CRITICAL finding
appended to `docs/followups.md`.

Review per section, as you go. A review after finalize would cover every section under one
return, and the surface would already re-export whatever a CRITICAL finding is about.

**Fixing a CRITICAL is a re-run, not a new plan.** A section finding: run
`/project-workers:implement-section <pkg>/<section>` again — its step 6 picks up follow-ups addressed to it and
the latest review, fixes them, ticks them off. A surface finding from `/project-workers:review-package`: run
`/project-workers:finalize-package <pkg>` again, then `/project-workers:review-package <pkg>`. `/project-workers:plan-change` is needed only
when the package is already shipped and the fix would change a name in `interface.md` — the
implementer refuses that without a slug and tells you so.

## Code conventions

Knowledge is scoped **by role**, through each agent's `skills:` frontmatter. That is the only
mechanism in Claude Code that scopes by agent — rules scope by file path or not at all, which
is the wrong axis here, since the architect and designer need the size limits and never open a
`.py` file.

| Skill | arch | design | impl | review | doc |
|---|:--:|:--:|:--:|:--:|:--:|
| `project-structure` — layout, size limits, config placement, naming | ✓ | ✓ | ✓ | ✓ | — |
| `python-style-guide` — inside a file: docstrings, function shape, `__init__.py`, naming | — | — | ✓ | ✓ | — |
| `python-implementation` — splitting mechanics, config code | — | — | invoked | — | — |
| `workspace-scaffold` — pyproject, import-linter, mkdocs skeletons | invoked | — | invoked | — | — |
| `planning-templates` — headings for every planning document | invoked | — | — | — | — |
| `security-review` — checklist | — | — | invoked | invoked | — |

Three conventions in `python-style-guide` are marked *Project convention* because they go
beyond or beside Google's guide:

- **`__init__.py`.** The top-level `__init__.py` of a package exposes *only the names a
  consumer outside the package needs* — a downstream package or a CLI command, each named in
  `surface.md` — resolved lazily (PEP 562) so `import data` costs nothing until a name is
  touched. Written by `/project-workers:finalize-package`, and by nothing else. Every nested one is empty.
  Inside a package, import from the defining module; from another package, import from its top
  level only. import-linter enforces the second.
- **CLI commands live in `src/<pkg>/cli.py`**, one function per command, registered under
  `[project.scripts]`. There is no `scripts/` directory: an entry point must be importable
  from the installed package, and a file beside `src/` is not. A command's docstring names
  every argument — it is the `--help` text and the docs page.
- **Docstrings on everything.** Every module, class, function, and method; one line is enough
  for a private helper. Google style, `Args:` without types, `Examples:` in doctest form on
  public entry points, cross-references in mkdocstrings syntax. The docs build runs strict in
  CI — that is the docstring-rot catch. Agents never read the generated site; they read the
  curated `interface.md`.
- **Function shape.** Phases inside a function are fine and each gets a one-line purpose
  comment; a helper is extracted only when the jump buys something (reuse, I/O split from
  transformation, a retry wrapper, a phase that needs its own docstring, the seam under the
  soft limit). No single-use helpers whose name restates three lines. The reviewer's test: the
  main path reads top to bottom with at most one jump per phase.

**Enforced, not intended.** Dependency direction between packages, "consumers import the top
level only", and section layering inside a package are import-linter contracts in the root
`pyproject.toml`: `layers` for direction (indirect chains count), `forbidden` for internals.
The repo contract carries the target block; the first `/project-workers:implement-section` of each package
grows `root_packages` and the layers list; `/project-workers:finalize-package` adds the `forbidden` contract.
`lint-imports` runs in CI beside `ruff check`.

`.claude/rules/python-standards.md` is a pointer scoped to `**/*.py` for **you**, working
interactively, where no agent frontmatter applies. Merge `pyproject-lint-config.toml` into the
root `pyproject.toml`; it ships beside this README rather than inside a skill so there is one
copy.

## `docs/` layout

```
docs/
├── brief.md                        your input to /project-workers:plan-repo
├── architecture.md                 THE REPO CONTRACT                         (plan-repo)
├── decisions.md                    D<n> ledger, Scope: field                 (architect stubs / you / implementer)
├── followups.md                    queue, entries `- [ ] <pkg>/<section>: …` (implementer, reviewer, sync-plan)
├── assessment.md                   repo survey                               (map-project, plan-repo extend)
├── api/<pkg>.md                    docs-site API pages                       (finalize-project)
├── packages/
│   └── data/
│       ├── brief.md                the package brief, if given               (plan-package)
│       ├── assessment.md           package survey                            (plan-package)
│       ├── contract.md             THE PACKAGE CONTRACT                      (plan-package)
│       ├── design/<section>.md     one per section                           (designer)
│       ├── integration.md          reconciliation, plan-time                 (architect)
│       ├── surface.md              design of the public surface              (architect, at unify)
│       └── interface.md            THE PUBLIC SURFACE AS SHIPPED             (finalize-package)
├── reviews/
│   ├── 2026-09-04-data-ingest.md   one per section review
│   └── 2026-09-08-data-package.md  one per package review
└── plans/
    ├── synced.md                   which plan sections are folded in         (sync-plan)
    └── add-vwap/                   one folder per /project-workers:plan-change run
        ├── assessment.md           what the change touches + Downstream impact
        ├── contract-delta.md       changed contracts and interfaces only
        ├── data/clean.md           delta design per affected section
        └── integration.md          reconciliation + canonical doc updates
```

**Canonical vs proposal.** Everything outside `plans/` describes the code as it is, with one
honest exception: a greenfield design describes intended code until its section ships — which
is exactly why implementers read READMEs and `interface.md` over designs for anything they
consume. `plans/*` are proposals; they stay as history after they ship and are never edited.
`/project-workers:sync-plan` is the one skill allowed to move content from the second into the first, after
verifying the code exists.

**Package status is derived, never written down:** `contract.md` exists → planned; every
section README → built; `interface.md` → shipped. Only a shipped package can be planned
against without the consumed names being marked provisional.

## Hand-off diagram

```
you ── /project-workers:plan-repo ────────────▶ architect ──▶ docs/architecture.md, decision stubs   (may stop for questions)

you ── /project-workers:plan-package data ────▶ architect ──▶ docs/packages/data/contract.md
                                architect ──┬──▶ designer (data/ingest)  ──▶ design/ingest.md
                                            ├──▶ designer (data/clean)   ──▶ design/clean.md
                                            └──▶ designer (data/storage) ──▶ design/storage.md
                                architect ◀── summaries (≤10 lines each)
                                architect ──▶ integration.md, surface.md, decision stubs

you ── docs/decisions.md (answers)

you ── /project-workers:implement-section data/ingest ──▶ implementer ──▶ src/data/ingest/, tests, section README
                                          implementer ──▶ followups.md, decisions.md Applied:
you ── /project-workers:review-section data/ingest ─────▶ reviewer ──▶ docs/reviews/<date>-data-ingest.md, followups

you ── /project-workers:finalize-package data ──────────▶ implementer (surface mode) ──▶ src/data/__init__.py, pipelines/, cli.py, docs/api/data.md
                                          implementer ──▶ docs/packages/data/interface.md
you ── /project-workers:review-package data ────────────▶ reviewer ──▶ docs/reviews/<date>-data-package.md

you ── /project-workers:plan-package analysis ──────────▶ architect reads docs/packages/data/interface.md as upstream …

you ── /project-workers:plan-change "…" ────────────────▶ architect ──▶ docs/plans/<slug>/ (+ Downstream impact)
you ── /project-workers:sync-plan <slug> ───────────────▶ architect ──▶ contracts, designs, surface.md, interface.md updated
you ── /project-workers:finalize-project ───────────────▶ documenter ──▶ packages/*/README.md, docs/api/*.md, README.md
```

Every arrow into an agent carries a file path, not a conversation.

## Gotchas

- **Nobody can ask you anything.** The architect stops and writes stubs; designers,
  implementers, and reviewers turn missing information into a stated assumption plus an open
  question, or a blocker returned to you.
- **Re-running the same command is the continue action** after a stop. Doing nothing in the
  ledger means "accept the assumptions".
- **Return size is context cost.** Designers and implementers return short summaries; the
  content is on disk. If you want detail, read the file.
- **Descriptions are always loaded.** Keep agent `description` fields short — the combined
  budget warns at 15,000 tokens. Detail goes in the body, which loads only when the agent runs.
- **Nesting depth.** Architect (layer 1) spawning designers (layer 2) is within the default
  three-layer limit. `/project-workers:plan-repo` deliberately does not spawn package architects — that would
  put designers at layer 3 and plan every package at once, which is not how you work.
- **`/project-workers:finalize-package` has no partial mode.** Every section needs a README, a review newer
  than it, and no open review-sourced follow-up; a public surface is a promise consumers build
  against. `/project-workers:status <pkg> --gate` shows exactly what is missing.
- **Expect blockers on the first implement run of an adopted repo.** Unanswered questions with
  no fallback assumption stop the implementer by design. Answer them in `docs/decisions.md` and
  re-run.
- **import-linter needs the packages importable.** Run `lint-imports` inside the workspace
  environment (`uv run lint-imports`), and expect it to fail on a package listed in
  `root_packages` that has no code yet — which is why the block grows as packages are built.
- **The docs site builds strict from the first section.** The scaffold writes a stub
  `docs/index.md` and a nav naming only files that exist; `/project-workers:finalize-package` adds each
  package's API page; `/project-workers:finalize-project` regenerates the index. MkDocs' default `docs_dir` is
  `docs/` — your planning docs — and the scaffold keeps it, excluding `plans/**`; change it in
  the repo contract's Toolchain before the first scaffold if you would rather not publish them.
- **Instruction-only boundaries.** "Write only under `docs/`" is an instruction, not an
  enforcement. To enforce it, add a `PreToolUse` hook on `Write|Edit` in `settings.json`
  rejecting paths outside `docs/` for the architect, designer, and documenter — hooks from
  settings files do run inside subagents.
- **Parallel sections.** Add `isolation: worktree` to `implementer.md` frontmatter and each run
  works in its own git worktree. Only for sections `integration.md` shows as independent — and
  note that `.gitignore`, `docs/followups.md`, `docs/decisions.md`, and the root
  `pyproject.toml` are shared files that runs append to, so expect to merge them.
- **Interactive session for a hard section:** `claude --agent implementer` gives the main thread
  the implementer's system prompt, tools, and model, so you get the blocking rules and return
  format while steering turn by turn.

Reference: https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/skills
