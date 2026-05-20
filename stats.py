from collections import Counter


def build_theme_stats(leads):
    counter = Counter()

    for lead in leads:
        for theme in lead.get("themes", []):
            counter[theme] += 1

    return counter


def build_emotion_stats(leads):
    counter = Counter()

    for lead in leads:
        for emotion in lead.get("emotions", []):
            counter[emotion] += 1

    return counter


def count_trust_conflicts(leads):
    count = 0

    conflict_themes = {
        "Retrieval trust conflicts",
        "Citation verification failures",
    }

    conflict_phrases = [
        "cannot trust",
        "can't trust",
        "wrong source",
        "conflicting source",
        "conflicting sources",
    ]

    for lead in leads:
        themes = set(lead.get("themes", []))
        preview = lead.get("text_preview", "").lower()

        has_theme = bool(themes.intersection(conflict_themes))
        has_phrase = any(phrase in preview for phrase in conflict_phrases)

        if has_theme or has_phrase:
            count += 1

    return count
