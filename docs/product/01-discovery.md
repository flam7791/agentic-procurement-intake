# 1. Discovery: why buying a service takes weeks before anyone buys it

Status: v0.1, October 2026. Owner: product owner (Flavio).

## How this discovery was done, and what it is not

This is an **assumption-led discovery**. It draws on my experience of procurement processes in
large international organisations, including an AI consultancy procurement, and on common
public-procurement practice (thresholds, framework agreements, split-purchase rules).
**No user interviews were run for this portfolio MVP.** Every claim about users below is
therefore a hypothesis with a kill condition, and [08-metrics-and-pilot.md](08-metrics-and-pilot.md)
says how each is tested in the first weeks with real users. The organisation, the policy and the
requests are fictional.

## The problem

In an international organisation, a manager who needs an evaluator, an editor or a software team
does not start by buying. They start by writing an email to procurement. What follows is a
loop: which category is this, which method applies, where is the TOR, what is the budget code,
have you bought this before, why this supplier. Each answer takes a day or a week, and the
request reaches a procurement officer in a state the officer cannot approve.

The part of that problem this product addresses is narrow on purpose: **the gap between "I need
this" and a request a procurement officer can approve on first review.** Sourcing, evaluation of
offers and contracting are out of scope. They are someone else's process and someone else's
system.

## Who has the problem

| Persona | Job to be done | What hurts today (hypothesis) |
|---|---|---|
| **Requesting manager** (primary user, occasional: a few requests a year) | "When I need outside help, I want to know what procurement needs from me and get a TOR started, so that work begins when it is needed." | Does not know the categories, thresholds or template; learns them by rework; a TOR starts from an old file found on a shared drive. |
| **Procurement officer** (primary user, daily) | "When a request reaches me, I want it complete, correctly classified and with the method already argued, so that my review is a decision, not an investigation." | Most requests arrive incomplete; time goes to chasing answers and spotting split purchases by memory. |
| **Budget holder** (approver) | "When I sign off spend, I want to see that the method and the value are right, so that I sign once." | Signs on trust, or reopens questions procurement already asked. |
| **Head of procurement** (owner of the policy) | "When we use AI in procurement, I want the rules applied the same way every time and every decision taken by a person, so that an audit finds nothing to fix." | Rules applied unevenly; no trail of why a method was chosen; fear that AI means automated approvals. |

## As-is journey (summary; the full blueprint is in [02-service-blueprint.md](02-service-blueprint.md))

1. Requester emails procurement with a paragraph and, sometimes, an old TOR.
2. Officer replies with questions: category, value, dates, budget code, deliverables.
3. Requester answers some; officer asks again.
4. Officer checks thresholds and past purchases by hand; may spot a split purchase, may not.
5. Requester rewrites the TOR to the template.
6. Officer approves, or returns it; above a threshold, the budget holder signs.

## Hypotheses (tested in the pilot, see 08)

- **H1 Problem: rework dominates.** More than half of requests need two or more back-and-forth
  rounds before an officer can decide. *Kill if* fewer than a third do, in a sample of 30 recent
  requests from the procurement inbox.
- **H2 Value: approvable on first review.** With the intake desk, at least 70% of requests are
  approved on first officer review, at least 30 points above the comparison unit, and median time
  from submission to approval falls by at least 30%. *Kill if* first-review approval is less than
  15 points above the comparison unit.
- **H3 Trust: officers accept the agent's recommendation.** Officers agree with the recommended
  method in at least 90% of cases, and every disagreement is explained. *Kill if* any disagreement
  is a rule the agent applied wrongly and it recurs after a fix.
- **H4 Control: it is accepted as human-decided.** The head of procurement and internal audit sign
  off the human-control design, and requesters can say who approved their request. *Kill if* the
  head of procurement or audit will not sign off.
- **H5 Adoption: occasional users come back.** At least 60% of requesters in the pilot unit use
  the desk for their next request without being reminded. *Kill if* under 40%.

## What we do not know

- Whether requesters will answer structured questions, or prefer to write a paragraph and be
  interviewed (the reason the chat channel, US-14, is Next and not Later).
- How much of officers' time is rework versus judgment that no tool should take over.
- Whether units' 12-month history is reliable enough for the split-purchase check (data quality of
  the request history is the first thing the pilot measures).

## Interview guide for the pilot's first week

Five requesters, three officers, one budget holder, the head of procurement. Thirty minutes each.

1. Tell me about the last service you bought (or approved). Walk me through it from the first email.
2. Where did it stop and wait? Who was waiting for whom?
3. What did you have to look up or ask that you could not find yourself?
4. *(Officers)* Of the last ten requests you received, how many could you approve as they arrived?
   What was missing in the others?
5. *(Officers)* How do you spot a split purchase today?
6. What would make you distrust a recommendation from an AI assistant in this process?
7. Who should be able to approve, and who must never be able to?

Listen for: number of rounds, the items that are always missing, workarounds (old TORs, a
colleague who knows), and the trust line in question 6.
