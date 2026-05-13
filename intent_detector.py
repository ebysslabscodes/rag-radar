PRODUCTION_SIGNALS = {
    "in production": 5,
    "production": 4,
    "enterprise": 5,
    "customers": 4,
    "deployed": 4,
    "real users": 5,
    "our pipeline": 4,
    "our system": 3,
    "client": 3,
    "clients": 3,
    "b2b": 4,
}


def detect_production_intent(text):
    lower = text.lower()

    score = 0
    matched = []

    for phrase, points in PRODUCTION_SIGNALS.items():
        if phrase in lower:
            score += points
            matched.append(phrase)

    return score, matched
