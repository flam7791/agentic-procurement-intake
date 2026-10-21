# Judge report - agentic-procurement-intake v0.1.0

Independent pass by a separate reviewer (a subagent with the rubric, the spec and the evals, and
no part in the build), 21 October 2026. Stage: prototype; operational readiness not scored.

## Scores (0-2 each)

| # | Criterion | Before fixes | After fixes | Note |
|---|---|---|---|---|
| 1 | Spec fit | 2 | 2 | All loop steps, three checkpoints, three output formats; AC2 covered by the samples |
| 2 | Platform fit | 2 | 2 | Package installs; quick start runs as written; CI on Python 3.10 and 3.12 |
| 3 | Limits | 2 | 2 | No model-loaded artefacts in v0.1 |
| 4 | Instruction clarity | 2 | 2 | Deterministic rules; every recommendation shows its rule |
| 5 | Grounding, no fabrication | 1 | 2 | AC3 test matched substrings; now whole tokens, with a planted-figure test |
| 6 | Boundaries, injection | 1 | 2 | Any typed role could decide; now a procurement-owned roster, and the identity limit is stated |
| 7 | Loop and checkpoints | 2 | 2 | Approving a flagged case now needs the officer's note |
| 8 | Testability | 2 | 2 | 12 cases with observable pass conditions; regression set marked |
| | **Total** | **14/16** | **16/16 (self-assessed after fixes)** | |

Verdict before fixes: fix then ship; no blocking failure.

## What was fixed

1. AC3 check rewritten as a whole-token comparison; `test_US07_the_check_catches_an_invented_figure` proves an invented "500" no longer hides inside "9500".
2. `workflow.decide` checks a role roster owned by procurement (`config/policy.json`); README and 06 now state that v0.1 identity is asserted, not authenticated, and the pilot release gate requires single sign-on roles and a protected case store.
3. Approving a case with a SPLIT or SOLE flag requires a note (test added).
4. README test count corrected (42 test runs, 32 functions); `trace.py` says "test functions".
5. Consistency: H2 and H4 worded the same across discovery, investment case, PRD, roadmap and pilot; US-13 and US-14 placed the same in the backlog, roadmap and README; process table sorted and the tie explained; SAFe and design-thinking methods named in the README; weekly discovery cadence added to the pilot.

## Residual issues

- Identity and case-file integrity rely on the environment in v0.1 (stated as a limitation and a release-gate item).
- Keyword classification and framework scope are checked on a small author-written sample.
- After-fix scores are the builder's assessment, not a second independent pass.
