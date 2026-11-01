#!/usr/bin/env python3
# Adapted for open-jx from l0cka/legal-skills (commit 5bfb3d8),
# plugins/legal-skills/skills/route-case-citation/scripts/parse_citation.py
# Copyright (c) 2026 l0cka. Licensed under the MIT License; see THIRD-PARTY-NOTICES.md.
# open-jx changes: the court and report-series maps are read from
# references/case-publishers.json (built from packs/*/case-law.yaml) and the route
# names the official publisher rather than a verification skill. Court identifiers
# may carry a bracketed suffix, e.g. SGHC(A) (open-jx 0.2.0).
"""Parse a case citation and report the official publisher route.

Offline helper: it parses citation text and maps the court identifier or
report series to the official publisher recorded in the open-jx packs. It makes
no network requests and proves nothing about whether the cited decision exists.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NEUTRAL = re.compile(
    r"\[(?P<year>1[89]\d\d|20\d\d)\]\s+(?P<court>(?:[A-Za-z][A-Za-z0-9]*[A-Za-z]|[A-Za-z]+)(?:\([A-Za-z]\))?)\s+(?P<number>\d+)"
)
REPORTED = re.compile(
    r"\((?P<year>1[89]\d\d|20\d\d)\)\s+(?P<volume>\d+)\s+(?P<series>[A-Z][A-Za-z ]*?)\s+(?P<page>\d+)"
)

PUBLISHERS_FILE = Path(__file__).resolve().parents[1] / "references" / "case-publishers.json"


def load_publishers(path: Path = PUBLISHERS_FILE) -> tuple[dict, dict]:
    """Court id -> publisher record, and report series -> record, built from the open-jx packs."""
    data = json.loads(path.read_text(encoding="utf-8"))
    courts = {}
    for p in data["publishers"]:
        for cid in p["court_ids"]:
            courts[cid.upper()] = p
    series = {s["series"].upper(): s for s in data.get("report_series", [])}
    return courts, series


def matched_int(match: re.Match[str], group: str) -> int:
    try:
        return int(match.group(group))
    except (IndexError, ValueError) as exc:
        raise ValueError(f"invalid numeric citation group {group!r}") from exc


def parse(text: str, courts: dict | None = None, series_map: dict | None = None) -> dict[str, object]:
    """Parse one citation string into a routing record."""
    if courts is None or series_map is None:
        courts, series_map = load_publishers()
    neutral = NEUTRAL.search(text)
    if neutral:
        court_id = neutral.group("court").upper()
        court = courts.get(court_id)
        record: dict[str, object] = {
            "input": text.strip(),
            "citation_type": "medium-neutral",
            "year": matched_int(neutral, "year"),
            "court_id": neutral.group("court"),
            "number": matched_int(neutral, "number"),
        }
        if court is None:
            record["route"] = None
            record["note"] = f"unrecognised court identifier {court_id!r}"
        else:
            record["court"] = court["court"]
            record["pack_entry"] = court["id"]
            record["publisher"] = court["publisher"]
            record["route"] = court["url"]
            record["access"] = court["access"]
            if court["access"] == "not-mapped":
                record["note"] = "official publisher route not mapped; report the citation as unverifiable unless checked by a person"
            elif court["access"] == "human-browser-only":
                record["note"] = "use a human-operated browser session; never automate around a bot challenge"
        return record

    reported = REPORTED.search(text)
    if reported:
        series_id = reported.group("series").strip().upper().replace(" ", "")
        series = series_map.get(series_id)
        record = {
            "input": text.strip(),
            "citation_type": "reported",
            "year": matched_int(reported, "year"),
            "volume": matched_int(reported, "volume"),
            "series_id": reported.group("series").strip(),
            "page": matched_int(reported, "page"),
        }
        if series is None:
            record["route"] = None
            record["note"] = "unrecognised report series; resolve to a medium-neutral citation before verification"
        else:
            record["series"] = series["name"]
            record["route"] = series["resolve_via"]
            record["note"] = (
                "reported citation: resolve to a medium-neutral citation at the "
                "official publisher before treating the decision as verified"
            )
        return record

    return {
        "input": text.strip(),
        "citation_type": "unknown",
        "route": None,
        "note": "no medium-neutral or reported citation found; search the court publisher by case name",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("citation", nargs="+", help="citation text, for example '[2023] HCA 12'")
    args = parser.parse_args()
    courts, series_map = load_publishers()
    records = [parse(citation, courts, series_map) for citation in args.citation]
    json.dump(records if len(records) > 1 else records[0], sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
