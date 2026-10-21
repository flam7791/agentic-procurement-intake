"""Acceptance tests. Each test name starts with the backlog story it proves (docs/team/backlog.csv).

tools/trace.py fails CI if a story marked Done has no test here: the Definition of Done is
enforced, not just written down.
"""
from __future__ import annotations

import csv
import itertools
import json
import re
from datetime import date
from pathlib import Path

import pytest

from intake_desk.agent import (APPROVED, AWAITING_BUDGET_HOLDER, AWAITING_OFFICER, AWAITING_REQUESTER,
                               NEEDS_INFO, RETURNED, IntakeAgent)
from intake_desk.cli import main
from intake_desk.events import collect
from intake_desk.policy import load_policy
from intake_desk.render import to_html, to_json, to_markdown
from intake_desk.request import RequestError, load_history, request_from_dict
from intake_desk.workflow import WorkflowError, confirm, decide, load_case, save_case

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "sample"
POLICY = load_policy()
HISTORY = load_history(SAMPLE / "history.csv")
DAY = date(2026, 10, 21)


def sample(rid: str) -> dict:
    return json.loads((SAMPLE / "requests" / f"{rid}.json").read_text(encoding="utf-8"))


def run(raw: dict, history=None):
    return IntakeAgent(POLICY, HISTORY if history is None else history).run(request_from_dict(raw))


def complete(**over) -> dict:
    """A complete, valid request; override any field."""
    raw = sample("R-101")
    raw.update(over)
    return raw


# ---- US-01 intake --------------------------------------------------------------------------------

def test_US01_partial_request_becomes_questions_not_an_error():
    case = run(sample("R-103"))
    assert case.status == NEEDS_INFO
    assert len(case.questions) >= 6
    assert any("cost" in q for q in case.questions) and any("budget code" in q for q in case.questions)


@pytest.mark.parametrize("field,value,msg", [
    ("start", "12/11/2026", "start"),
    ("estimated_value", "about 40k", "estimated_value"),
    ("requester", "jane.doe@example.org", "pseudonymous"),
])
def test_US01_malformed_input_stops_with_the_field_name(field, value, msg):
    with pytest.raises(RequestError, match=msg):
        request_from_dict(complete(**{field: value}))


# ---- US-02 category ------------------------------------------------------------------------------

def test_US02_chosen_category_is_used_as_is():
    case = run(sample("R-104"))
    assert case.category["id"] == "consulting_services" and case.category["how"] == "chosen by requester"


def test_US02_category_inferred_from_text_for_requester_to_confirm():
    case = run(sample("R-101"))
    assert case.category["id"] == "consulting_services"
    assert "requester to confirm" in case.category["how"]


def test_US02_no_match_becomes_a_question_listing_the_options():
    case = run(sample("R-103"))
    assert case.category["id"] is None
    q = case.questions[0]
    assert q.startswith("Which category") and "consulting_services" in q and "it_services" in q


# ---- US-03 method --------------------------------------------------------------------------------

@pytest.mark.parametrize("value,method", [(9999, "M1"), (10000, "M2"), (149999, "M2"), (150000, "M3")])
def test_US03_method_follows_policy_thresholds_and_boundaries_go_up(value, method):
    case = run(complete(estimated_value=value), history=[])
    assert case.method["id"] == method
    assert f"{value:,}" in case.method["rule"] and case.method["threshold"] in case.method["rule"]


def test_US03_thresholds_come_from_the_policy_file(tmp_path):
    raw = json.loads((ROOT / "config" / "policy.json").read_text(encoding="utf-8"))
    raw["methods"][1]["below"] = 40000
    p = tmp_path / "policy.json"
    p.write_text(json.dumps(raw), encoding="utf-8")
    case = IntakeAgent(load_policy(p), []).run(request_from_dict(complete(estimated_value=45000)))
    assert case.method["id"] == "M3"


# ---- US-04 reuse ---------------------------------------------------------------------------------

def test_US04_covered_need_goes_to_a_framework_call_off():
    case = run(sample("R-102"))
    assert case.reuse["framework_id"] == "FA-2026-02" and case.reuse["coverage"] == "covered"
    assert case.method["recommended"] == "Call-off under FA-2026-02"


