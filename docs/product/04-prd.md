# 4. Product requirements: procurement intake desk v0.1

Status: approved for MVP build, October 2026. Owner: product owner. Reviewers (planned): head of
procurement, a procurement officer, internal audit, data protection officer, tech lead.

## Problem statement

Requests to buy services reach procurement incomplete, misclassified and without a usable TOR, so
the first weeks go to rework instead of buying. (Evidence and hypotheses:
[01-discovery.md](01-discovery.md); the redesigned process: [02-service-blueprint.md](02-service-blueprint.md).)

## Goal for v0.1

**Approvable on first review.** A requester goes from a described need to a confirmed request
package with every required item met, and a procurement officer can decide from the package alone:
method with its rule, reuse checked, policy flags explained, TOR drafted, audit trail attached.

## Non-goals for v0.1

- Not sourcing, evaluation of offers or contracting: the product ends at an approved request.
- Not a system of record: cases are files; integration with the procurement suite comes after the pilot.
- No automated decisions of any kind: the agent prepares; people confirm, approve, return and sign off.
- No model-written text: v0.1 drafts from the template; model wording is US-13, behind a fact validator.
- No conversational channel: the request arrives as answers to a guided form (chat is US-14).
- No supplier recommendations or contact with suppliers.

## Users and the core flow

1. The **requester** answers the intake questions (title, need, objective, scope, deliverables,
   dates, value, budget code, supervisor, personal data, supplier if any).
2. `intake-desk run` prepares the case: screening, category, reuse check, 12-month total, method,
   sole-source check, TOR draft, checklist, routing. Missing items come back as questions.
3. The requester reads the draft and **confirms** it (`intake-desk confirm`).
4. The **procurement officer** in the routed queue **approves or returns** it with a note.
5. At or above the sign-off threshold, a **budget holder** (not the officer, not the requester)
   **signs off**.
6. Each confirmation emits a usage event in the ai-adoption-tracker format, so the pilot's own
   scale-or-stop review rests on evidence.

## Requirements

| ID | Requirement | Priority | Story |
|---|---|---|---|
| R1 | Accept partial requests; turn every gap into one plain question; stop only on malformed input, naming the field | Must | US-01 |
| R2 | Category chosen, or inferred and confirmed; ambiguity becomes a question listing the options | Must | US-02 |
| R3 | Method from the procurement-owned policy file; the rule names the method, value and threshold band | Must | US-03 |
| R4 | Active framework agreement with enough ceiling -> call-off; scope uncertain -> officer confirms | Must | US-04 |
| R5 | Method set on the unit's 12-month total for the category; split purchases flagged with both methods | Must | US-05 |
| R6 | Named supplier on a competitive method requires a justification | Must | US-06 |
| R7 | TOR drafted from the template; unknowns marked [TO CONFIRM]; no number or date that is not in the request | Must | US-07 |
| R8 | Completeness checklist; case blocked while a required item is unmet | Must | US-08 |
| R9 | Human checkpoints and four eyes enforced in code; the agent role cannot decide | Must | US-09 |
| R10 | Instruction-like text in a request flagged, withheld from the draft, never followed; case blocked until rewritten | Must | US-10 |
| R11 | Package as Markdown, HTML (light and dark) and JSON, with the audit trail of tool calls and the decisions by people | Must | US-11 |
| R12 | Usage events in the ai-adoption-tracker format with pseudonymous ids | Should | US-12 |

Acceptance criteria per story: [../team/backlog.csv](../team/backlog.csv). Each Done story is
proved by a named test ([../team/traceability.md](../team/traceability.md)).

## Success metrics

| Metric | Type | Target for the pilot | Source |
|---|---|---|---|
| Requests approved on first officer review | North star (user value) | from the baseline (H1 expects under 40%) to 70%, and 30 points above the comparison unit | case history: approved without a return |
| Median days from submission to approval | Outcome | -30% against the baseline and the comparison unit | case history (US-16) |
| Rework rounds per request | Outcome | median 1 or fewer | returns + needs-information cycles |
| Officer agreement with the recommended method | Guardrail (trust) | 90% or more; every disagreement explained | officer note on approval |
| Decisions taken by the agent | Guardrail (control) | 0, always | workflow log; test in CI |
| Returning requesters | Adoption | 60% use it for their next request unprompted | case files by pseudonymous id |

## Risks

| Risk | Mitigation |
|---|---|
| Officers rubber-stamp the recommendation | The rule and evidence are shown, not just the answer; agreement tracked; sampled reviews in OPERATIONS.md |
| Requesters game the value to stay under a threshold | 12-month total and split flag; the value stated is in the TOR the requester confirms |
| The policy file drifts from the real policy | Owned by procurement; versioned; every change re-runs the regression set |
| Staff read it as surveillance of who buys what | Pseudonymous ids; no per-person reporting; DPO reviews the event schema |
| Prompt injection through form fields | Screening blocks the case; no tool can approve whatever the text says; planted-injection eval in CI |
| "AI approves purchases" headline | Approval is impossible for the agent by construction; the package says who decided |

## Release criteria for v0.1

All Must stories Done and proved by tests in CI; the sample requests exercise every outcome (AC2);
the no-approval property holds for every tested sequence (AC4); the scrub check is clean; the
README states that the organisation and data are fictional.
