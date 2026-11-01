---
name: jx-dates-and-deadlines
description: >-
  Adds a labelled jurisdiction overlay on dates after the Legal for Cowork skill
  has answered: business-day and working-day definitions, local and regional
  public holidays, statutory rules for counting time, and where limitation
  periods are found, for Australia (each state and territory), New Zealand and
  Singapore.
  Computes candidate court and tribunal deadlines from verified rule and
  holiday tables. Use after extract-obligations-and-deadlines,
  build-case-chronology, summarize-legal-matters or identify-regulatory-gaps
  when an Australian, New Zealand or Singapore pack is loaded; when the user asks "when is
  the defence due", "when must we appeal" or "what is the limitation period";
  or about business days, public holidays, Matariki, anniversary days or
  Melbourne Cup Day in a deadline.
license: Apache-2.0
metadata:
  author: open-jx contributors
  version: "0.1.1"
---

# Dates and deadlines overlay (open-jx)

Show where a local calendar or time-counting rule could change a date the Legal
for Cowork skill reported. You flag the dependency and never recalculate its
dates. Candidate procedural deadlines come only from the bundled script.

## Before you start

- Use the pack content that **jx-router** loaded. If no `**Jurisdiction:**`
  brief appears earlier in this conversation, run jx-router first.
- Wait until the Legal for Cowork skill has finished. Never overwrite a date it
  reported.

## What to check

For each deadline, notice period or time limit in the original output:

1. **Day basis.** Does the document define "Business Day", "Working Day" or
   "day", and by reference to which place? If not defined, name the places whose
   holidays could apply (the governing-law jurisdiction and the place of
   performance or notice).
2. **Local holidays.** Use the pack's dated holiday table (`deadlines` section)
   for those places, with its coverage dates and caveats, including part-state
   or regional days (for example metropolitan-only days in Victoria, regional
   anniversary days in New Zealand, and bank-only holidays). If no table covers
   the place or the date, name the official holiday source instead. Never list
   holiday dates from memory.
3. **Statutory counting rules.** Where a time limit comes from legislation or
   court rules, point to the pack's `time_computation` entries (for example how
   the first day is counted, and what happens when the last day is not a
   business day). Some New Zealand "working day" definitions exclude a
   Christmas and New Year period; the pack names where to check.
4. **Limitation periods.** If the output mentions a limitation date, or the user
   asks for a limitation period, give the pack's candidate general period and
   authority for the governing jurisdiction, plus every special-regime flag
   that may apply (child abuse, defamation, personal injury, contribution,
   deceased estates, disability, fraud and concealment). Call it a candidate;
   the period that applies is always a counsel decision.

## Candidate court and tribunal deadlines

Only when the user asks for a procedural deadline (a defence, appearance,
appeal or tribunal application) and gives the trigger date:

1. Find the rule: run `python scripts/compute_deadline.py --list`, or read
   [references/deadline-rules.md](references/deadline-rules.md). Match the
   forum and step to one `table_id` and `period_rule_id`. If none matches, say
   the rule is not in the tables and give no date.
2. Compute with the script, never by mental arithmetic:
   `echo '{"table_id": "...", "period_rule_id": "...", "trigger_date": "YYYY-MM-DD"}' | python scripts/compute_deadline.py`
   The script reads [references/deadline-tables.json](references/deadline-tables.json).
3. Report its result exactly. `computed` → "Candidate date: <date> (<day>)"
   with the citation, the provisions applied and every warning.
   `identify_only` → name the rule and give the script's reason; give no date.
4. If scripts cannot run in this session, identify the rule and its citation
   and say no date was computed.
5. Every candidate date carries: "Candidate only — the responsible lawyer must
   confirm before reliance; confirm the registry was open."

## Output

After the Legal for Cowork output, add exactly one section:

```
#### Jurisdiction overlay — <pack ids with versions> (<status>)

| Date item | Basis in document | Local calendar point | Pack reference |
| --- | --- | --- | --- |
```

Put candidate deadlines in a second table under the same heading:

```
| Step | Rule | Trigger date | Candidate date | Warnings |
| --- | --- | --- | --- | --- |
```

If nothing applies: `No jurisdiction-specific date observations from <packs>.`
End with: `Pack checklist — verify each reference against the primary text.`

Licence notice for the adapted script and data: [references/THIRD-PARTY-NOTICES.md](references/THIRD-PARTY-NOTICES.md).

## Guardrails

- Never state that a deadline has passed, been met or been missed because of a
  local rule. Say what the date depends on.
- Never compute a limitation expiry date or say a claim is time-barred.
- Never produce a procedural date except from the script's `computed` result.
- Never list public holiday dates from memory; cite the official source in the pack.
