# `integration.md` — reconciliation after the designers return

Package scope writes `docs/packages/<pkg>/integration.md`; change scope writes
`docs/plans/<slug>/integration.md`; `/project-workers:map-project` and adoption runs write it about existing
code (see the last section). Read every design you delegated — those files, not the whole
directory — before writing.

1. **Contract deviations** — each place a design departs from the package contract: which
   section, what changed, resolution (`update contract` | `update design` | `needs user
   decision`).

2. **Cross-section mismatches** — a type, signature, or name two designs treat differently.
   Same resolution format.

3. **Dependency order** — the order sections should be implemented, with reason. This is the
   order the user will type `/project-workers:implement-section` in, and `/project-workers:implement-section` refuses a
   section whose dependencies are unbuilt, so the order must respect the Sections table's
   `Depends on`.

4. **Shared work** — utilities, fixtures, tables, or infrastructure more than one section
   needs, and which section owns it. Write each entry as something the owning section could
   build from — name, signature or schema, and who consumes it. This is the one place such an
   item is specified: you cannot edit the owner's design doc to add it, so an entry that only
   gestures at the need ships as nothing at all, and the consuming section blocks.

5. **Risks** — from designers' pitfalls, deduplicated and ranked.

6. **Decisions needed from user** — by `D<n>`, each with your recommendation.

7. **Repo contract deviations** — each place a design or this package's needs depart from
   `docs/architecture.md`. Resolution is `update repo contract` **only when no shipped
   package provides or consumes the shape** (check `ls docs/packages/*/interface.md`) — then
   edit `docs/architecture.md` and note it here. Otherwise `needs plan-change`, with a stub
   scoped `repo`.

8. **Canonical doc updates** *(change plans only)* — which canonical docs `/project-workers:sync-plan` must
   update once the code ships — contracts, designs, `surface.md`, `interface.md`, the repo
   contract's Boundaries — and what each change is. Specific enough that someone with no
   memory of this run could apply it.

**On a mapping or adoption run** the content is different in kind: **Contract deviations**
become places the code contradicts its own stated conventions; **Cross-section mismatches**
become real inconsistencies between existing sections; **Dependency order** is the order
someone would rebuild these sections in; add a **Coverage** heading saying which parts of the
package a design doc now describes and which it does not.
