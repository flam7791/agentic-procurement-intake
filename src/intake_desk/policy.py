"""Procurement policy: thresholds, categories, framework agreements and the TOR template.

The policy file is owned by the procurement unit. The agent reads it; it never changes it.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

DEFAULT_POLICY = Path(__file__).resolve().parents[2] / "config" / "policy.json"


@dataclass(frozen=True)
class Method:
    id: str
    name: str
    below: float | None  # None = no upper bound


@dataclass(frozen=True)
class Category:
    id: str
    label: str
    keywords: tuple[str, ...]
    queue: str


@dataclass(frozen=True)
class Framework:
    id: str
    category: str
    supplier: str
    valid_until: date
    ceiling_remaining: float
    scope_keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class TorSection:
    id: str
    title: str
    source: str
    required: bool


@dataclass
class Policy:
    version: str
    currency: str
    aggregation_months: int
    methods: list[Method]
    budget_holder_signoff_from: float
    senior_officer_from: float
    categories: dict[str, Category]
    frameworks: list[Framework]
    tor_sections: list[TorSection] = field(default_factory=list)
    roles: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def method_for(self, value: float) -> Method:
        for m in self.methods:
            if m.below is None or value < m.below:
                return m
        raise ValueError("policy has no open-ended method")

    def threshold_text(self, m: Method) -> str:
        lower = 0.0
        for prev in self.methods:
            if prev.id == m.id:
                break
            lower = prev.below or lower
        if m.below is None:
            return f"{self.currency} {lower:,.0f} and above"
        return f"{self.currency} {lower:,.0f} to under {m.below:,.0f}"


class PolicyError(ValueError):
    pass


def load_policy(path: str | Path | None = None) -> Policy:
    p = Path(path) if path else DEFAULT_POLICY
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        methods = [Method(m["id"], m["name"], m["below"]) for m in raw["methods"]]
        cats = {k: Category(k, v["label"], tuple(w.lower() for w in v["keywords"]), v["queue"])
                for k, v in raw["categories"].items()}
        fas = [Framework(f["id"], f["category"], f["supplier"], date.fromisoformat(f["valid_until"]),
                         float(f["ceiling_remaining"]), tuple(w.lower() for w in f.get("scope_keywords", [])))
               for f in raw.get("framework_agreements", [])]
        secs = [TorSection(s["id"], s["title"], s["from"], bool(s["required"])) for s in raw["tor_sections"]]
        pol = Policy(raw["version"], raw["currency"], int(raw["aggregation_months"]), methods,
                     float(raw["budget_holder_signoff_from"]), float(raw["senior_officer_from"]),
                     cats, fas, secs,
                     {k: tuple(v) for k, v in raw.get("roles", {}).items() if not k.startswith("_")})
    except (KeyError, TypeError, ValueError) as e:
        raise PolicyError(f"policy file {p.name} is invalid: {e!r}") from e
    if not methods or methods[-1].below is not None:
        raise PolicyError("the last method must have no upper bound (below: null)")
    for f in fas:
        if f.category not in cats:
            raise PolicyError(f"framework {f.id} names unknown category {f.category}")
    return pol
