# How open-jx works with Legal for Cowork

Both plugins run side by side. Legal for Cowork does the legal task and produces
its own output exactly as designed. open-jx sets the jurisdiction first and adds
a separately labelled jurisdiction section after that output.

## Runtime sequence

1. **Trigger.** `jx-router` is selected when a legal request names a
   jurisdiction, a document has a governing-law clause, or the user's custom
   instructions ask for it.
2. **Resolve and load.** The router maps labels to legal units ("Australia" →
   `au` plus the state; "New Zealand" → `nz`). It reads
   `references/jurisdictions.md` and the matching pack files, then prints the
   brief:
   ```
   **Jurisdiction:** New South Wales, Australia — packs au@0.1.0, au-nsw@0.1.0 (draft)
   Detected from: governing-law clause, cl 22.1 · Overlays: jx-personal-identifiers, jx-execution-and-governance
   ```
3. **Prepare.**
   - `jx-personal-identifiers` applies to the whole task.
   - `jx-sources-and-citation` applies to research and writing.
   - `jx-court-ai-rules` prints a **Court AI note** before any work that may be
     used in proceedings.
4. **Original skill runs unchanged.** Its question cards, guardrails, hand-off
   rules, source limits and output format all stand.
5. **Overlay.** After the original output, an after-skill adds
   `#### Jurisdiction overlay — <packs> (<status>)` with a table of
   observations and pack references, ending with "Pack checklist — verify each
   reference against the primary text."

## Routing table

| Legal for Cowork skill | Before | After |
| --- | --- | --- |
| check-execution-readiness | identifiers | execution and governance |
| draft-new-contract | identifiers | execution and governance |
| analyze-related-contracts | identifiers | execution and governance |
| draft-minutes-and-resolutions | identifiers | execution and governance |
| extract-obligations-and-deadlines | identifiers | dates and deadlines |
| summarize-legal-matters | identifiers | dates and deadlines |
| build-case-chronology | court AI rules, identifiers | dates and deadlines |
| identify-regulatory-gaps | sources and citation | dates and deadlines |
| compare-across-jurisdictions | sources and citation | — |
| legal-reasoning, draft-legal-memo | sources and citation (+ court AI rules if for filing) | — |
| explain-legal-concepts, edit-contract, review-contract, compare-key-terms | identifiers | — |
| check-defined-terms, check-cross-references, summarize-redlines, create-playbook, improve-legal-prompt | identifiers | — |

## Compatibility rules

- **Output order.** Overlays always follow the original output as a separate
  section. Some original skills must end their reply at a fixed point, so
  nothing is inserted inside their tables or before their closing questions.
- **Source limits.** Where an original skill forbids outside research (the
  execution-readiness check does), overlays use only the installed packs.
- **Hand-off rules.** Overlays never do work an original skill assigns to
  another skill.
- **Guardrails.** If an open-jx rule and a Legal for Cowork guardrail
  conflict, the Legal for Cowork guardrail wins.
- **Naming.** Every add-on skill uses the `jx-` prefix, so none collides with a
  built-in skill (Copilot Cowork does not let plugin skills override built-in
  skills).
- **Data, not instructions.** Packs are compiled to Markdown reference files
  inside `jx-router`. Their text is data, and validation rejects
  instruction-like text in packs.

## Direct requests

Some requests have no matching Legal for Cowork skill, and an open-jx skill
answers them directly:

- **Citation and legislation checks** go to jx-sources-and-citation. It routes
  each citation to the issuing court's official publisher, never automates
  around bot challenges, and gives one of five outcomes.
- **Procedural deadlines and limitation periods** go to jx-dates-and-deadlines.
  Candidate dates come only from the bundled script, and limitation periods are
  candidates with special-regime flags.

## Graceful degradation

| Situation | Behaviour |
| --- | --- |
| open-jx switched off or not installed | Legal for Cowork runs as shipped |
| Jurisdiction with no pack | Brief says "no open-jx pack installed"; no overlay |
| "Australia" with no state | `au` only; brief says state-specific items are not loaded |
| Jurisdiction-neutral task | Brief says "not required"; identifiers rule only |
| Nothing detected, local law needed | One question: "Which jurisdiction should I use?" |
| Pack status `unmaintained` or `stale` | Router warns in the brief |
| Deadline rule unverified, date outside the holiday table, or inside an uncertain window | Script returns `identify_only`; the rule is named and no date is given |
| Scripts can't run in the session | Rule and citation identified; no date computed |
| Court with no mapped publisher | Citation reported `UNVERIFIABLE`, never as fabricated |

## Limits to know

- **Skill selection is probabilistic.** Copilot Cowork chooses skills from
  their descriptions, and plugin hooks and slash commands are not supported
  yet. Detection is reinforced by the router description, a gate at the top of
  every overlay skill, the users' custom instructions and the visible brief
  line. The trigger rate is measured by the eval suite.
- **Companion file limit.** A skill can carry at most 20 companion files.
  `jx-router` holds one index plus one file per pack. Past 19 packs, the build
  groups subdivision packs into one file per country automatically. Beyond
  that, publish regional builds.
- **Built-in skill versions.** The routing table names the Legal for Cowork
  skills as of version 1.0.10. Re-run the eval suite when Microsoft updates them.
