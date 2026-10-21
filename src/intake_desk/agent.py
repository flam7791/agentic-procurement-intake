"""The intake agent: a bounded tool loop that turns a request into an approvable package.

A planner picks the next tool from a fixed set, given what is known so far; each tool reads the
request, the history and the procurement policy, and writes one part of the case; every call is
recorded in the audit trail with its reason. The v0.1 planner is rule-based, so every run is
reproducible and testable. A model planner (roadmap: Later) would choose from the same tools,
under the same policy and the same human checkpoints; it would not get new powers.

What the agent never does, whatever the input: approve, commit funds, contact or select a
supplier, change a threshold, follow an instruction found inside a request.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .policy import Policy
from .request import PastRequest, Request
from .screen import screen

MAX_STEPS = 12
TO_CONFIRM = "[TO CONFIRM: {}]"

# statuses
NEEDS_INFO = "Needs information"
AWAITING_REQUESTER = "Draft ready: requester to confirm"
AWAITING_OFFICER = "With procurement officer"
AWAITING_BUDGET_HOLDER = "With budget holder"
APPROVED = "Approved"
RETURNED = "Returned to requester"


@dataclass
class Case:
    request: Request
    policy_version: str
    status: str = NEEDS_INFO
    category: dict = field(default_factory=dict)
    value: dict = field(default_factory=dict)
    method: dict | None = None
    reuse: dict | None = None
    flags: list[dict] = field(default_factory=list)
    tor: list[dict] = field(default_factory=list)
    checklist: list[dict] = field(default_factory=list)
    route: dict = field(default_factory=dict)
    approvals_needed: list[str] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)
    history: list[dict] = field(default_factory=list)

    @property
    def questions(self) -> list[str]:
        return [c["question"] for c in self.checklist if c["required"] and not c["met"]]

    @property
    def blocking_flags(self) -> list[dict]:
        return [f for f in self.flags if f["severity"] == "blocking" and not f.get("cleared_by")]

    @property
    def ready(self) -> bool:
        return not self.questions

    def next_step(self) -> str:
        return {
            NEEDS_INFO: "Requester answers the questions below; the agent re-runs the checks.",
            AWAITING_REQUESTER: "Requester reads the draft TOR and confirms it (intake-desk confirm).",
            AWAITING_OFFICER: f"Procurement officer in '{self.route.get('queue', '?')}' approves or returns.",
            AWAITING_BUDGET_HOLDER: "Budget holder signs off (value at or above the sign-off threshold).",
            APPROVED: "Approved by people. Sourcing starts under the recommended method.",
            RETURNED: "Requester revises the request and submits it again.",
        }[self.status]

    def to_dict(self) -> dict:
        return {
            "request": self.request.to_dict(), "policy_version": self.policy_version, "status": self.status,
            "next_step": self.next_step(), "category": self.category, "value": self.value,
            "method": self.method, "reuse": self.reuse, "flags": self.flags, "tor": self.tor,
            "checklist": self.checklist, "questions": self.questions, "route": self.route,
            "approvals_needed": self.approvals_needed, "trace": self.trace, "history": self.history,
        }


class RulePlanner:
    """Chooses the next tool. Returns (tool, reason) or None when the loop is done."""

    ORDER = ("screen", "classify", "aggregate", "reuse", "method", "sole_source", "draft", "check", "route")

    def next(self, case: Case, done: set[str]) -> tuple[str, str] | None:
        for tool in self.ORDER:
            if tool in done:
                continue
            if tool in ("reuse",) and not case.category.get("id"):
                return tool, "skip: category unknown, ask first"
            if tool in ("aggregate", "method") and (case.request.estimated_value is None or not case.category.get("id")):
                return tool, "skip: value or category unknown, ask first"
            return tool, {
                "screen": "requester text is untrusted: screen it before using it",
                "classify": "the category decides the queue, the template and the frameworks",
                "aggregate": "thresholds apply to the unit's 12-month total for the category",
                "reuse": "an existing framework agreement beats a new tender",
                "method": "the method follows from the aggregate value and the thresholds",
                "sole_source": "a named supplier outside a framework needs a justification",
                "draft": "officers review a TOR, not an email thread",
                "check": "turn every gap into a question before an officer sees the case",
                "route": "send the package to the right queue with the approvals it needs",
            }[tool]
        return None


class IntakeAgent:
    def __init__(self, policy: Policy, history: list[PastRequest] | None = None, planner=None):
        self.policy = policy
        self.history = history or []
        self.planner = planner or RulePlanner()

    def run(self, req: Request) -> Case:
        case = Case(request=req, policy_version=self.policy.version)
        done: set[str] = set()
        for n in range(1, MAX_STEPS + 1):
            nxt = self.planner.next(case, done)
            if nxt is None:
                break
            tool, reason = nxt
            done.add(tool)
            if reason.startswith("skip:"):
                case.trace.append({"step": n, "tool": tool, "reason": reason, "result": "skipped"})
                continue
            result = getattr(self, f"_{tool}")(case)
            case.trace.append({"step": n, "tool": tool, "reason": reason, "result": result})
        case.status = AWAITING_REQUESTER if case.ready else NEEDS_INFO
        return case

    # ---- tools -------------------------------------------------------------------------------

    def _screen(self, case: Case) -> str:
        req = case.request
        fields = {f: getattr(req, f) for f in req.FREE_TEXT}
        fields.update({f"deliverables[{i}]": d.item for i, d in enumerate(req.deliverables, 1)})
        hits = screen(fields)
        by_field: dict[str, list[dict]] = {}
        for h in hits:
            by_field.setdefault(h["field"], []).append(h)
        for name, hs in by_field.items():
            rules = ", ".join(h["rule"] for h in hs)
            case.flags.append({"id": "SCREEN", "severity": "blocking", "field": name,
                               "text": f"Instruction-like text in '{name}' ({rules}): \"{hs[0]['excerpt']}\". "
                                       "Treated as data, not followed; the field is withheld from the draft."})
        return f"{len(hits)} finding(s) in {len(by_field)} field(s)" if hits else "clean"

    def _classify(self, case: Case) -> str:
        req, cats = case.request, self.policy.categories
        if req.category:
            if req.category in cats:
                case.category = {"id": req.category, "label": cats[req.category].label, "how": "chosen by requester"}
                return f"{req.category} (chosen by requester)"
            case.category = {"id": None, "how": f"'{req.category}' is not a policy category"}
        text = req.text().lower()
        scores = {cid: sum(1 for k in c.keywords if k in text) for cid, c in cats.items()}
        best = max(scores.values()) if scores else 0
        top = sorted(cid for cid, s in scores.items() if s == best and s > 0)
        if len(top) == 1:
            case.category = {"id": top[0], "label": cats[top[0]].label,
                             "how": f"inferred from the request text ({best} keyword match(es)); requester to confirm"}
            return f"{top[0]} (inferred, score {best})"
        case.category = {"id": None, "candidates": top or sorted(cats),
                         "how": "ambiguous" if top else "no match"}
        return "unknown: " + ("tie between " + ", ".join(top) if top else "no keyword match")

    def _aggregate(self, case: Case) -> str:
        req, months = case.request, self.policy.aggregation_months
        since = _months_before(req.submitted, months)
        related = [p for p in self.history
                   if p.unit == req.unit and p.category == case.category["id"]
                   and since <= p.date <= req.submitted and p.status != "cancelled" and p.id != req.id]
        total = req.estimated_value + sum(p.value for p in related)
        case.value = {"own": req.estimated_value, "aggregate": total, "window_months": months,
                      "related": [{"id": p.id, "date": p.date.isoformat(), "value": p.value} for p in related]}
        return f"own {req.estimated_value:,.0f}, aggregate {total:,.0f} over {len(related)} related request(s)"

    def _reuse(self, case: Case) -> str:
        req, cat = case.request, case.category["id"]
        text = req.text().lower()
        for fa in self.policy.frameworks:
            if fa.category != cat or fa.valid_until < req.submitted:
                continue
            if req.estimated_value is not None and req.estimated_value > fa.ceiling_remaining:
                continue
            covered = not fa.scope_keywords or any(k in text for k in fa.scope_keywords)
            case.reuse = {"framework_id": fa.id, "supplier": fa.supplier, "valid_until": fa.valid_until.isoformat(),
                          "coverage": "covered" if covered else "possible: officer to confirm scope",
                          "recommendation": f"Call off under framework agreement {fa.id} instead of a new competition."}
            return f"{fa.id} ({case.reuse['coverage']})"
        return "no active framework agreement for this category"

    def _method(self, case: Case) -> str:
        pol, agg, own = self.policy, case.value["aggregate"], case.value["own"]
        m_agg, m_own = pol.method_for(agg), pol.method_for(own)
        case.method = {"id": m_agg.id, "name": m_agg.name, "basis": "aggregate 12-month value",
                       "value": agg, "threshold": pol.threshold_text(m_agg),
                       "rule": f"{m_agg.id} {m_agg.name}: {pol.currency} {agg:,.0f} "
                               f"({'12-month total' if agg != own else 'this request'}) falls in {pol.threshold_text(m_agg)}"}
        if case.reuse and case.reuse["coverage"] == "covered":
            case.method["recommended"] = f"Call-off under {case.reuse['framework_id']}"
            case.method["rule"] += f"; framework {case.reuse['framework_id']} covers the need, so no new competition"
        else:
            case.method["recommended"] = m_agg.name
        if m_own.id != m_agg.id:
            case.flags.append({"id": "SPLIT", "severity": "attention",
                               "text": f"Possible split purchase: on its own this request ({pol.currency} {own:,.0f}) "
                                       f"would be {m_own.id}, but with {len(case.value['related'])} related request(s) "
                                       f"from {case.request.unit} in the last {pol.aggregation_months} months the total is "
                                       f"{pol.currency} {agg:,.0f}, which requires {m_agg.id}. Method set on the total."})
        return case.method["rule"]

    def _sole_source(self, case: Case) -> str:
        req = case.request
        if not req.preferred_supplier:
            return "no supplier named"
        if case.reuse and case.reuse["coverage"] == "covered":
            return "supplier named, but the framework applies; preference noted for the officer"
        if case.method and case.method["id"] == self.policy.methods[0].id:
            return "supplier named; direct purchase allows it"
        case.flags.append({"id": "SOLE", "severity": "attention",
                           "text": f"Requester names a supplier ({req.preferred_supplier}) for a competitive method. "
                                   + ("Justification given: officer to assess." if req.sole_source_justification
                                      else "No justification given: required before review.")})
        return "justification " + ("given" if req.sole_source_justification else "missing")

    def _draft(self, case: Case) -> str:
        req, cur = case.request, self.policy.currency
        withheld = {f["field"] for f in case.flags if f["id"] == "SCREEN"}

        def val(field_name: str, text: str, missing: str) -> tuple[str, str]:
            if field_name in withheld:
                return TO_CONFIRM.format("text withheld pending review of a screening flag"), "withheld"
            return (text, "drafted") if text else (TO_CONFIRM.format(missing), "to_confirm")

        out = []
        for sec in self.policy.tor_sections:
            s = sec.source
            if s in ("need", "objective", "scope", "qualifications"):
                text, st = val(s, getattr(req, s), f"{sec.title.lower()} from the requester")
            elif s == "deliverables":
                lines = [f"- {d.item} (due {d.due.isoformat()})" if d.due else
                         f"- {d.item} (due {TO_CONFIRM.format('date')})"
                         for i, d in enumerate(req.deliverables, 1) if f"deliverables[{i}]" not in withheld]
                period = (f"Contract period: {req.start.isoformat()} to {req.end.isoformat()}."
                          if req.start and req.end else "Contract period: " + TO_CONFIRM.format("start and end dates"))
                text = "\n".join(lines + [period]) if lines else TO_CONFIRM.format("deliverables with due dates") + "\n" + period
                st = "drafted" if lines and req.start and req.end and all(d.due for d in req.deliverables) else "to_confirm"
            elif s == "supervisor_role":
                text, st = ((f"The contractor reports to the {req.supervisor_role}, {req.unit}.", "drafted")
                            if req.supervisor_role else (TO_CONFIRM.format("who supervises the contractor"), "to_confirm"))
            elif s == "estimated_value":
                if req.estimated_value is None:
                    text, st = TO_CONFIRM.format("estimated value"), "to_confirm"
                else:
                    code = req.budget_code or TO_CONFIRM.format("budget code")
                    text = (f"Estimated value: {cur} {req.estimated_value:,.0f}, funded from budget code {code}. "
                            "Payment against deliverables accepted by the supervisor.")
                    st = "drafted" if req.budget_code else "to_confirm"
            elif s == "handles_personal_data":
                if req.handles_personal_data is None:
                    text, st = TO_CONFIRM.format("does the work involve personal data?"), "to_confirm"
                elif req.handles_personal_data:
                    text, st = ("The work involves personal data. The contractor processes it only for this "
                                "assignment, under the organisation's data protection terms, and returns or "
                                "deletes it at the end of the contract."), "drafted"
                else:
                    text, st = "The work does not involve personal data.", "drafted"
            elif s == "method":
                if case.method and case.method["recommended"].startswith("Call-off"):
                    text = f"Not applicable: call-off under {case.reuse['framework_id']}; the framework's terms apply."
                elif case.method and case.method["id"] == self.policy.methods[0].id:
                    text = "Not applicable for a direct purchase."
                elif case.method:
                    text = ("Offers are evaluated on technical merit and price; weights "
                            + TO_CONFIRM.format("set by the procurement officer") + ".")
                else:
                    text = TO_CONFIRM.format("depends on the method")
                st = "drafted"
            else:
                text, st = TO_CONFIRM.format(sec.title.lower()), "to_confirm"
            out.append({"id": sec.id, "title": sec.title, "text": text, "status": st, "required": sec.required})
        case.tor = out
        n = sum(1 for x in out if x["status"] == "drafted")
        return f"{n}/{len(out)} sections drafted, {len(out) - n} to confirm"

    def _check(self, case: Case) -> str:
        req = case.request
        cat = case.category
        items = [
            ("category", "Category confirmed", bool(cat.get("id")),
             "Which category fits best: " + ", ".join(cat.get("candidates") or []) + "?" if not cat.get("id") else ""),
            ("title", "Short title", bool(req.title), "What is a short title for this purchase?"),
            ("need", "Background: why this is needed", bool(req.need), "Why is this needed, and what happens if it is not bought?"),
            ("objective", "Objective", bool(req.objective), "What should be different when the work is done?"),
            ("scope", "Scope of work", bool(req.scope), "What exactly will the supplier do (and not do)?"),
            ("deliverables", "Deliverables with due dates", bool(req.deliverables) and all(d.due for d in req.deliverables),
             "What will be delivered, and by which date for each item?"),
            ("dates", "Contract start and end", bool(req.start and req.end and req.start <= req.end),
             "When should the work start and end?" if not (req.start and req.end) else "The end date is before the start date: which is right?"),
            ("value", "Estimated value", req.estimated_value is not None, "Roughly how much will this cost, all in?"),
            ("budget", "Budget code", bool(req.budget_code), "Which budget code funds it?"),
            ("supervisor", "Supervisor named (by role)", bool(req.supervisor_role), "Who will supervise the supplier (role)?"),
            ("personal_data", "Personal data question answered", req.handles_personal_data is not None,
             "Will the supplier see or process personal data?"),
        ]
        if any(f["id"] == "SOLE" for f in case.flags):
            items.append(("sole_source", "Justification for the named supplier", bool(req.sole_source_justification),
                          f"Why only {req.preferred_supplier}? Give the reason a competition would not work."))
        if case.blocking_flags:
            items.append(("screening", "No unresolved screening flags", False,
                          "Part of the request reads like an instruction to the system. Rewrite the flagged field as a description of the need."))
        case.checklist = [{"id": i, "label": label, "required": True, "met": met, "question": q if not met else ""}
                          for i, label, met, q in items]
        case.checklist.append({"id": "qualifications", "label": "Required qualifications (recommended)",
                               "required": False, "met": bool(req.qualifications), "question": ""})
        met = sum(1 for c in case.checklist if c["required"] and c["met"])
        total = sum(1 for c in case.checklist if c["required"])
        return f"{met}/{total} required items met"

    def _route(self, case: Case) -> str:
        pol = self.policy
        cat = case.category.get("id")
        queue = pol.categories[cat].queue if cat else "Procurement - Intake triage"
        value = (case.value or {}).get("aggregate", case.request.estimated_value or 0)
        level = "senior officer" if value >= pol.senior_officer_from else "officer"
        case.route = {"queue": queue, "officer_level": level}
        case.approvals_needed = ["procurement officer"]
        if (case.request.estimated_value or 0) >= pol.budget_holder_signoff_from:
            case.approvals_needed.append("budget holder")
        return f"{queue} ({level}); approvals: {', '.join(case.approvals_needed)}"


def _months_before(d: date, months: int) -> date:
    y, m = divmod(d.month - 1 - months, 12)
    year, month = d.year + y, m + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)
