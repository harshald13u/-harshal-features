#!/usr/bin/env python3
"""auto_publish_next.py — publish the NEXT pending blog in blog/_queue/queue.json.
Runs publish_blog (EN post + embedded cover OR auto-generated cover + FULL on-page SEO
+ sitemap + news-sitemap + posts.json), generates the EN narration (mastered), marks the
item done, and prints PUBLISHED_SLUG=<slug>. Caller handles Hindi twin + git.
Idempotent: re-running publishes the next pending item only."""
import os, sys, json
HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(HERE))
QDIR=os.path.join(ROOT,"blog","_queue"); QJSON=os.path.join(QDIR,"queue.json")
sys.path.insert(0,HERE)
import publish_blog, gen_audio_pro

def slug_of(docx):
    ex=publish_blog.extract_docx(docx)
    meta,_=publish_blog.parse_metadata_block(ex["paragraphs"])
    return meta["Slug"].strip()

def main():
    q=json.load(open(QJSON,encoding="utf-8"))
    item=next((x for x in q if x.get("status")=="pending"),None)
    if not item: print("QUEUE_EMPTY"); return
    docx=os.path.join(QDIR,item["file"])
    slug=slug_of(docx)
    print(f"[auto] publishing {item['file']}  slug={slug}")
    publish_blog.publish_blog(docx)
    post_dir=os.path.join(ROOT,"blog","posts",slug)
    try:
        gen_audio_pro.generate(post_dir,"en","en-IN-NeerjaExpressiveNeural")
    except Exception as e:
        print("[auto] EN audio note:",repr(e)[:140])
    item["status"]="done"; item["slug"]=slug
    import datetime
    IST=datetime.timezone(datetime.timedelta(hours=5,minutes=30))
    item["published_at"]=datetime.datetime.now(IST).strftime("%Y-%m-%dT%H:%M:%S+05:30")
    try:
        pj={p["slug"]:p for p in json.load(open(os.path.join(ROOT,"blog","posts.json")))["posts"]}
        if pj.get(slug,{}).get("title"): item["title"]=pj[slug]["title"]
    except Exception: pass
    item["lang_en"]=True
    json.dump(q,open(QJSON,"w"),ensure_ascii=False,indent=2)
    print("PUBLISHED_SLUG="+slug)

if __name__=="__main__": main()
