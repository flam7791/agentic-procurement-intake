# 9. Product decision log

One entry per decision that someone could reasonably question later. Newest last.

### D1 - Build thin to learn, reuse to scale, keep buy open (Oct 2026)
**Context.** Five options: improve the form only, buy the procurement suite's AI module, reuse the
enterprise assistant platform, build, or partner ([03](03-options-and-investment-case.md)).
**Decision.** Build a thin MVP to test the hypotheses; plan the enterprise assistant platform as the
channel at scale, calling the same policy engine; re-evaluate buying at the suite's next roadmap
review. Ship the improved form to the comparison unit as the control.
**Trade-off.** Code to own during the pilot. In exchange: rules testable in CI, human control
provable, and a measured answer to "what does the agent add beyond a better form".
**Revisit when.** The pilot ends, or the suite's guided buying covers services and TORs.

### D2 - The agent prepares; people decide, enforced in code (Oct 2026)
**Context.** Auto-approving small, complete requests was proposed as the obvious efficiency win.
**Decision.** No status change past the draft without a named person in a named role; the agent role
is refused by the workflow, and a test tries every short sequence of actions to prove it.
**Why.** The gain from auto-approval is small (small requests are quick to approve) and the cost of
one wrong automated approval is the whole product's licence to operate.

### D3 - Thresholds and frameworks in a procurement-owned file, not in code (Oct 2026)
**Decision.** The policy is a versioned JSON file owned by procurement; the agent reads it and
never writes it.
**Why.** Thresholds are policy, not engineering. A change should be a procurement decision recorded
in their minutes, followed by the regression set, not a pull request.

### D4 - Rule-based planner for v0.1; a model planner must earn its place (Oct 2026)
**Context.** "Agentic" suggests a model deciding the next step.
**Decision.** v0.1 uses a fixed, inspectable planner over a bounded tool set, with every call in the
audit trail. A model planner (US-18) can later choose among the same tools, under the same policy
and checkpoints, only if pilot evidence shows requests the rules handle badly.
**Why.** Officers and auditors must be able to predict what the agent does. Reproducibility first;
flexibility when evidence asks for it.

### D5 - Method on the 12-month total, with the split flagged, not refused (Oct 2026)
**Decision.** The method is set on the unit's 12-month total for the category; a possible split is
an attention flag for the officer, not a blocking error.
**Why.** Related requests are often legitimate (separate needs that share a category). The rule
protects the threshold; the judgment about intent stays with a person.

### D6 - Request text is data; instruction-like text blocks the case (Oct 2026)
**Decision.** Flag and withhold, block until rewritten; never follow.
**Trade-off.** Some false positives cost the requester a rewrite. Measured as a guardrail in the
pilot; the patterns were checked against ordinary procurement wording (a test proves "approved
budget" and "previous policy" are not flagged).

### D7 - Template drafting first, model wording later and behind a validator (Oct 2026)
**Decision.** v0.1 drafts the TOR from the template with the requester's own answers; any number or
date not in the request is a test failure. Model wording (US-13) may only rephrase confirmed
answers, and a validator rejects anything new.
**Why.** The discovery found rework, not prose quality, to be the bottleneck. An invented deliverable
or date in a TOR is worse than a plain one.

### D8 - Usage events in the adoption tracker's format (Oct 2026)
**Decision.** The desk emits confirmation and rating events in the format of
[ai-adoption-tracker](https://github.com/flam7791/ai-adoption-tracker).
**Why.** The desk is itself an AI use case; its scale-or-stop decision should rest on the same
evidence as every other pilot in the portfolio.
