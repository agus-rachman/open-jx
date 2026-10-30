# Contributing to open-jx

Thank you for helping. You can add a jurisdiction, improve an existing pack,
improve a skill, or add eval cases.

## Ground rules

1. **No copied content.** Don't copy text from the Legal for Cowork plugin,
   commercial legal databases or paywalled commentary. Short quotations of
   legislation and court practice notes are fine.
2. **Observations, not advice.** Pack entries describe what to look for in a
   document. The validator rejects phrases like "is enforceable" and "you must".
3. **Cite everything.** Every legal entry needs an authority and an https
   source, preferably the official register.
4. **No confidential material.** No client names, firm precedents, playbooks or
   matter details anywhere, including tests and commit history.
5. **Sign off your commits** under the Developer Certificate of Origin:
   `git commit -s`.

## Add a jurisdiction

1. Open an issue with the **New jurisdiction** template. Name the jurisdiction,
   its code, the maintainers, and a qualified reviewer.
2. Copy `packs/_template/` to `packs/<code>/`. Codes are ISO 3166 in lower
   case: `sg` for a country, `ca-on` for a subdivision. In Copilot Cowork, the
   `jx-new-pack` skill can draft the files with you.
3. Fill at least `pack.yaml`, `sources.yaml`, `citation.yaml`,
   `identifiers.yaml` and `calendar.yaml`. Leave `verified` and `verified_by`
   as `null`.
4. Run:
   ```
   python tools/validate_packs.py packs/<code>
   python tools/build_plugin.py
   python evals/check_package.py dist/open-jx-<version>.zip
   ```
5. Add eval cases (see `evals/README.md`), including **at least one fail-closed
   case** where the skills must refuse or leave a point undecided. Then run
   `python evals/score.py lint`.
6. Open a pull request using the template. CI runs the same checks.

## Review and status

- A **core maintainer** reviews structure, wording and guardrails.
- A **qualified reviewer** for the jurisdiction checks every legal entry
  against the primary source and sets `verified` (the date, quoted) and
  `verified_by` (their GitHub handle).
- When every legal entry is verified, the reviewer may set the pack to `beta`.
  A second qualified reviewer can then make it `stable`.
- Reviewers are added to `CODEOWNERS` for their pack.

## Imported data

Some Australian entries come from l0cka/legal-skills (MIT). Generated files
(`deadlines.yaml`, `privacy.yaml`) are never edited by hand. Refresh them with
`python tools/import_legal_skills.py --upstream <checkout>`, then review the diff.
Hand-written entries with a `provenance` block keep that block when edited.
Upstream evidence states don't count as open-jx verification: reviewers still
set `verified` and `verified_by`.

The deadline script computes only from entries whose upstream
`evidence.state` is `verified`. Never change an evidence state to make a
computation run.

## Keep packs current

- Entries verified more than 12 months ago produce warnings; more than 24
  months, errors.
- A scheduled CI job runs weekly to check pack links and freshness.
- If a pack's maintainers don't respond for 90 days, it becomes `unmaintained`
  and the router warns users.

## Improve a skill

Skill changes affect every jurisdiction, so they need a core maintainer's
approval. They also need a full eval run on at least the AU and NZ cases, with
the scorer self-test passing (`python evals/selftest/selftest.py`).
