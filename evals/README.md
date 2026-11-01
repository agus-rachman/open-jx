# open-jx eval suite

This suite checks that open-jx and the Legal for Cowork skills work side by side
in Microsoft Copilot Cowork:

- **Trigger:** the router fires and loads the right packs.
- **Overlay:** the right pack entries are cited.
- **Non-interference:** the original skill's output and position don't change.
- **Guardrails:** no leaked identifiers, no advice wording, no restricted court
  content.

## What's here

| Path | Purpose |
| --- | --- |
| `check_package.py` | Static checks on the built zip against the Copilot Cowork packaging rules. No tenant needed. |
| `cases/cases.yaml` | 37 cases. 23 run side by side with Legal for Cowork across every Australian state and territory, the Commonwealth and New Zealand, plus a jurisdiction with no pack (Hong Kong), a conflict case and an injection case. 9 cover computed deadlines, fail-closed deadlines, citation routing, limitation and privacy. 5 cover Singapore: company and individual deeds, NRIC suppression, the court AI Guide and a fail-closed deadline. |
| `cases/trigger.yaml` | 49 short prompts that test router selection only. |
| `fixtures/` | Synthetic `.docx` documents (fictional parties and planted fake identifiers) plus the generator script. |
| `score.py` | `lint`, `sheet` and `score` commands. |
| `rubric.md` | Reviewer rubric for the qualities a script can't judge. |
| `selftest/` | Synthetic passing and failing transcripts that prove the scorer catches each failure. |

## Release gates

| Measure | What it counts | Gate |
| --- | --- | --- |
| Trigger | Router brief present with the correct packs (cases + trigger set) | ≥ 95% |
| Overlay | Expected overlay sections, pack references and mentions | ≥ 90% |
| Non-interference | Original markers present, overlay after the original, same position as baseline, clean baseline | 100% |
| Guardrails | No leaked identifiers, no advice wording, no restricted court content, withheld line | 100% |
| Court notes | Court AI note present, before the original output, citing the right entry | 100% |

## Running a pilot evaluation

1. **Build and check the package.**
   ```
   python tools/build_plugin.py
   python evals/check_package.py dist/open-jx-0.1.0.zip
   python evals/score.py lint
   ```
2. **Install it for testers.** Share the zip with the tester group (see
   `docs/COPILOT-SETUP.md`). Testers add the pilot custom-instruction snippet,
   but without a default jurisdiction, so the trigger cases that expect a
   question can pass.
3. **Create a run folder.**
   ```
   python evals/score.py sheet --run evals/runs/2026-11-pilot
   ```
   This writes `RUNSHEET.md` (what to attach, type and answer for every case)
   and empty transcript files.
4. **Run every case twice**, each in a new conversation:
   - **baseline:** open-jx switched off in the conversation's Sources picker.
   - **addon:** open-jx switched on.

   Paste every assistant reply into `baseline/<case>.md` or `addon/<case>.md`.
   Run the trigger prompts once each with open-jx on and save them to
   `trigger/<id>.md`.
5. **Score.**
   ```
   python evals/score.py score --run evals/runs/2026-11-pilot
   ```
   This writes `report.md`, `results.csv` and `results.json`. The exit code is 1
   if a gate fails.
6. **Review.** The AU and NZ reviewers grade a sample with `rubric.md`,
   including at least every failed case and every execution and court case.

Model output varies between runs. For a release decision, run the full suite
at least twice and use the lower score.

## Adding cases for a new jurisdiction

Contributors who add a pack should add at least three cases:

- an execution or governance case
- a dates case
- a trigger prompt per detection signal (name, governing-law wording, court,
  identifier)

Each case's fixtures go in `fixtures/make_fixtures.py`. Use fictional parties
and fake identifiers. Then run `python evals/score.py lint`.

Cases with `original_skill: none` have no Legal for Cowork skill behind them.
Run them in add-on mode only.

## Self-test

```
python evals/selftest/selftest.py
```

This must print `0 self-test failure(s)` before any change to `score.py` is merged.
