---
name: plan-change
description: Plan a change to shipped code in one or more packages. Assesses what the change touches and which downstream packages consume it, seeds canonical docs if missing, scopes the affected sections, runs parallel delta designs, and writes a unified integration doc under docs/plans/. Required for any change to a shipped package's public surface.
argument-hint: "<change description, or path to a file containing it>"
context: fork
agent: architect
background: false
disable-model-invocation: true
---

Plan the following change at **change scope**:

$ARGUMENTS

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `architect` subagent — the agent is not
> registered, usually because the project-workers plugin was installed or updated after Claude
> Code started. Stop, tell the user to run `/reload-plugins` (or restart Claude Code),
> verify with `/agents`, and re-run. Do not plan in the main thread.

If the argument is a file path, read it and treat its contents as the change description. If
it is empty, look for the most recent `docs/plans/*/assessment.md` whose plan has no
`integration.md` — a re-run after the interview rule stopped — and continue that plan.

## Steps

1. **Name the plan.** Derive a short kebab-case slug from the change — it becomes a permanent
   directory name and the second argument to `/project-workers:implement-section`, so make it something you
   would recognize in six months. All plan outputs go under `docs/plans/<slug>/`.

2. **Assess.** Spawn an `Explore` subagent (thoroughness: very thorough) to locate the code,
   tests, config, and docs the change touches: affected packages and sections, entry points,
   existing types and interfaces involved, current test coverage for those paths, and anything
   fragile. `Explore` cannot write files, so verify its citations with your own `Read`/`Grep`
   and write the result yourself to `docs/plans/<slug>/assessment.md`.

   Then read the canonical docs: `docs/architecture.md`, and for every affected package its
   `contract.md`, `design/*.md`, `surface.md`, and `interface.md`; plus `docs/decisions.md`
   and `docs/followups.md`. If canonical docs are thin, the most recent
   `docs/plans/*/integration.md` may hold contracts a previous change established.

