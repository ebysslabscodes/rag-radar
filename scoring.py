def score_post(text):
    lower = text.lower()

    rag_gate_terms = [
        "rag",
        "retrieval",
        "retriever",
        "rerank",
        "reranking",
        "vector db",
        "vector database",
        "semantic search",
        "top-k",
        "langchain",
        "langgraph",
        "llamaindex",
    ]

    # Hard gate
    if not any(term in lower for term in rag_gate_terms):
        return 0, []

    score = 0
    reasons = []

    signals = {
        # Core RAG
        "rag": 3,
        "retrieval": 4,
        "retrieval quality": 6,
        "semantic search": 4,
        "rerank": 4,
        "reranking": 4,
        "top-k": 3,
        "vector db": 3,
        # Governance / trust
        "trust": 7,
        "trusted": 6,
        "source": 4,
        "sources": 4,
        "citation": 7,
        "citations": 7,
        "verify": 5,
        "verification": 5,
        "stale": 8,
        "outdated": 8,
        # Failure signals
        "hallucination": 6,
        "hallucinations": 6,
        "wrong answer": 7,
        "incorrect": 5,
        "conflicting": 5,
        "bad retrieval": 7,
        "garbage": 4,
        "gigo": 5,
        # Operational
        "production": 5,
        "in production": 6,
        "real-world": 5,
        "trust in retrieval": 10,
    }

    matched = set()

    for phrase, points in signals.items():
        if phrase in lower:
            score += points
            matched.add(phrase)

    return score, sorted(matched)
