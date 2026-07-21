#!/usr/bin/env python3
"""update_schedule_snapshot.py - refresh the embedded SNAP in blog/schedule/index.html
from the current queue.json + posts.json. Excludes already-published slugs from 'upcoming'
so a post never shows as both published and scheduled. Called at the end of each auto-publish."""
import os,json,datetime,re
def build(root):
    q=json.load(open(os.path.join(root,"blog/_queue/queue.json"),encoding="utf-8"))
    en=json.load(open(os.path.join(root,"blog/posts.json")))["posts"]
    hiset={p["slug"] for p in json.load(open(os.path.join(root,"hi/blog/posts.json")))["posts"]}
    IST=datetime.timezone(datetime.timedelta(hours=5,minutes=30)); now=datetime.datetime.now(IST)
    def live(p):
        pa=p.get("publishAt")
        if not pa: return True
        try: return datetime.datetime.fromisoformat(pa)<=now
        except Exception: return True
    ha=lambda s:os.path.exists(os.path.join(root,"blog/posts",s,"audio.mp3"))
    pub=[{"slug":p["slug"],"title":p["title"],"date":p.get("date",""),
          "url":p.get("url") or "/blog/posts/%s/"%p["slug"],"hi":p["slug"] in hiset,
          "audio":ha(p["slug"]),"topic":p.get("topic","")}
         for p in sorted([x for x in en if live(x)],key=lambda x:(x.get("date",""),x.get("slug","")),reverse=True)]
    staged=sorted([{"slug":p["slug"],"title":p["title"],"topic":p.get("topic",""),"when":p["publishAt"]}
                   for p in en if not live(p)], key=lambda x:x["when"])
    enslugs={p["slug"] for p in en}
    legacy=[{"slug":it.get("slug",""),"title":it.get("title") or it.get("file",""),"topic":it.get("topic","")}
            for it in q if it.get("status")=="pending" and it.get("slug") not in enslugs]
    up=staged+legacy
    return {"generated":now.strftime("%d %b %Y, %I:%M %p IST"),
            "published":pub,"upcoming":up,
            "counts":{"published":len(pub),"upcoming":len(up),"hi_done":sum(1 for p in pub if p["hi"])}}

def update(root):
    snap=build(root); f=os.path.join(root,"blog/schedule/index.html")
    h=open(f,encoding="utf-8").read()
    h2,n=re.subn(r"const SNAP=\{.*?\};\nconst BASE",
                 "const SNAP="+json.dumps(snap,ensure_ascii=False)+";\nconst BASE",h,count=1,flags=re.S)
    if n==1: open(f,"w",encoding="utf-8").write(h2)
    return snap,n
if __name__=="__main__":
    import sys
    root=sys.argv[1] if len(sys.argv)>1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    s,n=update(root); print(("ok" if n==1 else "SNAP-marker-missing"),"pub",s["counts"]["published"],"up",s["counts"]["upcoming"],"hi",s["counts"]["hi_done"])
