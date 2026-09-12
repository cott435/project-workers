---
name: sync-plan
description: Fold a shipped change plan back into the canonical docs. Applies the Canonical doc updates from docs/plans/slug/integration.md to the repo contract, the affected package contracts, design docs, surface.md, and interface.md, so the canonical docs keep describing the code as it actually is.
argument-hint: "<plan-slug>"
arguments: [plan]
context: fork
agent: architect
background: false
disable-model-invocation: true
---

Fold the shipped plan **$plan** back into the canonical documents — **sync scope**.

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `architect` subagent — the agent is not
> registered, usually because the project-workers plugin was installed or updated after Claude
> Code started. Stop, tell the user to run `/reload-plugins` (or restart Claude Code),
> verify with `/agents`, and re-run. Do not plan in the main thread.

If `$plan` reached you unsubstituted, take the slug from `$ARGUMENTS`.

Run this once every section of a change has been implemented and its tests pass. Until you
do, the design docs, contracts, and `interface.md` files describe the code as it was *before*
the change — and those stale docs are what the next `/project-workers:plan-change` hands its designers, what
`/project-workers:plan-package` hands the next package as its upstream, and what `/project-workers:implement-section` ranks in
its order of authority. Drift compounds per change; this is the step that stops it.

## Steps

1. **Read the plan.** `docs/plans/$plan/integration.md` — its **Canonical doc updates**
   section is your work list — plus `docs/plans/$plan/contract-delta.md`,
   `docs/plans/$plan/assessment.md` (its **Downstream impact**), and each
   `docs/plans/$plan/<pkg>/<section>.md`.

2. **Check what is already synced.** Read `docs/plans/synced.md` if it exists. It records which
   sections of which plans have already been folded in, so a re-run does not fold the same delta
   twice — which would duplicate interfaces and re-delete behavior that is already gone. Skip
   any section listed there for this slug.

3. **Verify each section shipped.** A section counts as shipped when all three hold: the files
   its design's **Module plan** names exist; the interfaces its **Interfaces** section declares
   are present with matching signatures; and its section `README.md` exists and describes them.
   Check with `Read`/`Grep` on the paths the design names — you are confirming the code matches
   the plan's shape, not re-reviewing its quality, which is `/project-workers:review-section`'s job.

   Sections divide into three, and partial plans are normal — implementation happens one section
   at a time, so most `/project-workers:sync-plan` runs will find some sections pending:

   - **Shipped** → fold it in (steps 4–8).
   - **Not implemented** → skip it. Do not update its canonical docs; that would put a
     future-tense claim into a document whose whole value is being true. List it in your return
     as pending, and note that `/project-workers:sync-plan $plan` should be run again once it ships.
   - **Partially shipped** — some interfaces present, others missing → fold in only what you can
     verify, and treat the rest as pending. Say exactly which parts you folded.

   Where shipped code diverges from the plan, **the code** is what canonical docs describe. The
   section README's **Implementation notes** records deviations; read them and write what was
   built, not what was proposed.

4. **Update `docs/packages/<pkg>/design/<section>.md`** for each shipped section: fold the delta
   into the baseline so the result reads as one coherent description of the section as it is
   now — not a baseline with a changelog stapled to it. Remove behavior the change removed.
   Update the **Skills used**, **Module plan**, **Interfaces**, and **Tests** sections to match
   what exists. Resolve **Open questions** that the change answered.

5. **Update `docs/packages/<pkg>/contract.md`** for each affected package: apply the delta's
   **Package contract: <pkg>** Added / Changed / Removed to the Sections table, Section
   interfaces, Pipelines, and Consumes — only the parts belonging to sections you verified as
   shipped.

6. **Update `docs/packages/<pkg>/surface.md` and `interface.md`** where the delta's
   **Interface: <pkg>** group names them and the surface code has actually changed (check
   `__init__.py`, `pipelines/`, `cli.py`). `interface.md` describes what shipped — copy
   signatures from the code, not from the delta. Then recompute its **Consumers (computed)**
   snapshot with the same greps `/project-workers:plan-change` uses, and for any consumer that the plan did not
   adapt and that has no follow-up yet, append one to `docs/followups.md` naming the changed
   names.

7. **Update `docs/architecture.md`**: apply the delta's **Repo contract** group to the
   Boundaries and Shared conventions — only for shapes whose providing sections you verified as
   shipped. Update the **Open decisions** list from `docs/decisions.md` as it now stands.

8. **Reconcile `docs/packages/<pkg>/integration.md`.** Fold in cross-section resolutions the
   change established, and drop entries it resolved. If it does not exist — a package that only
   ever ran `/project-workers:plan-change` — create it now from the plan's integration doc plus the canonical
   designs.

9. **Record what you synced.** Append to `docs/plans/synced.md` (create if absent), one line per
   section folded:

   ```
   - add-vwap / data/clean — synced 2026-09-09
   ```

   This is what makes re-running safe. Without it, a second `/project-workers:sync-plan $plan` after the
   remaining sections ship would fold the already-applied delta in a second time.

10. **Check the decision ledger.** For each `D<n>` this plan raised, confirm `Status:` and
    `Applied:` match reality: `decided` with no `Applied:` line and no matching code means it
    was answered but never built. Do not edit those fields — they belong to the user and the
    implementer. List every mismatch in your return.

11. **File what you could not fix.** Where the shipped code contradicts the plan in a way that
    looks like a defect rather than a deliberate deviation, append it to `docs/followups.md`
    addressed to that section. Your return message dies with this fork; the follow-up queue is
    what the next `/project-workers:implement-section` actually reads.

12. **Return**: canonical docs updated, sections folded, sections still pending and why,
    `interface.md` files changed and the consumers notified, decisions decided-but-not-applied,
    and follow-ups filed.

## Constraints

- This is the one skill that may edit canonical docs. Edit `docs/architecture.md`,
  `docs/packages/<pkg>/{contract,integration,surface,interface}.md`, and
  `docs/packages/<pkg>/design/*.md`; append to `docs/followups.md` and `docs/plans/synced.md`.
- Never edit a plan's own documents under `docs/plans/<slug>/` — a plan is history once it ships,
  and rewriting it destroys the record of what was actually proposed. `docs/plans/synced.md` is
  a ledger about plans rather than part of one, so appending to it is fine.
- No code, config, or tests.
- Never write a claim you did not verify against the code. An unverifiable claim goes in your
  return message as a question, not into a canonical doc as a fact.
