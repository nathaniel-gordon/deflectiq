"""Support Deflection RAG — Chain of Responsibility Escalation Ladder & Interactive CLI.

Usage
-----
    python -m sdr demo                      # run batch deflection matrix benchmark
    python -m sdr                           # interactive deflection prompt loop
    python -m sdr deflect "my ticket query" # single ticket routing check
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .corpus import TEST_TICKETS
from .engine import DeflectionEngine

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"
BOOSTS = OUT / "boosts.json"


def cmd_demo(no_llm: bool = True) -> None:
    OUT.mkdir(exist_ok=True)
    print("=================================================================")
    print("  SUPPORT DEFLECTION RAG — CHAIN OF RESPONSIBILITY ESCALATION    ")
    print("=================================================================")
    eng = DeflectionEngine(boosts_path=BOOSTS, use_llm=not no_llm)
    
    print("\n[1/3] Sample Ticket Decisions through Escalation Ladder:\n")
    sample_cases = [TEST_TICKETS[0], TEST_TICKETS[2], TEST_TICKETS[8]]
    for text, expected in sample_cases:
        d = eng.decide(text)
        print(f"Incoming Ticket: {text[:75]}...")
        print(f"  -> Deflect: {d.deflect} | Confidence: {d.confidence:.2f} | Article: {d.article_id} (Expected: {expected})")
        for r in d.reasons:
            print(f"     * {r}")
        if d.answer:
            print(f"     * Automated Draft: {d.answer[:110]}...")
        print()

    print("[2/3] Evaluating Decision-Matrix Across Benchmark Test Corpus:")
    metrics = eng.run_batch(TEST_TICKETS)
    print(f"      Metrics: {metrics}")

    print("\n[3/3] Dynamic Feedback Loop & Article Weight Rebalancing:")
    before = eng.decide(TEST_TICKETS[0][0]).confidence
    eng.feedback("kb-sync-conflicts", helpful=True)
    eng.feedback("kb-sync-conflicts", helpful=True)
    after = eng.decide(TEST_TICKETS[0][0]).confidence
    print(f"      Confidence for sync-conflict query: {before:.2f} -> {after:.2f} (Boosts updated in {BOOSTS.name})")

    (OUT / "deflection_report.md").write_text(
        f"# Support Deflection Decision Matrix Report\n\nBenchmark: `{metrics}`\n\nEscalation Ladder: Rule Filters -> Semantic Match -> Confidence Gate -> Fallback to Human Tier.\n",
        encoding="utf-8"
    )
    print(f"\nReport -> {OUT / 'deflection_report.md'}")


def interactive_loop() -> None:
    OUT.mkdir(exist_ok=True)
    eng = DeflectionEngine(boosts_path=BOOSTS, use_llm=False)
    print("=================================================================")
    print("  Support Deflection Interactive Shell (Type 'quit' to exit)     ")
    print("=================================================================")
    while True:
        try:
            query = input("\nTicket > ").strip()
            if not query or query.lower() in ("quit", "exit", "q"):
                break
            dec = eng.decide(query)
            print(f"Decision: Deflect={dec.deflect} | Conf={dec.confidence:.2f} | Target={dec.article_id}")
            for r in dec.reasons:
                print(f"  - {r}")
            if dec.answer:
                print(f"\nDraft Answer:\n{dec.answer}")
        except (KeyboardInterrupt, EOFError):
            break
    print("\nExiting interactive shell.")


def main() -> None:
    p = argparse.ArgumentParser(description="Support Deflection RAG — Chain of Responsibility")
    p.add_argument("--demo", action="store_true", help="run demonstration & benchmark")
    p.add_argument("--deflect", type=str, help="evaluate a single ticket text")
    p.add_argument("--no-llm", action="store_true", default=True, help="offline deterministic fallback")
    args = p.parse_args()

    if args.deflect:
        OUT.mkdir(exist_ok=True)
        eng = DeflectionEngine(boosts_path=BOOSTS, use_llm=not args.no_llm)
        dec = eng.decide(args.deflect)
        print(f"deflect={dec.deflect} confidence={dec.confidence:.2f} article={dec.article_id}")
        print("\n".join(f"- {r}" for r in dec.reasons))
        if dec.answer:
            print(f"\nAnswer:\n{dec.answer}")
    elif args.demo:
        cmd_demo(no_llm=args.no_llm)
    elif len(sys.argv) == 1:
        # Default with no args: run demo non-interactively for test automation
        cmd_demo(no_llm=True)
    else:
        interactive_loop()


if __name__ == "__main__":
    main()
