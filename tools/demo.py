"""Run every sample request, then walk two through the human checkpoints.

    python tools/demo.py [--out out]

R-101 (under the sign-off threshold): requester confirms, officer approves.
R-102 (framework call-off, above the threshold): requester confirms, officer approves, a different
budget holder signs off. Everything else stays where the agent left it, waiting for a person.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from intake_desk.cli import main  # noqa: E402


def run(*args: str) -> None:
    if main(list(args)) != 0:
        raise SystemExit(f"failed: intake-desk {' '.join(args)}")


def demo(out: str) -> None:
    samples = ROOT / "data" / "sample"
    for req in sorted((samples / "requests").glob("*.json")):
        run("run", str(req), "--history", str(samples / "history.csv"), "--out", out)
    o = Path(out)
    run("confirm", str(o / "R-101.case.json"), "--by", "req-4821", "--rating", "up", "--date", "2026-10-13")
    run("decide", str(o / "R-101.case.json"), "--role", "procurement_officer", "--by", "po-17", "--approve",
        "--date", "2026-10-14")
    run("confirm", str(o / "R-102.case.json"), "--by", "req-1907", "--rating", "up", "--date", "2026-10-15")
    run("decide", str(o / "R-102.case.json"), "--role", "procurement_officer", "--by", "po-22", "--approve",
        "--note", "Call-off confirmed; scope within FA-2026-02 lot 1.", "--date", "2026-10-16")
    run("decide", str(o / "R-102.case.json"), "--role", "budget_holder", "--by", "bh-03", "--approve",
        "--date", "2026-10-19")
    print()
    run("queue", out)
    print()
    run("events", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    demo(ap.parse_args().out)