def test_US04_expired_or_exhausted_frameworks_are_ignored():
    late = run(sample("R-102") | {"submitted": "2028-03-01", "start": "2028-03-10", "end": "2028-08-01"})
    assert late.reuse is None
    big = run(sample("R-102") | {"estimated_value": 950000})
    assert big.reuse is None and big.method["id"] == "M3"


def test_US04_uncertain_scope_is_left_to_the_officer():
    raw = sample("R-102") | {"title": "Helpdesk staffing", "need": "Extra helpdesk staff for the move.",
                             "scope": "Two technicians on site for three months.", "objective": "Shorter queues.",
                             "qualifications": "Certified support technicians."}
    raw["deliverables"] = [{"item": "Monthly staffing report", "due": "2027-01-15"}]
    case = run(raw)
    assert case.reuse["coverage"].startswith("possible")
    assert not case.method["recommended"].startswith("Call-off")


# ---- US-05 split purchase ------------------------------------------------------------------------

def test_US05_twelve_month_total_sets_the_method_and_flags_the_split():
    case = run(sample("R-104"))
    assert case.value["aggregate"] == 24500
    assert {r["id"] for r in case.value["related"]} == {"H-0533", "H-0587"}  # H-0412 too old, H-0645 cancelled
    assert case.method["id"] == "M2"
    flag = next(f for f in case.flags if f["id"] == "SPLIT")
    assert "M1" in flag["text"] and "M2" in flag["text"]


def test_US05_other_units_and_categories_do_not_count():
    case = run(sample("R-104") | {"unit": "Research Division"})
    assert case.value["aggregate"] == 9500 and not any(f["id"] == "SPLIT" for f in case.flags)


# ---- US-06 sole source ---------------------------------------------------------------------------

def test_US06_named_supplier_without_justification_is_a_required_question():
    case = run(sample("R-105"))
    assert any(f["id"] == "SOLE" for f in case.flags)
    assert case.status == NEEDS_INFO and "Quantis Data" in case.questions[0]
    fixed = run(sample("R-105") | {"sole_source_justification": "Only licensed source of the 2000-2010 series."})
    assert fixed.status == AWAITING_REQUESTER and any(f["id"] == "SOLE" for f in fixed.flags)


def test_US06_direct_purchase_and_framework_call_off_do_not_trigger_it():
    small = run(complete(estimated_value=5000, preferred_supplier="Any Co (fictional)"), history=[])
    fa = run(sample("R-102") | {"preferred_supplier": "Northgate Digital (fictional)"})
    assert not any(f["id"] == "SOLE" for f in small.flags + fa.flags)


# ---- US-07 TOR draft -----------------------------------------------------------------------------

NUMBERS = re.compile(r"\d[\d,.\-]*\d|\d")


def number_tokens(text: str) -> set[str]:
    """Whole number and date tokens, thousands separators removed: '9,500' -> '9500'."""
    out = set()
    for tok in NUMBERS.findall(text):
        tok = tok.replace(",", "")
        out.add(tok[:-2] if tok.endswith(".0") else tok)
    return out


def invented_numbers(case, raw: dict) -> set[str]:
    allowed = number_tokens(json.dumps(raw))
    if case.reuse:
        allowed |= number_tokens(case.reuse["framework_id"])
    return {t for sec in case.tor for t in number_tokens(sec["text"])} - allowed


@pytest.mark.parametrize("rid", ["R-101", "R-102", "R-103", "R-104", "R-105", "R-106"])
def test_US07_every_number_and_date_in_the_draft_comes_from_the_request(rid):
    raw = sample(rid)
    assert invented_numbers(run(raw), raw) == set()


def test_US07_the_check_catches_an_invented_figure():
    """The check above must not pass by substring: '500' is not in a request that says 9500."""
    raw = sample("R-104")
    case = run(raw)
    case.tor[0]["text"] += " A further USD 500 covers travel; kick-off on 2026-10-30."
    assert invented_numbers(case, raw) == {"500", "2026-10-30"}


