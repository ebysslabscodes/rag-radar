import time
import requests
import json
from datetime import datetime
from pathlib import Path

from keywords import KEYWORDS, SUBREDDITS
from scoring import score_post

from theme_detector import detect_themes, detect_emotions
from stats import build_theme_stats, build_emotion_stats

from intent_detector import detect_production_intent
from visual_summary import generate_visual_summary

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {"User-Agent": "rag-radar/0.1 by Ebysslabs"}

REQUEST_DELAY_SECONDS = 2
RESULT_LIMIT_PER_SEARCH = 5
DIGEST_LIMIT = 10


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


def main():
    leads = {}

    print("Scanning Reddit for RAG pain signals...\n")

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

                score, reasons = score_post(text)

                themes = detect_themes(text)
                emotions = detect_emotions(text)

                intent_score, intent_matches = detect_production_intent(text)

                if score <= 0:
                    continue

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
                }

    for lead in leads.values():
        engagement_score = min(lead["upvotes"] / 10, 10) + min(lead["comments"] / 5, 10)

        lead["engagement_score"] = round(engagement_score, 2)
        lead["final_score"] = round(
            lead["score"] + lead["intent_score"] + engagement_score, 2
        )

    sorted_leads = sorted(leads.values(), key=lambda x: x["final_score"], reverse=True)

    theme_stats = build_theme_stats(sorted_leads)
    emotion_stats = build_emotion_stats(sorted_leads)

    today = datetime.now().strftime("%Y-%m-%d")

    json_path = OUTPUT_DIR / f"leads_{today}.json"
    digest_path = OUTPUT_DIR / f"digest_{today}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sorted_leads, f, indent=2, ensure_ascii=False)

    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(f"# RAG Radar — Weekly Signals ({today})\n\n")

        f.write("Scanned:\n")
        f.write(f"- {len(sorted_leads)} relevant Reddit discussions\n")

        subreddit_counts = {}

        for lead in sorted_leads:
            subreddit = lead["subreddit"]
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1

        for subreddit, count in sorted(subreddit_counts.items()):
            f.write(f"- {count} r/{subreddit} posts\n")

        f.write("\n")

        f.write("## Top recurring themes\n\n")
        if theme_stats:
            for i, (theme, count) in enumerate(theme_stats.most_common(5), start=1):
                f.write(f"{i}. {theme} ({count})\n")
        else:
            f.write("No recurring themes detected.\n")

        f.write("\n")

        f.write("## Most common emotional pattern\n\n")
        if emotion_stats:
            top_emotion, count = emotion_stats.most_common(1)[0]
            f.write(f'"{top_emotion}" ({count})\n\n')
        else:
            f.write("No emotional pattern detected.\n\n")

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
                f"- Themes: {', '.join(lead['themes']) if lead['themes'] else 'None detected'}\n"
            )
            f.write(
                f"- Emotional patterns: {', '.join(lead['emotions']) if lead['emotions'] else 'None detected'}\n\n"
            )
            f.write(f"{lead['text_preview']}\n\n")
            f.write("---\n\n")

    print(f"Done. Found {len(sorted_leads)} leads.")
    print(f"JSON saved to: {json_path}")
    print(f"Digest saved to: {digest_path}")

    visual_path = OUTPUT_DIR / f"weekly_summary_{today}.png"

    generate_visual_summary(sorted_leads, subreddit_counts, visual_path, today)

    print(f"Visual summary saved to: {visual_path}")


if __name__ == "__main__":
    main()
