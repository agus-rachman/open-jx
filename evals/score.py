#!/usr/bin/env python3
"""Score open-jx side-by-side eval runs recorded from Copilot Cowork.

Copilot Cowork has no public automation API for skills, so a tester runs each
case in the app and saves the assistant's reply as text. This script prepares
the run folder and scores what was recorded.

    python evals/score.py sheet  --run evals/runs/2026-11-pilot
    #   creates the run folder, RUNSHEET.md (what to type and attach) and empty
    #   transcript files: addon/<case>.md, baseline/<case>.md, trigger/<id>.md

    python evals/score.py lint
    #   checks that cases reference real fixtures, packs and pack entry ids

    python evals/score.py score  --run evals/runs/2026-11-pilot [--cases AU-NSW-EXEC-01,...]
    #   scores every non-empty transcript; writes report.md, results.csv and
    #   results.json in the run folder; exit code 1 if a release gate fails

Transcript files: paste the full reply text of every assistant turn in the
conversation (Copilot's "Copy" button keeps Markdown). Empty files count as
"not run" and are excluded from rates but listed in the report.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
CASES = HERE / "cases" / "cases.yaml"
TRIGGER = HERE / "cases" / "trigger.yaml"

GATES = {"trigger": 0.95, "overlay": 0.90, "non_interference": 1.0, "guardrails": 1.0, "court_notes": 1.0}

BRIEF = re.compile(r"\*\*Jurisdiction:\*\*", re.I)
PACK_ID = re.compile(r"\b([a-z]{2}(?:-[a-z]{2,3})?)@\d+\.\d+\.\d+")
OVERLAY = re.compile(r"^#{2,5}\s*Jurisdiction overlay\s*[—–-]", re.I | re.M)
COURT = re.compile(r"\*\*Court AI note:\*\*", re.I)
WITHHELD = re.compile(r"Withheld under open-jx identifier rules", re.I)
SOURCES = re.compile(r"Sources and citation per open-jx pack", re.I)
POSITION = re.compile(r"Position:\s*\**\s*([^*\n]+?)\s*\.?\s*\*\*", re.I)
ADVICE = re.compile(
    r"\b(is|are|was) (validly executed|valid|invalid|enforceable|unenforceable|binding|compliant|non-compliant)\b"
    r"|\byou (must|should)\b|\bin breach\b|\btime-barred\b", re.I)
HEDGE = re.compile(r"\b(whether|not|no view|counsel)\b", re.I)


# ---------------------------------------------------------------- helpers
def load_cases():
    data = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    defaults = data.get("defaults", {})
    out = []
    for c in data["cases"]:
        c = {**{"answers": defaults.get("answers", [])}, **c}
        exp = c.setdefault("expect", {})
        exp.setdefault("no_advice", defaults.get("no_advice", True))
        out.append(c)
    return out


def load_trigger():
    return yaml.safe_load(TRIGGER.read_text(encoding="utf-8"))["prompts"]


def read(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return text or None


def squash(s: str) -> str:
    return re.sub(r"[\s\-]", "", s)


def brief_block(text: str) -> str | None:
    m = BRIEF.search(text)
    if not m:
        return None
    lines = text[m.start():].splitlines()
    return "\n".join(lines[:3])


def first_index(text: str, needles: list[str]) -> int | None:
    """Earliest position of any needle (case-sensitive: markers are output headings)."""
    idx = [text.find(n) for n in needles]
    idx = [i for i in idx if i >= 0]
    return min(idx) if idx else None


def overlay_section(text: str) -> tuple[int | None, str]:
    m = OVERLAY.search(text)
    return (m.start(), text[m.start():]) if m else (None, "")


def court_block(text: str) -> tuple[int | None, str]:
    m = COURT.search(text)
    if not m:
        return None, ""
    return m.start(), "\n".join(text[m.start():].splitlines()[:4])


def advice_hits(section: str) -> list[str]:
    hits = []
    for m in ADVICE.finditer(section):
        before = section[max(0, m.start() - 60):m.start()]
        if not HEDGE.search(before):
            hits.append(m.group(0))
    return hits


class Result:
    def __init__(self, case_id: str):
        self.case_id = case_id
        self.checks: list[dict] = []  # {name, group, ok, soft, detail}

    def add(self, name, group, ok, detail="", soft=False):
        self.checks.append({"name": name, "group": group, "ok": bool(ok), "soft": soft, "detail": detail})

    @property
    def hard_fail(self):
        return [c for c in self.checks if not c["ok"] and not c["soft"]]

    @property
    def status(self):
        if not self.checks:
            return "not run"
        return "pass" if not self.hard_fail else "fail"


# ---------------------------------------------------------------- scoring
def score_case(case: dict, addon: str | None, baseline: str | None) -> Result:
    r = Result(case["id"])
    if addon is None:
        return r
    exp = case["expect"]
    soft = set(exp.get("soft", []))
    orig_markers = (exp.get("original") or {}).get("markers", [])
    orig_idx = first_index(addon, orig_markers) if orig_markers else None

    # Router
    rt = exp.get("router")
    if rt:
        block = brief_block(addon)
        r.add("router.present", "trigger", block is not None, "no '**Jurisdiction:**' brief found" if block is None else "")
        if block is not None:
            found = set(PACK_ID.findall(block))
            if rt.get("no_pack"):
                r.add("router.no_pack", "trigger", "no open-jx pack" in block.lower() and not found, f"brief: {block.splitlines()[0][:120]}")
            if rt.get("packs"):
                need = set(rt["packs"])
                r.add("router.packs", "trigger", need <= found, f"expected {sorted(need)}, found {sorted(found)}")
                if rt.get("exact"):
                    r.add("router.exact", "trigger", found == need, f"extra packs {sorted(found - need)}" if found - need else "")
            for t in rt.get("text", []):
                r.add(f"router.text:{t}", "trigger", t.lower() in block.lower(), f"'{t}' not in brief")
            if orig_idx is not None:
                r.add("router.before_original", "non_interference", addon.find(block[:20]) < orig_idx, "brief appears after the original output")

    # Original output intact
    for mk in orig_markers:
        r.add(f"original.marker:{mk}", "non_interference", mk in addon, f"'{mk}' missing in add-on run")

    # Overlay
    ov = exp.get("overlay")
    ov_idx, ov_text = overlay_section(addon)
    if ov is not None:
        if ov.get("expected"):
            r.add("overlay.present", "overlay", ov_idx is not None, "no '#### Jurisdiction overlay —' section", soft="overlay.present" in soft)
            if ov_idx is not None:
                for ref in ov.get("refs", []):
                    r.add(f"overlay.ref:{ref}", "overlay", ref in ov_text, f"entry {ref} not cited", soft="overlay.refs" in soft)
                for m in ov.get("mentions", []):
                    r.add(f"overlay.mention:{m}", "overlay", m.lower() in ov_text.lower(), f"'{m}' not mentioned", soft="overlay.mentions" in soft)
                if orig_idx is not None:
                    r.add("overlay.after_original", "non_interference", ov_idx > orig_idx, "overlay appears before or inside the original output")
                r.add("overlay.checklist_footer", "overlay", "verify" in ov_text.lower(), "no 'verify against the primary text' footer", soft=True)
        else:
            r.add("overlay.absent", "non_interference", ov_idx is None, "an overlay appeared where none should")

    # Court AI note
    cn = exp.get("court_note")
    c_idx, c_text = court_block(addon)
    if cn:
        r.add("court_note.present", "court_notes", c_idx is not None, "no '**Court AI note:**' block")
        if c_idx is not None:
            for ref in cn.get("refs", []):
                r.add(f"court_note.ref:{ref}", "court_notes", ref in c_text, f"entry {ref} not cited in the note")
            if orig_idx is not None:
                r.add("court_note.before_original", "court_notes", c_idx < orig_idx, "court note appears after the original output")

    if exp.get("sources_line"):
        r.add("sources_line", "overlay", bool(SOURCES.search(addon)), "no 'Sources and citation per open-jx pack' line", soft="sources_line" in soft)
    if exp.get("cite_regex"):
        r.add("cite_regex", "overlay", re.search(exp["cite_regex"], addon) is not None, f"no match for /{exp['cite_regex']}/", soft="cite_regex" in soft)
    for item in exp.get("contains", []):
        options = item if isinstance(item, list) else [item]
        found = any(o.lower() in addon.lower() for o in options)
        label = " | ".join(options)
        r.add(f"contains:{label}", "overlay", found, f"none of [{label}] found", soft="contains" in soft)

    # Guardrails
    if exp.get("withheld"):
        r.add("withheld_line", "guardrails", bool(WITHHELD.search(addon)), "no 'Withheld under open-jx identifier rules' line", soft="withheld" in soft)
    for f in exp.get("forbidden", []):
        leaked = f.lower() in addon.lower() or (any(ch.isdigit() for ch in f) and squash(f) in squash(addon))
        r.add(f"forbidden:{f}", "guardrails", not leaked, f"'{f}' reproduced")
    for rx in exp.get("forbidden_regex", []):
        m = re.search(rx, addon, re.M)
        r.add(f"forbidden_regex:{rx}", "guardrails", m is None, f"matched: {m.group(0)!r}" if m else "")
    if exp.get("no_advice"):
        hits = advice_hits(ov_text) + advice_hits(c_text)
        r.add("no_advice", "guardrails", not hits, f"advice wording: {hits[:3]}")

    # Parity with baseline
    parity = exp.get("parity", "none")
    if parity != "none":
        if baseline is None:
            r.add(f"parity.{parity}", "non_interference", False, "baseline transcript not recorded", soft=True)
        elif parity == "position":
            pa, pb = POSITION.search(addon), POSITION.search(baseline)
            same = bool(pa and pb and pa.group(1).strip().lower() == pb.group(1).strip().lower())
            r.add("parity.position", "non_interference", same,
                  f"baseline '{pb.group(1) if pb else None}' vs add-on '{pa.group(1) if pa else None}'")
        elif parity == "markers":
            missing = [m for m in orig_markers if m not in baseline]
            r.add("parity.markers", "non_interference", not missing,
                  f"baseline lacks {missing} — check the case runs the same skill in both modes" if missing else "")
        if baseline is not None and BRIEF.search(baseline):
            r.add("baseline.clean", "non_interference", False, "baseline run shows a jurisdiction brief: open-jx was not switched off")
    return r


def score_trigger(item: dict, text: str | None) -> dict:
    if text is None:
        return {"id": item["id"], "status": "not run", "detail": ""}
    expect = item["expect"]
    block = brief_block(text)
    found = set(PACK_ID.findall(block or ""))
    if expect == "none":
        ok = not found
        detail = f"found {sorted(found)}" if found else ""
    elif expect == "no_pack":
        ok = bool(block) and "no open-jx pack" in block.lower() and not found
        detail = "" if ok else "expected a 'no open-jx pack' brief"
    elif expect == "ask":
        ok = "which jurisdiction" in text.lower() and not found
        detail = "" if ok else f"expected a question; found {sorted(found) or 'no question'}"
    else:
        ok = found == set(expect)
        detail = "" if ok else f"expected {sorted(expect)}, found {sorted(found) or 'no brief'}"
    return {"id": item["id"], "status": "pass" if ok else "fail", "detail": detail}


def rate(ok, total):
    return (ok / total) if total else None


# ---------------------------------------------------------------- commands
def cmd_sheet(run: Path):
    cases, trig = load_cases(), load_trigger()
    for sub in ("addon", "baseline", "trigger"):
        (run / sub).mkdir(parents=True, exist_ok=True)
    meta = run / "run.yaml"
    if not meta.exists():
        meta.write_text(yaml.safe_dump({
            "run_id": run.name, "date": dt.date.today().isoformat(), "tester": "", "tenant": "",
            "platform": "Microsoft 365 Copilot Cowork", "legal_for_cowork_version": "", "open_jx_version": "0.1.0",
            "custom_instructions": "pilot snippet from docs/COPILOT-SETUP.md, without a default jurisdiction",
            "notes": ""}, sort_keys=False))
    for c in cases:
        for sub in ("addon", "baseline"):
            p = run / sub / f"{c['id']}.md"
            if not p.exists():
                p.write_text("")
    for t in trig:
        p = run / "trigger" / f"{t['id']}.md"
        if not p.exists():
            p.write_text("")
    lines = [f"# Run sheet — {run.name}", "",
             "Fixtures are in `evals/fixtures/`. Start a **new conversation for every run**.",
             "", "- **baseline**: in Sources & Skills, switch the open-jx plugin OFF for the conversation.",
             "- **addon**: switch open-jx ON. Legal for Cowork skills are on in both.",
             "- Answer any question card with the case's scripted answers, in order.",
             "- Paste every assistant reply in the conversation into the matching file, in order.", "",
             "## Side-by-side cases", ""]
    for c in cases:
        lines += [f"### {c['id']} — {c['title']}", "",
                  f"- Skill under test: `{c['original_skill']}`",
                  f"- Attach: {', '.join(c['fixtures']) or 'nothing'}",
                  f"- Prompt: `{c['prompt']}`",
                  f"- Scripted answers: {'; '.join(c['answers'])}",
                  f"- Save to: `baseline/{c['id']}.md` and `addon/{c['id']}.md`", ""]
    lines += ["## Trigger set (open-jx ON, no files)", "", "| ID | Prompt | Expect |", "| --- | --- | --- |"]
    for t in trig:
        lines.append(f"| {t['id']} | {t['prompt']} | {t['expect']} |")
    (run / "RUNSHEET.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"run folder ready: {run} ({len(cases)} cases x 2 modes, {len(trig)} trigger prompts)")


def cmd_score(run: Path, only: set[str] | None):
    cases = [c for c in load_cases() if not only or c["id"] in only]
    results = [score_case(c, read(run / "addon" / f"{c['id']}.md"), read(run / "baseline" / f"{c['id']}.md")) for c in cases]
    trig = [score_trigger(t, read(run / "trigger" / f"{t['id']}.md")) for t in load_trigger()] if not only else []

    groups: dict[str, list[bool]] = {g: [] for g in GATES}
    for r in results:
        for ch in r.checks:
            if ch["soft"]:
                continue
            groups.setdefault(ch["group"], []).append(ch["ok"])
    trig_run = [t for t in trig if t["status"] != "not run"]
    trig_ok = sum(t["status"] == "pass" for t in trig_run)
    case_router = [ch["ok"] for r in results for ch in r.checks if ch["group"] == "trigger" and not ch["soft"]]
    metrics = {
        "trigger": rate(trig_ok + sum(case_router), len(trig_run) + len(case_router)),
        "overlay": rate(sum(groups["overlay"]), len(groups["overlay"])),
        "non_interference": rate(sum(groups["non_interference"]), len(groups["non_interference"])),
        "guardrails": rate(sum(groups["guardrails"]), len(groups["guardrails"])),
        "court_notes": rate(sum(groups["court_notes"]), len(groups["court_notes"])),
    }
    gates = {k: (None if metrics[k] is None else metrics[k] >= v) for k, v in GATES.items()}
    ran = [r for r in results if r.status != "not run"]

    # report.md
    def pct(x):
        return "—" if x is None else f"{x:.0%}"
    L = [f"# open-jx eval report — {run.name}", "", f"Scored {dt.datetime.now():%Y-%m-%d %H:%M}.", "",
         "| Measure | Score | Gate | Result |", "| --- | --- | --- | --- |"]
    for k, g in GATES.items():
        L.append(f"| {k.replace('_', ' ')} | {pct(metrics[k])} | {g:.0%} | {'—' if gates[k] is None else ('pass' if gates[k] else 'FAIL')} |")
    L += ["", f"Cases: {sum(r.status == 'pass' for r in ran)} passed, {sum(r.status == 'fail' for r in ran)} failed, "
          f"{len(results) - len(ran)} not run. Trigger prompts: {trig_ok}/{len(trig_run)} passed, {len(trig) - len(trig_run)} not run.", "",
          "## Cases", "", "| Case | Result | Failed checks | Warnings |", "| --- | --- | --- | --- |"]
    for r in results:
        fails = "; ".join(f"{c['name']} ({c['detail']})" if c["detail"] else c["name"] for c in r.hard_fail)
        warns = "; ".join(f"{c['name']} ({c['detail']})" if c["detail"] else c["name"] for c in r.checks if c["soft"] and not c["ok"])
        L.append(f"| {r.case_id} | {r.status} | {fails or '—'} | {warns or '—'} |")
    if trig:
        L += ["", "## Trigger set", "", "| ID | Result | Detail |", "| --- | --- | --- |"]
        L += [f"| {t['id']} | {t['status']} | {t['detail'] or '—'} |" for t in trig]
    (run / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    with (run / "results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "check", "group", "ok", "soft", "detail"])
        for r in results:
            for c in r.checks:
                w.writerow([r.case_id, c["name"], c["group"], c["ok"], c["soft"], c["detail"]])
        for t in trig:
            w.writerow([t["id"], "trigger", "trigger", t["status"] == "pass", False, t["detail"]])
    (run / "results.json").write_text(json.dumps({
        "metrics": metrics, "gates": gates,
        "cases": [{"id": r.case_id, "status": r.status, "checks": r.checks} for r in results],
        "trigger": trig}, indent=2), encoding="utf-8")

    print("\n".join(L[:9 + len(GATES)]))
    print(f"\nreport: {run / 'report.md'}")
    failed_gate = any(v is False for v in gates.values())
    return 1 if failed_gate else 0


def cmd_lint() -> int:
    """Check that cases point at real fixtures, packs and pack entry ids."""
    sys.path.insert(0, str(HERE.parent / "tools"))
    from validate_packs import load_yaml  # noqa: E402
    packs_dir = HERE.parent / "packs"
    packs = {p.name for p in packs_dir.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))}
    ids = set()
    for f in packs_dir.glob("*/*.yaml"):
        if f.parent.name.startswith("_"):
            continue
        data = load_yaml(f) or {}
        for v in data.values() if isinstance(data, dict) else []:
            if isinstance(v, list):
                ids |= {e["id"] for e in v if isinstance(e, dict) and "id" in e}
    problems = []
    cases = load_cases()
    seen = set()
    for c in cases:
        if c["id"] in seen:
            problems.append(f"{c['id']}: duplicate case id")
        seen.add(c["id"])
        for fx in c["fixtures"]:
            if not (HERE / "fixtures" / fx).exists():
                problems.append(f"{c['id']}: fixture {fx} missing (run evals/fixtures/make_fixtures.py)")
        exp = c["expect"]
        for p in (exp.get("router") or {}).get("packs", []):
            if p not in packs:
                problems.append(f"{c['id']}: router pack {p} does not exist")
        refs = (exp.get("overlay") or {}).get("refs", []) + (exp.get("court_note") or {}).get("refs", [])
        for ref in refs:
            if ref not in ids:
                problems.append(f"{c['id']}: pack entry {ref} does not exist")
    for t in load_trigger():
        if isinstance(t["expect"], list):
            for p in t["expect"]:
                if p not in packs:
                    problems.append(f"{t['id']}: pack {p} does not exist")
    for p in problems:
        print("ERROR", p)
    print(f"{len(cases)} cases, {len(load_trigger())} trigger prompts, {len(ids)} pack entry ids; {len(problems)} problem(s)")
    return 1 if problems else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("sheet", help="create a run folder and run sheet")
    s1.add_argument("--run", type=Path, required=True)
    s2 = sub.add_parser("score", help="score a recorded run")
    s2.add_argument("--run", type=Path, required=True)
    s2.add_argument("--cases", help="comma-separated case ids to score")
    sub.add_parser("lint", help="check cases against fixtures and packs")
    a = ap.parse_args(argv)
    if a.cmd == "lint":
        return cmd_lint()
    if a.cmd == "sheet":
        cmd_sheet(a.run)
        return 0
    return cmd_score(a.run, set(a.cases.split(",")) if a.cases else None)


if __name__ == "__main__":
    sys.exit(main())
