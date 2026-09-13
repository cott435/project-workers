# Adopting an existing repo

For a repo that has code but no `docs/`, or whose canonical docs have drifted from the code far
enough to mislead. Two levels, one run each, bottom-up.

```
/project-workers:map-project [scope]
```

Forks into the **architect** at repo scope, document mode. It spawns `Explore` to map the repo —
packages, the imports between them, entry points, top-level `__init__.py` exports, the shapes
crossing package boundaries, config, error and logging patterns, toolchain — verifies the paths
it cites, and writes `docs/assessment.md`. Then the interview rule: the package decomposition
(these become permanent directory names), which conventions are intentional, what is out of
scope. If it has unasked questions it stubs them in `docs/decisions.md` and **stops** (see
**Questions** on the home page); otherwise it writes `docs/architecture.md` describing the repo
**as it is** — a cyclic import graph is recorded as cyclic, a missing convention as missing —
seeds the ledger, and files a follow-up for every concrete defect it found. Nothing in this run
proposes a change.

On a repo whose canonical docs already exist, it treats each as a claim to check against the
code: keeps wording the code agrees with, rewrites what the code contradicts, removes what no
longer exists, and reports every edit as *stale doc corrected* or *code looks wrong, filed as a
follow-up*.

Then, per package, lowest in dependency order first:

```
/project-workers:plan-package <pkg>
```

runs in **document mode** because the package directory has code: the assessment is a survey of
that code, the contract is written as it is, every designer runs `Mode: document`, the
integration doc gains a **Coverage** heading, and `surface.md` is transcribed from the top-level
`__init__.py`, entry points, and CLI as they exist. If the top-level `__init__.py` already
re-exports, `interface.md` is written too and the package counts as shipped. If it is empty,
`surface.md` is marked *inferred*, no `interface.md` is written, and the package is not shipped
until `/project-workers:finalize-package` runs. What looks wrong becomes a follow-up addressed to its section.

From here the repo is on the same loop as a new one: answer decisions, then
`/project-workers:implement-section` for follow-ups and `/project-workers:plan-change` for anything that alters a
shipped surface. Expect blockers on the first implement run — unanswered questions with no
fallback assumption stop the implementer by design.
