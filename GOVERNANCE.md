# Governance

## Roles

| Role | Who | Responsibilities |
| --- | --- | --- |
| Repository owner | the project founder | Releases, licences, final decisions, admin access |
| Core maintainers | repository owner plus invited contributors | Skills, schema, tooling, CI, evals; review every pull request for structure and guardrails |
| Pack maintainers | listed in each `pack.yaml` and `CODEOWNERS` | Keep their pack current; triage `pack-correction` issues |
| Qualified reviewers | lawyers admitted in the pack's jurisdiction | Verify legal entries; approve status changes to `beta` and `stable` |

For v0.1, the core team is the repository owner. Internal Australian and New
Zealand reviewers are the first pack maintainers and reviewers. Reviewers act in
a personal capacity: their review is not legal advice, and it is not given on
behalf of their employer.

## Decisions

- Pack content: the pack's qualified reviewer decides. A core maintainer can
  block for structure, wording or guardrail reasons only.
- Skills, schema and releases: lazy consensus among core maintainers over five
  working days. The repository owner decides if there is no consensus.
- Disputes: open an issue labelled `governance`. The repository owner decides
  within 14 days.

## Releases

A release requires:

1. CI passing: pack validation, package checks, eval lint and the scorer self-test.
2. A full eval run on Copilot Cowork that meets the gates in `evals/README.md`,
   with the report attached to the release.
3. Release notes listing pack status changes.

## Continuity

At least two people hold admin access to the repository. Ownership can move to a
GitHub organisation without any change to the licences.
