#!/usr/bin/env python3
"""gen_audio.py blog/posts/<slug> [...] — ENGLISH narration.
LOCKED voice: en-IN-NeerjaExpressiveNeural. Thin wrapper over gen_audio_pro.py
(mastered pipeline). Re-run until it prints DONE. Requires edge-tts + ffmpeg."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_audio_pro as G
for d in sys.argv[1:]:
    print(d); G.generate(d,"en","en-IN-NeerjaExpressiveNeural")
