"""Usage events in the ai-adoption-tracker format (date, use_case_id, user_id, action).

So the intake desk's own pilot can be reviewed for scale, iterate or stop on evidence. One
`task_completed` per request confirmed by its requester, and the requester's optional thumbs
rating as feedback. User ids are the pseudonymous requester ids; nothing else leaves the case.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

from .workflow import load_case

FIELDS = ["date", "use_case_id", "user_id", "action"]


def collect(cases_dir: str | Path, use_case_id: str) -> list[dict]:
    rows = []
    for p in sorted(Path(cases_dir).glob("*.case.json")):
        case = load_case(p)
        for h in case.history:
            if h["role"] == "requester" and h["action"] == "confirmed draft":
                rows.append({"date": h["date"], "use_case_id": use_case_id, "user_id": h["by"], "action": "task_completed"})
                if h.get("rating") in ("up", "down"):
                    rows.append({"date": h["date"], "use_case_id": use_case_id, "user_id": h["by"],
                                 "action": "feedback_positive" if h["rating"] == "up" else "feedback_negative"})
    return rows


def to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()
