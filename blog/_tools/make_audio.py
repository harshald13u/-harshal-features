#!/usr/bin/env python3
"""make_audio.py <slug> — generate BOTH narrations (EN + HI) for a published post.
LOCKED voices (must be identical on EVERY blog post): EN = en-IN-NeerjaExpressiveNeural,
HI = hi-IN-SwaraNeural. Delegates to gen_audio_pro.py (resumable synth + section pauses +
finance-term normalization + EBU R128 loudness mastering, 128kbps mono). Re-run until both
print DONE (long posts may need a 2nd run; cached chunks persist). Requires edge-tts + ffmpeg."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_audio_pro as G
EN_VOICE="en-IN-NeerjaExpressiveNeural"; HI_VOICE="hi-IN-SwaraNeural"
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def main(slug):
    en=os.path.join(ROOT,"blog","posts",slug); hi=os.path.join(ROOT,"hi","blog","posts",slug)
    if os.path.isdir(en): print("EN:"); G.generate(en,"en",EN_VOICE)
    else: print("  ! no EN dir",en)
    if os.path.isdir(hi): print("HI:"); G.generate(hi,"hi",HI_VOICE)
    else: print("  ! no HI dir",hi)
if __name__=="__main__":
    if len(sys.argv)<2: print("usage: make_audio.py <slug>"); sys.exit(1)
    main(sys.argv[1])
