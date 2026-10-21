"""intake-desk: prepare a purchase request for approval; people decide.

    intake-desk run REQUEST.json [--history H.csv] [--policy P.json] [--out DIR]
    intake-desk confirm CASE.case.json --by REQUESTER_ID [--rating up|down] [--date YYYY-MM-DD]
    intake-desk decide CASE.case.json --role procurement_officer|budget_holder --by ID (--approve | --return --note TEXT)
    intake-desk queue DIR
    intake-desk events DIR [--use-case-id UC-INTAKE] [--out events.csv]
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .agent import IntakeAgent
from .events import collect, to_csv
from .policy import PolicyError, load_policy
from .render import to_html, to_markdown
from .request import RequestError, load_history, load_request
from .workflow import WorkflowError, confirm, decide, load_case, save_case


def _write_all(case, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    base = out / case.request.id
    p = save_case(case, base.with_suffix(".case.json"))
    base.with_suffix(".md").write_text(to_markdown(case), encoding="utf-8")
    base.with_suffix(".html").write_text(to_html(case), encoding="utf-8")
    return p


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="intake-desk", description=__doc__.splitlines()[0])
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="prepare a request package")
    r.add_argument("request")
    r.add_argument("--history")
    r.add_argument("--policy")
    r.add_argument("--out", default="out")

    c = sub.add_parser("confirm", help="requester confirms the draft")
    c.add_argument("case")
    c.add_argument("--by", required=True)
    c.add_argument("--rating", choices=["up", "down"])
    c.add_argument("--date")

    d = sub.add_parser("decide", help="officer or budget holder approves or returns")
    d.add_argument("case")
    d.add_argument("--role", required=True)
    d.add_argument("--by", required=True)
    g = d.add_mutually_exclusive_group(required=True)
    g.add_argument("--approve", action="store_true")
    g.add_argument("--return", dest="ret", action="store_true")
    d.add_argument("--note", default="")
    d.add_argument("--date")
    d.add_argument("--policy")

    q = sub.add_parser("queue", help="list cases by status")
    q.add_argument("dir")

    e = sub.add_parser("events", help="usage events in the ai-adoption-tracker format")
    e.add_argument("dir")
    e.add_argument("--use-case-id", default="UC-INTAKE")
    e.add_argument("--out")

    a = ap.parse_args(argv)
    try:
        if a.cmd == "run":
            agent = IntakeAgent(load_policy(a.policy), load_history(a.history))
            case = agent.run(load_request(a.request))
            p = _write_all(case, Path(a.out))
            print(f"{case.request.id}: {case.status} | method: "
                  f"{case.method['recommended'] if case.method else 'not determined'} | "
                  f"flags: {', '.join(f['id'] for f in case.flags) or 'none'} | "
                  f"questions: {len(case.questions)} | {p}")
        elif a.cmd in ("confirm", "decide"):
            day = date.fromisoformat(a.date) if a.date else date.today()
            case = load_case(a.case)
            if a.cmd == "confirm":
                confirm(case, a.by, day, a.rating)
            else:
                decide(case, a.role, a.by, a.approve, day, a.note, roster=load_policy(a.policy).roles)
            _write_all(case, Path(a.case).parent)
            print(f"{case.request.id}: {case.status}. Next: {case.next_step()}")
        elif a.cmd == "queue":
            rows = [load_case(p) for p in sorted(Path(a.dir).glob("*.case.json"))]
            print(f"{'id':10} {'status':38} {'queue':28} {'readiness':9} flags")
            for cs in rows:
                req = [x for x in cs.checklist if x["required"]]
                print(f"{cs.request.id:10} {cs.status:38} {cs.route.get('queue', '-'):28} "
                      f"{sum(x['met'] for x in req)}/{len(req):<7} {','.join(f['id'] for f in cs.flags) or '-'}")
        elif a.cmd == "events":
            text = to_csv(collect(a.dir, a.use_case_id))
            if a.out:
                Path(a.out).write_text(text, encoding="utf-8")
            else:
                sys.stdout.write(text)
    except (RequestError, PolicyError, WorkflowError, FileNotFoundError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
