"""Tests for the bundled scripts, run against the built package (python tools/build_plugin.py first).

    python -m unittest discover -s tests
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "build" / "package" / "skills"
COMPUTE = SKILLS / "jx-dates-and-deadlines" / "scripts" / "compute_deadline.py"
PARSE = SKILLS / "jx-sources-and-citation" / "scripts" / "parse_citation.py"


def compute(table, rule, trigger):
    req = json.dumps({"table_id": table, "period_rule_id": rule, "trigger_date": trigger})
    out = subprocess.run([sys.executable, str(COMPUTE)], input=req, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def parse(*citations):
    out = subprocess.run([sys.executable, str(PARSE), *citations], capture_output=True, text=True, check=True)
    data = json.loads(out.stdout)
    return data if isinstance(data, list) else [data]


@unittest.skipUnless(COMPUTE.exists(), "build the package first")
class DeadlineScript(unittest.TestCase):
    def test_nsw_defence_rolls_over_holidays(self):
        r = compute("nsw-courts", "ucpr-defence-after-service", "2026-12-23")
        self.assertEqual(r["status"], "computed")
        self.assertEqual(r["candidate_date"], "2027-01-20")
        self.assertTrue(any("draft" in w for w in r["warnings"]), "draft pack warning expected")

    def test_federal_court_christmas_exclusion(self):
        r = compute("cth-federal-courts", "fcr-defence-after-service", "2026-12-01")
        self.assertEqual((r["status"], r["candidate_date"]), ("computed", "2027-01-20"))

    def test_fail_closed_on_unverified_rule(self):
        r = compute("vic-courts", "vic-scr-appearance-after-service", "2026-11-02")
        self.assertEqual(r["status"], "identify_only")
        self.assertNotIn("candidate_date", r)

    def test_fail_closed_outside_holiday_coverage(self):
        r = compute("wa-courts", "wa-rsc-defence-after-appearance-or-soc", "2027-12-20")
        self.assertEqual(r["status"], "identify_only")
        self.assertIn("does not cover", r["reason"])

    def test_fail_closed_in_uncertain_window(self):
        r = compute("act-courts", "act-cpr-noir-or-defence-after-service", "2026-12-01")
        self.assertEqual(r["status"], "identify_only")

    def test_every_table_lists(self):
        out = subprocess.run([sys.executable, str(COMPUTE), "--list"], capture_output=True, text=True, check=True)
        tables = json.loads(out.stdout)
        for t in ("nsw-courts", "vic-courts", "qld-courts", "wa-courts", "sa-courts", "tas-courts", "act-courts",
                  "nt-courts", "cth-federal-courts", "art", "ncat", "vcat", "qcat"):
            self.assertIn(t, tables)


@unittest.skipUnless(PARSE.exists(), "build the package first")
class CitationScript(unittest.TestCase):
    def test_routes(self):
        hca, nswsc, fcafc, vsca, nzsc, aljr, none = parse(
            "[2023] HCA 12", "[2025] NSWSC 101", "[2024] FCAFC 7", "[2022] VSCA 3", "[2020] NZSC 1",
            "(2020) 94 ALJR 1", "Smith v Jones")
        self.assertEqual((hca["route"], hca["access"]), ("https://www.hcourt.gov.au/", "direct"))
        self.assertEqual(nswsc["route"], "https://www.caselaw.nsw.gov.au/")
        self.assertEqual(fcafc["access"], "human-browser-only")
        self.assertEqual(vsca["access"], "not-mapped")
        self.assertEqual(nzsc["route"], "https://www.courtsofnz.govt.nz/")
        self.assertEqual((aljr["citation_type"], aljr["route"]), ("reported", "au.case.hca"))
        self.assertEqual(none["citation_type"], "unknown")

    def test_bracketed_court_ids(self):
        sghca, sgca = parse("[2026] SGHC(A) 9", "[2024] SGCA 1")
        self.assertEqual((sghca["citation_type"], sghca["court_id"], sghca["number"]), ("medium-neutral", "SGHC(A)", 9))
        self.assertEqual((sgca["court_id"], sgca["number"]), ("SGCA", 1))
        self.assertEqual(sghca["route"], "https://www.judiciary.gov.sg/judgments")
        self.assertEqual(sghca["pack_entry"], "sg.case.appellate-division")

    def test_square_bracket_reported(self):
        slr, slrr = parse("[2020] 2 SLR 1151", "[2005] 1 SLR(R) 1")
        self.assertEqual((slr["citation_type"], slr["route"]), ("reported", "sg.case.court-of-appeal"))
        self.assertEqual((slrr["citation_type"], slrr["route"]), ("reported", "sg.case.court-of-appeal"))


if __name__ == "__main__":
    unittest.main()
