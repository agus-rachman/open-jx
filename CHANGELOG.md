# Changelog

## 0.1.2 — 2026-11-15

Adds Hong Kong. The `hk` pack is a draft seed (version 0.1.0): none of its 51
entries is verified yet. Its 2026 holiday table and seed High Court rules are
in the `pending-verification` state, so the deadline script refuses every Hong
Kong computation until a reviewer verifies them.

### Hong Kong pack (`packs/hk`)

- Detection: names, HKSAR governing-law wording, courts, CR and BR numbers,
  "Cap." citations. "Limited" or "HK$" alone needs a second signal; PRC law is
  not a Hong Kong signal.
- Sources (e-Legislation, the Judiciary Legal Reference System, HKLII,
  Companies Registry, IRD, PCPD and regulators); citation rules from the
  university guides, including bilingual texts.
- Identifiers: HKID, passport, Mainland travel permit and MPF numbers
  (withheld); CR and BR numbers (matched).
- Execution: Companies Ordinance (Cap. 622) ss 121, 124, 127 and 128;
  Conveyancing and Property Ordinance (Cap. 219) ss 19–20 for individuals'
  deeds; Electronic Transactions Ordinance (Cap. 553) Schedule 1; witnessing,
  registrable charges, powers of attorney, stamp duty.
- Governance: minutes, members' written resolutions, records, AGM, directors'
  interests.
- Calendar: IGCO (Cap. 1) s 71, RHC O 3, the gale warnings ordinance (Cap. 62),
  general and statutory holidays, candidate limitation periods.
- Deadlines: 2026 general holidays; typhoon signal No. 8, black rainstorm and
  "extreme conditions" contingent closures; seed RHC acknowledgment-of-service
  and defence rules.
- Court AI: the Judiciary's July 2024 guidelines (judges and staff) and the
  court-user guidelines in preparation. No restricted content.
- Privacy: PDPO (Cap. 486) with voluntary breach notification, s 33 not in
  operation, doxxing offences, the HKID code, direct marketing, and the
  critical infrastructure ordinance (Cap. 653).
- Case law: HKCFA, HKCA, HKCFI, HKDC, HKFC and HKLdT, and the HKCFAR, HKLRD and
  HKC report series.

### Engine

- Holiday tables may declare `contingent_closures` (closures that cannot be
  dated in advance). `compute_deadline.py` reports each one as a warning and
  lists them in the result; dates are not changed.
- `jx-personal-identifiers` never relies on a check digit to decide whether to
  withhold a value.

### Evals

- 7 Hong Kong cases (company signing, individual e-signed deed, HKID,
  fail-closed deadline, typhoon and rainstorm business days, voluntary breach
  notification, court AI note) and 5 trigger prompts; 2 new fixtures.
- The no-pack case and trigger prompt now use Malaysia (`MY-DEGRADE-01`, `T32`).
- 4 new script tests (contingent closures, Hong Kong citations, Hong Kong fail
  closed).

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
