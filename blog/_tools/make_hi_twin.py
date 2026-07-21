#!/usr/bin/env python3
"""make_hi_twin(slug, content_map, root) -> builds hi/blog/posts/<slug>/index.html from the EN page.
Does ALL deterministic transforms (lang, hreflang trio, /hi/ URLs, absolute cover/author/icon paths,
breadcrumb + theme + audio + share + byline-role + reading-time + date UI strings, related-card
auto-translation from hi posts.json), then applies content_map (EN text -> Hindi) for the headline,
meta, article h2/h3/p/li, bio, etc., rebuilds JSON-LD articleBody from the translated article, and
also adds the reciprocal hi-IN hreflang to the EN page. Returns list of leftover-English snippets."""
import os,re,json
MON_EN=['January','February','March','April','May','June','July','August','September','October','November','December']
MON_HI=['जनवरी','फ़रवरी','मार्च','अप्रैल','मई','जून','जुलाई','अगस्त','सितंबर','अक्टूबर','नवंबर','दिसंबर']
TOPIC_HI={'stock-market':'शेयर बाज़ार','markets':'शेयर बाज़ार','macros':'मैक्रो','commodities':'कमोडिटीज़','geopolitics':'भू-राजनीति'}
CRUMB_TOPIC={'Stock Market':'शेयर बाज़ार','Macros':'मैक्रो','Commodities':'कमोडिटीज़','Geopolitics':'भू-राजनीति','Markets':'शेयर बाज़ार'}

def _det(h,slug):
    h=re.sub(r'<a href="https://www\.google\.com/search\?q=[^"]*"[^>]*>(.*?)</a>', r'\1', h, flags=re.S)  # unwrap auto-entity links
    EB=f"https://harshaldasani.pages.dev/blog/posts/{slug}/"
    HB=f"https://harshaldasani.pages.dev/hi/blog/posts/{slug}/"
    h=h.replace('<html lang="en" data-theme="dark">','<html lang="hi" data-theme="dark">')
    h=h.replace('content="en-IN"','content="hi-IN"')
    h=h.replace('property="og:locale" content="en_IN"','property="og:locale" content="hi_IN"')
    h=h.replace('"inLanguage": "en-IN"','"inLanguage": "hi-IN"')
    h=h.replace(EB+'"',HB+'"').replace(EB+'#article"',HB+'#article"')
    h=re.sub(r'\n<link rel="alternate" hreflang="[^"]*" href="[^"]*">','',h)  # strip all alternates
    h=h.replace(f'<link rel="canonical" href="{HB}">', f'<link rel="canonical" href="{HB}">\n<link rel="alternate" hreflang="hi-IN" href="{HB}">\n<link rel="alternate" hreflang="en-IN" href="{EB}">\n<link rel="alternate" hreflang="x-default" href="{EB}">', 1)
    h=h.replace('data-light="cover.jpg" data-dark="cover-dark.jpg"', f'data-light="/blog/posts/{slug}/cover.jpg" data-dark="/blog/posts/{slug}/cover-dark.jpg"')
    h=h.replace('<img src="cover.jpg" ', f'<img src="/blog/posts/{slug}/cover.jpg" ').replace('<img src="cover-dark.jpg" ', f'<img src="/blog/posts/{slug}/cover-dark.jpg" ')
    h=h.replace('src="../../../harshal-dasani.jpg"','src="/harshal-dasani.jpg"')
    for ic in ['apple-touch-icon.png','icon-192.png','icon-512.png','manifest.json']:
        h=h.replace(f'href="../../../{ic}"',f'href="/{ic}"')
    h=h.replace('href="../../feed.xml"','href="/blog/feed.xml"')
    h=h.replace('&larr; Back to Blogs','&larr; ब्लॉग पर वापस').replace('<a href="../../">Blogs</a>','<a href="../../">ब्लॉग</a>')
    for en,hi in CRUMB_TOPIC.items(): h=h.replace(f'<span>{en}</span>',f'<span>{hi}</span>')
    h=h.replace('aria-label="Toggle light / dark theme" title="Toggle theme"','aria-label="लाइट / डार्क थीम बदलें" title="थीम बदलें"')
    h=h.replace('<span>Markets professional</span>','<span>बाज़ार विशेषज्ञ</span>')
    h=h.replace('"jobTitle": "Markets professional"','"jobTitle": "बाज़ार विशेषज्ञ"')
    h=h.replace('Harshal Dasani, Markets professional','Harshal Dasani, बाज़ार विशेषज्ञ')
    h=re.sub(r'(aria-label="Reading time">)(\d+) min read &middot; (\d+) words(</span>)',
             lambda m:m.group(1)+m.group(2)+' मिनट पढ़ें &middot; '+m.group(3)+' शब्द'+m.group(4), h)
    def hdate(m):
        mm=re.match(r'\s*(\d{1,2}) (\w+) (\d{4})\s*$',m.group(2))
        if mm and mm.group(2) in MON_EN:
            return m.group(1)+f"{int(mm.group(1))} {MON_HI[MON_EN.index(mm.group(2))]} {mm.group(3)}"+m.group(3)
        return m.group(0)
    h=re.sub(r'(itemprop="datePublished"[^>]*>)([^<]*)(</time>)', hdate, h)
    h=h.replace('Listen to this article','इस लेख को सुनें')
    h=h.replace('aria-label="Play article"','aria-label="लेख चलाएँ"').replace('aria-label="Playback speed"','aria-label="प्लेबैक गति"').replace('aria-label="Download audio"','aria-label="ऑडियो डाउनलोड करें"')
    h=h.replace("setAttribute('aria-label','Pause')","setAttribute('aria-label','रोकें')").replace("setAttribute('aria-label','Play')","setAttribute('aria-label','चलाएँ')")
    h=h.replace('aria-label="Share this article"','aria-label="इस लेख को साझा करें"').replace('<span class="share-label">Share</span>','<span class="share-label">साझा करें</span>')
    h=h.replace('>Key takeaways<','>मुख्य बातें<')
    h=h.replace('<h2>Related analysis</h2>','<h2>संबंधित विश्लेषण</h2>').replace('aria-label="Related analysis"','aria-label="संबंधित विश्लेषण"')
    return h

