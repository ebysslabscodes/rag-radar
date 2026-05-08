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
