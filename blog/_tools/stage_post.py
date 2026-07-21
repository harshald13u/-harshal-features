#!/usr/bin/env python3
"""stage_post(root, slug, date 'YYYY-MM-DD') — set a post's date to its scheduled day and
add publishAt=<date>T09:15:00+05:30 to its posts.json (EN) and hi posts.json (HI if present)
entries, so the date-gate keeps it hidden until 9:15 IST on that day."""
import os,json,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import set_post_date
def stage(root,slug,date):
    set_post_date.set_post_date(root,slug,date)
    pa=f"{date}T09:15:00+05:30"
    for pj in [os.path.join(root,"blog/posts.json"),os.path.join(root,"hi/blog/posts.json")]:
        if not os.path.exists(pj): continue
        j=json.load(open(pj,encoding="utf-8"))
        for p in j["posts"]:
            if p["slug"]==slug: p["publishAt"]=pa
        json.dump(j,open(pj,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    return pa
if __name__=="__main__":
    print(stage(sys.argv[1],sys.argv[2],sys.argv[3]))
