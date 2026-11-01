# Changelog

## 0.1.1 — 2026-11-02

Housekeeping. No change to skill behaviour or pack content.

- Pack versions set to 0.1.0 to match the release (they read 0.2.0), and the
  malformed `jx-sources-and-citation` skill version is fixed.
- `docs/COPILOT-SETUP.md` restored: install steps and the custom-instruction
  snippet that makes `jx-router` run first. The README links to it again.
- Product name standardised to "Microsoft Copilot Cowork".
- Placeholder reviewer handles removed from CODEOWNERS.
- Leftover "v0.2" wording removed from the eval docs, cases and self-test
  transcripts.

## 0.1.0 — 2026-10-31

First release, for a pilot on Microsoft Copilot Cowork. All packs are `draft`:
no entry has yet been verified by an open-jx reviewer.

### Skills

- `jx-router`: detects the jurisdiction, loads packs, prints the jurisdiction brief
  and routes to overlays.
- `jx-personal-identifiers`: suppresses local personal identifiers.
- `jx-sources-and-citation`: official sources, AGLC and NZ Law Style Guide
  citation, point-in-time legislation checks, and case citation routing to
  official publishers (bundled `parse_citation.py`, five outcomes).
- `jx-execution-and-governance`: signing, deed, attorney and minutes overlay.
- `jx-dates-and-deadlines`: business days, dated holiday tables, candidate
  limitation periods with special-regime flags, and candidate court and tribunal
  deadlines from the bundled `compute_deadline.py`. The script refuses for
  unverified rules, dates outside coverage and uncertain windows.
- `jx-court-ai-rules`: court generative-AI rules before work that may be filed.
- `jx-new-pack`: contributor helper, including a fail-closed eval case per pack.

### Packs

`au`, `au-nsw`, `au-vic`, `au-qld`, `au-wa`, `au-sa`, `au-tas`, `au-act`, `au-nt` and
`nz`, plus `_template`. Each pack holds:

- detection signals, sources with point-in-time terms, citation rules
- personal and company identifiers
- execution and governance checklists
- calendar, limitation and court AI entries
- case-law publishers and terminology

Australian packs also carry `law_checked_as_at`. They include:

- dated holiday tables (2026–2027) and court and tribunal time rules
  (`deadlines.yaml`);
- state privacy regimes (`privacy.yaml`).

### Third-party material

Holiday tables, court computation rules, limitation data, privacy-regime routing,
case-law publisher routes, enduring power of attorney and remote-witnessing
pinpoints, the point-in-time and case-law methods, and two scripts are adapted from
l0cka/legal-skills (MIT, commit 5bfb3d8). Each imported entry carries
`provenance`. See THIRD-PARTY-NOTICES.md. Refresh with
`tools/import_legal_skills.py`.

### Tooling

- Pack JSON Schema and validator: advice-language and instruction lint,
  freshness, verification rules.
- Plugin builder producing a Copilot Cowork zip and a Claude plugin zip, plus
  icons and a link checker.
- Tests for the bundled scripts. CI runs every check, with a weekly link and
  freshness job.

### Evals

- 32 cases, 23 of them side by side with Legal for Cowork; they include
  injection, conflict, no-pack and fail-closed deadline cases.
- 44 trigger prompts.
- Synthetic fixtures, a scorer with release gates, a package checker, a
  reviewer rubric and a scorer self-test.
