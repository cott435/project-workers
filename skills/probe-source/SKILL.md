---
name: probe-source
description: Research one external data source for one package - check the credential, read the official docs, call the endpoints the section needs, and write the observed schema, pagination, limits, and error shapes to docs/packages/<pkg>/sources/<source>.md with a scrubbed sample and a re-runnable probe script. /project-workers:plan-package runs this itself for every section with a source; run it directly after an API changes, or to add a source after planning.
argument-hint: "<pkg> <source> [purpose - what the section needs from it]"
arguments: [pkg, source]
context: fork
agent: researcher
background: false
disable-model-invocation: true
---

Probe source **$source** for package **$pkg** — **probe mode**.

> **Guard.** If you can see earlier conversation turns, or you have an `AskUserQuestion` tool, you are
> running in the main conversation rather than as the `researcher` subagent — the agent is not
> registered, usually because the project-workers plugin was installed or updated after Claude
> Code started. Stop, tell the user to run `/reload-plugins` (or restart Claude Code),
> verify with `/agents`, and re-run. Do not probe in the main thread.

If `$pkg` reached you unsubstituted — literally the text `$pkg` — take the first token of
`$ARGUMENTS` as the package and the second as the source. Everything after the second token is
the purpose; it may be empty.

## Resolve the prompt

Build your probe-mode prompt from what exists, so a direct run matches an architect-spawned one:

- `Source:` `$source`, lowercase, the token the package contract's `source` column uses.
- `Purpose:` the argument text if given; else the `responsibility` of the row in
  `docs/packages/$pkg/contract.md`'s Sections table whose `source` is `$source`; else a
  blocker — "no purpose given and none on file".
- `Env var:` the name the repo contract's **Shared conventions** gives for this source, else
  `discover`.
- `Extracted skill:` `.claude/skills/<skill>/` for the `docs/legacy/inventory.md` row whose
  `skill` or `resource` names `$source`, else `none`.
- `Write to:` `docs/packages/$pkg/sources/$source.md`.

`docs/packages/$pkg/` need not exist yet — create `sources/` under it. Nor need
`docs/architecture.md`: probing before planning is allowed, and for a data-heavy brief it is a
sensible first step.

## Steps

Run your **Probe mode** procedure, steps 1–7. A credential failure still writes the doc — with
**Credentials** filled and every later heading `not probed` — before returning the blocker.

## Constraints

- Write only `docs/packages/$pkg/sources/$source.md`, `$source.sample.json`, and
  `$source.probe.py`. Never touch the contracts, the designs, or `packages/`.
- One source per run. Several sources are several runs — or one `/project-workers:plan-package $pkg`, which
  probes them all in parallel.
