"""A purchase request as a guided form or chat would collect it, plus the unit's request history.

Missing answers are allowed: the agent turns them into questions. Malformed files are not: they
stop with the field name. Requesters are identified by a pseudonymous id, never an email address.
"""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path


class RequestError(ValueError):
    pass


@dataclass
class Deliverable:
    item: str
    due: date | None


@dataclass
class Request:
    id: str
    submitted: date
    requester: str
    unit: str
    title: str = ""
    need: str = ""
    objective: str = ""
    scope: str = ""
    deliverables: list[Deliverable] = field(default_factory=list)
    start: date | None = None
    end: date | None = None
    estimated_value: float | None = None
    budget_code: str = ""
    category: str = ""
    qualifications: str = ""
    supervisor_role: str = ""
    handles_personal_data: bool | None = None
    preferred_supplier: str = ""
    sole_source_justification: str = ""

    FREE_TEXT = ("title", "need", "objective", "scope", "qualifications", "sole_source_justification")

    def text(self) -> str:
        """All free text the requester wrote, for classification and screening."""
        parts = [getattr(self, f) for f in self.FREE_TEXT] + [d.item for d in self.deliverables]
        return " ".join(p for p in parts if p)

    def to_dict(self) -> dict:
        d = asdict(self)
        for k in ("submitted", "start", "end"):
            d[k] = d[k].isoformat() if d[k] else None
        d["deliverables"] = [{"item": x.item, "due": x.due.isoformat() if x.due else None}
                             for x in self.deliverables]
        return d


def _date(raw, name: str) -> date | None:
    if raw in (None, ""):
        return None
    try:
        return date.fromisoformat(str(raw))
    except ValueError as e:
        raise RequestError(f"field '{name}' is not an ISO date (YYYY-MM-DD): {raw!r}") from e


def request_from_dict(raw: dict) -> Request:
    for k in ("id", "submitted", "requester", "unit"):
        if not raw.get(k):
            raise RequestError(f"field '{k}' is required")
    if "@" in str(raw["requester"]):
        raise RequestError("field 'requester' must be a pseudonymous id, not an email address")
    value = raw.get("estimated_value")
    if value not in (None, ""):
        try:
            value = float(value)
        except (TypeError, ValueError) as e:
            raise RequestError(f"field 'estimated_value' is not a number: {value!r}") from e
        if value <= 0:
            raise RequestError("field 'estimated_value' must be positive")
    else:
        value = None
    pd = raw.get("handles_personal_data")
    if pd not in (None, True, False):
        raise RequestError("field 'handles_personal_data' must be true, false or null")
    dels = []
    for i, d in enumerate(raw.get("deliverables") or [], 1):
        if not isinstance(d, dict) or not d.get("item"):
            raise RequestError(f"deliverable {i} needs an 'item'")
        dels.append(Deliverable(str(d["item"]).strip(), _date(d.get("due"), f"deliverables[{i}].due")))
    text = {k: str(raw.get(k) or "").strip() for k in
            ("title", "need", "objective", "scope", "budget_code", "category", "qualifications",
             "supervisor_role", "preferred_supplier", "sole_source_justification")}
    return Request(id=str(raw["id"]), submitted=_date(raw["submitted"], "submitted"),
                   requester=str(raw["requester"]), unit=str(raw["unit"]), deliverables=dels,
                   start=_date(raw.get("start"), "start"), end=_date(raw.get("end"), "end"),
                   estimated_value=value, handles_personal_data=pd, **text)


def load_request(path: str | Path) -> Request:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise RequestError(f"{Path(path).name} is not valid JSON: {e}") from e
    return request_from_dict(raw)


@dataclass(frozen=True)
class PastRequest:
    id: str
    date: date
    unit: str
    category: str
    value: float
    status: str


def load_history(path: str | Path | None) -> list[PastRequest]:
    if not path:
        return []
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = {"id", "date", "unit", "category", "value", "status"} - set(reader.fieldnames or [])
        if missing:
            raise RequestError(f"history file is missing column(s): {', '.join(sorted(missing))}")
        for n, row in enumerate(reader, 2):
            try:
                out.append(PastRequest(row["id"], date.fromisoformat(row["date"]), row["unit"],
                                       row["category"], float(row["value"]), row["status"].strip().lower()))
            except ValueError as e:
                raise RequestError(f"history row {n}: {e}") from e
    return out
