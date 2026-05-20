# rag-radar — Production Retrieval Risk Intelligence

Monitoring where retrieval systems fail in production — before those failures become generation risks.

Operational intelligence layer for identifying retrieval reliability failures, governance gaps, and trust instability across deployed RAG systems.

**No automation. No spam. No noise.**

---

## Overview

rag-radar continuously monitors public discussions around production RAG systems and retrieval infrastructure to identify recurring operational failures before they become downstream generation risks.

The system detects:

- Retrieval trust conflicts
- Citation verification failures
- Stale retrieval behavior
- Reranker instability
- Chunking degradation
- Governance exposure patterns

Outputs include:

- Operational retrieval risk summaries
- Governance exposure mapping
- Weekly ecosystem telemetry
- Production reliability trend analysis

Built with Python and designed for lightweight operational telemetry workflows.

---

## What this is

A retrieval risk intelligence system focused on operational retrieval failures, governance exposure, and trust instability inside modern RAG pipelines.

---

## What this is not

This repository does not:

- Auto-reply or DM users
- Generate outreach automatically
- Store or publish collected leads publicly
- Operate as a spam or growth bot
- Automate engagement workflows

Human-in-the-loop by design.

---

## Example Production Risk Signals

```text
RAG Radar — Weekly Risk Signals

Captured:
- 128 relevant discussions
- 31 r/ArtificialIntelligence posts
- 25 r/LangChain posts
- 24 r/LocalLLaMA posts

Top recurring failure patterns:
1. Chunk-size instability
2. Citation verification failures
3. Reranker inconsistency
4. Retrieval trust conflicts
5. Stale document retrieval

Most common production pattern:
"The system works in demos but breaks in production"
```

---

## Retrieval Reliability Index (RRI)

RRI is an internal telemetry metric estimating the current stability of the retrieval ecosystem based on detected operational failures and governance-related exposure.

Factors include:

- Trust conflicts
- Citation failures
- Stale retrieval
- Reranker instability
- Retrieval governance exposure

---

## Governance Mapping

rag-radar identifies recurring retrieval reliability failures across the ecosystem.

RISWIS maps those recurring operational failures to enforceable retrieval governance controls before generation.

| rag-radar Signal | RISWIS Control |
|---|---|
| Citation failures | Source trust verification |
| Trust conflicts | Policy-aware ranking |
| Chunk instability | Chunk governance |
| Stale retrieval | Freshness weighting |
| Reranker instability | Tier-weighted scoring |

Together they form:

```text
Retrieval Risk Intelligence → Retrieval Governance → LLM
```

---

## Flow

```text
Ecosystem Discussions → rag-radar → Risk Signals → Manual Engagement
```

---

## Controls

- Run script → scans and scores discussions
- Review digest → identify high-signal conversations
- Respond manually → engage where relevant

---

## Files

- `main.py` — scanning and digest generation
- `keywords.py` — search terms and source configuration
- `scoring.py` — signal scoring logic
- `theme_detector.py` — recurring theme detection
- `stats.py` — signal aggregation and statistics

---

## Run

```bash
pip install -r requirements.txt
python main.py
```

---

## Output

```text
outputs/
  leads_YYYY-MM-DD.json
  digest_YYYY-MM-DD.md
```

---

## Why This Exists

Modern AI systems frequently fail before generation due to retrieval instability, weak source trust, stale data, and governance gaps.

rag-radar exists to continuously surface those operational retrieval risks across the ecosystem.

The goal is measurable retrieval reliability intelligence — not social automation.

---

## Related

> Same retrieval. Different decision.

[RISWIS — Retrieval Governance Layer](https://riswis.com)

---

## License

Licensed under the Ebysslabs Ethical Use License v1.1  
© 2026 Ronald Reed (Ebysslabs)
