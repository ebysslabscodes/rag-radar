RISWIS_MAPPING = {
    "Stale document retrieval": "Freshness weighting",
    "Citation verification failures": "Source verification",
    "Retrieval trust conflicts": "Policy-aware ranking",
    "Reranker inconsistency": "Audit trail visibility",
    "Chunk-size instability": "Chunk governance controls",
}


def map_theme_to_governance(theme_list):
    mappings = []

    for theme in theme_list:
        if theme in RISWIS_MAPPING:
            mappings.append(
                {
                    "theme": theme,
                    "governance_need": RISWIS_MAPPING[theme],
                }
            )

    return mappings
