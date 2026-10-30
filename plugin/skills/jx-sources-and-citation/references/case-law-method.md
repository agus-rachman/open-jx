# Case citation check

Adapted for open-jx from l0cka/legal-skills (commit 5bfb3d8),
`plugins/legal-skills/references/case-law-verification-method.md`. Copyright (c)
2026 l0cka, MIT License (see THIRD-PARTY-NOTICES.md). Extended with New Zealand
routes from the open-jx `nz` pack.

Use this when the user asks you to check citations, or before work is filed
(see jx-court-ai-rules). The check confirms that a judgment exists at the
issuing court's official publisher, and that quoted passages appear in it. It
does not summarise judgments, assess precedential weight, or report later
treatment.

## Route

1. Run `scripts/parse_citation.py "<citation>"` (several citations can be
   passed at once). It reads the court and report-series map from
   `references/case-publishers.json`, built from the packs' `case-law` entries.
   If you can't run scripts, read the court identifier yourself and look it up
   in the loaded packs' `case_law` section.
2. **Medium neutral citation** `[YEAR] COURT NUMBER`, e.g. `[2023] HCA 12` or
   `[2020] NZSC 1`: the court identifier gives the publisher.
3. **Reported citation** `(YEAR) VOLUME SERIES PAGE`: resolve it to a medium
   neutral citation through the issuing court's search before verifying.
   Report series are proprietary. The High Court publisher includes CLR volumes
   1–100.

## Access

- `direct`: one targeted lookup per citation; never crawl or bulk-download.
- `human-browser-only` (the Federal Court, Queensland): never solve or work
  around a bot challenge. Give the user the manual search route, or report the
  citation as `UNVERIFIABLE`.
- `not-mapped`: the publisher route isn't recorded yet. Report `UNVERIFIABLE`
  unless a person checks it.
- Free aggregators (AustLII, NZLII, Jade) can help locate a judgment, but they
  are not the verification source.

## Results (exactly one per citation)

- `VERIFIED` — found at the official publisher. Record the case name, court,
  date and URL from the publisher's page.
- `VERIFIED WITH QUALIFICATIONS` — found, but the name differs, a restriction
  notation applies, or the match is near rather than exact.
- `UNVERIFIABLE` — the publisher couldn't be consulted, or a reported citation
  couldn't be resolved. This is not evidence of fabrication.
- `NOT FOUND` — the issuing court's own database was searched and has no
  match. This is a strong signal for a person to check; never present it as an
  accusation.
- `OUTSIDE SCOPE` — treatment, interpretation, advice, or a court in no
  installed pack.

## Quotes and restrictions

Check quotes only against text opened from the official publisher in this
session. Try the exact passage first, then a normalised form (straight
quotes, collapsed spaces). Report the paragraph number. A near match is
`VERIFIED WITH QUALIFICATIONS` with the differences listed.

Before quoting any judgment, check for restriction, suppression or
non-publication notations and anonymised names. If one applies, report it and
don't reproduce the restricted content.

Record for every outcome: URLs inspected, the date and time zone of the check,
and what remains unverified.
