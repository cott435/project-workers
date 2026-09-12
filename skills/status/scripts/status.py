#!/usr/bin/env python3
"""Print where every package and section stands, derived from docs/ and the code.

Usage:  python3 status.py [pkg] [--gate]

Nothing here is written down by anyone; it is all derived: a package is planned when its
contract exists, built when every section has a README, shipped when interface.md exists. A
section is reviewed when a review file is dated on or after its README's last change.
`--gate` exits 1 when the named package fails /finalize-package's preconditions.
"""

from __future__ import annotations

import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
DOCS = ROOT / "docs"


def table_rows(md: str, must_have: tuple[str, ...]) -> list[dict[str, str]]:
    """Return the rows of the first markdown table whose header contains every name in must_have."""
    lines = md.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        header = [c.strip().lower() for c in line.strip("|").split("|")]
        if all(any(m in h for h in header) for m in must_have) and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            rows = []
            for row in lines[i + 2:]:
                if not row.startswith("|"):
                    break
                cells = [c.strip() for c in row.strip("|").split("|")]
                rows.append({h: (cells[k] if k < len(cells) else "") for k, h in enumerate(header)})
            return rows
    return []


def col(row: dict[str, str], name: str) -> str:
    """Fetch a cell by a loose header match, stripping backticks."""
    for h, v in row.items():
        if name in h:
            return v.strip("`* ")
    return ""


def last_change(path: Path) -> dt.date | None:
    """Date a file last changed: git commit date if committed, else mtime."""
    if not path.exists():
        return None
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)], capture_output=True, text=True, cwd=ROOT)
        if out.stdout.strip():
            return dt.date.fromisoformat(out.stdout.strip())
    except (OSError, ValueError):
        pass
    return dt.date.fromtimestamp(path.stat().st_mtime)


def latest_review(stem: str) -> tuple[dt.date | None, str]:
    """Newest docs/reviews/<date>-<stem>.md → (date, verdict)."""
    best: tuple[dt.date, Path] | None = None
    for f in (DOCS / "reviews").glob(f"*-{stem}.md"):
        m = re.match(r"(\d{4}-\d{2}-\d{2})-", f.name)
        if m:
            d = dt.date.fromisoformat(m.group(1))
            if best is None or d > best[0]:
                best = (d, f)
    if not best:
        return None, ""
    v = re.search(r"^Verdict:\s*(.+)$", best[1].read_text(), re.M)
    return best[0], (v.group(1).strip() if v else "?")


def open_followups(target: str) -> tuple[int, int]:
    """(open items addressed to target, of which review-sourced)."""
    f = DOCS / "followups.md"
    if not f.exists():
        return 0, 0
    total = crit = 0
    for line in f.read_text().splitlines():
        if line.startswith("- [ ]") and re.match(rf"- \[ \]\s*{re.escape(target)}\s*:", line):
            total += 1
            if "review " in line:
                crit += 1
    return total, crit


def markers(path: Path) -> int:
    """Count TODO(decision ...) markers under a path."""
    if not path.exists():
        return 0
    return sum(len(re.findall(r"TODO\(decision", p.read_text(errors="ignore"))) for p in path.rglob("*.py"))


def packages() -> list[tuple[str, Path]]:
    arch = DOCS / "architecture.md"
    out: list[tuple[str, Path]] = []
    if arch.exists():
        for row in table_rows(arch.read_text(), ("package", "path")):
            name, path = col(row, "package"), col(row, "path")
            if name and not name.startswith("-"):
                out.append((name, ROOT / (path or ".")))
    if not out:
        out = [(d.name, ROOT / "packages" / d.name) for d in sorted((DOCS / "packages").glob("*")) if d.is_dir()]
    return out


