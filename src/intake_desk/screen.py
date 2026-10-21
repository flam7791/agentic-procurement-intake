"""Untrusted-text screening.

Everything a requester writes is data. Text that reads like an instruction to the system (approve
this, ignore the rules, change the method) is flagged, kept out of the TOR draft, and blocks the
case until a person has looked at it. It is never acted on.
"""
from __future__ import annotations

import re

PATTERNS = [
    ("override-instructions", re.compile(r"\b(ignore|disregard|override)\b.{0,40}\b(instruction|rule|policy|polic(y|ies)|threshold|previous|above)s?\b", re.I)),
    ("self-approval", re.compile(r"\b(mark|set|treat|consider)\b.{0,30}\b(as\s+)?approved\b|\bapprove (this|it|the request)\b|\bauto-?approve\b", re.I)),
    ("method-steering", re.compile(r"\b(set|change|use|switch)\b.{0,30}\b(method|procedure)\b.{0,30}\b(direct|single|sole)\b", re.I)),
    ("role-play", re.compile(r"\b(you are now|act as|system prompt|developer mode)\b", re.I)),
]


def screen(fields: dict[str, str]) -> list[dict]:
    """Return one finding per (field, pattern) hit: {'field', 'rule', 'excerpt'}."""
    out = []
    for name, text in fields.items():
        if not text:
            continue
        for rule, rx in PATTERNS:
            m = rx.search(text)
            if m:
                s = text.rfind(" ", 0, max(0, m.start() - 10)) + 1
                e = text.find(" ", min(len(text), m.end() + 10))
                excerpt = text[s:e if e != -1 else len(text)].strip()
                out.append({"field": name, "rule": rule, "excerpt": ("..." if s else "") + excerpt + ("..." if e != -1 else "")})
    return out
