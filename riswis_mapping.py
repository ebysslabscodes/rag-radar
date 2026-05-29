RISWIS_MAPPING = {
    "Stale document retrieval": "Freshness-aware retrieval controls",
    "Citation verification failures": "Source trust verification",
    "Retrieval trust conflicts": "Policy-aware retrieval ranking",
    "Reranker inconsistency": "Retrieval audit visibility",
    "Chunk-size instability": "Chunk boundary governance",
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
