#!/usr/bin/env python3
"""make_audio.py <slug> — generate BOTH narrations for a published post.

Writes:
  blog/posts/<slug>/audio.mp3        (EN, voice en-IN-PrabhatNeural)  from body.md
  hi/blog/posts/<slug>/audio.mp3     (HI, voice hi-IN-MadhurNeural)   from the Hindi twin's visible prose

Why chunked+concurrent: each sandbox bash call caps ~45s and background procs don't
survive between calls, so we split into 3 paragraph-aligned chunks, synth them with
asyncio.gather, then `ffmpeg -f concat -c copy`. Requires: pip install edge-tts ; ffmpeg.

The post template renders the audio player and HIDES it when audio.mp3 is absent —
so this file MUST be run for every post (EN + HI) per the standing bilingual rule.
"""
import os, sys, re, html, math, asyncio, subprocess, tempfile
import edge_tts
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VOICE = {"en": "en-IN-PrabhatNeural", "hi": "hi-IN-MadhurNeural"}

def en_text(slug):
    md = open(f"{ROOT}/blog/posts/{slug}/body.md", encoding="utf-8").read()
    out = []
    for ln in md.split("\n"):
        s = ln.strip()
        if not s or s.upper().startswith("COVER"): continue
        out.append(re.sub(r"^#{1,3}\s*", "", s))
    return [p for p in out if p]

class _Prose(HTMLParser):
    SKIP_CLASS = ("key-takeaways","post-faq","related","share","crumb","byline",
                  "audio-player","reading-time","tag","footer","colophon","hd-legal","post-meta","mast")
    SKIP_TAGS = {"script","style","nav","footer","aside","figure","figcaption","button","header"}
    def __init__(s): super().__init__(); s.cap=None; s.buf=[]; s.out=[]; s.skip=[]
    def handle_starttag(s,t,a):
        d=dict(a); cls=d.get("class","")
        if t in s.SKIP_TAGS or any(k in cls for k in s.SKIP_CLASS): s.skip.append(t); return
        if s.skip: return
        if t in ("h1","h2","h3","p"): s.cap=t; s.buf=[]
    def handle_endtag(s,t):
        if s.skip and t==s.skip[-1]: s.skip.pop(); return
        if s.skip: return
        if t==s.cap:
            x=re.sub(r"\s+"," ",html.unescape("".join(s.buf))).strip()
            if x: s.out.append(x)
            s.cap=None; s.buf=[]
    def handle_data(s,data):
        if s.cap and not s.skip: s.buf.append(data)

def hi_text(slug):
    h = open(f"{ROOT}/hi/blog/posts/{slug}/index.html", encoding="utf-8").read()
    h = re.sub(r"<head>.*?</head>", "", h, flags=re.S)
    p=_Prose(); p.feed(h); return p.out

async def _synth_chunks(paras, voice, out_path):
    k=3; size=math.ceil(len(paras)/k); tmp=[]
    async def one(text, dst): await edge_tts.Communicate(text, voice).save(dst)
    tasks=[]
    for i in range(k):
        chunk="\n".join(paras[i*size:(i+1)*size]).strip()
        if not chunk: continue
        dst=f"{out_path}.part{i}.mp3"; tmp.append(dst); tasks.append(one(chunk,dst))
    await asyncio.gather(*tasks)
    lst=out_path+".list.txt"
    open(lst,"w").write("".join(f"file '{os.path.basename(t)}'\n" for t in tmp))
    subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0",
                    "-i",lst,"-c","copy",out_path], cwd=os.path.dirname(out_path) or ".", check=True)
    for t in tmp+[lst]:
        try: os.remove(t)
        except OSError: pass

def main():
    slug=sys.argv[1]
    only=sys.argv[2] if len(sys.argv) > 2 else None  # optional: "en" or "hi" (each fits a short shell window)
    if only in (None, "en"):
        asyncio.run(_synth_chunks(en_text(slug), VOICE["en"], f"{ROOT}/blog/posts/{slug}/audio.mp3"))
        print("EN audio ->", f"blog/posts/{slug}/audio.mp3")
    if only in (None, "hi"):
        asyncio.run(_synth_chunks(hi_text(slug), VOICE["hi"], f"{ROOT}/hi/blog/posts/{slug}/audio.mp3"))
        print("HI audio ->", f"hi/blog/posts/{slug}/audio.mp3")

if __name__ == "__main__":
    main()
