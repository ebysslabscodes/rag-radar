# rag-radar — RAG Ecosystem Signal Tracker

![rag-radar preview](preview.png)

Community signal layer for retrieval reliability and trust failures.

Surfaces recurring retrieval and trust failures from real-world RAG discussions across Reddit communities.

**No automation. No spam. No noise.**

---

## Overview

rag-radar monitors public RAG discussions and extracts recurring reliability signals from real builders and production conversations.

Once executed:

- Scans selected Reddit communities for RAG-related discussions
- Scores posts based on retrieval and trust signals
- Detects recurring themes and emotional patterns
- Outputs ranked digests and weekly signal summaries

Runs locally using Python.

---

## What this is

A lightweight ecosystem signal layer for identifying:

- Retrieval quality failures
- Citation verification problems
- Reranker instability
- Stale or conflicting sources
- Production reliability concerns
- Trust breakdowns in RAG pipelines

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

## Example Weekly Signals

```text
RAG Radar — Weekly Signals

Captured:
- 128 relevant Reddit discussions
- 31 r/ArtificialIntelligence posts
- 25 r/LangChain posts
- 24 r/LocalLLaMA posts

Top recurring themes:
1. Chunk-size instability
2. Citation verification failures
3. Reranker inconsistency
4. Retrieval trust conflicts
5. Stale document retrieval

Most common emotional pattern:
"The system works in demos but breaks in production"
```

---

## Flow

```text
Reddit → rag-radar → Weekly Signals → Manual Engagement
```

---

## Controls

- Run script → scans and scores discussions
- Review digest → identify high-signal conversations
- Respond manually → engage where relevant

---

## Files

- `main.py` — scanning and digest generation
- `keywords.py` — search terms and subreddit sources
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

## Purpose

rag-radar exists to help identify recurring reliability and trust issues across the retrieval ecosystem before they become downstream generation failures.

The goal is visibility — not automation.

---

## Related

```text
Retriever → Governance → LLM
```

> Same retrieval. Different decision.

[RISWIS — Governance Retrieval Layer](https://riswis.com)

---

## License

Licensed under the Ebysslabs Ethical Use License v1.1  
© 2026 Ronald Reed (Ebysslabs)