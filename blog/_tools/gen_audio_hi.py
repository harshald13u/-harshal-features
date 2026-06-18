#!/usr/bin/env python3
"""gen_audio_hi.py hi/blog/posts/<slug> [...] — HINDI narration.
LOCKED voice: hi-IN-SwaraNeural. Thin wrapper over gen_audio_pro.py (mastered
pipeline). Re-run until it prints DONE. Requires edge-tts + ffmpeg."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_audio_pro as G
for d in sys.argv[1:]:
    print(d); G.generate(d,"hi","hi-IN-SwaraNeural")
