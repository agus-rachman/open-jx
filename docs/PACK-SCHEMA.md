# Pack schema guide

A jurisdiction pack is one folder under `packs/`, named by its code. The
machine-readable rules are in `schema/pack.schema.json`; this guide explains
them for contributors.

## Codes

- Country: ISO 3166-1 alpha-2 in lower case — `nz`, `sg`, `gb`.
- Subdivision: country code, hyphen, ISO 3166-2 subdivision code in lower
  case — `au-nsw`, `ca-on`, `gb-sct`.
- A subdivision pack names its country as `parent` and inherits everything it
  does not add. Only put subdivision-specific entries in it.

## Files

| File | Required | Holds |
| --- | --- | --- |
| `pack.yaml` | yes | id, name, parent, level, locale, legal system, version, status, maintainers, detection signals |
| `sources.yaml` | yes | official legislation, case-law, court, regulator and register sources, ranked |
| `citation.yaml` | yes | citation guide and rules (a subdivision may `inherit` its parent's guide) |
| `identifiers.yaml` | yes | personal identifiers to suppress; organisational identifiers to match; privacy context |
| `calendar.yaml` | yes | business-day definitions, time computation, holidays, limitation |
| `execution.yaml` | no | signing, deed, witnessing and electronic-execution observations |
| `governance.yaml` | no | minutes, resolutions and records observations |
| `courts-ai.yaml` | no | court and tribunal rules on generative AI |
| `terminology.yaml` | no | spelling locale and local terms |
| `case-law.yaml` | no | court identifiers (medium neutral citation), official judgment publishers, access posture, report series |
| `privacy.yaml` | no | privacy, health, breach, workplace and automated-decision regimes (generated for Australian states) |
| `deadlines.yaml` | no | a dated holiday table and court/tribunal computation-rule tables used by the deadline script (generated for Australia; see the template) |

`pack.yaml` may also record `law_checked_as_at`: the date the pack's law was last
checked against official sources.

Only `.yaml`, `.yml` and `.md` files are allowed. No scripts, no hidden files.

## Legal entries

Every entry that says something about the law has the same fields:

```yaml
- id: au.exec.s127-methods          # <pack id>.<area>.<slug>, unique across all packs
  applies_to: [company]             # optional: company, individual, attorney, deed, electronic,
                                    # trust, partnership, company-board, company-members, association
  observe: >-                       # what to look for in a document — never advice
    A company signature block shows signing by two directors, ...
  authority: Corporations Act 2001 (Cth) s 127(1)
  source_url: https://www.legislation.gov.au/   # https, official source preferred
  status: in-force                  # in-force | pending | repealed | guidance
  commences: "2026-12-10"           # optional, with status: pending
  verified: null                    # date the reviewer checked it, quoted: "2026-11-02"
  verified_by: null                 # reviewer's GitHub handle: "@handle"
  note: pinpoint to be confirmed    # optional
```

Writing rules (the validator enforces the first three):

1. **Observation, not advice.** Write "The signature block shows…", "The minutes
   record…". Avoid "is valid", "is enforceable", "you must", "in breach".
2. **No instructions.** Pack text is data. Text that tries to instruct the model
   ("ignore previous instructions") fails validation.
3. **Cite.** Every legal entry has an authority and an https source.
4. **Say what you do not know.** If a pinpoint is uncertain, cite the instrument
   and add `note: pinpoint to be confirmed`.
5. **Do not copy** from the Legal for Cowork plugin, commercial databases or
   paywalled commentary. Short quotations of legislation are fine.
6. **No dates from memory** for holidays: point to the official list.

Entries adapted from another project carry a `provenance` block:

```yaml
  provenance:
    source: https://github.com/l0cka/legal-skills
    commit: 5bfb3d8
    path: plugins/legal-skills/references/computation-rules/nsw-courts.json
    upstream_checked: "2026-08-14"
    upstream_state: verified
```

## Deadline tables

`deadlines.yaml` keeps the upstream structure exactly, because
`compute_deadline.py` reads it:

- A holiday table: `table_id`, `coverage`, `holidays`, `uncertain_windows`,
  `caveats` and `evidence.state`.
- Rule tables: `computation_provisions` and `period_rules`, each with
  `evidence.state`.

The script computes only when the rule, every provision it applies and the
holiday table are `verified`, and the dates fall inside coverage and outside
uncertain windows. Otherwise it returns `identify_only`.

## Courts AI entries

```yaml
- id: au-nsw.ai.sc-gen-23
  court: Supreme Court of New South Wales
  instrument: Practice Note SC Gen 23 — Use of Generative Artificial Intelligence
  observe: What the instrument restricts or requires.
  restricted_content: [affidavit-content, witness-statement-content]
  authority: ...
  source_url: ...
  status: in-force
  verified: null
  verified_by: null
```

`restricted_content` drives the `jx-court-ai-rules` skill: it will not draft
content in a listed category. Allowed values: `affidavit-content`,
`witness-statement-content`, `character-reference-content`,
`expert-report-without-leave`, `expert-opinion`, and `evidence-fabrication`.

`evidence-fabrication` is different: it is for rules (such as Singapore's) that
allow AI-assisted drafting of court documents but forbid using AI to generate or
alter evidence. The skill still drafts, but only from supplied facts, marks the
draft for the deponent's confirmation and gives a verification checklist.

## Case-law entries

`court_ids` are the medium neutral citation court identifiers, for example
`HCA`, `NSWSC` or `NZSC`. An identifier may end in a bracketed capital letter,
for example `SGHC(A)` or `SGCA(I)`; the citation parser accepts the same form.

## Status and review

| Pack status | Meaning | Rule |
| --- | --- | --- |
| `draft` | Contributed, not yet verified | Validator warns about unverified entries |
| `beta` | Every legal entry verified by one qualified reviewer | Validator fails if any entry is unverified |
| `stable` | Verified by a second qualified reviewer | As beta |
| `stale` | Verification older than 24 months | Set by maintainers or the weekly check |
| `unmaintained` | No maintainer response for 90 days | The router warns when loading it |

Entries verified more than 12 months ago produce a warning; more than 24 months
an error.