def _related(h,root):
    """Auto-translate related-card category/title/excerpt using EN->HI posts.json maps."""
    en={p['slug']:p for p in json.load(open(os.path.join(root,'blog/posts.json')))['posts']}
    hi={p['slug']:p for p in json.load(open(os.path.join(root,'hi/blog/posts.json')))['posts']}
    for slug in re.findall(r'class="related-card" href="\.\./([^/"]+)/"', h):
        ep,hp=en.get(slug),hi.get(slug)
        if not ep or not hp: continue
        if ep.get('title') and hp.get('title'): h=h.replace('>'+ep['title']+'<','>'+hp['title']+'<')
        if ep.get('excerpt') and hp.get('excerpt'): h=h.replace('>'+ep['excerpt']+'<','>'+hp['excerpt']+'<')
        lbl=TOPIC_HI.get(ep.get('topic',''))
        if lbl:
            # category span uses uppercase-ish label via CSS; the text is the topic label
            for en_lbl,hi_lbl in CRUMB_TOPIC.items():
                h=h.replace('color:var(--accent)">'+en_lbl+'<','color:var(--accent)">'+hi_lbl+'<')
    return h

def make_hi_twin(slug, content_map, root=None):
    root=root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    enf=os.path.join(root,'blog/posts',slug,'index.html')
    h=open(enf,encoding='utf-8').read()
    h=_det(h,slug)
    # content map (longest-first to avoid partial overlaps)
    for en in sorted(content_map, key=len, reverse=True):
        hi=content_map[en]
        if not (en and hi): continue
        h=h.replace(en,hi)
        en_esc=en.replace("&","&amp;")
        if en_esc!=en: h=h.replace(en_esc,hi)
    h=_related(h,root)
    # rebuild JSON-LD articleBody from the (now-translated) <article>
    m=re.search(r'<article[^>]*>(.*?)</article>',h,re.S)
    if m:
        txt=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',m.group(1))).strip()
        h=re.sub(r'("articleBody": ")[^"]*(")', lambda z:z.group(1)+txt+z.group(2), h, count=1)
    od=os.path.join(root,'hi/blog/posts',slug); os.makedirs(od,exist_ok=True)
    open(os.path.join(od,'index.html'),'w',encoding='utf-8').write(h)
    # reciprocal hi-IN on EN page
    EB=f"https://harshaldasani.pages.dev/blog/posts/{slug}/"; HB=f"https://harshaldasani.pages.dev/hi/blog/posts/{slug}/"
    e=open(enf,encoding='utf-8').read()
    if 'hreflang="hi-IN"' not in e:
        e=e.replace(f'<link rel="alternate" hreflang="en-IN" href="{EB}">\n<link rel="alternate" hreflang="x-default" href="{EB}">',
                    f'<link rel="alternate" hreflang="en-IN" href="{EB}">\n<link rel="alternate" hreflang="hi-IN" href="{HB}">\n<link rel="alternate" hreflang="x-default" href="{EB}">',1)
        open(enf,'w',encoding='utf-8').write(e)
    # leftover English in the HI article (Latin words length>=4)
    art=re.search(r'<article[^>]*>(.*?)</article>',h,re.S)
    leftover=[]
    if art:
        txt=re.sub(r'<[^>]+>',' ',art.group(1))
        leftover=sorted(set(re.findall(r'[A-Za-z]{4,}', txt)) - {'SpaceX','Tesla','xAI','PayPal','eBay','Neuralink','Starlink','Starship','NVIDIA','GPU','AI','USD','INR','CEO','IPO','EV','JLR','TELCO','TCS'})
    return leftover
