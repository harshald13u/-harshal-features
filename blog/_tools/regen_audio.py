#!/usr/bin/env python3
"""regen_audio.py [--fresh] <slug> [<slug>...] — regenerate EN+HI audio (resumable). Re-run until DONE."""
import os,sys,shutil,subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import gen_audio_pro as G
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fresh="--fresh" in sys.argv
force="--force" in sys.argv
for slug in [a for a in sys.argv[1:] if not a.startswith("--")]:
    for pre,lang,voice in [("blog","en","en-IN-NeerjaExpressiveNeural"),("hi/blog","hi","hi-IN-SwaraNeural")]:
        d=os.path.join(ROOT,pre,"posts",slug)
        if not os.path.exists(os.path.join(d,"index.html")): continue
        out=os.path.join(d,"audio.mp3")
        if fresh: shutil.rmtree(os.path.join(d,".acache"),ignore_errors=True)
        if force:
            if os.path.exists(out): os.remove(out)
        elif os.path.exists(out):
            try:
                idx=os.path.join(d,"index.html")
                up_to_date = os.path.getmtime(out) >= os.path.getmtime(idx)
                if up_to_date and subprocess.run(["ffprobe","-v","error","-show_entries","stream=sample_rate","-of","csv=p=0",out],capture_output=True,text=True).stdout.strip()=="48000":
                    print("  skip (up-to-date 48k)",slug,lang); continue
            except Exception: pass
        try: G.generate(d,lang,voice)
        except Exception as e: print("  ERR",slug,lang,repr(e)[:100])
