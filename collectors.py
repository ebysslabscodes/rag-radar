import requests

HN_URL = "https://hn.algolia.com/api/v1/search"
GITHUB_SEARCH_URL = "https://api.github.com/search/issues"


def collect_hackernews(keyword, limit=5):
    params = {
        "query": keyword,
        "tags": "story,comment",
        "hitsPerPage": limit,
    }

    try:
        response = requests.get(HN_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        results = []

        for hit in data.get("hits", []):
            title = hit.get("title") or hit.get("story_title") or "Untitled HN item"
            text = hit.get("comment_text") or hit.get("story_text") or title
            url = (
                hit.get("url")
                or hit.get("story_url")
                or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            )

            results.append(
                {
                    "id": f"hn_{hit.get('objectID')}",
                    "platform": "Hacker News",
                    "source": "Hacker News",
                    "title": title,
                    "text": text,
                    "url": url,
                    "upvotes": hit.get("points", 0) or 0,
                    "comments": hit.get("num_comments", 0) or 0,
                }
            )

        return results

    except Exception as e:
        print(f"Hacker News error | keyword='{keyword}': {e}")
        return []


def collect_github(keyword, limit=5):
    query = f"{keyword} RAG retrieval LLM in:title,body"

    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": limit,
    }

    headers = {"Accept": "application/vnd.github+json", "User-Agent": "rag-radar"}

    try:
        response = requests.get(
            GITHUB_SEARCH_URL,
            params=params,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        results = []

        for item in data.get("items", []):
            repo_url = item.get("repository_url", "")
            repo_name = repo_url.replace("https://api.github.com/repos/", "")

            title = item.get("title", "Untitled GitHub item")
            body = item.get("body") or ""

            results.append(
                {
                    "id": f"github_{item.get('id')}",
                    "platform": "GitHub",
                    "source": repo_name or "GitHub",
                    "title": title,
                    "text": f"{title}\n{body}",
                    "url": item.get("html_url", ""),
                    "upvotes": (
                        item.get("reactions", {}).get("+1", 0)
                        if item.get("reactions")
                        else 0
                    ),
                    "comments": item.get("comments", 0) or 0,
                }
            )

        return results

    except Exception as e:
        print(f"GitHub error | keyword='{keyword}': {e}")
        return []
