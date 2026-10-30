---
name: jx-personal-identifiers
description: >-
  Adds the loaded jurisdiction's personal identifiers (for example tax file
  numbers, Medicare numbers, IRD numbers, NHI numbers, driver licence and
  passport numbers) to the list of details that must never be reproduced, and
  sets how company numbers (ACN, ABN, ARBN, NZBN) are handled. Use with every
  Legal for Cowork skill once jx-router has loaded an Australian or New Zealand
  pack, or when a document contains an Australian or New Zealand personal
  identifier.
license: Apache-2.0
metadata:
  author: open-jx contributors
  version: "0.1.0"
---

# Local personal identifiers (open-jx)

Extend personal-data minimisation to the identifiers of the loaded jurisdiction.
This adds to the Legal for Cowork rules; it never relaxes them.

## Before you start

This skill uses the pack content that **jx-router** loaded in this conversation.
If no jurisdiction brief (a line starting `**Jurisdiction:**`) appears earlier in
this conversation, run jx-router first.

## Rules

1. **Never reproduce a personal identifier** listed under `identifiers.personal`
   in a loaded pack: not in an answer, table, quote, summary, draft, minutes or
   tracker, even when the user asks for the column. Refer to the field and its
   location instead: "the employee's tax file number field (Schedule 2) is
   completed".
2. **Recognise them by context, not only format.** Use each entry's
   `pattern_hint` (for example "9 digits, often written 123 456 789, near the
   words TFN or tax file number"). A number that matches a pattern but has no
   supporting context is not assumed to be an identifier; say so if it matters.
3. **Company identifiers may be quoted and compared** (entries under
   `identifiers.organisational`, such as ACN, ABN, ARBN, NZBN, NZ company
   number). They are needed to match parties across a document. Exception: an
   ABN or NZBN that belongs to an individual sole trader is quoted only where
   the task needs party matching.
4. **Quoting around a value.** When a quotation would contain a protected
   value, quote the label and replace the value with `[withheld]`.
5. **Statutory restrictions.** Some identifiers carry their own legal handling
   rules (pack entries name them, for example the tax file number rules in
   Australia). Mention the existence of such a rule as an observation only when
   the document handles the identifier; do not advise on compliance.

## Output

No separate section is needed. If the task's output withheld any identifier,
add one line at the end of the overlay section (or of the answer, if no
overlay applies): `Withheld under open-jx identifier rules: <identifier names> (<locations>).`
