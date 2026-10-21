# 5. Roadmap and prioritisation

Status: v0.1, October 2026. Owner: product owner. Vocabulary follows the Scaled Agile Framework:
epics and features, Weighted Shortest Job First (WSJF), Program Increment (PI) objectives.

## 5.1 How the MVP was cut

The MVP is the smallest thing that tests the three hypotheses that would kill the product (H1
rework, H2 complete on arrival, H3 officer trust) and the one that would stop it being allowed at
all (H4 control). Everything that makes it nicer to use but does not test a hypothesis waits:
chat (US-14), model wording (US-13), queue views (US-15).

## 5.2 What comes next, ranked by WSJF

WSJF = cost of delay / job size, where cost of delay = business value + time criticality + risk
reduction or opportunity enablement. Relative scores on the modified Fibonacci scale (1, 2, 3, 5,
8, 13, 20), set by the product owner with the tech lead; job size from the team's estimate.

| Item | Business value | Time criticality | Risk reduction / opportunity | Cost of delay | Job size | WSJF | Rank |
|---|---|---|---|---|---|---|---|
| US-16 Cycle-time and rework measures | 8 | 13 | 8 | 29 | 3 | **9.67** | 1 |
| US-15 Officer queue with ageing and service levels | 5 | 3 | 2 | 10 | 3 | **3.33** | 2 |
| US-14 Conversational intake in the collaboration platform | 13 | 5 | 8 | 26 | 8 | **3.25** | 3 |
| US-13 Model-assisted TOR wording with a fact validator | 5 | 2 | 3 | 10 | 5 | **2.00** | 4 |
| US-17 Catalogue and past-purchase reuse | 5 | 1 | 3 | 9 | 5 | **1.80** | 5 |
| Procurement-suite integration (case becomes the record) | 8 | 3 | 5 | 16 | 13 | **1.23** | 6 |
| US-18 Model planner behind the same policy engine | 3 | 1 | 5 | 9 | 8 | **1.13** | 7 |

The calls worth explaining:

- **Measurement first.** US-16 outranks everything because the pilot cannot reach a go / no-go
  without a measured cycle time. Time criticality 13: without it, six weeks of pilot produce opinions.
- **Chat goes third, just behind the queue view.** Almost the same WSJF, but the queue view is a
  third of the size and de-risks the officers' side first. Chat is the biggest adoption lever (H5) and the
  start of the reuse path in [03](03-options-and-investment-case.md); it enters the PI as an
  uncommitted objective.
- **Model wording is fourth, on purpose, and below the PI 2 capacity line.** It makes drafts read
  better, but readability is not the bottleneck the discovery found. It ships only behind the validator that already proves AC3.
- **A model planner is last.** The rule planner is reproducible and auditable; a model planner
  earns its place only if evidence shows requests the rules handle badly.

## 5.3 Now / Next / Later

| Horizon | What | Exit condition |
|---|---|---|
| **Now** (v0.1, done) | Policy engine, agent loop, human checkpoints, package, events | All Must stories Done with tests; AC1 to AC5 green in CI |
| **Next** (PI 2: pilot) | US-16, US-15; US-14 if capacity; six-week pilot in one unit with a comparison unit | Go / no-go decision on H2 and H3; H4 signed by the head of procurement |
| **Later** (PI 3+, only after go) | Channel on the enterprise assistant platform at scale; procurement-suite integration; US-13; second process (HR policy questions) | Second unit live; cycle-time gain holds outside the pilot unit |

## 5.4 PI 2 objectives (pilot increment)

| Objective | Type | Business value (1-10) | Measured by |
|---|---|---|---|
| Baseline and cycle-time measures live before the first pilot request | Committed | 10 | US-16 in production; baseline from 30 historical requests |
| One unit uses the desk for all new service requests for six weeks | Committed | 9 | Share of the unit's requests entered through the desk |
| Officers review from the package alone, with queue ageing visible | Committed | 7 | US-15; officer survey at week 3 |
| Head of procurement and internal audit sign off the control design | Committed | 8 | Signed note on 06-human-control.md |
| Requesters answer intake questions in chat | Uncommitted | 6 | US-14 in the pilot unit |

## 5.5 Kill criteria (fixed before the pilot)

Stop the product, keep the improved form and template, and write up why, when any of these holds
at the end of the pilot:

- First-review approval does not improve by 15 points over the comparison unit.
- Officers disagree with the recommended method in more than 10% of cases for reasons that are
  rules, not judgment, and the disagreement recurs after a fix.
- The head of procurement or internal audit will not sign off the human-control design.
