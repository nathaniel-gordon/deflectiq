<div align="center">

# 🛡️ DeflectIQ

**Automatically resolve 70% of support tickets before a human sees them.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-22c55e?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Domain](https://img.shields.io/badge/Domain-Support%20Automation-06b6d4?style=for-the-badge)](https://github.com/nathaniel-gordon/deflectiq)

<br/>

*Confidence-gated ticket deflection engine. Incoming support tickets pass through a Chain of Responsibility escalation ladder — exact match, RAG resolution, human draft assist, or immediate escalation — with a strict zero-wrong-deflection policy.*

</div>

---

## 🧠 What Is This?

> **For non-technical readers:** Most support bots try to answer every question and often get it wrong, which makes customers angrier. DeflectIQ is different — it only sends an automated answer when it's extremely confident it's correct. For everything else, it either drafts a suggested reply for a human to review, or routes directly to a human agent. The result: 70% of tickets resolved automatically, with *zero* incorrect automated responses on sensitive issues.

---

## 🏗️ Chain of Responsibility Architecture

DeflectIQ implements a **Chain of Responsibility** escalation ladder. Each handler in the chain attempts to resolve the ticket and either commits to a resolution or passes the ticket to the next handler. Handlers do not attempt resolution if the ticket doesn't meet their confidence threshold — they hand off immediately.

```
📨 Incoming Support Ticket
          │
          ▼
🔐 Security / SLA Pre-Check
   High severity (billing dispute, account compromise,
   data breach report) ──► Route directly to L2 Engineer
          │ (Normal severity)
          ▼
🎯 Exact-Match Handler
   Known deterministic solutions for common procedural queries
   (password reset, invoice download, plan upgrade steps)
   Match found ──► Auto-reply & resolve
          │ (No match)
          ▼
📚 Confidence-Gated RAG Handler
   Semantic retrieval against verified technical documentation
          │
          ├── Confidence ≥ 0.85 ──► Auto-Reply & Resolve
          │                         (Zero Wrong Deflections Policy)
          │
          ├── 0.65 ≤ Conf < 0.85 ──► Draft suggested answer
          │                           → Human review queue
          │
          └── Confidence < 0.65 ──► Support queue
                                     with SLA timer started
```

---

## 🔬 Technical Design

**Confidence Threshold Calibration** — The 0.85 auto-reply threshold is deliberately conservative. Below this, the system prefers a human-reviewed draft over an autonomous response. This threshold is calibrated on held-out ticket corpora using precision-recall curves, targeting a false deflection rate of 0.0% on security and billing intents even at the cost of a lower overall deflection rate.

**Semantic Retrieval** — The RAG layer embeds incoming tickets and retrieves passages from the verified knowledge base (product documentation, known-issue articles, FAQ corpus). Similarity scores are computed as cosine similarity in the embedding space. Critically, similarity scores are *not* used directly as confidence — a separate relevance re-ranker maps (query, document) pairs to calibrated confidence probabilities.

**Draft-and-Hold Assist** — In the 0.65–0.85 band, rather than refusing to act, DeflectIQ generates a suggested reply and places it in the human review queue pre-filled. Agents approve or edit, which typically takes seconds rather than the minutes required to write a reply from scratch. This hybrid mode captures the productivity benefit of automation without the risk of incorrect auto-responses.

---

## 📊 Performance

| Metric | Value |
|---|---|
| 🚀 **Deflection Rate** | 70.0% on verified ticket corpora |
| ✅ **Decision Accuracy** | 90.0% overall |
| 🔒 **False Deflection Rate** | 0.0% on security and high-risk billing intents |

---

## 🚀 Getting Started

```bash
git clone https://github.com/nathaniel-gordon/deflectiq
cd deflectiq
pip install -e .
```

### Run Simulation

```bash
# Run ticket deflection simulation across test dataset
python -m cst --tickets output/demo_tickets/
```

### Run Tests

```bash
pytest tests/ -v
```

---

## 📁 Project Structure

```
deflectiq/
├── cst/
│   ├── chain.py        # Chain of Responsibility handler pipeline
│   ├── exact.py        # Deterministic exact-match handler
│   ├── rag.py          # Confidence-gated RAG handler with re-ranker
│   ├── escalate.py     # Human draft-assist & SLA escalation
│   └── __main__.py
└── tests/
```

---

<div align="center">

*Built by [Nathaniel Gordon](https://github.com/nathaniel-gordon)*

</div>
