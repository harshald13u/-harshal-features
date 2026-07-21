#!/usr/bin/env python3
"""Rework journey-post layout: split the key-takeaways box into (a) the real 4 takeaways
and (b) the year-by-year timeline rendered in the body with each YEAR bold + accent colour.
Order: intro -> Key Takeaways box -> year timeline -> 'The pattern is the point' -> closing.
Idempotent. Works on EN and HI pages. Returns (new_html, changed)."""
import re
def _split_year(li):
    m=re.match(r'^\s*(.{0,26}?\d{4})\s{2,}(.+)$', li, re.S)
    if m and re.sub(r'<[^>]+>','',m.group(1)).strip() and len(re.sub(r'<[^>]+>','',m.group(1)).strip())<=30:
        return m.group(1).strip(), m.group(2).strip()
    return None
def fix_html(html):
    am=re.search(r'(<article[^>]*>)(.*?)(</article>)',html,re.S)
    if not am: return html, False
    inner=am.group(2)
    boxm=re.search(r'<div class="key-takeaways">.*?</ul>\s*</div>',inner,re.S)
    if not boxm: return html, False
    box=boxm.group(0)
    kt=re.search(r'<div class="kt-label">(.*?)</div>',box,re.S)
    ktlabel=kt.group(1) if kt else "Key takeaways"
    lis=re.findall(r'<li>(.*?)</li>',box,re.S)
    takeaways=[]; years=[]
    for li in lis:
        sp=_split_year(li)
        (years if sp else takeaways).append(sp if sp else li)
    if not years: return html, False
    rest=inner[:boxm.start()]+inner[boxm.end():]
    h2m=re.search(r'<h2\b[^>]*>.*?</h2>',rest,re.S)
    pre = rest[:h2m.start()] if h2m else rest
    post = rest[h2m.start():] if h2m else ''
    intro='\n'.join(m.group(0) for m in re.finditer(r'<p\b[^>]*>.*?</p>',pre,re.S) if re.sub(r'<[^>]+>','',re.search(r'<p\b[^>]*>(.*?)</p>',m.group(0),re.S).group(1)).strip())
    boxn='<div class="key-takeaways"><div class="kt-label">'+ktlabel+'</div><ul>'+''.join('<li>'+t+'</li>' for t in takeaways)+'</ul></div>'
    tl='<div class="post-timeline" style="margin:26px 0 8px">'+''.join(
        f'<p class="yr-row" style="margin:0 0 15px;line-height:1.62"><b class="yr" style="color:var(--accent);font-weight:700;margin-right:6px">{y}</b> {r}</p>'
        for y,r in years)+'</div>'
    new_inner='\n'+intro+'\n'+boxn+'\n'+tl+'\n'+post.strip()+'\n'
    out=html[:am.start(2)]+new_inner+html[am.end(2):]
    arttxt=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',new_inner)).strip()
    out=re.sub(r'("articleBody": ")[^"]*(")', lambda z:z.group(1)+arttxt+z.group(2), out, count=1)
    return out, True

_HM={'जनवरी','फरवरी','फ़रवरी','मार्च','अप्रैल','मई','जून','जुलाई','अगस्त','सितंबर','सितम्बर','अक्टूबर','नवंबर','नवम्बर','दिसंबर','दिसम्बर'}
_EM={'jan','feb','mar','apr','may','jun','jul','aug','sep','sept','oct','nov','dec','january','february','march','april','june','july','august','september','october','november','december'}
def _year_prefix(p_inner):
    t=p_inner.lstrip()
    if t.startswith('<b class="yr"'): return None
    m=re.match(r'^(\d{1,2}\s+)?([A-Za-zऀ-ॿ.]+\s+)?(\d{4})(?=[\s,–—.])', t)
    if not m: return None
    word=(m.group(2) or '').strip().rstrip('.')
    if word and (word.lower() not in _EM) and (word not in _HM): return None
    return m.group(0).strip()
def _style_plain_years(html):
    am=re.search(r'(<article[^>]*>)(.*?)(</article>)',html,re.S)
    if not am: return html, False
    inner=am.group(2)
    paras=list(re.finditer(r'(<p\b[^>]*>)(.*?)(</p>)',inner,re.S))
    rows=sum(1 for m in paras if _year_prefix(m.group(2)) or m.group(2).lstrip().startswith('<b class="yr"'))
    if rows<4: return html, False
    state={'c':False}
    def repl(m):
        pi=m.group(2); pre=_year_prefix(pi)
        if not pre: return m.group(0)
        rest=pi.lstrip()[len(pi.lstrip())-len(pi.lstrip()):]  # placeholder
        rest=pi.lstrip()[len(pre):]
        state['c']=True
        return m.group(1)+'<b class="yr" style="color:var(--accent);font-weight:700;margin-right:6px">'+pre+'</b>'+rest+m.group(3)
    newinner=re.sub(r'(<p\b[^>]*>)(.*?)(</p>)', repl, inner, flags=re.S)
    if not state['c']: return html, False
    out=html[:am.start(2)]+newinner+html[am.end(2):]
    txt=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',newinner)).strip()
    out=re.sub(r'("articleBody": ")[^"]*(")', lambda z:z.group(1)+txt+z.group(2), out, count=1)
    return out, True
_orig_fix_html=fix_html
def fix_html(html):
    out,ch=_orig_fix_html(html)
    if ch: return out, True
    return _style_plain_years(html)
