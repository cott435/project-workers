"""Render the project-workers plugin as an MkDocs site for reading.

Usage:  python3 site/build_site.py [bundle] [--evals evals.json]

`bundle` defaults to the repo root (the parent of this script's directory). Writes
site/docs/ — every agent and skill as a page with its frontmatter shown as a table, the
plugin README as the home page, the flow page, the rule and the lint config — then writes
site/mkdocs.yml by appending a generated nav to mkdocs-base.yml.

The nav is generated, so adding a skill or a reference file needs no edit here: re-run this,
then `mkdocs serve` from site/.

Any .md file you drop in site/notes/ is included under a "Notes" section — that is where
design docs and decision records go.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).parent
DOCS = HERE / "docs"

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)

# Reading order for the workflow skills: the order you actually run them, not alphabetical.
WORKFLOW_ORDER = [
    "plan-repo", "plan-package", "implement-section", "review-section",
    "finalize-package", "review-package", "plan-change", "sync-plan",
    "finalize-project", "map-project",
]


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter as ordered dict of raw strings, body)."""
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    key = None
    for line in m.group(1).splitlines():
        if re.match(r"^\s+- ", line) and key:
            fm[key] = (fm[key] + ", " if fm[key] else "") + line.strip()[2:].strip()
            continue
        mm = re.match(r"^([\w-]+):\s*(.*)$", line)
        if mm:
            key = mm.group(1)
            fm[key] = mm.group(2).strip()
    return fm, text[m.end():]


def fm_table(fm: dict[str, str]) -> str:
    """Render frontmatter as a two-column table so it is visible in the site."""
    if not fm:
        return ""
    pipe = "\\|"
    rows = "\n".join(f"| `{k}` | {v.replace('|', pipe) or '—'} |" for k, v in fm.items())
    return f"| frontmatter | value |\n|---|---|\n{rows}\n\n"


def demote(body: str) -> str:
    """Shift markdown headings down one level so the page title stays the H1."""
    return re.sub(r"^(#{1,5}) ", lambda m: "#" * (len(m.group(1)) + 1) + " ", body, flags=re.M)


def write_page(rel: str, title: str, fm: dict[str, str], body: str, source: str) -> None:
    out = DOCS / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    head = f"# {title}\n\n*Source: `{source}`*\n\n{fm_table(fm)}"
    out.write_text(head + demote(body))


