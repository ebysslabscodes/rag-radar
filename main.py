import requests
import json
from datetime import datetime
from pathlib import Path
from keywords import KEYWORDS, SUBREDDITS
from scoring import score_post

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {"User-Agent": "rag-radar/0.1"}


def search_reddit(subreddit, keyword, limit=10):
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": keyword,
        "restrict_sr": "1",
        "sort": "new",
        "limit": limit,
    }

    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get("data", {}).get("children", [])
    except Exception as e:
        print(f"Error: {e}")
        return []


def main():
    leads = {}

    print("Scanning Reddit for RAG pain signals...\n")

    for subreddit in SUBREDDITS:
        for keyword in KEYWORDS:
            posts = search_reddit(subreddit, keyword)

            for item in posts:
                post = item["data"]
                post_id = post["id"]

                if post_id in leads:
                    continue

                title = post.get("title", "")
                body = post.get("selftext", "")
                text = f"{title}\n{body}"

                score, reasons = score_post(text)

                if score <= 0:
                    continue

                leads[post_id] = {
                    "subreddit": subreddit,
                    "title": title,
                    "url": "https://reddit.com" + post.get("permalink", ""),
                    "score": score,
                    "reasons": reasons,
                    "text_preview": text[:400],
                }

    sorted_leads = sorted(leads.values(), key=lambda x: x["score"], reverse=True)

    today = datetime.now().strftime("%Y-%m-%d")

    with open(f"outputs/leads_{today}.json", "w", encoding="utf-8") as f:
        json.dump(sorted_leads, f, indent=2)

    with open(f"outputs/digest_{today}.md", "w", encoding="utf-8") as f:
        f.write(f"# RAG Radar — {today}\n\n")

        for i, lead in enumerate(sorted_leads[:10], start=1):
            f.write(f"## {i}. {lead['title']}\n")
            f.write(f"- r/{lead['subreddit']}\n")
            f.write(f"- Score: {lead['score']}\n")
            f.write(f"- URL: {lead['url']}\n\n")
            f.write(f"{lead['text_preview']}\n\n")
            f.write("---\n\n")

    print(f"Done. Found {len(sorted_leads)} leads.")


if __name__ == "__main__":
    main()
