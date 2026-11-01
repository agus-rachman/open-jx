---
name: jx-sources-and-citation
description: >-
  Gives legal research and writing the loaded jurisdiction's official sources,
  their order of authority, and its citation style (AGLC for Australia, the New
  Zealand Law Style Guide for New Zealand). Use before a legal memo, legal
  reasoning, a regulatory gap analysis, a cross-jurisdiction comparison or an
  explanation of a legal concept that concerns Australia, an Australian state
  or territory, or New Zealand; when the user asks where to find Australian or
  New Zealand legislation, cases or regulator guidance; and when the user asks
  to "check these citations", "verify this case", "is this section still in
  force" or "what did the Act say on <date>".
license: Apache-2.0
metadata:
  author: open-jx contributors
  version: "0.1.1"
---

# Official sources and citation (open-jx)

Point research at the right official sources for the loaded jurisdiction and
keep citations in its local style. The Legal for Cowork skill still decides
what to research and how to present it.

## Before you start

Use the pack content that **jx-router** loaded. If no `**Jurisdiction:**`
brief appears earlier in this conversation, run jx-router first.

## Sources

1. **Offer the pack's sources.** When the Legal for Cowork skill asks which
   source types are approved, offer the pack's `sources` entries by name, in
   `rank` order (1 = official text). Do not add sources that are not in the pack
   unless the user names them.
2. **Official text first.** Prefer the official legislation register for the
   jurisdiction; use free reprints (AustLII, NZLII, Jade) to locate material,
   then confirm currency against the official register and record the version
   or "as at" date.
3. **Split federal and state law.** For Australia, decide per point whether the
   law is Commonwealth or state and territory. Topics usually governed by state
   and territory law include deeds and conveyancing, leases and residential
   tenancies, limitation periods, powers of attorney, stamp duty, public
   holidays, long service leave, and the separate (if similar) defamation,
   work health and safety and civil procedure Acts. When the user says
   "Australia" for such a topic, tell the comparison skill to treat each state
   or territory as a separate jurisdiction, or ask which ones are in scope.
4. **No pack, no shortcut.** If the jurisdiction has no pack, research proceeds
   exactly as the Legal for Cowork skill directs, without this skill.

## Checking legislation at a date

When the task relies on what a provision said on a particular date, or the
user asks to check a legislation citation, follow
[references/point-in-time-method.md](references/point-in-time-method.md):
one instrument, the consolidated text covering the date (use the pack's
`consolidated_term`), commencement and currency checked, and one result —
`VERIFIED`, `VERIFIED WITH QUALIFICATIONS` or `NOT VERIFIED`.

## Checking case citations

When the user asks to check citations, or work will be filed, follow
[references/case-law-method.md](references/case-law-method.md). Route each
citation with `scripts/parse_citation.py`, which reads
[references/case-publishers.json](references/case-publishers.json), and give
one result per citation: `VERIFIED`, `VERIFIED WITH QUALIFICATIONS`,
`UNVERIFIABLE`, `NOT FOUND` or `OUTSIDE SCOPE`. Never work around a
publisher's bot challenge. Never call an unverifiable citation fabricated.

Present the results as a table:

| Citation | Court | Official publisher | Result | Evidence |
| --- | --- | --- | --- | --- |

## Citation style

Apply the pack's `citation` guide (name, edition, rules and examples) to any
citation the task produces, unless the user asks for another style or the
organisation's template uses one. Never invent a citation, pinpoint, report
series or neutral citation number. Where a pinpoint cannot be confirmed,
cite the instrument and say the pinpoint needs checking.

Licence notice for the adapted script and data: [references/THIRD-PARTY-NOTICES.md](references/THIRD-PARTY-NOTICES.md).

## Output

No separate section, and nothing inserted into the Legal for Cowork output.
After that output, add one line naming what this skill supplied, for example:
`Sources and citation per open-jx pack au@0.1.0 (AGLC, 4th edition).`
