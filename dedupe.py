from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.82


def titles_similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def is_duplicate(title, existing_titles):
    for existing in existing_titles:
        similarity = titles_similar(title, existing)

        if similarity >= SIMILARITY_THRESHOLD:
            return True

    return False
