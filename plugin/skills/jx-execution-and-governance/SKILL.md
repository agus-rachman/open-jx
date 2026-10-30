---
name: jx-execution-and-governance
description: >-
  Adds a labelled jurisdiction overlay of execution and governance observations
  after the Legal for Cowork skill has answered: company signing methods,
  deeds, witnessing, electronic signing, company-number consistency, and
  statutory minutes and written-resolution checkpoints for Australia (each
  state and territory) and New Zealand. Use after check-execution-readiness,
  draft-new-contract, analyze-related-contracts or draft-minutes-and-resolutions
  when an Australian or New Zealand pack is loaded, or when the user asks
  "does this meet NSW execution requirements", "is the deed signed properly
  for NZ" or "check the minutes against the Corporations Act".
license: Apache-2.0
metadata:
  author: open-jx contributors
  version: "0.1.0"
---

# Execution and governance overlay (open-jx)

Add jurisdiction-specific observations about how a document is signed or how a
meeting is recorded. You observe and point to the pack entry; you never decide
whether execution is valid or a resolution was passed.

## Before you start

- Use the pack content that **jx-router** loaded. If no `**Jurisdiction:**`
  brief appears earlier in this conversation, run jx-router first.
- Wait until the Legal for Cowork skill has finished its own output. Do not
  repeat, re-rank, re-word or contradict its findings or its position.
- If that skill does not allow outside research (the execution-readiness check
  does not), use only the loaded packs. Do not browse.

## What to check

Work only from the supplied document and the pack entries under `execution` and
`governance`.

**Execution (contracts, deeds, variations)**

1. **Party type and signing method.** For each party, identify whether it is a
   company, an individual, an attorney, a trustee or a partnership, and compare
   its signature block with the pack's signing-method entries for that type
   (for example the two-director / director-and-secretary / sole-director
   methods in Australia, or the director-signature and witness requirements in
   New Zealand). Report what the block shows and which entry it relates to.
2. **Deed indications.** If the document calls itself a deed or uses "executed
   as a deed" or "signed, sealed and delivered", list the pack's deed entries
   for the governing jurisdiction (witnessing, sealing, delivery, electronic
   deeds) and report what the block shows against each.
3. **Witness lines.** Report whether witness fields required by the matched
   entry are present and completed, by field only (never the values).
4. **Electronic signing.** If the document refers to electronic or split
   execution, point to the pack's electronic-execution entries.
5. **Company identifiers.** Compare ACN, ABN, ARBN or NZBN and company names
   (including "Pty Ltd" or "Limited") across the parties clause, recitals and
   signature blocks. Report any mismatch.

**Governance (minutes and resolutions)**

6. **Statutory checkpoints.** For each `governance` entry that applies to the
   body (company board, members, or other body named in the pack), report what
   the draft minutes contain: for example a place for the chair's signature and
   date, recorded declarations of interest, and whether a written resolution
   records the signature or assent of every director.

## Output

After the Legal for Cowork output, add exactly one section:

```
#### Jurisdiction overlay — <pack ids with versions> (<status>)

| Observation | Location | Pack reference | For counsel |
| --- | --- | --- | --- |
```

- **Observation**: what the document shows, in neutral words.
- **Location**: clause, schedule or signature block, with the file name.
- **Pack reference**: the entry `id` and its authority, for example
  `au.exec.s127-methods — Corporations Act 2001 (Cth) s 127(1)`.
- **For counsel**: the question the observation raises, never the answer.

If no entry applies, write one line instead of a table:
`No jurisdiction-specific execution or governance observations from <packs>.`

End with: `Pack checklist — verify each reference against the primary text.`

## Guardrails

- Never write that a document is validly executed, binding, enforceable, or
  that a resolution was validly passed or quorum was met.
- Never invent a signatory, witness, date, seal or company number.
- Never reproduce personal details from signature blocks (see jx-personal-identifiers).
- Never edit the document or propose wording unless the Legal for Cowork skill
  in use is a drafting skill and the user asked for wording; then mark it
  "Suggested wording — for counsel review".
