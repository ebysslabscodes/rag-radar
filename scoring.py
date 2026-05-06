def score_post(text):
    lower = text.lower()
    score = 0
    reasons = []

    signals = {
        "rag": 3,
        "retrieval": 3,
        "bad": 2,
        "hallucination": 3,
        "source": 2,
        "trust": 4,
        "rerank": 3,
        "context": 2,
    }

    for word, points in signals.items():
        if word in lower:
            score += points
            reasons.append(word)

    return score, reasons