def build_nav(agents: list[str], workflow: list[tuple[str, str]],
              knowledge: list[tuple[str, str]], notes: list[tuple[str, str]],
              has_evals: bool) -> str:
    """Generate the nav block from what was actually written."""
    lines = ["nav:", "  - Home (README): index.md", "  - The flow: flow.md"]
    lines.append("  - Agents:")
    lines += [f"      - {a}: agents/{a}.md" for a in agents]
    lines.append("  - Workflow skills:")
    lines += [f"      - {title}: {path}" for title, path in workflow]
    lines.append("  - Knowledge skills:")
    lines += [f"      - {title}: {path}" for title, path in knowledge]
    lines.append("  - Rules and config:")
    lines.append("      - rule python-standards: rules/python-standards.md")
    lines.append("      - pyproject-lint-config.toml: config/pyproject-lint-config.md")
    if notes:
        lines.append("  - Notes:")
        lines += [f"      - {title}: {path}" for title, path in notes]
    if has_evals:
        lines.append("  - Evals: evals.md")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle", nargs="?", default=str(HERE.parent),
                    help="plugin root (default: the repo root above site/)")
    ap.add_argument("--evals", default=None)
    args = ap.parse_args()
    bundle = Path(args.bundle).resolve()

    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()

    # Home: the plugin README, headings demoted under a title.
    readme_path = bundle / "README.md"
    if readme_path.exists():
        readme = re.sub(r"^# .*\n", "", readme_path.read_text(), count=1)
        (DOCS / "index.md").write_text(
            "# project_workers\n\n*Source: `README.md`*\n\n" + demote(readme))
    else:
        (DOCS / "index.md").write_text("# project_workers\n\nNo README.md found in the bundle.\n")

    shutil.copy(HERE / "flow.md", DOCS / "flow.md")
    shutil.copy(HERE / "extra.css", DOCS / "extra.css")

    # Agents
    agents = []
    for p in sorted((bundle / "agents").glob("*.md")):
        fm, body = split_frontmatter(p.read_text())
        write_page(f"agents/{p.stem}.md", f"agent: {p.stem}", fm, body, f"agents/{p.name}")
        agents.append(p.stem)

    # Skills — a skill that forks into an agent is a workflow skill; the rest are knowledge.
    workflow: dict[str, tuple[str, str]] = {}
    knowledge: list[tuple[str, str]] = []
    for p in sorted((bundle / "skills").glob("*/SKILL.md")):
        fm, body = split_frontmatter(p.read_text())
        name = p.parent.name
        kind = "workflow" if fm.get("context") == "fork" else "knowledge"
        title = f"/project-workers:{name}" if kind == "workflow" else name
        rel = f"skills/{kind}/{name}.md"
        write_page(rel, title, fm, body, f"skills/{name}/SKILL.md")
        (workflow.setdefault(name, (title, rel)) if kind == "workflow"
         else knowledge.append((title, rel)))
        refs = p.parent / "references"
        if refs.exists():
            for r in sorted(refs.glob("*.md")):
                rrel = f"skills/{kind}/{name}-{r.stem}.md"
                write_page(rrel, f"{name} / {r.stem}", {}, r.read_text(),
                           f"skills/{name}/references/{r.name}")
                knowledge.append((f"{name} / {r.stem}", rrel))

    ordered = [workflow[n] for n in WORKFLOW_ORDER if n in workflow]
    ordered += [v for k, v in sorted(workflow.items()) if k not in WORKFLOW_ORDER]

    # Rules and config
    fm, body = split_frontmatter((bundle / "rules" / "python-standards.md").read_text())
    write_page("rules/python-standards.md", "rule: python-standards", fm, body,
               "rules/python-standards.md")
    toml = (bundle / "pyproject-lint-config.toml").read_text()
    (DOCS / "config").mkdir(exist_ok=True)
    (DOCS / "config" / "pyproject-lint-config.md").write_text(
        "# pyproject-lint-config.toml\n\n*Source: `pyproject-lint-config.toml`*\n\n"
        "```toml\n" + toml + "\n```\n")

    # Notes: anything dropped in site/notes/
    notes: list[tuple[str, str]] = []
    notes_dir = HERE / "notes"
    if notes_dir.exists():
        for n in sorted(notes_dir.glob("*.md")):
            shutil.copy(n, DOCS / f"note-{n.name}")
            title = n.stem.replace("-", " ")
            notes.append((title, f"note-{n.name}"))

    # Evals, if given
    has_evals = False
    if args.evals:
        data = json.loads(Path(args.evals).read_text())
        lines = ["# Eval definitions\n", f"*Source: `{Path(args.evals).name}`*\n",
                 f"\n{data.get('notes', '')}\n"]
        for e in data["evals"]:
            lines.append(
                f"\n## {e['id']} — {e['name']}\n\n**Invocation:** `{e['invocation']}`  \n"
                f"**Fixture:** {e['fixture']}\n\n**Prompt:** {e['prompt']}\n\n"
                f"**Expected:** {e['expected_output']}\n")
        (DOCS / "evals.md").write_text("\n".join(lines))
        has_evals = True

    nav = build_nav(agents, ordered, knowledge, notes, has_evals)
    (HERE / "mkdocs.yml").write_text((HERE / "mkdocs-base.yml").read_text() + "\n" + nav)

    print(f"wrote {sum(1 for _ in DOCS.rglob('*.md'))} pages under {DOCS}")
    print(f"wrote nav with {len(agents)} agents, {len(ordered)} workflow skills, "
          f"{len(knowledge)} knowledge pages, {len(notes)} notes")


if __name__ == "__main__":
    main()
