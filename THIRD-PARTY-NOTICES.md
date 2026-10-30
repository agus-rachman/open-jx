# Third-party notices

open-jx includes material adapted from the following project.

## l0cka/legal-skills

- Source: https://github.com/l0cka/legal-skills (commit 5bfb3d8, 17 October 2026)
- Licence: MIT (full text below)

What open-jx uses:

| open-jx file | Upstream source | Use |
| --- | --- | --- |
| `packs/*/deadlines.yaml` (generated) | `plugins/legal-skills/references/holidays/*.json`, `plugins/legal-skills/references/computation-rules/*.json` | Holiday tables and court/tribunal time-computation rules, kept in upstream structure with evidence states |
| `packs/au-*/privacy.yaml` (generated) | `plugins/legal-skills/skills/route-australian-privacy-jurisdiction/references/state-territory-coverage.json` | State and territory privacy, health, breach, workplace and automated-decision regimes |
| `packs/*/calendar.yaml` (limitation and time-computation entries) | `plugins/legal-skills/skills/map-limitation-periods/references/limitation-registry.json`, computation-rule tables | Candidate limitation periods, special regimes, interpretation-Act and court-rule pinpoints |
| `packs/*/case-law.yaml` (Australian entries) | `plugins/legal-skills/references/case-law-verification-method.md`, `.../route-case-citation/scripts/parse_citation.py` | Court identifiers, official publishers, access posture |
| `packs/au-nsw|au-vic|au-qld/execution.yaml` (attorney and remote-witnessing entries) | `plugins/legal-skills/references/{nsw,vic,qld}-execution-formalities.md` | Pinpoints for enduring powers of attorney and audio-visual witnessing |
| `packs/*/sources.yaml` (`consolidated_term`) | `plugins/legal-skills/references/point-in-time-method.md` | Publisher terminology |
| `plugin/skills/jx-dates-and-deadlines/scripts/compute_deadline.py` | `.../compute-procedural-deadlines/scripts/compute_deadline.py` | Deadline computation (adapted to a combined tables file) |
| `plugin/skills/jx-sources-and-citation/scripts/parse_citation.py` | `.../route-case-citation/scripts/parse_citation.py` | Citation parsing (adapted to read publishers from packs) |
| `plugin/skills/jx-sources-and-citation/references/point-in-time-method.md`, `case-law-method.md` | `plugins/legal-skills/references/point-in-time-method.md`, `case-law-verification-method.md` | Methods (adapted and extended to New Zealand) |

Upstream evidence states and check dates are preserved in each entry's
`provenance`. open-jx reviewer verification (`verified`, `verified_by`) is
separate and starts empty. Re-import with `tools/import_legal_skills.py`.

### MIT License text

```
MIT License

Copyright (c) 2026 l0cka

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
