#!/usr/bin/env python3
import os,re,json,html
def read(p): return open(p,encoding="utf-8").read()
def vis(f):
    t=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',f,flags=re.S|re.I)
    return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',t))).strip()
def article(h):
    m=re.search(r'<article[^>]*itemprop="articleBody"[^>]*>(.*?)</article>',h,re.S); return m.group(1) if m else None
def dev(s): return len(re.findall(r'[ऀ-ॿ]',s))
def years_of(h):
    rows=re.findall(r'<b class="yr"[^>]*>(.*?)</b>(.*?)</p>',h,re.S)
    out=[]
    for y,r in rows:
        yt=vis(y); m=re.search(r'(?:19|20)\d{2}',yt); out.append((m.group(0) if m else yt, vis(r)))
    return out
enj=json.load(open("blog/posts.json"))["posts"]
flags=[]
def F(sc,m): flags.append((sc,m))
# --- Hindi leftover-English ---
for p in enj:
    s=p["slug"]; f=f"hi/blog/posts/{s}/index.html"
    if not os.path.exists(f): continue
    h=read(f)
    t=re.search(r"<title>(.*?)</title>",h,re.S); ttl=vis(t.group(1)) if t else ""
    if ttl and dev(ttl)==0: F("hi:"+s,f"TITLE all-English: {ttl[:50]}")
    md=re.search(r'<meta\s+name="description"\s+content="([^"]*)"',h); desc=html.unescape(md.group(1)) if md else ""
    if desc and dev(desc)==0: F("hi:"+s,f"META-DESC all-English: {desc[:50]}")
    h1=re.search(r'<h1[^>]*>(.*?)</h1>',h,re.S); 
    if h1 and dev(vis(h1.group(1)))==0 and len(vis(h1.group(1)))>10: F("hi:"+s,f"H1 all-English: {vis(h1.group(1))[:50]}")
    af=article(h)
    if af:
        txt=vis(af)
        # longest run of consecutive Latin words (break on devanagari)
        words=txt.split(); run=0; best=0; bi=0; start=0
        for i,w in enumerate(words):
            if re.search(r'[ऀ-ॿ]',w): 
                if run>best: best=run; bi=start
                run=0
            elif re.match(r'^[A-Za-z][A-Za-z.&\'-]*$',w):
                if run==0: start=i
                run+=1
            else:
                if run>best: best=run; bi=start
                run=0
        if run>best: best=run; bi=start
        if best>=8: F("hi:"+s,f"{best}-word English run: \"{' '.join(words[bi:bi+best])[:90]}\"")
# --- Journey timeline integrity (EN + HI) + EN/HI parity ---
for p in enj:
    s=p["slug"]
    if "-journey-in-numbers" not in s: continue
    for lang,pre in [("en","blog/posts/"),("hi","hi/blog/posts/")]:
        f=f"{pre}{s}/index.html"
        if not os.path.exists(f): continue
        rows=years_of(read(f))
        yrs=[y for y,_ in rows]
        # duplicate year
        seen=set()
        for y in yrs:
            if y in seen: F(f"{lang}:{s}",f"duplicate year row {y}")
            seen.add(y)
        # empty rest
        for y,r in rows:
            if len(r)<8: F(f"{lang}:{s}",f"year {y} has near-empty text: '{r}'")
        # ordering (count inversions on 4-digit years)
        nums=[int(y) for y,_ in rows if y.isdigit()]
        inv=sum(1 for i in range(len(nums)-1) if nums[i]>nums[i+1])
        if inv>=3: F(f"{lang}:{s}",f"{inv} out-of-order years: {nums}")
    # EN/HI year-set parity
    en_y=set(y for y,_ in years_of(read(f"blog/posts/{s}/index.html"))) if os.path.exists(f"blog/posts/{s}/index.html") else set()
    hi_y=set(y for y,_ in years_of(read(f"hi/blog/posts/{s}/index.html"))) if os.path.exists(f"hi/blog/posts/{s}/index.html") else set()
    if en_y and hi_y and en_y!=hi_y:
        F(f"parity:{s}",f"EN-only years {sorted(en_y-hi_y)} | HI-only {sorted(hi_y-en_y)}")
print(f"=== CONTENT AUDIT: {len(flags)} flags ===")
for sc,m in flags: print(f"{sc} | {m}")