3. **Downstream impact.** For every affected package that has an `interface.md`, compute its
   consumers — do not look for a maintained list, there is none:

   ```
   grep -rln "from <pkg>\b\|import <pkg>\b" packages/*/src | grep -v "^packages/<pkg>/"
   grep -l "<pkg>" docs/packages/*/contract.md          # then read each Consumes table
   ```

   The first finds **shipped** consumers; the second finds **planned** ones (a package whose
   contract's **Consumes** table names `<pkg>`). For each consumer, list which public names it
   uses that this change adds, removes, or alters. Write this as the **Downstream impact**
   section of the assessment: consumer | shipped or planned | names affected | what breaks.

   A change that alters nothing in an `interface.md` has no downstream impact; say so in one
   line rather than skipping the heading.

4. **Interview rule.** Decide what you would ask — an ambiguity in the existing code that
   decides how the change should be shaped, a section boundary the repo does not settle,
   whether a downstream consumer should be adapted in this plan or left to break with a
   follow-up. Check the ledger; stub anything unasked tagged
   `Raised by: /project-workers:plan-change <slug> (interview)` and **stop** with the stop message. Otherwise
   proceed. Ask *before* step 5: seeding a contract names sections, and those names become
   permanent.

5. **Seed anything canonical that is missing.** Before designing the change, make sure the
   documents every later step reads actually exist:

   - **No `docs/architecture.md`** → write one now, describing the repo **as it is today**,
     from the assessment: the packages you can identify, the shapes crossing them, the
     conventions actually in use, and an explicit note where there is no convention at all.
   - **No `docs/packages/<pkg>/contract.md` for an affected package** → the package has never
     been adopted. Seeding a whole package here is a run of its own: say so in your return and
     recommend `/project-workers:plan-package <pkg>` (document mode) before this change, unless the change
     touches a single section — then write the contract as-is from `references/package-contract.md`
     and, if the top-level `__init__.py` re-exports anything, seed `interface.md` from it.
   - **No `docs/packages/<pkg>/design/<section>.md` for a section this change touches** → that
     section needs a baseline before it can have a delta. See step 7, which runs it in two
     waves.
   - **No `docs/decisions.md`** → create it.

   Seeding is not modifying. Writing a baseline that describes shipped code upholds the rule
   that canonical docs describe reality; editing an existing canonical doc to describe a change
   that has not shipped would break it. **Create what is missing; never revise what is there.**

   If the repo is big enough that mapping it properly is its own job, say so in your return and
   recommend `/project-workers:map-project` rather than seeding half of it. If a canonical doc exists but the
   assessment shows it is badly out of date, do not quietly design against it and do not
   rewrite it here: record each contradiction in the assessment, note it in your return, and
   recommend `/project-workers:map-project`, which is the skill allowed to reconcile canonical docs with
   reality.

6. **Scope.** Decide which sections the change touches, including downstream consumer
   sections you are adapting in this plan. Invoke `planning-templates`, read
   `references/contract-delta.md`, and write `docs/plans/<slug>/contract-delta.md` to it —
   only the contracts added, changed, or removed, grouped by which contract, with every altered
   shipped-surface name carrying its old and new signature.

6b. **Probe.** For every affected section whose `source` — from the package contract, or the
   contract-delta for a section this change adds — has no probe doc whose **Credentials**
   reads `valid`, run your **Probing** section: one researcher per source, in parallel, before
   any designer. The credential stop applies here exactly as in `/project-workers:plan-package`. A probe
   doc that exists and is `valid` is not re-probed, however old; wave B says what to do when it
   is older than the code.

7. **Delegate**, in two waves. Everything inside a wave runs in parallel; wave B waits for
   wave A, because a delta needs its baseline to exist first.

   **Wave A — baselines.** Only for sections the change touches that have no design doc
   (from step 5). One designer each:
   - `Mode: document`
   - `Contracts (highest first): docs/packages/<pkg>/contract.md, docs/architecture.md` — the
     canonical contracts, **not** the delta. A baseline describes shipped code.
   - `Upstream interfaces:` the shipped `interface.md` paths for that package's dependencies
   - `Source probes:` `docs/packages/<pkg>/sources/<source>.md` for the section's source, or `none`
   - `Existing design: none` · `Assessment: docs/plans/<slug>/assessment.md`
   - `Write your design to: docs/packages/<pkg>/design/<section>.md`

   **Wave B — the change.** One designer per affected section:
   - `Mode: change` for a section that exists; `Mode: new` for one this change creates. Mode
     describes the section, not the run.
   - `Contracts (highest first): docs/plans/<slug>/contract-delta.md,
     docs/packages/<pkg>/contract.md, docs/architecture.md`
   - `Upstream interfaces:` as above — and for a downstream consumer being adapted, the
     provider's `interface.md` *plus* the contract-delta, which says what will change
   - `Source probes:` as above. When the change alters how a source is parsed and its probe
     doc is older than the section's README, say in your return that
     `/project-workers:probe-source <pkg> <source>` should run before `/project-workers:implement-section`
   - `Existing design: docs/packages/<pkg>/design/<section>.md` — including the baseline wave A
     just wrote — or `none` for a section being added
   - `Assessment: docs/plans/<slug>/assessment.md`
   - `Skills to invoke:` that section's project skills
   - `Write your design to: docs/plans/<slug>/<pkg>/<section>.md`

   With no wave-A sections, this is one parallel batch and the two-wave structure costs nothing.

8. **Unify.** Read the design docs you delegated, read `references/integration.md`, and write
   `docs/plans/<slug>/integration.md` to it, including **Canonical doc updates**: which
   canonical docs must change once the code ships — `contract.md`, `design/*.md`,
   `surface.md`, `interface.md`, and the repo contract's Boundaries — and what each change is.
   That section is the input to `/project-workers:sync-plan`, so write it for someone with no memory of this
   run.

   For each planned-only consumer from step 3 that this plan does not adapt, append
   `- [ ] <consumer>/<section>: <provider> <name> changes under plan <slug> — <date>` to
   `docs/followups.md`, so its `/project-workers:plan-package` or `/project-workers:implement-section` finds it.

9. **Record decisions.** Append `D<n>` stubs to `docs/decisions.md` for every open question,
   continuing the existing numbering, scoped to the sections they bind. Reference them by
   number in the integration doc.

10. **Return** your standard summary — slug first, the Downstream impact one line per
    consumer — ending with the next command:
    `/project-workers:implement-section <first affected section in dependency order> <slug>`

## Constraints

- Never modify an existing canonical document. Creating a missing one per step 5 is required;
  revising one to describe unshipped code is forbidden. Changes to canonical docs happen in
  `/project-workers:sync-plan`, after the code exists.
- No code, config, or tests.
- If the change touches one section and no contracts or interfaces, say so in the return and
  produce the assessment (with its one-line Downstream impact), that one design doc, and a
  short `integration.md` — dependency order and decisions only. Skip `contract-delta.md`.
  `/project-workers:implement-section` expects an integration doc, so a minimal one is still required.
