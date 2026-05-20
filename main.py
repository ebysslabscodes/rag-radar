import time
import requests
import json
from datetime import datetime
from pathlib import Path

from keywords import KEYWORDS, SUBREDDITS
from scoring import score_post
from theme_detector import detect_themes, detect_emotions
from stats import (
    build_theme_stats,
    build_emotion_stats,
    count_trust_conflicts,
)
from intent_detector import detect_production_intent
from visual_summary import generate_visual_summary
from riswis_mapping import map_theme_to_governance
from dedupe import is_duplicate
from history import load_history, save_history, calculate_delta

# ---------------------------------------------------
# Output setup
# ---------------------------------------------------

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------
# Reddit request settings
# ---------------------------------------------------

HEADERS = {"User-Agent": "rag-radar/0.1 by Ebysslabs"}

REQUEST_DELAY_SECONDS = 2
RESULT_LIMIT_PER_SEARCH = 5
DIGEST_LIMIT = 10


# ---------------------------------------------------
# Severity classification
#
# Converts theme counts into dashboard-style severity.
# This makes the report feel closer to operational
# observability / reliability tooling.
# ---------------------------------------------------


def classify_severity(count):
    if count >= 40:
        return "CRITICAL"
    if count >= 25:
        return "HIGH"
    if count >= 10:
        return "MODERATE"
    return "LOW"


# ---------------------------------------------------
# Reddit Search
#
# Searches one subreddit for one keyword.
# Returns raw Reddit post objects.
# ---------------------------------------------------


def search_reddit(subreddit, keyword, limit=RESULT_LIMIT_PER_SEARCH):
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": keyword,
        "restrict_sr": "1",
        "sort": "new",
        "limit": limit,
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("children", [])

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for r/{subreddit} | keyword='{keyword}': {e}")
        return []

    except Exception as e:
        print(f"Error for r/{subreddit} | keyword='{keyword}': {e}")
        return []


# ---------------------------------------------------
# Production Excerpt Extraction
#
# Pulls a strong operational signal from the
# highest-ranked discussion.
#
# V1 keeps this simple and deterministic:
# use the title of the top-ranked lead.
#
# Purpose:
# turns the report from only stats into
# an intelligence-style report with a real signal.
# ---------------------------------------------------


def extract_production_excerpt(leads):
    if not leads:
        return None

    top_lead = leads[0]

    title = top_lead.get("title", "").strip()
    subreddit = top_lead.get("subreddit", "unknown")

    return {
        "excerpt": title,
        "subreddit": subreddit,
    }


# ---------------------------------------------------
# Main pipeline
#
# 1. Search Reddit
# 2. Deduplicate titles
# 3. Score posts
# 4. Detect themes/emotions/production intent
# 5. Add RISWIS governance mapping
# 6. Build telemetry + RRI
# 7. Export JSON
# 8. Export Markdown digest
# 9. Export PNG visual summary
# ---------------------------------------------------


