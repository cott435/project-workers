---
name: status
description: Print the checklist of where every package and section stands - planned, built, reviewed since its last build, open follow-ups, decision markers - derived from docs/ and the code, never from a status file. Use before /project-workers:finalize-package, before planning the next package, or whenever you have lost track of what is done.
argument-hint: "[pkg] [--gate]"
disable-model-invocation: true
---

Run the status script from the repo root and show its output verbatim:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/status.py $ARGUMENTS
```

Then, in two or three lines, say what the table means for the next command: which section is
next in order, which sections still need a review before `/project-workers:finalize-package`, which package
is ready to plan against. Do nothing else — no edits, no fixes.

With a package name, only that package is shown. With `--gate`, the script also prints the
`/project-workers:finalize-package` preconditions as PASS or FAIL with reasons — the same check that skill
runs before building the surface.

Everything printed is derived: a package is *planned* when `contract.md` exists, *built* when
every section has a README, *shipped* when `interface.md` exists; a section is *reviewed* when
a `docs/reviews/<date>-<pkg>-<section>.md` is dated on or after the README's last change;
"open followups" counts unchecked `docs/followups.md` entries addressed to that section, with
review-sourced ones (CRITICAL findings) counted separately because those block finalizing.