def test_US07_all_sections_present_in_template_order_and_unknowns_marked():
    case = run(sample("R-103"))
    assert [s["id"] for s in case.tor] == [s.id for s in POLICY.tor_sections]
    todo = {s["id"] for s in case.tor if s["status"] == "to_confirm"}
    assert {"objective", "scope", "deliverables", "budget", "data"} <= todo
    assert all("[TO CONFIRM" in s["text"] for s in case.tor if s["id"] in todo)


# ---- US-08 checklist -----------------------------------------------------------------------------

def test_US08_each_unmet_required_item_has_one_question_and_blocks():
    case = run(sample("R-103"))
    unmet = [c for c in case.checklist if c["required"] and not c["met"]]
    assert len(unmet) == len(case.questions) and all(c["question"] for c in unmet)
    assert case.status == NEEDS_INFO


def test_US08_recommended_items_never_block():
    case = run(sample("R-104") | {"qualifications": ""})
    assert case.status == AWAITING_REQUESTER
    assert not next(c for c in case.checklist if c["id"] == "qualifications")["met"]


def test_US08_end_before_start_is_caught():
    case = run(complete(start="2027-03-01", end="2027-01-01"))
    assert any("before the start" in q for q in case.questions)


# ---- US-09 human checkpoints ---------------------------------------------------------------------

def ready_case(value=45000):
    case = run(complete(estimated_value=value), history=[])
    assert case.status == AWAITING_REQUESTER
    return case


def test_US09_agent_cannot_confirm_approve_or_return():
    case = ready_case()
    with pytest.raises(WorkflowError):
        decide(case, "agent", "intake-agent", True, DAY)
    with pytest.raises(WorkflowError):
        confirm(case, "intake-agent", DAY)
    assert case.status == AWAITING_REQUESTER


def test_US09_requester_confirms_then_officer_approves_below_signoff():
    case = ready_case(45000)
    confirm(case, "req-4821", DAY)
    assert case.status == AWAITING_OFFICER
    with pytest.raises(WorkflowError):
        decide(case, "procurement_officer", "req-4821", True, DAY)  # own request
    decide(case, "procurement_officer", "po-17", True, DAY)
    assert case.status == APPROVED and [h["role"] for h in case.history] == ["requester", "procurement_officer"]


def test_US09_above_signoff_needs_a_different_budget_holder():
    roster = {"procurement_officer": ("po-17",), "budget_holder": ("po-17", "bh-03")}  # po-17 holds both roles
    case = ready_case(60000)
    confirm(case, "req-4821", DAY)
    decide(case, "procurement_officer", "po-17", True, DAY, roster=roster)
    assert case.status == AWAITING_BUDGET_HOLDER
    with pytest.raises(WorkflowError, match="four eyes"):
        decide(case, "budget_holder", "po-17", True, DAY, roster=roster)
    decide(case, "budget_holder", "bh-03", True, DAY, roster=roster)
    assert case.status == APPROVED


def test_US09_no_command_sequence_lets_the_agent_or_requester_approve():
    """AC4: try every ordered sequence of up to four actions by the agent and the requester."""
    actions = [("confirm", "req-4821"), ("confirm", "intake-agent"),
               ("procurement_officer", "req-4821"), ("budget_holder", "req-4821"),
               ("agent", "intake-agent"), ("agent", "req-4821")]
    for seq in itertools.product(actions, repeat=4):
        case = ready_case(60000)
        for kind, who in seq:
            try:
                if kind == "confirm":
                    confirm(case, who, DAY)
                else:
                    decide(case, kind, who, True, DAY)
            except WorkflowError:
                pass
        assert case.status != APPROVED and case.status != AWAITING_BUDGET_HOLDER


def test_US09_only_people_on_the_role_roster_can_decide():
    case = ready_case()
    confirm(case, "req-4821", DAY)
    with pytest.raises(WorkflowError, match="roster"):
        decide(case, "procurement_officer", "someone-else", True, DAY)
    with pytest.raises(WorkflowError, match="roster"):
        decide(case, "procurement_officer", "bh-03", True, DAY)  # a budget holder is not an officer
    assert case.status == AWAITING_OFFICER


def test_US09_approving_a_flagged_case_needs_the_officers_note():
    case = run(sample("R-104"))  # SPLIT flag
    confirm(case, "req-2264", DAY)
    with pytest.raises(WorkflowError, match="SPLIT"):
        decide(case, "procurement_officer", "po-17", True, DAY)
    decide(case, "procurement_officer", "po-17", True, DAY, note="Separate editions, separate needs.")
    assert case.status == APPROVED and case.history[-1]["note"]


