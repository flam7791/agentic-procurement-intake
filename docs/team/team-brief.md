# Team brief: procurement intake desk

One page for the people who take this from v0.1 to a running pilot. Read this first; everything
else is linked.

## Mission

Requests to buy services reach procurement ready to approve, so purchases start weeks earlier,
with the rules applied the same way every time and every decision taken by a person.

## Where we are

v0.1 works end to end on fictional data: a described need in, an approvable package out, three
human checkpoints enforced in code ([README](../../README.md#see-it)). Twelve stories are Done and
proved by tests in CI. What we do **not** know yet is whether real requests arrive complete and
whether officers trust the recommendations. Finding that out is the team's job in PI 2.

## What done looks like for PI 2 (five iterations of two weeks)

1. Cycle-time and rework measures live before the first pilot request (US-16).
2. Officers' queue with ageing (US-15); chat intake (US-14) if capacity allows.
3. Six-week pilot run in one unit, with the comparison unit, and the go / no-go taken on the
   rules in [08-metrics-and-pilot.md](../product/08-metrics-and-pilot.md).
4. Every confirmed problem from the pilot is a backlog item with a failing test.

## Constraints that are not up for debate in this phase

- **The agent prepares; people decide** (D2). No feature lets the agent role change a status past
  the draft. The test that tries every short action sequence stays green.
- **The policy belongs to procurement** (D3). Code reads `config/policy.json`; it never writes it.
- **Nothing invented in a TOR** (D7). Any model wording ships behind the fact validator.
- **Pseudonymous ids only.** Anything touching identifiers or the event schema goes past the DPO.
- **No new runtime dependencies** without a decision-log entry.

## Team and decision rights

| Role | Who (planned) | Owns |
|---|---|---|
| Product owner | Flavio | Problem, priorities (WSJF), backlog order, pilot design, story acceptance |
| Tech lead / engineer | to be named | Architecture, code quality, estimates, release |
| Engineer | to be named | Delivery of stories, tests |
| Service designer (30%) | to be named | Question wording, package readability, chat flow (US-14) |
| Head of procurement | sponsor | Policy file, pilot unit, go / no-go with the product owner |
| Senior procurement officer | champion | Sampled reviews, officer feedback |
| Internal audit, DPO | reviewers | Human-control sign-off; identifiers and events |

### RACI for the decisions that come up most

| Decision | Product owner | Tech lead | Engineers | Designer | Head of procurement | Audit / DPO |
|---|---|---|---|---|---|---|
| Backlog order and WSJF scores | A/R | C | C | C | C | I |
| Change to a threshold or framework | I | I | I | - | A/R | C |
| Raise a step's autonomy level | R | C | I | I | A | C |
| Change to identifiers or the event schema | R | C | R | - | I | A (DPO) |
| Release to the pilot | A | R | R | C | C | I |
| Go / no-go after the pilot | R | C | I | C | A | C |

## Where things are

Product case: [docs/product](../product/). Backlog: [backlog.csv](backlog.csv). Plan:
[iteration-plan.md](iteration-plan.md). Ways of working: [working-agreement.md](working-agreement.md).
Proof of Done: [traceability.md](traceability.md). Operating model: [OPERATIONS.md](../../OPERATIONS.md).
