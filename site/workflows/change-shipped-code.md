# Changing shipped code

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
