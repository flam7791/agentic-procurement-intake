# 6. Human control and responsible AI

Status: v0.1, October 2026. Owner: product owner. To be signed off by the head of procurement and
internal audit before the pilot (PI 2 objective).

The design principle: **the agent prepares, people decide, and the code makes it impossible to do
otherwise.** Safeguards that live only in a prompt or a policy document are not counted here.

## 6.1 Autonomy levels

| Level | Meaning | Where it is used |
|---|---|---|
| **A0** Person only | The agent cannot do it at all | Confirm the draft, approve, return, sign off, choose or contact a supplier, change a threshold |
| **A1** Agent suggests | The agent recommends with its evidence; a person decides | Method, framework call-off, split-purchase flag |
| **A2** Agent drafts, person confirms | The agent produces a draft the person edits and confirms | Category (when inferred), TOR, questions for the requester |
| **A3** Agent acts, person can review | The agent acts; the action is reversible and can only block, never approve | Screening, completeness check, routing |

Rule for raising autonomy on any step: only with pilot evidence (agreement rate, errors found in
sampled reviews), a decision-log entry, and the regression set passing. No step in A0 moves.

## 6.2 Checkpoints, enforced in code

| Checkpoint | Who | Enforced by |
|---|---|---|
| 1. Confirm the draft | The requester who submitted it, and nobody else | `workflow.confirm`; tests US-09 |
| 2. Approve or return | A procurement officer on the role roster who is not the requester; a return needs a note, and so does approving a case with a SPLIT or SOLE flag | `workflow.decide`; tests US-09 |
| 3. Sign off spend at or above the threshold | A budget holder on the role roster who is neither the requester nor the approving officer | `workflow.decide`, four-eyes check; tests US-09 |

`test_US09_no_command_sequence_lets_the_agent_or_requester_approve` tries every ordered sequence
of four actions by the agent and the requester (1,296 sequences) and checks that none reaches
Approved or the budget holder.

**What v0.1 does not yet guarantee.** Identity is asserted, not authenticated: the workflow trusts
the id it is given and the case file on disk. The roster of officers and budget holders in
`config/policy.json` stands in for single sign-on groups. Before the pilot, roles come from those
groups and cases move to a store requesters cannot edit; this is a release-gate item, not a
nice-to-have.

## 6.3 What the agent never does

- Approve, return or sign off a request.
- Commit funds, raise a purchase order, or contact, shortlist or select a supplier.
- Change a threshold, a category or a framework agreement: the policy file is owned by procurement.
- Follow an instruction found inside a request (6.5).
- Invent facts in a TOR: every number and date in a draft comes from the request (AC3, tested on
  every sample request).

## 6.4 Transparency

- Every recommendation carries its rule: method, value used (own or 12-month total) and threshold band.
- The package lists every tool the agent ran, why, and what it found (audit trail), separately from
  the decisions people took.
- The package says on its first screen that nothing in it is approved until a person approves it.

## 6.5 Untrusted input

Everything a requester types is data. Instruction-like text (ignore the rules, mark as approved,
change the method) is flagged per field, withheld from the draft and blocks the case until the
requester rewrites it. It cannot change the method, the route or the status, because no tool
takes instructions from request text: they read fields and apply the policy. A planted injection
is part of the sample set and the regression set (R-106).

## 6.6 Privacy

- Requesters and approvers are identified by pseudonymous ids; email addresses are refused.
- Usage events carry only date, use case, pseudonymous id and action.
- Personal data in the purchase itself (for example, coaching sessions) is a TOR question the
  requester answers, which adds the data-protection clause; the agent does not process that data.

## 6.7 Risk register

| Risk | Likelihood | Impact | Control | Owner |
|---|---|---|---|---|
| Wrong method recommended and approved without challenge | Medium | High | Rule shown; officer agreement tracked; monthly sampled review of 10 cases; regression set on every policy change | Product owner |
| Split purchase missed because history is incomplete | Medium | Medium | History data quality measured in week 1; officers keep their own check during the pilot | Head of procurement |
| Injection or manipulation through form fields | Low | High | Screening blocks; no tool can approve; planted cases in CI | Tech lead |
| Over-reliance: officers stop reading TORs | Medium | Medium | Sections marked [TO CONFIRM] stay visible; officer must write a note when returning | Product owner |
| Model wording (US-13) introduces unsupported commitments | Medium (when shipped) | High | Validator rejects any number, date, name or commitment not in the request; template text kept on rejection | Tech lead |
| Requesters perceive monitoring | Low | Medium | Pseudonymous ids; no per-person reporting; DPO review | Product owner + DPO |
