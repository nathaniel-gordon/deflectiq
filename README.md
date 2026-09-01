# DeflectIQ — Confidence-Gated Support Ticket Deflection RAG Engine

DeflectIQ is an automated tier-1 customer support triage and deflection system built around a **Chain of Responsibility** escalation ladder. Incoming customer tickets pass through sequential resolution filters:

1. **Direct Exact-Match Resolution**: Known deterministic solutions for common procedural queries.
2. **Confidence-Gated RAG**: Semantic retrieval against verified technical documentation with strict similarity thresholds.
3. **Draft-and-Hold Assist**: Generates a suggested reply for human agent review when confidence is moderate.
4. **Immediate Human Escalation**: Bypasses bot response entirely for security alerts, billing disputes, or low-confidence queries.

## Escalation Ladder

```
Incoming Support Ticket
          │
          ▼
 [Security / SLA Check] ──(High Severity)──► Escalate Directly to L2 Engineer
          │ (Normal)
          ▼
 [Semantic Document Retrieval]
          │
    Confidence ≥ 0.85 ──► Auto-Reply & Resolve (Zero Wrong Deflections Policy)
    0.65 ≤ Conf < 0.85 ──► Draft Suggested Answer for Human Queue
    Confidence < 0.65 ──► Route to Support Queue with SLA Timer
```

## Benchmarks

- **Deflection Rate**: 70.0% on verified ticket corpora.
- **Decision Accuracy**: 90.0% with **0.0% false deflection rate** on security and high-risk billing intents.

## Usage

```bash
# Run ticket deflection simulation across test dataset
python -m cst --tickets output/demo_tickets/
```

## Tests

```bash
pytest tests/ -v
```
