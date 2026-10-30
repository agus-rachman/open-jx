#!/usr/bin/env python3
"""Validate open-jx jurisdiction packs.

Usage:
    python tools/validate_packs.py                 # all packs under packs/
    python tools/validate_packs.py packs/sg        # one or more pack folders
    python tools/validate_packs.py --strict        # warnings fail too
    python tools/validate_packs.py --include-template

Checks: schema per file, required files, id and parent consistency, unique
entry ids, citations on every legal entry, verification required for beta and
stable packs, freshness, advice language, instruction-like text, file types.
Exit code 1 on any error (or any warning with --strict).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
SCHEMA = json.loads((ROOT / "schema" / "pack.schema.json").read_text())
FILE_MAP = SCHEMA["x-file-map"]
REQUIRED_FILES = ["pack.yaml", "sources.yaml", "citation.yaml", "identifiers.yaml", "calendar.yaml"]
ALLOWED_SUFFIXES = {".yaml", ".yml", ".md"}

ADVICE = re.compile(
    r"\b(is|are) (validly executed|valid|invalid|enforceable|unenforceable|binding|compliant|non-compliant)\b"
    r"|\byou (must|should|need to)\b|\bin breach\b|\bwe (advise|recommend)\b",
    re.I,
)
INJECTION = re.compile(
    r"ignore (all |any |the )?(previous|prior|above) instructions|system prompt|you are now|"
    r"disregard (the|your) (rules|guardrails)|<script|BEGIN GENERATED",
    re.I,
)
TEXT_FIELDS = ("observe", "note", "pattern_hint", "instrument", "example")


def _dates_to_str(obj):
    if isinstance(obj, (dt.date, dt.datetime)):
        return obj.isoformat()[:10]
    if isinstance(obj, dict):
        return {k: _dates_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_dates_to_str(v) for v in obj]
    return obj


def load_yaml(path: Path):
    """Load YAML; unquoted dates become ISO strings so the schema sees one type."""
    with path.open(encoding="utf-8") as f:
        return _dates_to_str(yaml.safe_load(f))


def iter_entries(fname: str, data) -> list[dict]:
    """Yield every dict that is a legal entry (has 'id') in a pack file."""
    out = []
    if not isinstance(data, dict):
        return out
    for key, val in data.items():
        if isinstance(val, list):
            out.extend(v for v in val if isinstance(v, dict) and "id" in v)
    return out


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, dict] = {}

    def err(self, where, msg):
        self.errors.append(f"ERROR   {where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"WARNING {where}: {msg}")


def validate_pack(folder: Path, all_ids: dict, rep: Report, today: dt.date, known_packs: set[str]):
    pid = folder.name
    prefix = "xx" if pid == "_template" else pid
    files = {p.name: p for p in folder.iterdir() if p.is_file()}
    for name, p in files.items():
        if p.suffix not in ALLOWED_SUFFIXES or name.startswith("."):
            rep.err(f"{pid}/{name}", "only .yaml, .yml and .md files are allowed in a pack (no scripts, no hidden files)")
    for req in REQUIRED_FILES:
        if req not in files:
            rep.err(pid, f"missing required file {req}")
    pack_meta = None
    n_entries = n_verified = 0
    for name, path in sorted(files.items()):
        if name not in FILE_MAP:
            if path.suffix in {".yaml", ".yml"}:
                rep.warn(f"{pid}/{name}", "unknown file; it will not be compiled into the plugin")
            continue
        try:
            data = load_yaml(path)
        except yaml.YAMLError as e:
            rep.err(f"{pid}/{name}", f"YAML parse error: {e}")
            continue
        schema = {"$ref": f"#/$defs/{FILE_MAP[name]}", "$defs": SCHEMA["$defs"]}
        for e in sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path)):
            loc = "/".join(str(x) for x in e.path) or "(root)"
            rep.err(f"{pid}/{name}:{loc}", e.message)
        if name == "pack.yaml" and isinstance(data, dict):
            pack_meta = data
            continue
        for entry in iter_entries(name, data):
            eid = entry.get("id", "?")
            where = f"{pid}/{name}:{eid}"
            if not str(eid).startswith(prefix + "."):
                rep.err(where, f"entry id must start with '{prefix}.'")
            if eid in all_ids:
                rep.err(where, f"duplicate entry id (also in {all_ids[eid]})")
            all_ids[eid] = f"{pid}/{name}"
            for field in TEXT_FIELDS:
                text = str(entry.get(field, "") or "")
                if ADVICE.search(text):
                    rep.err(where, f"advice-style wording in '{field}': {ADVICE.search(text).group(0)!r}; describe what to observe instead")
                if INJECTION.search(text):
                    rep.err(where, f"instruction-like text in '{field}' is not allowed in pack data")
            if "verified" in entry:
                n_entries += 1
                v = entry.get("verified")
                if v:
                    n_verified += 1
                    if not entry.get("verified_by"):
                        rep.err(where, "verified date without verified_by")
                    try:
                        age = (today - dt.date.fromisoformat(str(v))).days
                        if age > 730:
                            rep.err(where, f"verified {age} days ago (over 24 months): re-verify or mark the pack stale")
                        elif age > 365:
                            rep.warn(where, f"verified {age} days ago (over 12 months)")
                    except ValueError:
                        pass
    if pack_meta:
        if pack_meta.get("id") != prefix:
            rep.err(f"{pid}/pack.yaml", f"id '{pack_meta.get('id')}' must equal folder name '{pid}'")
        parent = pack_meta.get("parent")
        if parent and parent not in known_packs:
            rep.err(f"{pid}/pack.yaml", f"parent '{parent}' has no pack folder")
        if parent and not pid.startswith(parent + "-"):
            rep.warn(f"{pid}/pack.yaml", f"sub-national id should start with its parent ('{parent}-')")
        status = pack_meta.get("status")
        if status in ("beta", "stable") and n_verified < n_entries:
            rep.err(f"{pid}/pack.yaml", f"status '{status}' requires every legal entry to be verified ({n_verified}/{n_entries})")
        if status == "draft" and n_entries and n_verified < n_entries:
            rep.warn(pid, f"draft pack: {n_entries - n_verified} of {n_entries} legal entries not yet verified by a reviewer")
    rep.stats[pid] = {"entries": n_entries, "verified": n_verified,
                      "status": (pack_meta or {}).get("status"), "version": (pack_meta or {}).get("version")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="*", type=Path)
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--include-template", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="print errors and the summary only")
    args = ap.parse_args(argv)

    known = {p.name for p in PACKS.iterdir() if p.is_dir() and not p.name.startswith(".")}
    if args.folders:
        folders = [f.resolve() for f in args.folders]
    else:
        folders = sorted(p for p in PACKS.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not args.include_template:
        folders = [f for f in folders if f.name != "_template"]
    rep = Report()
    all_ids: dict[str, str] = {}
    today = dt.date.today()
    for f in folders:
        if not f.is_dir():
            rep.err(str(f), "not a folder")
            continue
        validate_pack(f, all_ids, rep, today, known | {"_template"})

    for line in rep.errors:
        print(line)
    if not args.quiet:
        for line in rep.warnings:
            print(line)
    print()
    print(f"{'pack':<10} {'version':<8} {'status':<12} {'verified':>10}")
    for pid, s in rep.stats.items():
        print(f"{pid:<10} {str(s['version']):<8} {str(s['status']):<12} {s['verified']:>4}/{s['entries']:<5}")
    print(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    if rep.errors or (args.strict and rep.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
