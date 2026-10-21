# Operations: sample operating model for the pilot

Designed for a pilot; operated so far as a prototype on fictional data. Thresholds below are the
plan, not measurements.

## 1. Release gate (ticked before each release to the pilot)

- [ ] CI green: all tests, `tools/trace.py` (every Done story has a test), demo walk-through, scrub check
- [ ] Regression set passes: every must-pass case in [evals/EVALS.md](evals/EVALS.md), including the no-self-approval sequence test
- [ ] Any change to `config/policy.json` approved by the head of procurement, version bumped, recorded in CHANGELOG
- [ ] Any change to a checkpoint or an autonomy level recorded in [06-human-control.md](docs/product/06-human-control.md) and the decision log
- [ ] DPO consulted if identifiers or the event schema changed
- [ ] Before the first pilot release only: roles come from single sign-on groups, not the sample roster, and case files live in a store requesters cannot edit
- [ ] Previous release tag kept; officers and the pilot unit told what changed, in two lines

A release that fails any line does not go out.

## 2. Rollout

One pilot unit and one comparison unit, six weeks, at least 25 requests. Success metrics and
decision rules are fixed in [08-metrics-and-pilot.md](docs/product/08-metrics-and-pilot.md) before
launch: widen when first-review approval rises by 30 points and cycle time falls by 30% against the
comparison unit with officer agreement at 90%; stop on any kill criterion.

## 3. Monitoring

| Signal | Source | Frequency | Alert when |
|---|---|---|---|
| Requests through the desk | case files vs the procurement inbox | weekly | under 50% of the unit's new requests by week 3 |
| Complete on arrival | checklist at first run | weekly | under 50% of cases reaching an officer had every required item at first submission |
| Officer agreement with the method | officer note on approval | weekly | under 90%, or any disagreement that is a rule error |
| Screening flags | SCREEN flags and officer review | weekly | any flag judged a real attempt (incident); false positives over 20% of flags |
| Agent decisions | workflow log | every release (CI) and weekly | any status change by the agent role (cannot happen; if seen, kill switch) |
| Sampled review | 10 cases re-checked by a senior officer by hand | every two weeks | any wrong method, missed framework or missed split |

There is no telemetry beyond case files and usage events (the tool is a local command in v0.1).
Format of the weekly log: [ops/sample-monitoring-log.csv](ops/sample-monitoring-log.csv) (invented values).

## 4. Feedback into tests

Every confirmed problem (a wrong method, a missed framework, a flag that should not have fired, a
question nobody could answer) becomes a test named after its story, failing, before the fix is
merged. The regression set grows from real use.

## 5. Change and drift

Re-run the regression set and the demo when: the policy file changes (thresholds, categories,
frameworks, template); the request history format changes; any tool or the planner changes. Roll
back to the previous tag if a must-pass case regresses and the fix is not ready the same day.

## 6. Incident runbook

| Incident | Detected by | Contain | Tell | Follow-up |
|---|---|---|---|---|
| Wrong method recommended and approved | sampled review, or an officer challenges it | re-open the case; officer decides again; release with the fix or roll back the policy version | head of procurement, the requester | failing test, fix, CHANGELOG line |
| Status changed without a person | weekly log check (should be impossible) | **kill switch**: stop using the desk, route requests back to the inbox | head of procurement, audit | root cause before restart; new sequence test |
| Real injection attempt in a request | SCREEN flag reviewed by an officer | case stays blocked; requester asked to rewrite | head of procurement | pattern added to the eval set |
| Personal data in a usage event | DPO spot check | delete the event file; re-export | DPO the same day | identifier check moved upstream |

## 7. Ownership and retirement

Owner: product owner. Backup: tech lead. Review every three months with the head of procurement.
Retire if the pilot hits a kill criterion, if requesters stop using it for two consecutive months,
or if the procurement suite's guided buying covers services and TORs (D1): tell users, route
requests back to the inbox, archive the repository with its last test run.
