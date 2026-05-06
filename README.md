# rag-radar — RAG Signal Scanner

Surfaces real-world RAG failures from live Reddit discussions.

**No automation. No spam. No noise.**

---

## Overview

Once executed:

- Scans selected subreddits for RAG-related discussions
- Scores posts based on retrieval and trust signals
- Outputs a ranked digest of high-signal leads

Runs locally using Python.

---

## What this is

A lightweight signal discovery tool for:

- Retrieval quality issues
- Hallucinations caused by weak context
- Outdated or conflicting sources
- Trust failures in RAG pipelines

## What this is not

This repository does not:

- Auto-reply or DM users
- Generate outreach messages automatically
- Store or share collected leads publicly
- Act as a bot or growth automation tool

---

## Flow

```
Reddit → rag-radar → Ranked Digest → Manual Engagement
```

---

## Controls

- Run script → scans and scores posts
- Review digest → select high-value conversations
- Respond manually → engage where it matters

---

## Files

- `main.py` — scanning and digest generation
- `keywords.py` — search terms and sources
- `scoring.py` — signal scoring logic

---

## Run

```bash
pip install -r requirements.txt
python main.py
```

---

## Output

```
outputs/
  leads_YYYY-MM-DD.json
  digest_YYYY-MM-DD.md
```

---

## Live Use

Designed for daily use:

- Identify real RAG pain points
- Track recurring failure patterns
- Find builders actively struggling with retrieval trust

---

## Related

```
Retriever → Governance → LLM
```

> Same retrieval. Different decision.

[RISWIS — Governance Retrieval Layer](https://riswis.com)

---

## License

Licensed under the Ebysslabs Ethical Use License v1.1  
© 2026 Ronald Reed (Ebysslabs)
