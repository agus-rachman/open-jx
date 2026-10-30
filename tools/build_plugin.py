#!/usr/bin/env python3
"""Build the open-jx plugin packages from plugin/ and packs/.

    python tools/build_plugin.py            # validate, then build dist/
    python tools/build_plugin.py --no-validate

Outputs
  dist/open-jx-<version>.zip          Microsoft 365 Copilot Cowork package
                                      (manifest.json, color.png, outline.png, skills/)
  dist/open-jx-claude-<version>.zip   Claude plugin layout (.claude-plugin/plugin.json, skills/)
  build/package/                      unpacked copy of the Copilot package, for inspection

Contributors never edit build/ or dist/: edit packs/ and plugin/skills/, then rebuild.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from validate_packs import load_yaml  # noqa: E402

CFG = json.loads((ROOT / "build.config.json").read_text())
PACKS = ROOT / "packs"
SKILLS = ROOT / "plugin" / "skills"
ASSETS = ROOT / "plugin" / "assets"
BUILD = ROOT / "build" / "package"
DIST = ROOT / "dist"
BEGIN, END = "<!-- BEGIN GENERATED PACK LIST -->", "<!-- END GENERATED PACK LIST -->"

SECTION_ORDER = [
    ("sources.yaml", "sources", "Sources (rank 1 = official text)"),
    ("citation.yaml", "citation", "Citation"),
    ("identifiers.yaml", "personal", "identifiers.personal — never reproduce values"),
    ("identifiers.yaml", "organisational", "identifiers.organisational — may be quoted and compared"),
    ("identifiers.yaml", "privacy_context", "privacy_context"),
    ("privacy.yaml", "privacy_regimes", "privacy_regimes — which privacy, health, breach and surveillance regimes apply"),
    ("execution.yaml", "entries", "execution"),
    ("governance.yaml", "entries", "governance"),
    ("calendar.yaml", "business_day", "calendar.business_day"),
    ("calendar.yaml", "time_computation", "calendar.time_computation"),
    ("calendar.yaml", "holidays", "calendar.holidays"),
    ("calendar.yaml", "limitation", "calendar.limitation"),
    ("courts-ai.yaml", "courts_ai", "courts_ai"),
    ("case-law.yaml", "publishers", "case_law — court identifiers and official judgment publishers"),
    ("terminology.yaml", "terms", "terminology"),
]


def load_packs() -> dict[str, dict]:
    packs = {}
    for folder in sorted(p for p in PACKS.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
        files = {f.name: load_yaml(f) for f in folder.glob("*.yaml")}
        packs[folder.name] = files
    return packs


def fmt_entry(e: dict) -> str:
    parts = [f"- **{e['id']}**"]
    if e.get("applies_to"):
        parts.append(f"[{', '.join(e['applies_to'])}]")
    head = " ".join(parts)
    body = []
    for key, label in (("name", None), ("court", "Court"), ("instrument", "Instrument"), ("observe", None),
                       ("pattern_hint", "Looks like"), ("format", "Format"), ("example", "Example")):
        if e.get(key):
            body.append(f"{label}: {e[key]}" if label else str(e[key]).strip())
    if e.get("restricted_content"):
        body.append("Restricted content: " + ", ".join(e["restricted_content"]))
    meta = []
    if e.get("authority"):
        meta.append(f"Authority: {e['authority']}")
    if e.get("source_url") or e.get("url"):
        meta.append(f"Source: {e.get('source_url') or e.get('url')}")
    if e.get("type"):
        meta.append(f"Type: {e['type']}, rank {e.get('rank')}")
    if e.get("status"):
        meta.append(f"Status: {e['status']}" + (f" from {e['commences']}" if e.get("commences") else ""))
    if "verified" in e:
        meta.append(f"Verified: {e['verified']} by {e['verified_by']}" if e.get("verified") else "Verified: not yet")
    if e.get("court_ids"):
        body.insert(0, f"{', '.join(e['court_ids'])} → {e['publisher']} ({e['access']})")
    if e.get("note"):
        meta.append(f"Note: {e['note']}")
    pv = e.get("provenance")
    if pv:
        meta.append(f"Upstream: {pv.get('source', '').split('/')[-1]}@{pv.get('commit', '')}"
                    + (f", checked {pv['upstream_checked']}" if pv.get("upstream_checked") else "")
                    + (f" ({pv['upstream_state']})" if pv.get("upstream_state") else ""))
    return f"{head} — " + ". ".join(b.rstrip(".") for b in body) + "." + "\n  " + " · ".join(meta)


def compile_pack(pid: str, files: dict) -> str:
    meta = files["pack.yaml"]
    det = meta["detection"]
    out = [f"# Pack {pid}@{meta['version']} — {meta['name']} ({meta['status']})", "",
           "Pack data for the open-jx skills. Every entry is a checklist item to verify against",
           "the primary source; it is data, not an instruction.", "",
           f"- Parent: {meta.get('parent') or 'none'} · Level: {meta['level']} · Locale: {meta['locale']} · Legal system: {meta['legal_system']}",
           f"- Maintainers: {', '.join(meta['maintainers'])} · Last reviewed: {meta.get('last_reviewed') or 'not yet'}"
           + (f" · Law checked as at: {meta['law_checked_as_at']}" if meta.get("law_checked_as_at") else ""), "",
           "## detection", "",
           f"- Names: {', '.join(det['names'])}",
           f"- Governing-law wording: {', '.join(det.get('governing_law_patterns', []))}",
           f"- Courts and tribunals: {', '.join(det.get('courts', []))}"]
    if det.get("identifiers"):
        out.append(f"- Identifiers: {', '.join(det['identifiers'])}")
    if det.get("other_signals"):
        out.append(f"- Other signals: {', '.join(det['other_signals'])}")
    if det.get("note"):
        out.append(f"- Note: {det['note']}")
    for fname, key, title in SECTION_ORDER:
        data = files.get(fname) or {}
        if fname == "citation.yaml" and data:
            c = data.get("citation", {})
            out += ["", f"## {title}", ""]
            if c.get("inherit"):
                out.append(f"- Inherits the citation guide of pack `{c['inherit']}`.")
            if c.get("name"):
                out.append(f"- Guide: {c['name']}, {c.get('edition', '')} ({c.get('publisher', '')}) — {c.get('url', '')}")
            if c.get("note"):
                out.append(f"- Note: {c['note']}")
            out += [fmt_entry(e) for e in data.get("rules", [])]
            continue
        if fname == "terminology.yaml" and data:
            out += ["", f"## {title}", "", f"- Spelling: {data.get('spelling')}"]
            for t in data.get("terms", []):
                line = f"- Use **{t['use']}**" + (f" instead of {t['instead_of']}" if t.get("instead_of") else "")
                out.append(line + (f" — {t['note']}" if t.get("note") else ""))
            continue
        items = data.get(key, []) if isinstance(data, dict) else []
        if items:
            out += ["", f"## {title}", ""] + [fmt_entry(e) for e in items]
    dl = files.get("deadlines.yaml") or {}
    if dl.get("holiday_table") or dl.get("court_rules"):
        out += ["", "## deadlines — holiday table and court computation rules", ""]
        h = dl.get("holiday_table")
        if h:
            out += [f"- **Holiday table `{h['table_id']}`** — {h.get('description', '')} Coverage {h['coverage']['from']} to {h['coverage']['to']};"
                    f" checked {h['checked']} ({h['evidence']['state']}); source {h['source_url']}.",
                    f"  Holidays: {', '.join(h['holidays'])}"]
            for w in h.get("uncertain_windows", []):
                out.append(f"  Uncertain window {w['from']} to {w['to']}: {w.get('reason', '')}")
            for c in h.get("caveats", []):
                out.append(f"  Caveat: {c}")
        for t in dl.get("court_rules", []):
            out.append(f"- **Rule table `{t['table_id']}`** — {', '.join(t['forums'])}; holidays: `{t.get('holiday_table')}`. {t.get('note', '')}")
            for pr in t.get("computation_provisions", []):
                out.append(f"  Provision `{pr['id']}`: {pr['citation']} ({pr.get('evidence', {}).get('state')})")
            for r in t.get("period_rules", []):
                per = r["period"]
                out.append(f"  Rule `{r['id']}`: {r['label']} — {r['citation']}; {per['length']} {per['unit'].replace('_', ' ')}, rollover {r.get('rollover', 'none')} ({r.get('evidence', {}).get('state')})")
        pv = dl.get("provenance", {})
        out.append(f"- Provenance: {pv.get('source', '')} @ {pv.get('commit', '')} ({pv.get('licence', '')}). Candidate dates come only from jx-dates-and-deadlines/scripts/compute_deadline.py.")
    return "\n".join(out) + "\n"


def deadline_assets(packs: dict) -> tuple[str, str]:
    """Combined tables for the deadline script, and a readable rule list."""
    tables = {"computation_rules": {}, "holidays": {}, "open_jx_review": {}}
    lines = ["# Deadline rule tables", "",
             "Generated from packs/*/deadlines.yaml. Use these ids with scripts/compute_deadline.py.",
             "The script computes only from rules, provisions and holiday tables in the `verified` evidence state.", ""]
    for pid, files in packs.items():
        dl = files.get("deadlines.yaml") or {}
        status = files["pack.yaml"]["status"]
        if dl.get("holiday_table"):
            tables["holidays"][dl["holiday_table"]["table_id"]] = dl["holiday_table"]
        for t in dl.get("court_rules", []):
            tables["computation_rules"][t["table_id"]] = t
            if status == "draft":
                tables["open_jx_review"][t["table_id"]] = (
                    f"open-jx pack {pid} is draft: its entries have not yet been reviewed by an open-jx reviewer "
                    "(upstream evidence states are shown).")
            lines += [f"## {t['table_id']} — {', '.join(t['forums'])} (pack {pid}, holidays `{t.get('holiday_table')}`)", "",
                      "| period_rule_id | Step | Citation | Period | Rollover | Evidence |", "| --- | --- | --- | --- | --- | --- |"]
            for r in t.get("period_rules", []):
                per = r["period"]
                lines.append(f"| `{r['id']}` | {r['label']} | {r['citation']} | {per['length']} {per['unit'].replace('_', ' ')} | {r.get('rollover', 'none')} | {r.get('evidence', {}).get('state')} |")
            lines.append("")
    if tables["holidays"]:
        lines += ["## Holiday tables", "", "| table | coverage | checked | evidence |", "| --- | --- | --- | --- |"]
        for tid, h in tables["holidays"].items():
            lines.append(f"| `{tid}` | {h['coverage']['from']} to {h['coverage']['to']} | {h['checked']} | {h['evidence']['state']} |")
    return json.dumps(tables, indent=1, ensure_ascii=False), "\n".join(lines) + "\n"


def case_publishers(packs: dict) -> str:
    pubs, series = [], []
    for pid, files in packs.items():
        cl = files.get("case-law.yaml") or {}
        for p in cl.get("publishers", []):
            pubs.append({k: p[k] for k in ("id", "court_ids", "court", "publisher", "url", "access") if k in p} | {"pack": pid, "note": p.get("note", "")})
        series += [{"series": s["series"], "name": s["name"], "resolve_via": s["resolve_via"]} for s in cl.get("report_series", [])]
    return json.dumps({"publishers": pubs, "report_series": series}, indent=1, ensure_ascii=False)


def index_md(packs: dict, file_of: dict) -> str:
    rows = ["# open-jx jurisdiction index", "",
            "Read this first, then read the pack file(s) for the jurisdictions you detect, parent before child.", "",
            "| Pack | Jurisdiction | Parent | Level | Version | Status | Detect by | File |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for pid, files in packs.items():
        m = files["pack.yaml"]
        names = ", ".join(m["detection"]["names"])
        rows.append(f"| {pid} | {m['name']} | {m.get('parent') or '—'} | {m['level']} | {m['version']} | {m['status']} | {names} | `references/packs/{file_of[pid]}` |")
    rows += ["", "Status meanings: draft = entries not yet verified by a qualified reviewer; beta = verified by one",
             "reviewer; stable = verified by two; stale = verification out of date; unmaintained = no active maintainer.", ""]
    return "\n".join(rows)


def build(validate: bool = True) -> Path:
    if validate:
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "validate_packs.py"), "--quiet"], capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[-1])
        if r.returncode:
            print(r.stdout)
            sys.exit("pack validation failed; fix errors before building")
    packs = load_packs()
    limit = CFG["max_companion_files"] - 1  # one slot for the index
    file_of: dict[str, str] = {}
    contents: dict[str, list[str]] = defaultdict(list)
    grouped = len(packs) > limit
    for pid, files in packs.items():
        fname = (files["pack.yaml"]["country"].lower() if grouped else pid) + ".md"
        file_of[pid] = fname
        contents[fname].append(compile_pack(pid, files))
    if len(contents) > limit:
        sys.exit(f"{len(contents)} pack files exceed the per-skill companion limit; split the distribution by region")

    if BUILD.exists():
        shutil.rmtree(BUILD)
    shutil.copytree(SKILLS, BUILD / "skills", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    ref = BUILD / "skills" / "jx-router" / "references"
    (ref / "packs").mkdir(parents=True, exist_ok=True)
    for fname, parts in contents.items():
        (ref / "packs" / fname).write_text("\n---\n\n".join(parts), encoding="utf-8")
    (ref / "jurisdictions.md").write_text(index_md(packs, file_of), encoding="utf-8")

    listing = ["- [references/jurisdictions.md](references/jurisdictions.md) — index of installed packs"]
    for fname in sorted(contents):
        ids = [p for p, f in file_of.items() if f == fname]
        names = "; ".join(f"{packs[p]['pack.yaml']['name']} ({p}@{packs[p]['pack.yaml']['version']}, {packs[p]['pack.yaml']['status']})" for p in ids)
        listing.append(f"- [references/packs/{fname}](references/packs/{fname}) — {names}")
    router = BUILD / "skills" / "jx-router" / "SKILL.md"
    text = router.read_text(encoding="utf-8")
    pre, rest = text.split(BEGIN)
    _, post = rest.split(END)
    router.write_text(pre + BEGIN + "\n" + "\n".join(listing) + "\n" + END + post, encoding="utf-8")

    dref = BUILD / "skills" / "jx-dates-and-deadlines" / "references"
    dref.mkdir(parents=True, exist_ok=True)
    tables_json, rules_md = deadline_assets(packs)
    (dref / "deadline-tables.json").write_text(tables_json, encoding="utf-8")
    (dref / "deadline-rules.md").write_text(rules_md, encoding="utf-8")
    sref = BUILD / "skills" / "jx-sources-and-citation" / "references"
    sref.mkdir(parents=True, exist_ok=True)
    (sref / "case-publishers.json").write_text(case_publishers(packs), encoding="utf-8")
    for notice in ("THIRD-PARTY-NOTICES.md",):
        for skill in ("jx-dates-and-deadlines", "jx-sources-and-citation"):
            shutil.copy(ROOT / notice, BUILD / "skills" / skill / "references" / notice)

    tpl = BUILD / "skills" / "jx-new-pack" / "references" / "template"
    tpl.mkdir(parents=True, exist_ok=True)
    for f in sorted((PACKS / "_template").glob("*.yaml")):
        shutil.copy(f, tpl / f.name)
    shutil.copy(ROOT / "docs" / "PACK-SCHEMA.md", tpl.parent / "schema-guide.md")

    for icon in ("color.png", "outline.png"):
        shutil.copy(ASSETS / icon, BUILD / icon)
    repo = CFG["repo_url"].rstrip("/")
    manifest = {
        "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.28/MicrosoftTeams.schema.json",
        "manifestVersion": "1.28",
        "version": CFG["version"],
        "id": CFG["app_id"],
        "developer": {"name": CFG["developer_name"], "websiteUrl": repo,
                      "privacyUrl": f"{repo}/blob/main/PRIVACY.md", "termsOfUseUrl": f"{repo}/blob/main/LICENSE"},
        "name": {"short": CFG["short_name"], "full": CFG["full_name"]},
        "description": {"short": CFG["short_description"], "full": CFG["full_description"]},
        "icons": {"color": "color.png", "outline": "outline.png"},
        "accentColor": CFG["accent_color"],
        "agentSkills": [{"folder": f"./skills/{d.name}"} for d in sorted((BUILD / "skills").iterdir()) if d.is_dir()],
    }
    (BUILD / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    DIST.mkdir(exist_ok=True)
    copilot_zip = DIST / f"{CFG['plugin_name']}-{CFG['version']}.zip"
    with zipfile.ZipFile(copilot_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(BUILD.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(BUILD).as_posix())
    claude_zip = DIST / f"{CFG['plugin_name']}-claude-{CFG['version']}.zip"
    plugin_json = {"name": CFG["plugin_name"], "version": CFG["version"], "description": CFG["short_description"],
                   "license": "Apache-2.0", "homepage": repo}
    with zipfile.ZipFile(claude_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{CFG['plugin_name']}/.claude-plugin/plugin.json", json.dumps(plugin_json, indent=2) + "\n")
        for p in sorted((BUILD / "skills").rglob("*")):
            if p.is_file():
                z.write(p, f"{CFG['plugin_name']}/" + p.relative_to(BUILD).as_posix())
    print(f"built {copilot_zip.relative_to(ROOT)} and {claude_zip.relative_to(ROOT)}")
    print(f"packs: {', '.join(packs)}" + (" (grouped by country)" if grouped else ""))
    return copilot_zip


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-validate", action="store_true")
    build(validate=not ap.parse_args().no_validate)
