#!/usr/bin/env python3
"""set_post_date(root, slug, new_date 'YYYY-MM-DD') — set a post's published date across
EN+HI HTML (visible byline, <time datetime>, JSON-LD datePublished), posts.json (EN+HI),
sitemap lastmod and news-sitemap publication_date. Used to reflect the REAL go-live day."""
import os,json,re
MONTHS_EN=['January','February','March','April','May','June','July','August','September','October','November','December']
MONTHS_HI=['जनवरी','फ़रवरी','मार्च','अप्रैल','मई','जून','जुलाई','अगस्त','सितंबर','अक्टूबर','नवंबर','दिसंबर']
def set_post_date(root,slug,new_date):
    y,m,d=map(int,new_date.split('-')); iso=f"{new_date}T09:00:00+05:30"
    hum_en=f"{d} {MONTHS_EN[m-1]} {y}"; hum_hi=f"{d} {MONTHS_HI[m-1]} {y}"
    out=[]
    for pj,w in [(os.path.join(root,'blog/posts.json'),'EN'),(os.path.join(root,'hi/blog/posts.json'),'HI')]:
        if os.path.exists(pj):
            j=json.load(open(pj,encoding='utf-8')); ch=False
            for p in j['posts']:
                if p['slug']==slug and p.get('date')!=new_date: p['date']=new_date; ch=True
            if ch: json.dump(j,open(pj,'w',encoding='utf-8'),ensure_ascii=False,indent=2); out.append(w+'/posts.json')
    for path,hum in [(os.path.join(root,'blog/posts',slug,'index.html'),hum_en),(os.path.join(root,'hi/blog/posts',slug,'index.html'),hum_hi)]:
        if not os.path.exists(path): continue
        h=open(path,encoding='utf-8').read(); o=h
        h=re.sub(r'("datePublished":\s*")[^"]*(")', lambda mm:mm.group(1)+iso+mm.group(2), h)
        h=re.sub(r'(itemprop="datePublished"\s+datetime=")[^"]*(")', lambda mm:mm.group(1)+iso+mm.group(2), h)
        h=re.sub(r'(itemprop="datePublished"[^>]*>)[^<]*(</time>)', lambda mm:mm.group(1)+hum+mm.group(2), h)
        if h!=o: open(path,'w',encoding='utf-8').write(h); out.append(os.path.relpath(path,root))
    sm=os.path.join(root,'sitemap.xml')
    if os.path.exists(sm):
        s=open(sm,encoding='utf-8').read(); o=s
        for loc in [f"/blog/posts/{slug}/",f"/hi/blog/posts/{slug}/"]:
            s=re.sub(r'(<loc>https://harshaldasani\.pages\.dev'+re.escape(loc)+r'</loc>\s*<lastmod>)[^<]*(</lastmod>)', lambda mm:mm.group(1)+new_date+mm.group(2), s)
        if s!=o: open(sm,'w',encoding='utf-8').write(s); out.append('sitemap.xml')
    ns=os.path.join(root,'news-sitemap.xml')
    if os.path.exists(ns):
        n=open(ns,encoding='utf-8').read(); o=n
        def fix(mm):
            b=mm.group(0)
            if f"/blog/posts/{slug}/" in b:
                b=re.sub(r'(<news:publication_date>)[^<]*(</news:publication_date>)', lambda z:z.group(1)+iso+z.group(2), b)
            return b
        n=re.sub(r'<url>.*?</url>', fix, n, flags=re.S)
        if n!=o: open(ns,'w',encoding='utf-8').write(n); out.append('news-sitemap.xml')
    return out
if __name__=='__main__':
    import sys; print(set_post_date(sys.argv[1],sys.argv[2],sys.argv[3]))
