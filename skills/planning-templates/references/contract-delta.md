# `docs/plans/<slug>/contract-delta.md`

**Only** what the change adds, changes, or removes. Reference unchanged contracts by name and
section rather than restating them; that is what keeps a delta a delta.

If the canonical contract does not exist, do not stretch this file to carry it. Seed the
canonical doc first — the skill that invoked you says how — and keep the delta a delta. A
contract stranded in a plan directory is invisible to every later run.

1. **Change goal** — one paragraph.

2. **Affected sections** — same columns as a package contract's Sections table, with
   qualified `<pkg>/<section>` names, including downstream consumer sections this plan adapts.

3. **Contract changes** — grouped by which contract, then Added / Changed / Removed within
   each group:
   - **Repo contract** — shapes and conventions in `docs/architecture.md`.
   - **Package contract: <pkg>** — one group per affected package: section interfaces,
     pipelines, Consumes rows.
   - **Interface: <pkg>** — one group per shipped surface the change alters. This is what
     consumers were built against, so every altered name is listed with its old and new
     signature, and every consumer from the assessment's **Downstream impact** is named.
