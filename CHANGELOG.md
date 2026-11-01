# Changelog

## 0.1.1 — 2026-11-02

Adds Singapore. The `sg` pack is a draft seed (version 0.1.0): none of its 43
entries is verified yet, and it has no holiday or court-rule tables, so the
deadline script refuses every Singapore computation.

### Singapore pack (`packs/sg`)

- Detection: names, governing-law wording, courts, UEN, "Pte. Ltd.", SICC. "SG"
  alone needs a second signal.
- Sources (Singapore Statutes Online, Singapore Courts judgments, eLitigation,
  ACRA, PDPC and regulators), SLR Style Guide citation rules.
- Identifiers: NRIC, FIN, work pass, passport, birth certificate (suppressed);
  UEN and GST number (matched).
- Execution: Companies Act 1967 ss 41A and 41B, sealing for individuals' deeds,
  attestation, Electronic Transactions Act exclusions, e-conveyancing, guarantees,
  stamp duty, lasting powers of attorney.
- Governance: minutes (s 188), written resolutions, interests, AGM dispensation.
- Calendar: Interpretation Act 1965 s 50, Rules of Court 2021, Holidays Act 1998,
  candidate limitation periods.
- Court AI: the Guide on the Use of Generative AI Tools by Court Users (all
  Singapore courts, from 1 October 2024).
- Privacy: PDPA, breach notification, NRIC guidelines, Do Not Call.
- Case law: court identifiers including SGHC(A), SGHC(I) and SGCA(I); the
  citation parser also reads square-bracket reported citations such as
  `[2020] 2 SLR 1151`.

### Evals

- 5 Singapore cases (company deed, individual deed, NRIC, court AI, fail-closed
  deadline) and 5 trigger prompts; 3 new fixtures.
- The no-pack case and trigger prompt now use Hong Kong (`HK-DEGRADE-01`, `T32`).

### Engine support for Singapore

- Schema: `court_ids` accept a bracketed suffix (`SGHC(A)`); new
  `restricted_content` value `evidence-fabrication`.
- `parse_citation.py` parses bracketed court identifiers; new script test.
- `jx-court-ai-rules` drafts under `evidence-fabrication` rules (first-cut
  affidavits allowed) without inventing or altering evidence.
- `jx-router` recognises Singapore signals (UEN, Pte. Ltd., SICC, "use the SG
  pack") and asks when "SG" appears alone.
- Other skills' descriptions name Singapore; point-in-time method adds Singapore
  Statutes Online.

### Housekeeping

- Pack versions aligned to 0.1.0, and the malformed `jx-sources-and-citation`
  skill version fixed.
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
