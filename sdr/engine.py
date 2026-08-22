"""Deflection engine: retrieval + confidence gate + feedback boosts + savings metrics."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .corpus import KB_ARTICLES, RESOLVED_TICKETS
from .llm import get_llm
from .retrieval import tokenize

HANDLING_COST_USD = 8.0     # avg human cost per ticket

# tickets containing these always route to a human, regardless of retrieval confidence
ESCALATION_TERMS = ("compensation", "refund", "legal", "lawyer", "lawsuit", "gdpr",
                    "merge my", "merge two", "transfer ownership", "delete my account",
                    "corrupted", "data loss", "sue")


@dataclass
class Decision:
    ticket: str
    deflect: bool
    confidence: float
    article_id: str | None
    article_title: str | None
    answer: str | None
    reasons: list[str] = field(default_factory=list)
    candidates: list[tuple[str, float]] = field(default_factory=list)


class DeflectionEngine:
    def __init__(self, boosts_path: str | Path | None = None,
                 deflect_threshold: float = 0.55, use_llm: bool = True):
        self.threshold = deflect_threshold
        self.boosts_path = Path(boosts_path) if boosts_path else None
        self.boosts: dict[str, float] = self._load_boosts()
        self.llm = get_llm() if use_llm else None
        # article bundles: article text + the resolved tickets it solved (vocabulary bridge —
        # customers phrase problems like past tickets, not like KB articles)
        bundles: dict[str, str] = {aid: f"{title} {body}"
                                   for aid, (title, body) in KB_ARTICLES.items()}
        for _, (subject, resolution, aid) in RESOLVED_TICKETS.items():
            bundles[aid] += f" {subject} {resolution}"
        self.article_ids = list(bundles)
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.vectorizer = TfidfVectorizer(tokenizer=tokenize, token_pattern=None,
                                          ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform([bundles[a] for a in self.article_ids])

    # ---------- feedback ----------
    def _load_boosts(self) -> dict[str, float]:
        if self.boosts_path and self.boosts_path.exists():
            return json.loads(self.boosts_path.read_text(encoding="utf-8"))
        return {}

    def feedback(self, article_id: str, helpful: bool) -> float:
        b = self.boosts.get(article_id, 1.0)
        b = min(b + 0.1, 1.5) if helpful else max(b - 0.15, 0.5)
        self.boosts[article_id] = round(b, 3)
        if self.boosts_path:
            self.boosts_path.parent.mkdir(parents=True, exist_ok=True)
            self.boosts_path.write_text(json.dumps(self.boosts, indent=2), encoding="utf-8")
        return b

    # ---------- deflection ----------
    def decide(self, ticket_text: str, k: int = 6) -> Decision:
        from sklearn.metrics.pairwise import cosine_similarity
        sims = cosine_similarity(self.vectorizer.transform([ticket_text]), self.matrix).ravel()
        boosted = [(aid, float(s) * self.boosts.get(aid, 1.0))
                   for aid, s in zip(self.article_ids, sims)]
        ranked = sorted(boosted, key=lambda kv: -kv[1])
        reasons = []
        top_id, top_cos = ranked[0]
        margin = top_cos - ranked[1][1]
        confidence = 0.6 * min(1.0, top_cos / 0.25) + 0.4 * min(1.0, margin / 0.15)
        reasons.append(f"bundle cosine {top_cos:.3f}, margin over runner-up {margin:.3f}")
        low = ticket_text.lower()
        blocked = [t for t in ESCALATION_TERMS if t in low]
        if blocked:
            reasons.append(f"escalation terms present: {blocked} — always human-handled")
            return Decision(ticket_text, False, round(confidence, 3), top_id,
                            KB_ARTICLES[top_id][0], None, reasons,
                            [(a, round(s, 4)) for a, s in ranked[:3]])
        deflect = confidence >= self.threshold
        reasons.append(f"confidence {confidence:.2f} {'>=' if deflect else '<'} "
                       f"threshold {self.threshold}")
        title, body = KB_ARTICLES[top_id]
        answer = None
        if deflect:
            answer = self._compose(ticket_text, top_id) or \
                f"This looks like: {title}. {body.split('. ')[0]}. Full steps: see article {top_id}."
        return Decision(ticket_text, deflect, round(confidence, 3), top_id, title, answer,
                        reasons, [(a, round(s, 4)) for a, s in ranked[:3]])

    def _compose(self, ticket: str, article_id: str) -> str | None:
        if self.llm is None:
            return None
        title, body = KB_ARTICLES[article_id]
        return self.llm.complete(
            f"Customer ticket: {ticket}\n\nKB article '{title}': {body}\n\n"
            "Write a short self-service reply that answers the ticket using only the article. "
            "End with: 'If this doesn't solve it, reply and a human will take over.'",
            system="You are a support deflection bot. Be accurate and brief.") or None

    # ---------- batch metrics ----------
    def run_batch(self, tickets: list[tuple[str, str | None]]) -> dict:
        rows = []
        for text, expected in tickets:
            d = self.decide(text)
            correct = (d.deflect and d.article_id == expected) or \
                      (not d.deflect and expected is None)
            rows.append({"deflected": d.deflect, "expected_deflectable": expected is not None,
                         "correct": correct, "confidence": d.confidence})
        n = len(rows)
        deflected = sum(r["deflected"] for r in rows)
        correct = sum(r["correct"] for r in rows)
        wrong_deflections = sum(1 for r in rows if r["deflected"] and not r["correct"])
        return {"tickets": n, "deflected": deflected,
                "deflection_rate": round(deflected / n, 3),
                "decision_accuracy": round(correct / n, 3),
                "wrong_deflections": wrong_deflections,
                "est_monthly_savings_usd": round(deflected / n * 1000 * HANDLING_COST_USD, 0),
                "assumption": "1000 tickets/month baseline"}
