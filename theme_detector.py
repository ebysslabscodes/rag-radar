THEMES = {
    "Retrieval trust conflicts": [
        "trust",
        "wrong source",
        "bad source",
        "untrusted",
        "reliable",
        "reliability",
        "source quality",
        "conflicting source",
        "conflicting sources",
    ],
    "Citation verification failures": [
        "citation",
        "citations",
        "source attribution",
        "verify",
        "verification",
        "hallucination",
        "hallucinations",
        "wrong citation",
        "fake citation",
    ],
    "Chunk-size instability": [
        "chunk",
        "chunks",
        "chunking",
        "chunk size",
        "split",
        "overlap",
        "context window",
    ],
    "Reranker inconsistency": [
        "rerank",
        "reranker",
        "reranking",
        "ranking",
        "top-k",
        "top k",
        "retrieval depth",
    ],
    "Stale document retrieval": [
        "stale",
        "old pdf",
        "outdated",
        "old docs",
        "old document",
        "old documents",
        "version drift",
        "last year's pdf",
        "deprecated",
    ],
}


EMOTIONAL_PATTERNS = {
    "The answer sounds correct but cannot be trusted": [
        "sounds right",
        "sounds correct",
        "confidently wrong",
        "can't trust",
        "cannot trust",
        "looks correct",
        "looks right",
        "answer sounded fine",
        "answer sounds fine",
        "good sounding",
    ],
    "The system works in demos but breaks in production": [
        "works in demos",
        "breaks in production",
        "production",
        "real user queries",
        "doesn't hold up",
        "would never hold up",
    ],
    "The right answer exists but retrieval misses it": [
        "not retrieving",
        "missed",
        "missing",
        "obvious in the documents",
        "should have been easy",
        "right chunk",
        "right answer",
    ],
}


def detect_themes(text):
    lower = text.lower()
    matched = []

    for theme, keywords in THEMES.items():
        for keyword in keywords:
            if keyword in lower:
                matched.append(theme)
                break

    return matched


def detect_emotions(text):
    lower = text.lower()
    matched = []

    for emotion, keywords in EMOTIONAL_PATTERNS.items():
        for keyword in keywords:
            if keyword in lower:
                matched.append(emotion)
                break

    return matched
