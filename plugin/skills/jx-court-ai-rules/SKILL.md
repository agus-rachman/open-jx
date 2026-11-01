---
name: jx-court-ai-rules
description: >-
  Checks court and tribunal rules on generative AI before preparing anything
  that may be filed, served or relied on in Australian or New Zealand
  proceedings: affidavits, witness statements, expert reports, submissions,
  chronologies, lists of documents. Use before build-case-chronology,
  draft-legal-memo or legal-reasoning when the user mentions a court, tribunal,
  filing, affidavit, witness statement, expert report or submissions, or names
  the Federal Court, a Supreme, District, County or Local Court, NCAT, VCAT,
  QCAT or a New Zealand court.
license: Apache-2.0
metadata:
  author: open-jx contributors
  version: "0.1.1"
---

# Court AI rules (open-jx)

Make the user aware of the court's rules on generative AI before work that may
end up in proceedings, and keep restricted content out of AI-generated drafts.

## Before you start

Use the pack content that **jx-router** loaded. If no `**Jurisdiction:**` brief
appears earlier in this conversation, run jx-router first.

## Steps

1. **Identify the forum** from the request or documents. If the work may be
   used in proceedings but no forum is named, ask once which court or tribunal.
2. **Match pack entries.** Find the `courts_ai` entries for that court (and its
   level of the hierarchy) in the loaded packs. If none match, say that no rule
   for that forum is recorded in the pack and that the user should check the
   court's current practice notes.
3. **Print a court AI note before the Legal for Cowork output**:

```
**Court AI note:** <court> — <practice note or guideline name> (pack entry <id>)
<one or two sentences on what the entry restricts or requires>. Confirm against the current practice note before relying on this work in proceedings.
```

4. **Restricted content.** If a matched entry says AI must not be used to
   generate a category of content (for example the content of an affidavit,
   witness statement or character reference, or an expert report without
   leave), do not generate that content. Say which entry applies and offer help
   that falls outside the restriction, such as a document index or a
   chronology for the lawyer's own working use, clearly labelled as such.
5. **Verification duties.** Where an entry requires verification of citations or
   evidence, remind the user that each citation and quotation must be checked
   against the source before filing, and offer the case citation check in
   jx-sources-and-citation, which routes each citation to the court's
   official publisher.
6. **Confidential material.** Where an entry restricts entering suppressed,
   subpoenaed, privileged or compulsorily obtained material into AI tools, ask
   the user to confirm the supplied material may be used before proceeding.

## Guardrails

- This skill flags court rules; it does not decide whether a use is permitted.
- Never draft content an entry restricts, even if the user insists; explain and
  offer permitted help instead.
- The Legal for Cowork skill's own guardrails continue to apply.
