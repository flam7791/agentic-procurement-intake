"""Human checkpoints. The only way a case moves past the draft is a person acting in a named role.

    requester confirms the draft  ->  procurement officer approves or returns
                                  ->  budget holder signs off (at or above the sign-off threshold)

The agent role can prepare and re-check a case; it cannot confirm, approve or return one. The
requester cannot approve their own request, and the budget holder must be a different person from
the officer who approved it (four eyes).
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .agent import (APPROVED, AWAITING_BUDGET_HOLDER, AWAITING_OFFICER, AWAITING_REQUESTER, RETURNED,
                    Case)
from .policy import load_policy
from .request import request_from_dict

ROLES = ("requester", "procurement_officer", "budget_holder", "agent")


class WorkflowError(PermissionError):
    pass


def _log(case: Case, day: date, role: str, by: str, action: str, note: str = "", **extra) -> None:
    case.history.append({"date": day.isoformat(), "role": role, "by": by, "action": action,
                         "from": extra.pop("from_status"), "to": case.status, "note": note, **extra})


def confirm(case: Case, by: str, day: date, rating: str | None = None) -> Case:
    if "@" in by:
        raise WorkflowError("use a pseudonymous id, not an email address")
    if by != case.request.requester:
        raise WorkflowError("only the requester who submitted the request can confirm the draft")
    if case.status != AWAITING_REQUESTER:
        raise WorkflowError(f"cannot confirm a case in status '{case.status}'"
                            + (f"; answer first: {'; '.join(case.questions)}" if case.questions else ""))
    if rating not in (None, "up", "down"):
        raise WorkflowError("rating must be 'up' or 'down'")
    before = case.status
    case.status = AWAITING_OFFICER
    _log(case, day, "requester", by, "confirmed draft", from_status=before, rating=rating)
    return case


def decide(case: Case, role: str, by: str, approve: bool, day: date, note: str = "",
           roster: dict[str, tuple[str, ...]] | None = None) -> Case:
    """An officer or budget holder decides. `roster` maps roles to the ids allowed to act in them
    (from the policy file; at pilot, from single sign-on groups). v0.1 trusts the id it is given."""
    if role == "agent":
        raise WorkflowError("the agent prepares cases; it cannot approve or return them")
    if role not in ("procurement_officer", "budget_holder"):
        raise WorkflowError(f"role '{role}' cannot decide on a case")
    if "@" in by:
        raise WorkflowError("use a pseudonymous id, not an email address")
    if by == case.request.requester:
        raise WorkflowError("the requester cannot decide on their own request")
    roster = load_policy().roles if roster is None else roster
    if by not in roster.get(role, ()):
        raise WorkflowError(f"'{by}' is not on the roster for the role '{role}'")
    flagged = [f["id"] for f in case.flags if f["severity"] == "attention"]
    if approve and role == "procurement_officer" and flagged and not note.strip():
        raise WorkflowError(f"approving a case flagged {', '.join(flagged)} needs a note recording the officer's judgment")
    if not approve and not note.strip():
        raise WorkflowError("returning a case needs a note telling the requester what to change")
    before = case.status
    if role == "procurement_officer":
        if case.status != AWAITING_OFFICER:
            raise WorkflowError(f"the officer decides only on cases '{AWAITING_OFFICER}', not '{case.status}'")
        if approve:
            case.status = AWAITING_BUDGET_HOLDER if "budget holder" in case.approvals_needed else APPROVED
        else:
            case.status = RETURNED
    else:
        if case.status != AWAITING_BUDGET_HOLDER:
            raise WorkflowError(f"the budget holder signs off only cases '{AWAITING_BUDGET_HOLDER}', not '{case.status}'")
        officers = {h["by"] for h in case.history if h["role"] == "procurement_officer" and h["action"] == "approved"}
        if by in officers:
            raise WorkflowError("four eyes: the budget holder must be a different person from the approving officer")
        case.status = APPROVED if approve else RETURNED
    _log(case, day, role, by, "approved" if approve else "returned", note, from_status=before)
    return case


# ---- persistence -------------------------------------------------------------------------------

def save_case(case: Case, path: str | Path) -> Path:
    p = Path(path)
    p.write_text(json.dumps(case.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def load_case(path: str | Path) -> Case:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    case = Case(request=request_from_dict(d["request"]), policy_version=d["policy_version"])
    for k in ("status", "category", "value", "method", "reuse", "flags", "tor", "checklist", "route",
              "approvals_needed", "trace", "history"):
        setattr(case, k, d[k])
    return case