def package_report(pkg: str, pkg_path: Path) -> tuple[list[str], list[str]]:
    """Lines to print and a list of finalize-gate failures."""
    pdocs = DOCS / "packages" / pkg
    have = {n: (pdocs / f"{n}.md").exists() for n in ("contract", "integration", "surface", "interface")}
    status = "shipped" if have["interface"] else ("planned" if have["contract"] else "unplanned")
    lines = [f"\n## {pkg}  —  {status}   " + "  ".join(f"{k}.md {'✓' if v else '·'}" for k, v in have.items())]
    fails: list[str] = []
    if not have["contract"]:
        return lines + ["  (no contract.md — run /plan-package)"], [f"{pkg}: no contract.md"]
    if not have["surface"]:
        fails.append(f"{pkg}: no surface.md")
    rows = table_rows((pdocs / "contract.md").read_text(), ("section", "path"))
    lines.append("  section              design  built  reviewed-since-build   open followups  markers")
    all_built = True
    for row in rows:
        sec = col(row, "section")
        if not sec:
            continue
        spath = ROOT / col(row, "path") if col(row, "path") else pkg_path / "src" / pkg / sec
        readme = spath / "README.md"
        design = (pdocs / "design" / f"{sec}.md").exists()
        built = readme.exists()
        all_built &= built
        rdate, verdict = latest_review(f"{pkg}-{sec}")
        bdate = last_change(readme)
        reviewed = bool(rdate and bdate and rdate >= bdate)
        fu, crit = open_followups(f"{pkg}/{sec}")
        mk = markers(spath)
        rev_txt = f"{'✓' if reviewed else '·'} {rdate or '—'} {verdict}".strip()
        lines.append(f"  {sec:<20} {'✓' if design else '·':^6} {'✓' if built else '·':^6}  {rev_txt:<22} {fu:>3} ({crit} review)  {mk:>5}")
        if not built:
            fails.append(f"{pkg}/{sec}: no README (unbuilt)")
        elif not reviewed:
            fails.append(f"{pkg}/{sec}: not reviewed since last build")
        if crit:
            fails.append(f"{pkg}/{sec}: {crit} open review-sourced follow-up(s)")
    sfu, _ = open_followups(f"{pkg}/surface")
    prd, pverdict = latest_review(f"{pkg}-package")
    lines.append(f"  surface: open followups {sfu}; package review {prd or '—'} {pverdict}")
    if all_built and status == "planned":
        lines[0] = lines[0].replace("planned", "built, not finalized")
    return lines, fails


def repo_report() -> list[str]:
    lines = ["\n## repo"]
    dec = DOCS / "decisions.md"
    if dec.exists():
        text = dec.read_text()
        entries = re.split(r"^## D", text, flags=re.M)[1:]
        opn = sum(1 for e in entries if re.search(r"^Status:\s*(open|deferred)", e, re.M))
        decided_unapplied = [e.split()[0] for e in entries if re.search(r"^Status:\s*decided", e, re.M) and not re.search(r"^Applied:\s*\S", e, re.M)]
        lines.append(f"  decisions: {len(entries)} total, {opn} open/deferred, decided without Applied: {', '.join('D' + d for d in decided_unapplied) or 'none'}")
    else:
        lines.append("  decisions: no ledger")
    plans = [p.parent.name for p in (DOCS / "plans").glob("*/integration.md")]
    synced = (DOCS / "plans" / "synced.md").read_text() if (DOCS / "plans" / "synced.md").exists() else ""
    unsynced = [s for s in plans if s not in synced]
    lines.append(f"  plans: {len(plans)} with integration.md, unsynced: {', '.join(unsynced) or 'none'}")
    fu = DOCS / "followups.md"
    if fu.exists():
        lines.append(f"  open followups: {sum(1 for l in fu.read_text().splitlines() if l.startswith('- [ ]'))}")
    return lines


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    gate = "--gate" in sys.argv
    only = args[0] if args else None
    if not DOCS.exists():
        print("no docs/ directory here — run from the repo root")
        return 2
    all_fails: list[str] = []
    for pkg, path in packages():
        if only and pkg != only:
            continue
        lines, fails = package_report(pkg, path)
        print("\n".join(lines))
        all_fails += fails
    if not only:
        print("\n".join(repo_report()))
    if gate:
        print("\nfinalize gate:", "PASS" if not all_fails else "FAIL")
        for f in all_fails:
            print("  -", f)
        return 1 if all_fails else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
