# DeflectIQ — Intelligent Support Ticket Deflection

> Resolve tickets before they reach your team. DeflectIQ answers routine support tickets from the knowledge base — but only when confident. It retrieves from KB articles and past resolved tickets, gates deflection on retrieval strength + margin + query-term coverage, and routes novel or vague tickets to humans by design.

## What DeflectIQ Does

- **Dual-source retrieval** — KB articles + past resolved tickets corroborate each other
- **Confidence-gated deflection** — deflects only when absolute score, margin, and term coverage all pass
- **Human escalation by default** — vague or novel queries fall through; never guesses wrong
- **Feedback learning** — human-resolved tickets are ingested back into retrieval corpus
- **Deflection analytics** — deflection rate, confidence distribution, topic breakdown

## Architecture

```
Support Ticket
    └─> DualRetriever       (KB articles + resolved tickets)
    └─> RRFRanker           (reciprocal-rank fusion)
    └─> DeflectionGate      (absolute score + margin + term coverage)
    └─> AnswerSynthesizer   (extractive answer from top passage)
    └─> EscalationRouter    (human queue on gate failure)
    └─> FeedbackIngester    (resolved tickets -> corpus)
    └─> ChainREPL           (interactive deflection shell)
```

## Quickstart

```bash
python -m sdr demo           # demo ticket deflection on synthetic support corpus
python -m sdr shell          # launch interactive deflection REPL
```

## Test

```bash
python tests/test_smoke.py
```

---

## 👤 Author & Contact

- **Author**: Nathaniel Gordon
- **Role**: Senior AI & Machine Learning Engineer
- **GitHub**: [github.com/nathaniel-gordon](https://github.com/nathaniel-gordon)
- **Portfolio / Upwork**: [upwork.com/freelancers/~015fe5a704f8943797](https://www.upwork.com/freelancers/~015fe5a704f8943797)
- **Email**: nathanielgordon346@gmail.com
- **Location**: Tallahassee, FL, USA
