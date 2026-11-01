# open-jx — Open Jurisdiction Packs

open-jx is an add-on plugin that gives the legal skills in Microsoft Copilot Cowork local knowledge for a specific jurisdiction. It never changes or copies those skills. It ships with packs for:

- the Commonwealth of Australia
- every Australian state and territory: NSW, Victoria, Queensland, Western
  Australia, South Australia, Tasmania, the ACT and the Northern Territory
- New Zealand
- Singapore (new in 0.1.1; draft seed pack, no deadline tables yet)

Anyone can contribute another jurisdiction as a data pack.

> **Not legal advice.** Pack entries are checklists that point to primary
> sources. Every v0.1 pack is `draft`: no entry has yet been verified by a
> qualified reviewer. Confirm every reference against the primary text before
> relying on it.

## What it adds

| Skill | What it does |
| --- | --- |
| `jx-router` | Detects the jurisdiction (from the user, a governing-law clause, a court, company numbers or a default), loads the packs and prints a jurisdiction brief |
| `jx-personal-identifiers` | Stops local identifiers being reproduced: tax file numbers, Medicare and IHI numbers, IRD and NHI numbers, licences, passports |
| `jx-sources-and-citation` | Supplies official legislation, case-law and regulator sources and the local citation style (AGLC4 for Australia, the NZ Law Style Guide for New Zealand, the SLR Style Guide for Singapore). Checks legislation at a date and routes case citations to each court's official publisher |
| `jx-execution-and-governance` | Adds an overlay after execution and minutes skills: s 127 signing methods, deeds and witnessing by state, s 180 (NZ), electronic signing, ACN, ABN and NZBN consistency, minutes and written-resolution checkpoints |
| `jx-dates-and-deadlines` | Adds an overlay after deadline skills: business and working days, dated holiday tables, time-counting rules, candidate limitation periods and special regimes. Computes candidate court and tribunal deadlines with a bundled script that refuses rather than guesses |
| `jx-court-ai-rules` | Flags court rules on generative AI (Federal Court GPN-AI, NSW SC Gen 23, NZ guidelines) and won't draft restricted content |
| `jx-new-pack` | Helps contributors create a new pack |

## How it works with the legal skills

```
request ──► jx-router ──► prepare (identifiers, sources, court AI note)
                                   │
                                   ▼
                   Legal for Cowork skill runs unchanged
                                   │
                                   ▼
          overlay section: "#### Jurisdiction overlay — <packs>"
```

The original skill's output always comes first and is never edited. See
[docs/INTEGRATION.md](docs/INTEGRATION.md) for the full routing table and
compatibility rules.

## Install in Microsoft Copilot Cowork

1. Download `open-jx-<version>.zip` from Releases, or build it yourself (below).
2. For a pilot group, each user can use Copilot Cowork to add the plugin from Customize menu. Admin can also upload it in the M365 admin centre.
3. Each user adds the custom-instruction snippet in
   [docs/COPILOT-SETUP.md](docs/COPILOT-SETUP.md), so the jurisdiction router
   runs before the legal skills.

## Build

```
pip install pyyaml jsonschema pillow python-docx
python tools/validate_packs.py          # check packs
python tools/build_plugin.py            # build dist/open-jx-<version>.zip (+ a Claude plugin zip)
python evals/check_package.py dist/open-jx-0.1.0.zip
python -m unittest discover -s tests     # bundled script tests
```

Set `repo_url` in `build.config.json` before building a release. The manifest's
developer, privacy and terms URLs are built from it.

## Evaluate

The eval suite runs every case with open-jx off and on, and scores trigger
accuracy, overlay accuracy, non-interference and guardrails against release
gates. See [evals/README.md](evals/README.md).

## Contribute a jurisdiction

Copy `packs/_template/`, fill it in and open a pull request. Details are in
[CONTRIBUTING.md](CONTRIBUTING.md) and [docs/PACK-SCHEMA.md](docs/PACK-SCHEMA.md).

## Repository layout

```
plugin/skills/      skill sources (SKILL.md per skill)
plugin/assets/      icons
packs/              jurisdiction packs (YAML) — contributors edit these
schema/             pack JSON Schema
tools/              validate_packs.py, build_plugin.py, make_icons.py
evals/              eval suite
docs/               integration, setup and schema guides
dist/, build/       generated — do not edit
```

## Third-party material

This release imports holiday tables, court time-computation rules, limitation
data, privacy-regime routing, case-law publisher routes and two scripts from
[l0cka/legal-skills](https://github.com/l0cka/legal-skills) under the MIT
licence. Every imported entry records the upstream commit and check date in
`provenance`. See [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). To refresh
from upstream, run `python tools/import_legal_skills.py --upstream <checkout>`
and review the diff.

## Licence

- Skills, tooling and evals: Apache License 2.0 ([LICENSE](LICENSE)).
- Pack content: Creative Commons Attribution 4.0 ([LICENSE-DATA](LICENSE-DATA)).

open-jx is an independent project. It is not affiliated with or endorsed by
Microsoft or by any employer of its contributors. "Copilot", "Microsoft 365"
and "Legal for Cowork" are used only to describe compatibility.
