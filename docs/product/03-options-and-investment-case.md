# 3. Where to start, and build, buy, reuse or stop

Status: v0.1, October 2026. Owner: product owner. All figures on this page are **illustrative
assumptions** for a fictional organisation, to show the reasoning; the pilot replaces them with a
measured baseline.

## 3.1 Which corporate process first

Eight candidate processes from corporate services, scored 1 (low) to 5 (high). "Control risk" is
scored so that 5 means low risk.

| Process | Value: time and errors removed | Feasibility: rules exist, data reachable | Control risk (5 = low) | Reuse: existing content and platforms | Evidence: can we measure it in 6 weeks | Total |
|---|---|---|---|---|---|---|
| **Procurement intake (request to approvable TOR)** | 4 | 5 | 4 | 4 | 5 | **22** |
| Staff questions on HR and payroll policy | 4 | 4 | 3 | 5 | 4 | 20 |
| Translation request routing | 2 | 5 | 5 | 4 | 4 | 20 |
| IT service request triage | 3 | 4 | 4 | 4 | 4 | 19 |
| Travel and expense claim checks | 3 | 4 | 3 | 3 | 5 | 18 |
| Meeting and event logistics | 3 | 3 | 5 | 3 | 3 | 17 |
| Consultant onboarding (accounts, access, induction) | 3 | 3 | 3 | 3 | 4 | 16 |
| Budget reallocation requests | 4 | 2 | 2 | 2 | 3 | 13 |

Why procurement intake first: written rules (thresholds, frameworks, template) make the agent's
recommendations checkable; every step ends at a natural human approval, so control is designed in,
not bolted on; and cycle time and rework are measurable in weeks. HR policy questions and
translation routing tie for second. HR is the natural second product: same pattern, much higher
value (translation routing scores well because it is easy, not because it matters much), at the
cost of higher sensitivity.

## 3.2 Options for procurement intake

| Option | What it is | For | Against | Indicative cost (illustrative) |
|---|---|---|---|---|
| **Stop** (improve without AI) | Better intake form, TOR template, FAQ | Cheapest; fixes the blank page | No split or framework check; still rounds of questions | 2-3 weeks of one analyst |
| **Buy** | Guided-buying or AI module of the procurement suite | Inside the system of record; vendor maintains it | Strong on catalogue goods, weak on services and TORs; licence cost; roadmap not ours | Licence per user per year + integration |
| **Reuse** | An agent on the organisation's enterprise assistant platform, grounded on the policy and template | Already licensed; staff already use it; governed tenant | Rules as prompts are hard to test; needs connectors for history and frameworks | Configuration + connectors, 4-6 weeks |
| **Build** (this MVP) | Policy engine + agent loop + package, as a service | Rules testable in CI; full control of human checkpoints; channel-agnostic | Code to own; not where users already work | 2 sprints, small team |
| **Partner** | Shared intake service with peer organisations | Shared cost and practice | Policies differ; slow to agree | Not costed |

### Decision (D1 in the [decision log](09-decision-log.md))

**Build thin to learn, reuse to scale, keep buy open.**

1. **Build** the thin MVP now: it is the fastest way to prove the rules, the human control and the
   value on real requests in one unit (H1 to H3), at the cost of two sprints.
2. **Reuse** for scale: if the pilot succeeds, the enterprise assistant platform becomes the
   channel (US-14), calling this policy engine as a service. Users get it where they work; the
   rules stay testable in one place.
3. **Buy** is re-evaluated at the next review of the procurement suite's roadmap. If guided buying
   covers services and TORs, the engine's rules move there and this product stops.
4. **Stop** is the control: the improved form and template are shipped anyway to the comparison
   unit, so the pilot measures what the agent adds beyond a better form.

## 3.3 Lean business case (epic hypothesis)

**For** requesting managers and procurement officers **who** lose weeks to rework before a purchase
can start, **the** procurement intake desk **is an** agent-prepared intake process **that** turns a
described need into a request a procurement officer can approve on first review. **Unlike** email
and an old TOR, **our solution** applies the rules the same way every time, shows its evidence,
and leaves every decision to a person.

**Business outcome hypotheses**
- Time from request to approval falls by at least 30% in the pilot unit: purchases start weeks
  earlier, which is the main value (H2).
- First-review approval reaches at least 70%, 30 points above the comparison unit (H2).
- No approval is ever taken by the agent; audit sign-off on the control design (H4).

**Leading indicators**: share of requests complete on arrival; rounds per request; officer
agreement with the recommended method (H3); returning requesters (H5).

**MVP**: this repository (v0.1) plus a six-week pilot in one unit with a comparison unit
([08-metrics-and-pilot.md](08-metrics-and-pilot.md)).

**Illustrative value model** (to be replaced by the pilot baseline). Released person-time is the
smaller and easier-to-count part of the value; earlier starts are the larger one.

| Assumption | Value |
|---|---|
| Service requests per year, organisation-wide | 600 |
| Rework rounds per request today | 2.3 |
| Person-time per round (requester + officer) | 45 minutes |
| Rounds removed by the desk | 50% |
| **Person-time released per year** | 600 x 2.3 x 0.75 h x 0.5 = **about 520 hours** |

Plus the harder-to-price gains: purchases starting weeks earlier, split purchases caught, an
audit trail for every method decision.

**Go / no-go after the pilot**: go when H2 and H3 hold and H4 is signed; iterate when H2 holds
partly; stop when first-review approval does not move by 15 points or officers distrust the
recommendations.
