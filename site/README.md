# The reading site

Renders the plugin — every agent, every skill, the rule, the lint config — as a browsable
MkDocs site. The bundle itself stays the source of truth; this only mirrors it.

## Build and read

```bash
pip install mkdocs mkdocs-material pymdown-extensions   # once
python3 site/build_site.py                              # from the repo root
cd site && mkdocs serve                                 # then open http://127.0.0.1:8000
```

`build_site.py` takes the repo root by default, so it needs no arguments. Re-run it after
editing any agent or skill; the nav is generated from what it finds, so a new skill or a new
`references/` file appears without editing any config.

Optional: `python3 site/build_site.py --evals evals.json` adds an Evals page.

## What is generated vs. authored

Generated, and gitignored — never edit these by hand:

- `site/docs/` — every page, rebuilt from scratch on each run
- `site/mkdocs.yml` — `mkdocs-base.yml` plus a generated nav
- `site/_site/` — the built HTML, if you run `mkdocs build`

Authored, and committed:

- `site/mkdocs-base.yml` — theme, extensions, CSS. Everything except the nav.
- `site/workflows/*.md` — one page per pipeline (new repo, changing shipped code, adopting
  an existing repo, …); reading order is `WORKFLOWS_ORDER` in `build_site.py`, unlisted files
  follow alphabetically
- `site/flow.md` — the hand-written orientation page: where truth comes from, the loop,
  the hand-offs, the order of authority
- `site/extra.css`
- `site/notes/*.md` — drop any design doc or decision record here and it gets a nav entry
  under "Notes"
