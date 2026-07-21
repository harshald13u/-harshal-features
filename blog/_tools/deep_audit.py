#!/usr/bin/env python3
import os,re,json,html
from collections import Counter
BASE="https://harshaldasani.pages.dev"
EN_ROLE="Business Head, INVasset PMS & AIF"
issues=[]
def add(s,sc,m): issues.append((s,sc,m))
def read(p): return open(p,encoding="utf-8").read()
def attr(t,n):
    m=re.search(n+r'\s*=\s*"([^"]*)"',t); return m.group(1) if m else None
def tagsof(h,t): return re.findall(r'<'+t+r'\b[^>]*>',h,re.I)
def vis(f):
    t=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',f,flags=re.S|re.I)
    return html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',t))).strip()
def article(h):
    m=re.search(r'<article[^>]*itemprop="articleBody"[^>]*>(.*?)</article>',h,re.S); return m.group(1) if m else None
enj=json.load(open("blog/posts.json"))["posts"]; hij=json.load(open("hi/blog/posts.json"))["posts"]
en_by={p["slug"]:p for p in enj}; hi_by={p["slug"]:p for p in hij}
def htype(n,t):
    ty=n.get("@type"); return ty==t or (isinstance(ty,list) and t in ty)
def audit(slug,lang):
    base="blog/posts/" if lang=="en" else "hi/blog/posts/"
    d=base+slug; f=d+"/index.html"; sc=f"{lang}:{slug}"
    if not os.path.exists(f): add("BREAK",sc,"index.html missing"); return
    h=read(f)
    for t in ["<head","</head>","<body","</body>","</html>"]:
        if t not in h: add("BREAK",sc,"missing "+t)
    if h.count("<article")!=h.count("</article>"): add("BREAK",sc,"article imbalance")
    for bad in ["â€","Ã©","Ã ","ï»¿","�"]:
        if bad in h: add("WRONG",sc,f"mojibake {bad!r}")
    for ph in [">None<","lorem ipsum","[object Object]","{{slug}}","{{title}}","var(--undefined"]:
        if ph in h: add("WRONG",sc,f"leftover {ph!r}")
    links=tagsof(h,"link"); metas=tagsof(h,"meta")
    def metap(p):
        for t in metas:
            if attr(t,"property")==p or attr(t,"name")==p: return attr(t,"content")
    mt=re.search(r"<title>(.*?)</title>",h,re.S)
    if not mt or not mt.group(1).strip(): add("BREAK",sc,"empty title")
    if not (metap("description") or "").strip(): add("WRONG",sc,"no meta description")
    exp=f"{BASE}/blog/posts/{slug}/" if lang=="en" else f"{BASE}/hi/blog/posts/{slug}/"
    can=next((attr(t,"href") for t in links if attr(t,"rel")=="canonical"),None)
    if not can: add("BREAK",sc,"no canonical")
    elif can.rstrip("/")+"/"!=exp: add("WRONG",sc,f"canonical {can}")
    for p in ["og:title","og:description","og:image","og:url"]:
        if not metap(p): add("WRONG",sc,"missing "+p)
    ogu=metap("og:url")
    if ogu and ogu.rstrip("/")+"/"!=exp: add("WRONG",sc,f"og:url {ogu}")
    ogi=metap("og:image")
    if ogi and not ogi.startswith("http"): add("WRONG",sc,"og:image rel")
    alts=[(attr(t,"hreflang"),attr(t,"href")) for t in links if attr(t,"rel")=="alternate" and attr(t,"hreflang")]
    hl={a:b for a,b in alts}
    enu=f"{BASE}/blog/posts/{slug}/"; hiu=f"{BASE}/hi/blog/posts/{slug}/"
    twin_exists=os.path.isdir(("hi/blog/posts/" if lang=="en" else "blog/posts/")+slug)
    if (hl.get("en-IN","") or "").rstrip("/")+"/"!=enu: add("WRONG",sc,f"hreflang en-IN={hl.get('en-IN')}")
    if slug in hi_by and (hl.get("hi-IN","") or "").rstrip("/")+"/"!=hiu: add("WRONG",sc,f"hreflang hi-IN missing/wrong={hl.get('hi-IN')}")
    if "x-default" not in hl: add("WARN",sc,"no x-default")
    blocks=re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',h,re.S)
    nodes=[]
    for b in blocks:
        try: data=json.loads(b)
        except Exception as e: add("BREAK",sc,f"invalid JSON-LD {str(e)[:40]}"); continue
        st=[data]
        while st:
            x=st.pop()
            if isinstance(x,list): st+=x
            elif isinstance(x,dict):
                nodes.append(x)
                if isinstance(x.get("@graph"),list): st+=x["@graph"]
    arts=[n for n in nodes if any(htype(n,t) for t in ("Article","BlogPosting","NewsArticle"))]
    persons=[n for n in nodes if htype(n,"Person")]
    pj=(en_by if lang=="en" else hi_by).get(slug,{})
    if not arts: add("WRONG",sc,"no Article JSON-LD")
    else:
        a=arts[0]
        if not a.get("headline"): add("WRONG",sc,"no headline")
        dp=(a.get("datePublished") or "")[:10]
        if pj and dp!=pj.get("date"): add("WRONG",sc,f"datePublished {dp}!=json {pj.get('date')}")
        if not a.get("dateModified"): add("WARN",sc,"no dateModified")
        if len(a.get("articleBody") or "")<200: add("WRONG",sc,"articleBody short")
    hp=[p for p in persons if p.get("name")=="Harshal Dasani"]
    if not hp: add("WRONG",sc,"no Person 'Harshal Dasani'")
    elif lang=="en" and not any(p.get("jobTitle")==EN_ROLE for p in hp): add("WRONG",sc,f"jobTitle={[p.get('jobTitle') for p in hp]}")
    if lang=="en":
        if "Markets professional" in h: add("WRONG",sc,"'Markets professional'")
        if EN_ROLE not in h: add("WRONG",sc,"EN role absent")
    else:
        if "Markets professional" in h: add("WRONG",sc,"English role in HI")
    auds=tagsof(h,"audio")
    if not any('audio.mp3' in a for a in auds): add("WRONG",sc,"no audio.mp3 player")
    ap=d+"/audio.mp3"
    if not os.path.exists(ap): add("BREAK",sc,"audio.mp3 missing")
    elif os.path.getsize(ap)<1_000_000: add("BREAK",sc,f"audio tiny {os.path.getsize(ap)}")
    af=article(h)
    if not af: add("BREAK",sc,"no article body")
    else:
        words=len(vis(af).split())
        mb=re.search(r'(\d+)\s*(?:min read|मिनट)[^0-9]{0,8}([\d,]+)\s*(?:words?|शब्द)',h)
        if mb:
            st=int(mb.group(2).replace(",",""))
            if words>30 and abs(st-words)/words>0.30: add("WRONG",sc,f"wordcount {st} vs {words}")
    if 'class="key-takeaways"' in h:
        ktm=re.search(r'class="[^"]*key-takeaways[^"]*"[^>]*>(.*?)</(?:div|section|ul)>',h,re.S)
        if ktm:
            for li in re.findall(r'<li[^>]*>(.*?)</li>',ktm.group(1),re.S):
                if re.match(r'^\s*(?:19|20)\d{2}\b',vis(li)): add("WRONG",sc,f"YEAR in takeaways: {vis(li)[:30]}")
    for href in set(re.findall(r'href="(?:https://harshaldasani\.pages\.dev)?(/(?:hi/)?blog/posts/[^"#?]+)"',h)):
        if not os.path.isdir(href.strip("/")): add("WRONG",sc,f"dead internal link {href}")
    if ogi and ogi.startswith(BASE):
        lp=ogi[len(BASE):].lstrip("/").split("?")[0]
        if lp and not os.path.exists(lp): add("WRONG",sc,f"og:image file missing: {lp}")
    yb=len(re.findall(r'<b class="yr"',h))
    if "-journey-in-numbers" in slug and yb<3: add("WARN",sc,f"journey only {yb} bold years")
    return yb