def main():
    leads = {}
    existing_titles = []

    print("Scanning Reddit for RAG pain signals...\n")

    # ---------------------------------------------------
    # Scan configured subreddits and keywords
    # ---------------------------------------------------

    for subreddit in SUBREDDITS:
        for keyword in KEYWORDS:
            posts = search_reddit(subreddit, keyword)

            time.sleep(REQUEST_DELAY_SECONDS)

            for item in posts:
                post = item.get("data", {})
                post_id = post.get("id")

                if not post_id or post_id in leads:
                    continue

                title = post.get("title", "")
                body = post.get("selftext", "")
                text = f"{title}\n{body}".strip()

                # ---------------------------------------------------
                # Duplicate detection
                #
                # Prevents repeated/cross-posted discussions from
                # inflating report counts.
                # ---------------------------------------------------

                if is_duplicate(title, existing_titles):
                    continue

                existing_titles.append(title)

                # ---------------------------------------------------
                # Core scoring + signal detection
                # ---------------------------------------------------

                score, reasons = score_post(text)

                themes = detect_themes(text)
                emotions = detect_emotions(text)

                intent_score, intent_matches = detect_production_intent(text)

                if score <= 0:
                    continue

                # ---------------------------------------------------
                # Store lead
                #
                # governance_mapping connects detected failure themes
                # to the RISWIS governance need.
                # ---------------------------------------------------

                leads[post_id] = {
                    "subreddit": subreddit,
                    "title": title,
                    "url": "https://reddit.com" + post.get("permalink", ""),
                    "score": score,
                    "upvotes": post.get("ups", 0),
                    "comments": post.get("num_comments", 0),
                    "intent_score": intent_score,
                    "intent_matches": intent_matches,
                    "reasons": reasons,
                    "text_preview": text[:400],
                    "themes": themes,
                    "emotions": emotions,
                    "governance_mapping": map_theme_to_governance(themes),
                }

    # ---------------------------------------------------
    # Engagement + final score
    #
    # Adds lightweight social signal weighting:
    # upvotes + comments.
    # ---------------------------------------------------

    for lead in leads.values():
        engagement_score = min(lead["upvotes"] / 10, 10) + min(lead["comments"] / 5, 10)

        lead["engagement_score"] = round(engagement_score, 2)
        lead["final_score"] = round(
            lead["score"] + lead["intent_score"] + engagement_score,
            2,
        )

    # ---------------------------------------------------
    # Sort by final score
    # ---------------------------------------------------

    sorted_leads = sorted(
        leads.values(),
        key=lambda x: x["final_score"],
        reverse=True,
    )

    # ---------------------------------------------------
    # Build summary stats
    # ---------------------------------------------------

    theme_stats = build_theme_stats(sorted_leads)
    emotion_stats = build_emotion_stats(sorted_leads)
    trust_conflict_count = count_trust_conflicts(sorted_leads)

    citation_failures = theme_stats.get("Citation verification failures", 0)
    stale_retrieval = theme_stats.get("Stale document retrieval", 0)

    # ---------------------------------------------------
    # Severity classification
    #
    # Adds LOW / MODERATE / HIGH / CRITICAL labels
    # to each tracked production failure theme.
    # ---------------------------------------------------

    severity_by_theme = {}

    for theme, count in theme_stats.items():
        severity_by_theme[theme] = classify_severity(count)

    # ---------------------------------------------------
    # Retrieval Reliability Index (RRI)
    #
    # V1 uses a simple weighted penalty model.
    # Consistency matters more than perfect math.
    # ---------------------------------------------------

    total_signals = len(sorted_leads)

    if total_signals > 0:
        weighted_failures = (
            trust_conflict_count * 2 + citation_failures * 1.5 + stale_retrieval * 1
        )

        max_possible_penalty = total_signals * 3

        rri = 100 - ((weighted_failures / max_possible_penalty) * 100)
        rri = max(0, min(100, round(rri)))
    else:
        rri = 100

    today = datetime.now().strftime("%Y-%m-%d")

    # ---------------------------------------------------
    # History snapshot
    #
    # Saves weekly telemetry into outputs/history.json.
    # ---------------------------------------------------

    history = load_history()

    snapshot = {
        "date": today,
        "total_signals": len(sorted_leads),
        "trust_conflicts": trust_conflict_count,
        "citation_failures": citation_failures,
        "stale_retrieval": stale_retrieval,
        "theme_counts": dict(theme_stats),
        "top_sentiment": (
            emotion_stats.most_common(1)[0][0] if emotion_stats else "None detected"
        ),
        "rri": rri,
    }

    history.append(snapshot)
    save_history(history)

    # ---------------------------------------------------
    # Week-over-week telemetry
    # ---------------------------------------------------

    previous = history[-2] if len(history) > 1 else None

    weekly_changes = {}

    if previous:
        weekly_changes = {
            "citation_failures": calculate_delta(
                citation_failures,
                previous.get("citation_failures", 0),
            ),
            "trust_conflicts": calculate_delta(
                trust_conflict_count,
                previous.get("trust_conflicts", 0),
            ),
            "stale_retrieval": calculate_delta(
                stale_retrieval,
                previous.get("stale_retrieval", 0),
            ),
        }

    theme_trends = {}

    if previous:
        previous_theme_counts = previous.get("theme_counts", {})

        for theme, current_count in theme_stats.items():
            previous_count = previous_theme_counts.get(theme, 0)

            theme_trends[theme] = calculate_delta(
                current_count,
                previous_count,
            )

    for theme, delta in theme_trends.items():
        if delta > 0:
            theme_trends[theme] = f"↑ +{delta}%"
        elif delta < 0:
            theme_trends[theme] = f"↓ {delta}%"
        else:
            theme_trends[theme] = "→ baseline"

    governance_counts = {}

    for lead in sorted_leads:
        for item in lead.get("governance_mapping", []):
            governance_need = item.get("governance_need")

            if governance_need:
                governance_counts[governance_need] = (
                    governance_counts.get(governance_need, 0) + 1
                )

    mapped_leads = 0

    for lead in sorted_leads:
        if lead.get("governance_mapping"):
            mapped_leads += 1

    riswis_governance_match = 0

    if sorted_leads:
        riswis_governance_match = round((mapped_leads / len(sorted_leads)) * 100)

    # ---------------------------------------------------
    # Production excerpt
    #
    # Pulls one real operational signal into the report.
    # ---------------------------------------------------

    production_excerpt = extract_production_excerpt(sorted_leads)

    json_path = OUTPUT_DIR / f"leads_{today}.json"
    digest_path = OUTPUT_DIR / f"digest_{today}.md"

    # ---------------------------------------------------
    # Export JSON
    # ---------------------------------------------------

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sorted_leads, f, indent=2, ensure_ascii=False)

    # ---------------------------------------------------
    # Export Markdown digest
    # ---------------------------------------------------

    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(f"# RAG Radar — Weekly Signals ({today})\n\n")

        # ---------------------------------------------------
        # Retrieval Reliability Index
        # ---------------------------------------------------

        f.write("## Retrieval Reliability Index (RRI)\n\n")
        f.write(f"RRI: {rri}/100\n\n")

        # ---------------------------------------------------
        # Week-over-week telemetry
        # ---------------------------------------------------

        if weekly_changes:
            f.write("## Week-over-week\n\n")

            f.write(f"Citation failures " f"{weekly_changes['citation_failures']}%\n")

            f.write(f"Trust conflicts " f"{weekly_changes['trust_conflicts']}%\n")

            f.write(f"Stale retrieval " f"{weekly_changes['stale_retrieval']}%\n\n")

        # ---------------------------------------------------
        # Scan summary
        # ---------------------------------------------------

        f.write("Scanned:\n")
        f.write(f"- {len(sorted_leads)} relevant Reddit discussions\n")

        subreddit_counts = {}

        for lead in sorted_leads:
            subreddit = lead["subreddit"]
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1

        for subreddit, count in sorted(subreddit_counts.items()):
            f.write(f"- {count} r/{subreddit} posts\n")

        f.write("\n")

        # ---------------------------------------------------
        # Theme summary
        # ---------------------------------------------------

        f.write("## Tracked production failure themes\n\n")

        if theme_stats:
            for i, (theme, count) in enumerate(
                theme_stats.most_common(5),
                start=1,
            ):
                severity = severity_by_theme.get(theme, "LOW")
                f.write(f"{i}. {theme} ({count}) — {severity}\n")
        else:
            f.write("No recurring themes detected.\n")

        f.write("\n")

        # ---------------------------------------------------
        # Retrieval Trend Direction
        # ---------------------------------------------------

        if theme_trends:
            f.write("## Retrieval Trend Direction\n\n")

            for theme, trend in theme_trends.items():
                f.write(f"- {theme} {trend}\n")

            f.write("\n")

        # ---------------------------------------------------
        # RISWIS Governance Match
        # ---------------------------------------------------

        f.write("## RISWIS Governance Match\n\n")

        f.write(
            f"{riswis_governance_match}% of detected retrieval "
            f"failures mapped to governance controls.\n\n"
        )

        if governance_counts:
            f.write("Most correlated governance needs:\n\n")

            sorted_governance = sorted(
                governance_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )

            for governance_need, count in sorted_governance[:5]:
                f.write(f"- {governance_need} ({count})\n")

            f.write("\n")

        # ---------------------------------------------------
        # Trust Conflict Frequency
        #
        # Measures how often discussions indicate
        # trust/governance failures in retrieval systems.
        # ---------------------------------------------------

        f.write("## Trust conflict frequency\n\n")

        f.write(
            f"Trusted sources outranked by weaker sources detected in "
            f"{trust_conflict_count} discussions this week.\n\n"
        )

        # ---------------------------------------------------
        # Most common production sentiment
        # ---------------------------------------------------

        f.write("## Most common production sentiment\n\n")

        if emotion_stats:
            top_emotion, count = emotion_stats.most_common(1)[0]
            f.write(f'"{top_emotion}" ({count})\n\n')
        else:
            f.write("No production sentiment detected.\n\n")

        # ---------------------------------------------------
        # Production Excerpt Section
        #
        # This adds a real ecosystem quote/signal.
        # It makes the report feel like operational
        # intelligence instead of only a statistics dump.
        # ---------------------------------------------------

        f.write("## Production Excerpt\n\n")

        if production_excerpt:
            f.write(f'> "{production_excerpt["excerpt"]}"\n\n')
            f.write(f'— r/{production_excerpt["subreddit"]}\n\n')
        else:
            f.write("No production excerpt detected.\n\n")

        # ---------------------------------------------------
        # Top leads
        # ---------------------------------------------------

        f.write("## Top leads\n\n")

        for i, lead in enumerate(sorted_leads[:DIGEST_LIMIT], start=1):
            f.write(f"### {i}. {lead['title']}\n")
            f.write(f"- Subreddit: r/{lead['subreddit']}\n")
            f.write(f"- Score: {lead['score']}\n")
            f.write(f"- Final score: {lead['final_score']}\n")
            f.write(f"- Intent score: {lead['intent_score']}\n")
            f.write(f"- Engagement score: {lead['engagement_score']}\n")
            f.write(f"- Upvotes: {lead['upvotes']}\n")
            f.write(f"- Comments: {lead['comments']}\n")
            f.write(f"- Link: {lead['url']}\n")
            f.write(f"- Reasons: {', '.join(lead['reasons'])}\n")

            f.write(
                f"- Themes: "
                f"{', '.join(lead['themes']) if lead['themes'] else 'None detected'}\n"
            )

            # ---------------------------------------------------
            # RISWIS governance mapping
            #
            # Converts detected failure theme into governance need.
            #
            # Example:
            # Citation verification failures → Source verification
            # ---------------------------------------------------

            if lead["governance_mapping"]:
                f.write("- Governance mapping:\n")

                for item in lead["governance_mapping"]:
                    f.write(f"  - {item['theme']} → " f"{item['governance_need']}\n")

            f.write(
                f"- Emotional patterns: "
                f"{', '.join(lead['emotions']) if lead['emotions'] else 'None detected'}\n\n"
            )

            f.write(f"{lead['text_preview']}\n\n")
            f.write("---\n\n")

    print(f"Done. Found {len(sorted_leads)} leads.")
    print(f"JSON saved to: {json_path}")
    print(f"Digest saved to: {digest_path}")

    # ---------------------------------------------------
    # Export PNG visual summary
    # ---------------------------------------------------

    visual_path = OUTPUT_DIR / f"weekly_summary_{today}.png"

    generate_visual_summary(
        sorted_leads,
        subreddit_counts,
        visual_path,
        today,
        theme_trends=theme_trends,
        riswis_governance_match=riswis_governance_match,
        governance_counts=governance_counts,
        trust_conflict_count=trust_conflict_count,
        production_excerpt=production_excerpt,
        severity_by_theme=severity_by_theme,
        rri=rri,
    )

    print(f"Visual summary saved to: {visual_path}")


if __name__ == "__main__":
    main()
