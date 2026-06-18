#!/usr/bin/env python3
"""make_cover.py — generate on-brand navy+gold blog cover cards (light + dark, 1600x900)
from a post title + topic, when a post has no embedded cover image.
Used by publish_blog.py as an automatic fallback. Pure PIL (no network)."""
import os
from PIL import Image, ImageDraw, ImageFont

FD="/usr/share/fonts/truetype/dejavu/"
def _f(name,size):
    for p in (FD+name, "/usr/share/fonts/truetype/liberation/"+name):
        if os.path.exists(p):
            try: return ImageFont.truetype(p,size)
            except: pass
    return ImageFont.load_default()

SERIF_B=lambda s:_f("DejaVuSerif-Bold.ttf",s)
SANS_B =lambda s:_f("DejaVuSans-Bold.ttf",s)
SANS   =lambda s:_f("DejaVuSans.ttf",s)

TOPIC_LABEL={"stock-market":"MARKET STRUCTURE","commodities":"COMMODITIES",
             "macros":"MACRO","geopolitics":"GEOPOLITICS"}

def _wrap(draw,text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if draw.textlength(t,font=font)<=maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def _spaced(s,n=2): return (" "*n).join(list(s))

def _card(title,topic,dark):
    W,H=1600,900
    if dark:
        top,bot=(10,22,46),(7,15,33); gold=(228,176,86); gold2=(240,210,138)
        sub=(150,165,190); rule=(212,166,74)
    else:
        top,bot=(243,239,229),(232,224,205); gold=(150,108,30); gold2=(184,133,43)
        sub=(90,104,128); rule=(184,133,43)
    img=Image.new("RGB",(W,H),top); px=img.load()
    for y in range(H):
        t=y/H
        r=int(top[0]+(bot[0]-top[0])*t); g=int(top[1]+(bot[1]-top[1])*t); b=int(top[2]+(bot[2]-top[2])*t)
        for x in range(W): px[x,y]=(r,g,b)
    d=ImageDraw.Draw(img)
    # soft gold glow blob (top-right)
    glow=Image.new("RGB",(W,H),(0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse([W-560,-260,W+160,360],fill=(int(gold[0]),int(gold[1]),int(gold[2])))
    from PIL import ImageFilter
    glow=glow.filter(ImageFilter.GaussianBlur(160))
    img=Image.blend(img,Image.composite(glow,img,Image.new("L",(W,H),40)),0.5) if dark else img
    d=ImageDraw.Draw(img)
    M=96
    # frame hairline
    d.rectangle([M-28,M-28,W-M+28,H-M+28],outline=(rule[0],rule[1],rule[2]),width=2)
    # kicker (topic)
    kf=SANS_B(26); kick=_spaced(TOPIC_LABEL.get(topic,"MARKETS"),2)
    d.text((M,M),kick,font=kf,fill=gold2)
    d.line([M,M+44,M+260,M+44],fill=(rule[0],rule[1],rule[2]),width=2)
    # title (serif, wrapped)
    size=104; tf=SERIF_B(size); maxw=W-2*M
    lines=_wrap(d,title,tf,maxw)
    while len(lines)>4 and size>56:
        size-=8; tf=SERIF_B(size); lines=_wrap(d,title,tf,maxw)
    lh=int(size*1.16); total=lh*len(lines)
    y=(H-total)//2+10
    for ln in lines:
        d.text((M,y),ln,font=tf,fill=gold2 if dark else (26,40,70)); y+=lh
    # bottom brand row
    bf=SANS_B(28)
    d.line([M,H-M-30,W-M,H-M-30],fill=(rule[0],rule[1],rule[2]),width=2)
    d.text((M,H-M-2),"HARSHAL DASANI",font=bf,fill=gold2 if dark else (26,40,70))
    bw=d.textlength("MARKETS WITH HARSHAL",font=SANS(24))
    d.text((W-M-bw,H-M+1),"MARKETS WITH HARSHAL",font=SANS(24),fill=sub)
    return img

def generate(title, topic, light_path, dark_path):
    topic=(topic or "").strip().lower()
    _card(title,topic,dark=False).save(light_path,"JPEG",quality=86)
    _card(title,topic,dark=True ).save(dark_path,"JPEG",quality=86)
    return light_path, dark_path

if __name__=="__main__":
    import sys
    t=sys.argv[1] if len(sys.argv)>1 else "SpaceX is not a rocket company. It's three."
    tp=sys.argv[2] if len(sys.argv)>2 else "stock-market"
    generate(t,tp,"/tmp/cv_light.jpg","/tmp/cv_dark.jpg")
    print("wrote /tmp/cv_light.jpg /tmp/cv_dark.jpg")