def test_US09_return_needs_a_note_and_needs_info_cannot_be_confirmed():
    case = ready_case()
    confirm(case, "req-4821", DAY)
    with pytest.raises(WorkflowError, match="note"):
        decide(case, "procurement_officer", "po-17", False, DAY)
    decide(case, "procurement_officer", "po-17", False, DAY, note="Add evaluation weights.")
    assert case.status == RETURNED
    with pytest.raises(WorkflowError, match="answer first"):
        confirm(run(sample("R-103")), "req-3350", DAY)


# ---- US-10 untrusted text ------------------------------------------------------------------------

def test_US10_instructions_in_a_request_are_flagged_withheld_and_not_followed():
    case = run(sample("R-106"))
    flags = [f for f in case.flags if f["id"] == "SCREEN"]
    assert len(flags) == 1 and flags[0]["field"] == "need" and flags[0]["severity"] == "blocking"
    background = next(s for s in case.tor if s["id"] == "background")
    assert "Ignore" not in background["text"] and "withheld" in background["text"]
    assert case.method["id"] == "M2"  # not steered to direct award
    assert case.status == NEEDS_INFO and case.status not in (APPROVED, AWAITING_OFFICER)


def test_US10_ordinary_wording_is_not_flagged():
    raw = complete(need="Management asked us to review the previous policy and the approved budget "
                        "before the board meeting; the method used last year was a direct purchase.")
    assert not any(f["id"] == "SCREEN" for f in run(raw).flags)


# ---- US-11 package -------------------------------------------------------------------------------

def test_US11_package_in_three_formats_with_audit_trail(tmp_path):
    for rid in ["R-101", "R-102", "R-103", "R-104", "R-105", "R-106"]:
        assert main(["run", str(SAMPLE / "requests" / f"{rid}.json"), "--history",
                     str(SAMPLE / "history.csv"), "--out", str(tmp_path)]) == 0
        for ext in (".case.json", ".md", ".html"):
            assert (tmp_path / f"{rid}{ext}").stat().st_size > 500
    case = load_case(tmp_path / "R-104.case.json")
    md, page = to_markdown(case), to_html(case)
    assert "Audit trail" in md and "SPLIT" in md and "prefers-color-scheme:dark" in page
    assert [t["tool"] for t in case.trace] == ["screen", "classify", "aggregate", "reuse", "method",
                                               "sole_source", "draft", "check", "route"]
    assert all(t["reason"] for t in case.trace)
    assert json.loads(to_json(case))["status"] == AWAITING_REQUESTER


def test_US11_sample_requests_exercise_every_outcome(tmp_path):
    """AC2: ready, needs information, reuse, split, sole source and injection all appear."""
    cases = [run(sample(f"R-10{i}")) for i in range(1, 7)]
    statuses = {c.status for c in cases}
    flags = {f["id"] for c in cases for f in c.flags}
    assert {AWAITING_REQUESTER, NEEDS_INFO} <= statuses
    assert {"SPLIT", "SOLE", "SCREEN"} <= flags
    assert any(c.reuse and c.method["recommended"].startswith("Call-off") for c in cases)


# ---- US-12 events --------------------------------------------------------------------------------

def test_US12_events_in_tracker_format_with_pseudonymous_ids(tmp_path):
    case = ready_case()
    confirm(case, "req-4821", DAY, rating="up")
    save_case(case, tmp_path / "R-101.case.json")
    save_case(run(sample("R-103")), tmp_path / "R-103.case.json")  # not confirmed: no event
    rows = collect(tmp_path, "UC-INTAKE")
    assert [r["action"] for r in rows] == ["task_completed", "feedback_positive"]
    assert all(r["user_id"] == "req-4821" and "@" not in r["user_id"] for r in rows)
    out = tmp_path / "events.csv"
    assert main(["events", str(tmp_path), "--out", str(out)]) == 0
    assert next(csv.reader(out.open(encoding="utf-8"))) == ["date", "use_case_id", "user_id", "action"]
