# Working agreement

## Definition of Ready (a story can enter an iteration when)

- It has a user, a need and a reason ("As a ... I want ... so that ...").
- Its acceptance criteria are observable: a reviewer can check each one without asking the author.
- Dependencies outside the team are resolved or named with an owner and a date (for example, the
  DPO's sign-off on a schema change).
- It is estimated, and it fits in one iteration (8 points or fewer; split otherwise).

## Definition of Done (a story is Done when)

- Every acceptance criterion is met and the product owner has accepted it at the demo.
- At least one test named `test_<STORY>_...` proves it; `python tools/trace.py` passes. CI enforces this.
- CI is green: tests, traceability, scrub check.
- Any changed rule, checkpoint or schema is updated in the PRD, 06-human-control.md or the decision log in the same PR.
- The CHANGELOG has a line for anything a user would notice.

## Rituals

| Ritual | When | Who | Output |
|---|---|---|---|
| Iteration planning | Monday, week 1, 60 min | Team | Iteration goal (one sentence) and committed stories |
| Stand-up | Daily, 15 min | Team | Blockers named with an owner |
| Backlog refinement | Wednesday, week 2, 45 min | Product owner, tech lead, one engineer | Next iteration's stories Ready, WSJF scores refreshed |
| Demo | Friday, week 2, 30 min | Team plus a requester and an officer (the real users) | Accepted / not accepted per story; feedback as new backlog items |
| Retrospective | Friday, week 2, 30 min | Team | One change to try next iteration |

## Pull requests

- Small: one story or less per PR. The title starts with the story id (`US-10: ...`).
- One reviewer from the team; the DPO as well if identifiers or the event schema change; the head of procurement if `config/policy.json` changes.
- The PR template's checklist is the Definition of Done.

## Disagreements

Decisions about *what* and *in which order* are the product owner's; about *how* the tech lead's. If either
is challenged, write the disagreement as a decision-log entry with both options; the accountable
person decides within two working days and the entry records why.
