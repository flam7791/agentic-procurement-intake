# Iteration plan

Planning assumption: two engineers and a part-time designer, two-week iterations, 16 points per
iteration (a guess until three iterations of real velocity exist). Iterations 1 to 3 are the MVP
in this repository: planned as iterations so scope and estimates can be inspected, but **built by
one person for this portfolio**, so the velocity is not evidence about a team.

## PI 1 (MVP)

### Iteration 1 - "understand the request, choose the method" (Done)

| Story | Points | Result |
|---|---|---|
| US-01 Accept partial requests | 3 | Done |
| US-02 Category chosen or inferred | 3 | Done |
| US-03 Method from policy thresholds | 3 | Done |
| US-04 Reuse first: framework call-off | 3 | Done |
| **Total** | **12** | |

Demo: an officer sees a method with its rule, and a framework call-off instead of a tender.

### Iteration 2 - "a draft an officer could approve" (Done)

| Story | Points | Result |
|---|---|---|
| US-05 Split-purchase guard | 3 | Done |
| US-06 Named supplier needs a justification | 2 | Done |
| US-07 TOR draft, nothing invented | 5 | Done |
| US-08 Completeness checklist and questions | 3 | Done |
| **Total** | **13** | |

Demo: a requester's partial request comes back as questions; a complete one as a draft TOR.

### Iteration 3 - "people decide, and it shows" (Done)

| Story | Points | Result |
|---|---|---|
| US-09 Human checkpoints and four eyes | 5 | Done |
| US-10 Request text is data | 3 | Done |
| US-11 Officer package with audit trail | 3 | Done |
| US-12 Usage events for the tracker | 2 | Done |
| **Total** | **13** | |

Demo: a request walked through requester, officer and budget holder; the agent's attempt to
approve refused; a planted instruction flagged and withheld.

## PI 2 (pilot), first iteration planned

Iteration goal: **the pilot can measure itself from day one.**

| Story | Points | WSJF rank | Note |
|---|---|---|---|
| US-16 Cycle-time and rework measures | 3 | 1 | Committed; blocks the pilot start |
| US-15 Officer queue with ageing | 3 | 2 | Committed |
| Baseline coding of 30 historical requests per unit | 3 | - | Committed; product owner with the champion |
| US-14 Chat intake: question flow and resumable state (first slice) | 5 | 3 | Stretch; split from the 8-point story |
| **Total** | **14** (9 committed) | | |

Risks: request history for the pilot unit may be incomplete (affects US-05 in the pilot); the
collaboration platform's connector approval may take longer than an iteration (affects US-14).
