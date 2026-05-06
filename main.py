import time
import requests
import json
from datetime import datetime
from pathlib import Path

from keywords import KEYWORDS, SUBREDDITS
from scoring import score_post

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

    json_path = OUTPUT_DIR / f"leads_{today}.json"
    digest_path = OUTPUT_DIR / f"digest_{today}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sorted_leads, f, indent=2, ensure_ascii=False)

    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(f"# RAG Radar — {today}\n\n")

        for i, lead in enumerate(sorted_leads[:DIGEST_LIMIT], start=1):
            f.write(f"## {i}. {lead['title']}\n")
            f.write(f"- r/{lead['subreddit']}\n")
            f.write(f"- Score: {lead['score']}\n")
            f.write(f"- URL: {lead['url']}\n")
            f.write(f"- CLICK: {lead['url']}\n")
            f.write(f"- Reasons: {', '.join(lead['reasons'])}\n\n")
            f.write(f"{lead['text_preview']}\n\n")
            f.write("---\n\n")

    print(f"Done. Found {len(sorted_leads)} leads.")
    print(f"JSON saved to: {json_path}")
    print(f"Digest saved to: {digest_path}")


if __name__ == "__main__":
    main()
