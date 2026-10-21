# Build spec - agentic-procurement-intake v0.1.0

Type: product MVP (agent with a command-line front end + generated request package)
Platform: Python 3.10+, no runtime dependencies, no model calls in v0.1
Stage: prototype, designed for a pilot (OPERATIONS.md is the pilot operating model)
Owner: product owner (Flavio)    Backup: tech lead (to be named at pilot)
Users: requesting staff (start a request), procurement officers (review and decide), budget holders (sign off above a threshold)
Spend cap: none in v0.1 (no model calls); model drafting (US-13) gets a per-request token cap before it ships
Confidentiality: public; every organisation, policy figure and request is fictional (Meridian Institute)

## Job
A staff member describes what they need to buy. The agent turns it into a request a procurement
officer can approve on first review: category, procurement method with its rule, a reuse check
against existing framework agreements, policy flags, a draft terms of reference (TOR), a
completeness checklist and the next human step. People decide; the agent prepares.

## Loop (one request)
- Intake: request JSON (the answers a guided form or chat collects) + 12-month request history + procurement-owned policy JSON
- Step 1 Screen: free-text fields treated as data; instruction-like text flagged, never followed
- Step 2 Understand: category (from the requester, or inferred by rules; ambiguous -> ask)
- Step 3 Reuse first: an active framework agreement for the category -> recommend a call-off, not a new tender
- Step 4 Method: aggregate value (this request + same unit, same category, last 12 months) against thresholds; split-purchase and sole-source checks
- Step 5 Draft: TOR from the procurement template; unknowns marked [TO CONFIRM], nothing invented
- Step 6 Check: completeness checklist; missing must-items become questions back to the requester
- Step 7 Route: officer queue by category and value; package as Markdown, HTML and JSON with the audit trail
- Human checkpoints: requester confirms the draft -> officer approves or returns -> budget holder signs off above the threshold. The agent can never move a case to Approved.
- Fallbacks: missing field -> question, not failure; unknown category -> question listing the options; malformed file -> stop with the field name
- Never: approves, commits funds, contacts or selects suppliers, changes thresholds, follows instructions found inside a request

## Acceptance criteria
- AC1 Every Done backlog story is proved by a named test (CI: tools/trace.py)
- AC2 The sample requests exercise every outcome: ready, needs information, reuse via framework, split-purchase flag, sole-source flag, injection flag
- AC3 Every number and date in a TOR draft appears in the request (whole-token match) or is a policy reference (framework agreement id); anything else is [TO CONFIRM]
- AC4 No sequence of commands lets the agent role, or the requester under their own id, approve a case; only ids on the procurement-owned role roster can decide; above the sign-off threshold, approval needs an officer and a different budget holder, neither of them the requester
- AC5 Every method recommendation names the rule, the aggregate value and the threshold

## Assumptions
- [ASSUMPTION] A guided form or chat can collect the request fields; the channel is out of scope for v0.1 (US-14)
- [ASSUMPTION] Thresholds and framework agreements in config/policy.json are a sample policy, not a real one
- [ASSUMPTION] Rework between requester and procurement is the main source of delay (H1, tested in the pilot)
