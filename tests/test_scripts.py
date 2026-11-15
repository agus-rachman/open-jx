"""Tests for the bundled scripts, run against the built package (python tools/build_plugin.py first).

    python -m unittest discover -s tests
"""
import json
import subprocess
import sys
import tempfile
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

    def test_contingent_closures_reported(self):
        evidence = {"state": "verified", "checked": "2026-01-01"}
        tables = {
            "holidays": {"xx": {
                "table_id": "xx", "source_url": "https://example.gov/", "checked": "2026-01-01",
                "evidence": evidence, "coverage": {"from": "2026-01-01", "to": "2026-12-31"},
                "holidays": ["2026-12-25"], "uncertain_windows": [], "caveats": [],
                "contingent_closures": [{"id": "xx.closure.storm", "trigger": "a storm warning is in force",
                                         "effect": "the registry closes", "authority": "Example Act s 1",
                                         "source_url": "https://example.gov/", "status": "in-force"}]}},
            "computation_rules": {"xx-courts": {
                "table_id": "xx-courts", "jurisdiction": "XX", "forums": ["Example Court"], "holiday_table": "xx",
                "computation_provisions": [],
                "period_rules": [{"id": "xx-defence", "label": "Defence", "citation": "r 1", "evidence": evidence,
                                  "period": {"length": 14, "unit": "calendar_days"}, "rollover": "next_business_day"}]}},
            "open_jx_review": {},
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(tables, f)
        req = json.dumps({"table_id": "xx-courts", "period_rule_id": "xx-defence", "trigger_date": "2026-12-11",
                          "tables_file": f.name})
        out = subprocess.run([sys.executable, str(COMPUTE)], input=req, capture_output=True, text=True, check=True)
        r = json.loads(out.stdout)
        Path(f.name).unlink()
        self.assertEqual((r["status"], r["candidate_date"]), ("computed", "2026-12-28"))
        self.assertEqual(r["contingent_closures"], ["xx.closure.storm"])
        self.assertTrue(any("xx.closure.storm" in w for w in r["warnings"]))

    def test_no_contingent_closures_by_default(self):
        r = compute("nsw-courts", "ucpr-defence-after-service", "2026-12-23")
        self.assertEqual(r["contingent_closures"], [])

    def test_hk_fails_closed_pending_verification(self):
        r = compute("hk-courts", "hk-rhc-defence", "2026-11-02")
        self.assertEqual(r["status"], "identify_only")
        self.assertIn("pending-verification", r["reason"])
        self.assertNotIn("candidate_date", r)

    def test_every_table_lists(self):
        out = subprocess.run([sys.executable, str(COMPUTE), "--list"], capture_output=True, text=True, check=True)
        tables = json.loads(out.stdout)
        for t in ("nsw-courts", "vic-courts", "qld-courts", "wa-courts", "sa-courts", "tas-courts", "act-courts",
                  "nt-courts", "cth-federal-courts", "art", "ncat", "vcat", "qcat", "hk-courts"):
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

    def test_two_word_courts_divisions_and_volumeless_reports(self):
        pubs = {"publishers": [
            {"id": "xx.case.ca", "court_ids": ["XXCA Civ", "XXCA Crim"], "court": "Example Court of Appeal",
             "publisher": "Example", "url": "https://example.gov/ca", "access": "direct"},
            {"id": "xx.case.hc", "court_ids": ["XXHC"], "court": "Example High Court",
             "publisher": "Example", "url": "https://example.gov/hc", "access": "direct"}],
            "report_series": [{"series": "XR", "name": "Example Reports", "resolve_via": "xx.case.ca"},
                              {"series": "XLT", "name": "Example Law Times", "resolve_via": "xx.case.hc"}]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(pubs, f)
        out = subprocess.run([sys.executable, str(PARSE), "--publishers", f.name, "[2024] XXCA Civ 123",
                              "[2025] XXHC 1383 (Admin)", "[2024] XR 1", "Smith v Jones 2024 XLT 55",
                              "[2024] XXCA  Crim 9", "paid 2024 XYZ 100 units"],
                             capture_output=True, text=True, check=True)
        Path(f.name).unlink()
        civ, admin, xr, xlt, crim, none = json.loads(out.stdout)
        self.assertEqual((civ["citation_type"], civ["pack_entry"], civ["number"]), ("medium-neutral", "xx.case.ca", 123))
        self.assertEqual((admin["pack_entry"], admin["number"], admin["division"]), ("xx.case.hc", 1383, "Admin"))
        self.assertEqual((xr["citation_type"], xr["route"], xr["page"]), ("reported", "xx.case.ca", 1))
        self.assertEqual((xlt["citation_type"], xlt["route"], xlt["year"]), ("reported", "xx.case.hc", 2024))
        self.assertEqual(crim["pack_entry"], "xx.case.ca")
        self.assertEqual(none["citation_type"], "unknown")

    def test_hong_kong_routes(self):
        cfi, ldt, cfar, hklrd = parse("[2026] HKCFI 123", "[2021] HKLdT 5", "(2020) 23 HKCFAR 1", "[2020] 1 HKLRD 1")
        self.assertEqual((cfi["citation_type"], cfi["pack_entry"]), ("medium-neutral", "hk.case.cfi"))
        self.assertEqual(cfi["route"], "https://legalref.judiciary.hk/")
        self.assertEqual(ldt["pack_entry"], "hk.case.lower")
        self.assertEqual((cfar["citation_type"], cfar["route"]), ("reported", "hk.case.cfa"))
        self.assertEqual((hklrd["citation_type"], hklrd["route"]), ("reported", "hk.case.cfi"))


if __name__ == "__main__":
    unittest.main()
