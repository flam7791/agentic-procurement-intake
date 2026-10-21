"""The request package an officer reads: Markdown, HTML (light and dark) and JSON."""
from __future__ import annotations

import html
import json
import re

from .agent import APPROVED, AWAITING_OFFICER, NEEDS_INFO, RETURNED, Case

MARK = re.compile(r"\[TO CONFIRM: [^\]]*\]")


def _readiness(case: Case) -> str:
    req = [c for c in case.checklist if c["required"]]
    return f"{sum(c['met'] for c in req)}/{len(req)}"


def to_json(case: Case) -> str:
    return json.dumps(case.to_dict(), indent=2, ensure_ascii=False) + "\n"


def to_markdown(case: Case) -> str:
    r = case.request
    cur = "USD"
    L = [f"# Request package {r.id}: {r.title or '(untitled)'}", "",
         f"**Status:** {case.status}  ", f"**Next human step:** {case.next_step()}  ",
         f"**Unit:** {r.unit} · **Requester:** {r.requester} · **Submitted:** {r.submitted.isoformat()} · "
         f"**Policy:** {case.policy_version}", "",
         "> Prepared by the intake agent. Nothing here is approved until a person approves it.", ""]
    L += ["## Summary", "", "| | |", "|---|---|",
          f"| Category | {case.category.get('label') or 'unknown'} ({case.category.get('how', '')}) |",
          f"| Recommended method | {case.method['recommended'] if case.method else 'not determined yet'} |",
          f"| Rule | {case.method['rule'] if case.method else '-'} |",
          f"| Reuse | {case.reuse['recommendation'] + ' (' + case.reuse['coverage'] + ')' if case.reuse else 'no framework agreement applies'} |",
          f"| Readiness | {_readiness(case)} required items |",
          f"| Route | {case.route.get('queue', '-')} ({case.route.get('officer_level', '-')}) |",
          f"| Approvals needed | {', '.join(case.approvals_needed) or '-'} |", ""]
    if case.value.get("related"):
        L += [f"Related requests counted in the {case.value['window_months']}-month total: "
              + ", ".join(f"{x['id']} ({x['date']}, {cur} {x['value']:,.0f})" for x in case.value["related"]), ""]
    if case.flags:
        L += ["## Flags", ""] + [f"- **{f['id']}** ({f['severity']}): {f['text']}" for f in case.flags] + [""]
    if case.questions:
        L += ["## Questions for the requester", ""] + [f"{i}. {q}" for i, q in enumerate(case.questions, 1)] + [""]
    L += ["## Draft terms of reference", ""]
    for s in case.tor:
        L += [f"### {s['title']}", "", s["text"], ""]
    L += ["## Completeness checklist", "", "| Item | Required | Met |", "|---|---|---|"]
    L += [f"| {c['label']} | {'yes' if c['required'] else 'no'} | {'yes' if c['met'] else '**no**'} |" for c in case.checklist]
    L += ["", "## Audit trail (agent)", "", "| Step | Tool | Why | Result |", "|---|---|---|---|"]
    L += [f"| {t['step']} | {t['tool']} | {t['reason']} | {t['result']} |" for t in case.trace]
    if case.history:
        L += ["", "## Decisions (people)", "", "| Date | Role | Who | Action | Note |", "|---|---|---|---|---|"]
        L += [f"| {h['date']} | {h['role']} | {h['by']} | {h['action']} | {h['note']} |" for h in case.history]
    return "\n".join(L) + "\n"


CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#1d2433;--muted:#5b6475;--line:#e3e6ec;--accent:#2457c5;
--ok:#1f7a4d;--okbg:#e6f4ec;--warn:#9a5b00;--warnbg:#fff3df;--bad:#b42318;--badbg:#fdecea;--tc:#fff1c2}
@media (prefers-color-scheme:dark){:root{--bg:#0f1420;--card:#171e2d;--ink:#e6e9ef;--muted:#9aa3b5;--line:#2a3347;
--accent:#7aa2ff;--ok:#5fd39a;--okbg:#14301f;--warn:#ffc266;--warnbg:#33260f;--bad:#ff8a80;--badbg:#3a1714;--tc:#4a3b0b}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:1040px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:0 0 10px}.muted{color:var(--muted)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}
.top{display:flex;gap:12px;flex-wrap:wrap;align-items:center;justify-content:space-between}
.pill{display:inline-block;border-radius:999px;padding:3px 12px;font-weight:600;font-size:13px}
.s-ok{background:var(--okbg);color:var(--ok)}.s-warn{background:var(--warnbg);color:var(--warn)}.s-bad{background:var(--badbg);color:var(--bad)}
.next{border-left:4px solid var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.k{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}.v{font-weight:600;margin-top:2px}
.flag{padding:10px 12px;border-radius:8px;margin:8px 0}.f-blocking{background:var(--badbg)}.f-attention{background:var(--warnbg)}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600}.tc{background:var(--tc);border-radius:4px;padding:0 3px}
.sec h3{font-size:14px;margin:12px 0 4px}.sec p{margin:0;white-space:pre-line}
.yes{color:var(--ok);font-weight:600}.no{color:var(--bad);font-weight:600}
"""


def _e(s) -> str:
    return html.escape(str(s))


def _tc(s: str) -> str:
    return MARK.sub(lambda m: f'<span class="tc">{m.group(0)}</span>', _e(s))


def to_html(case: Case) -> str:
    r = case.request
    cls = {APPROVED: "s-ok", AWAITING_OFFICER: "s-ok", NEEDS_INFO: "s-bad", RETURNED: "s-bad"}.get(case.status, "s-warn")
    m = case.method
    facts = [("Recommended method", m["recommended"] if m else "Not determined yet"),
             ("Reuse first", f"{case.reuse['framework_id']}: {case.reuse['coverage']}" if case.reuse else "No framework applies"),
             ("Readiness", f"{_readiness(case)} required items"),
             ("Route", f"{case.route.get('queue', '-')} · {case.route.get('officer_level', '-')}"),
             ("Approvals needed", ", ".join(case.approvals_needed) or "-"),
             ("Category", case.category.get("label") or "Unknown")]
    h = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
         f"<title>Request {_e(r.id)}</title><style>{CSS}</style></head><body><main>",
         "<div class='top'><div>"
         f"<div class='muted'>Request package · {_e(r.unit)} · requester {_e(r.requester)} · submitted {r.submitted.isoformat()}</div>"
         f"<h1>{_e(r.id)}: {_e(r.title or '(untitled)')}</h1></div>"
         f"<span class='pill {cls}'>{_e(case.status)}</span></div>",
         f"<div class='card next'><div class='k'>Next human step</div><div class='v'>{_e(case.next_step())}</div>"
         "<div class='muted' style='margin-top:6px'>Prepared by the intake agent. Nothing here is approved until a person approves it.</div></div>",
         "<div class='card'><div class='grid'>" + "".join(
             f"<div><div class='k'>{_e(k)}</div><div class='v'>{_e(v)}</div></div>" for k, v in facts) + "</div>"]
    if m:
        h.append(f"<p class='muted' style='margin:12px 0 0'>Rule: {_e(m['rule'])}</p>")
    if case.value.get("related"):
        rel = ", ".join(f"{x['id']} ({x['date']}, USD {x['value']:,.0f})" for x in case.value["related"])
        h.append(f"<p class='muted' style='margin:4px 0 0'>Counted in the {case.value['window_months']}-month total: {_e(rel)}</p>")
    h.append("</div>")
    if case.flags or case.questions:
        h.append("<div class='card'><h2>Flags and questions</h2>")
        h += [f"<div class='flag f-{_e(f['severity'])}'><b>{_e(f['id'])}</b> · {_e(f['severity'])}<br>{_e(f['text'])}</div>" for f in case.flags]
        if case.questions:
            h.append("<div class='k' style='margin-top:10px'>Questions for the requester</div><ol>"
                     + "".join(f"<li>{_e(q)}</li>" for q in case.questions) + "</ol>")
        h.append("</div>")
    h.append("<div class='card sec'><h2>Draft terms of reference</h2>"
             + "".join(f"<h3>{_e(s['title'])}</h3><p>{_tc(s['text'])}</p>" for s in case.tor) + "</div>")
    h.append("<div class='card'><h2>Completeness checklist</h2><table><tr><th>Item</th><th>Required</th><th>Met</th></tr>"
             + "".join(f"<tr><td>{_e(c['label'])}</td><td>{'yes' if c['required'] else 'no'}</td>"
                       f"<td class='{'yes' if c['met'] else 'no'}'>{'yes' if c['met'] else 'no'}</td></tr>" for c in case.checklist)
             + "</table></div>")
    h.append("<div class='card'><h2>Audit trail: what the agent did and why</h2><table><tr><th>#</th><th>Tool</th><th>Why</th><th>Result</th></tr>"
             + "".join(f"<tr><td>{t['step']}</td><td>{_e(t['tool'])}</td><td>{_e(t['reason'])}</td><td>{_e(t['result'])}</td></tr>" for t in case.trace)
             + "</table></div>")
    if case.history:
        h.append("<div class='card'><h2>Decisions by people</h2><table><tr><th>Date</th><th>Role</th><th>Who</th><th>Action</th><th>Note</th></tr>"
                 + "".join(f"<tr><td>{_e(x['date'])}</td><td>{_e(x['role'])}</td><td>{_e(x['by'])}</td><td>{_e(x['action'])}</td><td>{_e(x['note'])}</td></tr>" for x in case.history)
                 + "</table></div>")
    h.append("<p class='muted'>Fictional organisation and sample policy. Generated by intake-desk.</p></main></body></html>")
    return "\n".join(h) + "\n"
