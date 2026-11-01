---
name: jx-new-pack
description: >-
  Helps a contributor create a new open-jx jurisdiction pack (for example
  Singapore, Hong Kong, England and Wales, or a Canadian province) or extend an
  existing one, producing schema-valid YAML files ready for a pull request. Use
  when the user asks to "add a jurisdiction to open-jx", "create a jurisdiction
  pack", "contribute a pack for <country>", or "update the NSW pack".
license: Apache-2.0
metadata:
  author: open-jx contributors
  version: "0.1.1"
---

# Create or update a jurisdiction pack (open-jx)

Guide a contributor through producing a pack that passes the open-jx checks.
You draft files; a qualified reviewer for that jurisdiction must verify every
legal entry before the pack leaves `draft` status.

## Inputs to collect (one question card)

1. Jurisdiction name and code: ISO 3166-1 alpha-2 in lower case for a country
   (`sg`), plus `-` and the ISO 3166-2 subdivision code for a state or province
   (`ca-on`, `au-nsw`).
2. Parent pack, if any (a state's parent is its country).
3. Locale (`en-SG`, `en-CA`) and legal system (common law, civil law, mixed).
4. Contributor and reviewer GitHub handles.
5. Which files to fill now. The minimum viable pack is `pack.yaml`,
   `sources.yaml`, `citation.yaml`, `identifiers.yaml` and `calendar.yaml`.

## Files

Start from the template files in `references/template/` and follow
[references/schema-guide.md](references/schema-guide.md). The template files are:
`pack.yaml`, `sources.yaml`, `citation.yaml`, `identifiers.yaml`,
`execution.yaml`, `governance.yaml`, `calendar.yaml`, `courts-ai.yaml`,
`terminology.yaml`, `case-law.yaml` (court identifiers and official judgment
publishers), `privacy.yaml` (privacy regimes) and `deadlines.yaml` (a dated
holiday table and court computation-rule tables; leave `holiday_table: null`
and `court_rules: []` unless each entry has been checked against the official
publisher, because the deadline script computes only from `verified` entries).

Every pack should also get at least one fail-closed eval case: a request the
skills must refuse or leave undecided (for example a date outside the holiday
table's coverage, or a court with no mapped publisher).

## Rules for every legal entry

- One observation per entry, written as something to look for in a document,
  never as advice ("Signature block shows…", not "The company must…").
- `authority` names the instrument and pinpoint; if the pinpoint is unknown,
  name the instrument and set `note: pinpoint to be confirmed`.
- `source_url` is the official register or court page (https).
- `verified` and `verified_by` stay `null` until the reviewer confirms the entry.
- Do not copy text from the Legal for Cowork plugin, commercial services or
  paywalled commentary. Short quotations of legislation are fine.
- Prefer official government sources; free reprints may be listed with rank 2.

## Output

Produce each file as a separate code block (or as files, if the user asks),
followed by:

- the folder path: `packs/<code>/`
- a checklist: run `python tools/validate_packs.py packs/<code>`, open a pull
  request using the New jurisdiction template, request review from the named
  reviewer, and add the reviewer to `CODEOWNERS`.

## Guardrails

- Never mark an entry verified or a pack `beta` or `stable`; only reviewers do that.
- Never fill an entry from memory without saying it needs verification.
