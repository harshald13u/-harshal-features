#!/usr/bin/env python3
"""hi_extract(slug) -> dict of the exact EN strings make_hi_twin will need translated
(matches make_hi_twin's view: google auto-links unwrapped first). Keys: title, metadesc,
keywords, headline, bio, blogdesc, artdesc, blocks[]. Feed Hindi back as content_map."""
import re,html,os,json,sys
def extract(slug, root=None):
    root=root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    h=open(os.path.join(root,'blog/posts',slug,'index.html'),encoding='utf-8').read()
    h=re.sub(r'<a href="https://www\.google\.com/search\?q=[^"]*"[^>]*>(.*?)</a>', r'\1', h, flags=re.S)
    def g(p):
        m=re.search(p,h,re.S); return html.unescape(m.group(1).strip()) if m else ''
    descs=re.findall(r'"description":\s*"(.*?)"',h,re.S)
    out={'title':g(r'property="og:title" content="(.*?)"'),
         'metadesc':g(r'name="description" content="(.*?)"'),
         'keywords':g(r'name="keywords" content="(.*?)"'),
         'headline':g(r'"headline":\s*"(.*?)"'),
         'bio':html.unescape(descs[0]) if len(descs)>0 else '',
         'blogdesc':html.unescape(descs[1]) if len(descs)>1 else '',
         'artdesc':html.unescape(descs[2]) if len(descs)>2 else '',
         'blocks':[]}
    art=re.search(r'<article[^>]*>(.*?)</article>',h,re.S).group(1)
    for m in re.finditer(r'<(h2|h3|p|li)\b[^>]*>(.*?)</\1>',art,re.S):
        t=html.unescape(re.sub(r'<[^>]+>','',m.group(2))).strip()
        if t: out['blocks'].append(t)
    return out
if __name__=='__main__':
    print(json.dumps(extract(sys.argv[1]),ensure_ascii=False,indent=1))
