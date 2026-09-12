---
name: planning-templates
description: The heading-by-heading templates for every planning document the architect writes — repo contract, package contract, contract-delta, integration doc, surface doc. Invoke when about to write one of them and read only the reference for that document. Kept out of the architect's always-loaded prompt so a run pays for the templates it uses.
---

# Planning document templates

One reference file per document. Read the one you are about to write; do not read the others.
The architect's own prompt carries the rules that apply to all of them (what is canonical,
who may edit what, the ledger shape, the delegation prompt); these files carry only the
headings, the budget, and what goes under each heading.

| You are writing | Read |
|---|---|
| `docs/architecture.md` — the repo contract | `references/repo-contract.md` |
| `docs/packages/<pkg>/contract.md` — the package contract | `references/package-contract.md` |
| `docs/plans/<slug>/contract-delta.md` | `references/contract-delta.md` |
| `docs/packages/<pkg>/integration.md` or `docs/plans/<slug>/integration.md` | `references/integration.md` |
| `docs/packages/<pkg>/surface.md` | `references/surface.md` |

The reviewer, implementer, and documenter parse these documents by heading, so the headings
are a contract too: keep them, in order, spelled as written. Omit one only when it truly does
not apply, and leave a one-line note under it saying so.
