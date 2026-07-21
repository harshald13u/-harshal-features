#!/usr/bin/env python3
"""regen_feeds.py — regenerate blog/feed.xml (RSS) + news-sitemap.xml FRESH from posts.json,
gated to publishAt<=now (IST). RSS = newest 20 live posts. news-sitemap = rolling 48h of just-revealed
posts (EN+HI, Hindi titles for HI). Idempotent; safe to run daily from anywhere."""
import os,json,html
from datetime import datetime,timezone,timedelta
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
IST=timezone(timedelta(hours=5,minutes=30)); NOW=datetime.now(IST)
BASE="https://harshaldasani.pages.dev"; AUTHOR="Harshal Dasani"
ROLE="Business Head, INVasset PMS & AIF"
def load(p): return json.load(open(p,encoding="utf-8"))["posts"]
en=load("blog/posts.json"); hi_by={p["slug"]:p for p in load("hi/blog/posts.json")}
def eff(p):
    pa=p.get("publishAt")
    try: return datetime.fromisoformat(pa) if pa else datetime.fromisoformat(p["date"]+"T09:15:00+05:30")
    except Exception: return datetime.fromisoformat(p["date"]+"T09:15:00+05:30")
def esc(s): return html.escape(s or "",quote=True)
live=sorted([p for p in en if eff(p)<=NOW],key=eff,reverse=True)
# RSS
items=[]
for p in live[:20]:
    pub=eff(p).astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    url=p.get("url") or f"{BASE}/blog/posts/{p['slug']}/"
    items.append(f"""    <item>
      <title>{esc(p['title'])}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{pub}</pubDate>
      <description>{esc(p.get('excerpt',''))}</description>
      <dc:creator>{esc(AUTHOR)}</dc:creator>
    </item>""")
build=NOW.astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
rss=f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Harshal Dasani, Blog</title>
    <link>{BASE}/blog/</link>
    <atom:link href="{BASE}/blog/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Long-form notes on Indian equity markets, commodities, macro and geopolitics by Harshal Dasani, {esc(ROLE)}, Mumbai.</description>
    <language>en-IN</language>
    <copyright>(c) Harshal Dasani</copyright>
    <lastBuildDate>{build}</lastBuildDate>
    <generator>regen_feeds.py</generator>
    <ttl>60</ttl>
{chr(10).join(items)}
  </channel>
</rss>
"""
open("blog/feed.xml","w",encoding="utf-8").write(rss)
# news-sitemap rolling 48h
cut=NOW-timedelta(hours=48)
recent=sorted([p for p in en if cut<=eff(p)<=NOW],key=eff,reverse=True)
urls=[]
for p in recent:
    dt=eff(p).strftime("%Y-%m-%dT%H:%M:%S+05:30")
    for pre,lng in [("blog","en"),("hi/blog","hi")]:
        if pre=="hi/blog":
            if p["slug"] not in hi_by: continue
            title=hi_by[p["slug"]]["title"]
        else: title=p["title"]
        urls.append(f"""  <url>
    <loc>{BASE}/{pre}/posts/{p['slug']}/</loc>
    <news:news>
      <news:publication>
        <news:name>Harshal Dasani</news:name>
        <news:language>{lng}</news:language>
      </news:publication>
      <news:publication_date>{dt}</news:publication_date>
      <news:title>{esc(title)}</news:title>
    </news:news>
  </url>""")
news=f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
{chr(10).join(urls)}
</urlset>
"""
open("news-sitemap.xml","w",encoding="utf-8").write(news)
print(f"feed.xml: {len(items)} live items | news-sitemap.xml: {len(urls)} urls from {len(recent)} posts revealed in last 48h")
print("  recent:",[(p['slug'],eff(p).strftime('%Y-%m-%d %H:%M')) for p in recent])
