"""Smoke test: python tests/test_smoke.py"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sdr.corpus import TEST_TICKETS
from sdr.engine import DeflectionEngine


def main() -> None:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        eng = DeflectionEngine(boosts_path=Path(td) / "boosts.json", use_llm=False)

        m = eng.run_batch(TEST_TICKETS)
        assert m["decision_accuracy"] >= 0.7, m
        assert 0.3 <= m["deflection_rate"] <= 0.9, m
        assert m["wrong_deflections"] <= 1, m

        d = eng.decide("files named conflicted copy appearing everywhere")
        assert d.deflect and d.article_id == "kb-sync-conflicts", (d.deflect, d.article_id)
        assert d.answer and "conflict" in d.answer.lower()

        hard = eng.decide("please merge my two accounts and transfer ownership keeping billing")
        assert not hard.deflect, "complex account surgery must route to a human"

        # feedback raises confidence and persists
        before = eng.decide("conflicted copy files").confidence
        eng.feedback("kb-sync-conflicts", helpful=True)
        eng2 = DeflectionEngine(boosts_path=Path(td) / "boosts.json", use_llm=False)
        after = eng2.decide("conflicted copy files").confidence
        assert after >= before, (before, after)
        eng2.feedback("kb-linux-client", helpful=False)
        assert eng2.boosts["kb-linux-client"] < 1.0
    print(f"OK - {m}")


if __name__ == "__main__":
    main()


def test_smoke():
    main()
