# Reviewer rubric

The scorer checks structure. Qualified reviewers check substance. Score each
reviewed case 0–2 on each line, and record the scores in `review.csv` in the
run folder. Use these columns: `case, reviewer, accuracy, relevance, restraint,
noise, original_quality, comment`.

| Criterion | 0 | 1 | 2 |
| --- | --- | --- | --- |
| **Accuracy** — the overlay describes what the document shows, and the pack reference matches | Wrong fact or wrong entry | Minor imprecision | Accurate |
| **Relevance** — every overlay row matters for this document and jurisdiction | Mostly irrelevant rows | Some padding | All relevant |
| **Restraint** — observations only; legal conclusions left to counsel | States a conclusion (valid, compliant, time-barred) | Borderline phrasing | Neutral throughout |
| **Noise** — the overlay doesn't repeat the original findings | Duplicates most findings | Some duplication | No duplication |
| **Original quality** — the add-on run's original output is as good as the baseline run's | Worse (missing findings, changed position) | Slightly different | Equivalent |

## Release thresholds

- No 0 on Restraint or Original quality in any reviewed case.
- An average of at least 1.5 on Accuracy and Relevance across reviewed cases.

## Pack feedback

When a reviewer finds a wrong or missing pack entry, they open an issue
labelled `pack-correction`. The issue names the entry id, what is wrong, and
the primary source. Fixes go through the normal pull request review.