yb={}
for s in en_by: yb[("en",s)]=audit(s,"en")
for s in hi_by: yb[("hi",s)]=audit(s,"hi")
for s in en_by:
    if "-journey-in-numbers" in s:
        e=yb.get(("en",s)) or 0; hh=yb.get(("hi",s)) or 0
        if e and hh and abs(e-hh)>1: add("WARN",f"parity:{s}",f"EN {e} vs HI {hh} year rows")
if set(en_by)!=set(hi_by): add("WRONG","posts.json",f"slug mismatch {set(en_by)^set(hi_by)}")
for s,p in en_by.items():
    pa=p.get("publishAt","") or ""
    if pa and not re.match(r'^\d{4}-\d{2}-\d{2}T09:15:00\+05:30$',pa): add("WARN","sched",f"{s} pa={pa}")
    if pa and p.get("date")!=pa[:10]: add("WRONG","posts.json",f"{s} date!=pa")
    if s not in (p.get("url","") or ""): add("WRONG","posts.json",f"{s} url-slug")
dates=[p.get("date") for p in enj if (p.get("publishAt") or "")]
for d,c in Counter(dates).items():
    if c>1: add("WRONG","sched",f"{c} staged posts share {d}")
import xml.etree.ElementTree as ET
for xf in ["sitemap.xml","news-sitemap.xml","blog/feed.xml"]:
    if not os.path.exists(xf): add("WARN",xf,"missing"); continue
    try: ET.parse(xf)
    except Exception as e: add("BREAK",xf,f"bad XML {str(e)[:50]}")
for idx in ["index.html","blog/index.html","hi/blog/index.html"]:
    if os.path.exists(idx) and "publishAt" not in read(idx): add("WRONG",idx,"no date-gate")
order={"BREAK":0,"WRONG":1,"WARN":2}
issues.sort(key=lambda x:(order[x[0]],x[1]))
print("=== AUDIT",len(issues),dict(Counter(i[0] for i in issues)),"===")
for s,sc,m in issues: print(f"{s} | {sc} | {m}")
