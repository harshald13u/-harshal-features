#!/usr/bin/env python3
"""ping_indexnow.py <url> [<url> ...] — auto-submit URLs to IndexNow.

Notifies Bing, Yandex, Naver, Seznam, DuckDuckGo (Bing-backed) instantly — no login.
Google does NOT support IndexNow; Google discovers new posts via the sitemaps listed
in robots.txt on its own crawl. Run automatically by publish_blog.py and by a daily
scheduled task. Best-effort: never raises.
"""
import sys, json, urllib.request
KEY = "574287a080c566301ca9d3a722480c51"
HOST = "harshaldasani.pages.dev"
def ping(urls):
    urls = [u for u in urls if u]
    if not urls: return "no urls"
    body = json.dumps({
        "host": HOST, "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return f"IndexNow {r.status} for {len(urls)} url(s)"
    except Exception as e:
        return f"IndexNow skip: {e}"
if __name__ == "__main__":
    print(ping(sys.argv[1:]))
