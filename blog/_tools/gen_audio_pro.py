#!/usr/bin/env python3
"""gen_audio_pro.py — top-quality bilingual narration (RESUMABLE).
edge-tts neural voice -> sectioned synth (atomic per-chunk cache) -> ffmpeg
loudness mastering (highpass + EBU R128 loudnorm) -> 128kbps mono MP3.
Re-run the same command until it prints DONE; cached chunks persist between runs.
Usage: python3 gen_audio_pro.py <en|hi> <post_dir> --voice <V> [--out P] [--limit N]
"""
import os, re, sys, json, shutil, html as _h, asyncio, subprocess, tempfile
from html.parser import HTMLParser

RATE_EN="-4%"; RATE_HI="-3%"; HEAD_PAUSE=0.72; SEC_PAUSE=0.46; PRE_DISC_PAUSE=0.60; CHUNK=2400
EN_DISC="This is general information, not investment advice."
HI_DISC="यह सामान्य जानकारी है, कोई निवेश सलाह नहीं।"

class Prose(HTMLParser):
    SKIP_CLASS=("key-takeaways","post-faq","related","share","crumb","byline","audio","reading-time",
                "tag","footer","colophon","hd-legal","post-meta","mast","lang","nav","toc","source")
    SKIP_TAGS={"script","style","nav","footer","aside","figure","figcaption","button","header"}
    VOID={"img","br","hr","meta","link","input","source","col","area","base","wbr","embed","track"}
    def __init__(s): super().__init__(); s.cap=None; s.buf=[]; s.out=[]; s.skip=False; s.depth=0
    def handle_starttag(s,t,a):
        if s.skip:
            if t not in s.VOID: s.depth+=1
            return
        d=dict(a); cls=d.get("class","") or ""
        if t in s.SKIP_TAGS or any(k in cls for k in s.SKIP_CLASS): s.skip=True; s.depth=1; return
        if t in ("h1","h2","h3","p","li"): s.cap=t; s.buf=[]
    def handle_endtag(s,t):
        if s.skip:
            if t not in s.VOID:
                s.depth-=1
                if s.depth<=0: s.skip=False
            return
        if t==s.cap:
            x=re.sub(r"\s+"," ",_h.unescape("".join(s.buf))).strip()
            if x and len(x)>1: s.out.append(x)
            s.cap=None; s.buf=[]
    def handle_data(s,data):
        if s.cap and not s.skip: s.buf.append(data)

def get_blocks(post_dir):
    html=open(os.path.join(post_dir,"index.html"),encoding="utf-8").read()
    html=re.sub(r"<head>.*?</head>","",html,flags=re.S)
    m=re.search(r'<article[^>]*itemprop="articleBody"[^>]*>(.*?)</article>',html,re.S)
    p=Prose(); p.feed(m.group(1) if m else html)
    return [b for b in p.out if b]

EN_ACR={"RBI":"R B I","MPC":"M P C","GDP":"G D P","CPI":"C P I","WPI":"W P I","IPO":"I P O",
 "FIIs":"foreign institutional investors","FII":"F I I","DIIs":"domestic institutional investors","DII":"D I I",
 "FPI":"F P I","GST":"G S T","NBFC":"N B F C","PSU":"P S U","FMCG":"F M C G","NRI":"N R I","PMS":"P M S",
 "AIF":"A I F","EMI":"E M I","DXY":"the dollar index","CAD":"current account deficit","USD":"U S dollars",
 "INR":"the rupee","IT":"I T","AI":"A I","US":"U S","UK":"U K","EU":"E U","UAE":"U A E"}
def speechify_en(t):
    t=re.sub(r'https?://\S+',' ',t)
    t=re.sub(r'₹\s?',' rupees ',t); t=re.sub(r'\$\s?([\d][\d,.]*)',r'\1 dollars',t); t=t.replace('%',' percent')
    t=re.sub(r'\bbps\b','basis points',t); t=re.sub(r'\bbp\b','basis points',t)
    t=re.sub(r'\bFY\s?20(\d{2})\s?[-–]\s?(\d{2})\b',r'financial year 20\1 to \2',t)
    t=re.sub(r'\bFY\s?20(\d{2})\b',r'financial year 20\1',t); t=re.sub(r'\bFY\s?(\d{2})\b',r'financial year 20\1',t)
    t=re.sub(r'\bQ1\b','first quarter',t); t=re.sub(r'\bQ2\b','second quarter',t)
    t=re.sub(r'\bQ3\b','third quarter',t); t=re.sub(r'\bQ4\b','fourth quarter',t)
    t=re.sub(r'\bYoY\b','year on year',t); t=re.sub(r'\bQoQ\b','quarter on quarter',t); t=re.sub(r'\bMoM\b','month on month',t)
    t=re.sub(r'\bvs\.?\b','versus',t)
    for k,v in sorted(EN_ACR.items(),key=lambda x:-len(x[0])): t=re.sub(r'\b'+re.escape(k)+r'\b',v,t)
    t=t.replace('&',' and ').replace('→',' to ').replace('·',', ').replace('—',', ').replace('–',', ')
    t=re.sub(r'[*#]+',' ',t); return re.sub(r'[ \t]+',' ',t).strip()

HI_ACR={"RBI":"आर बी आई","MPC":"एम पी सी","GDP":"जी डी पी","CPI":"सी पी आई","IPO":"आई पी ओ","IT":"आई टी",
 "FII":"एफ आई आई","DII":"डी आई आई","GST":"जी एस टी","AI":"ए आई","US":"यू एस","USD":"यू एस डॉलर",
 "FPI":"एफ पी आई","PMS":"पी एम एस","AIF":"ए आई एफ","SIP":"एस आई पी","NBFC":"एन बी एफ सी"}
def speechify_hi(t):
    t=re.sub(r'https?://\S+',' ',t)
    t=re.sub(r'₹\s?',' रुपये ',t); t=re.sub(r'\$\s?([\d][\d,.]*)',r'\1 डॉलर',t); t=t.replace('%',' प्रतिशत')
    for k,v in sorted(HI_ACR.items(),key=lambda x:-len(x[0])): t=re.sub(r'\b'+re.escape(k)+r'\b',v,t)
    t=t.replace('&',' और ').replace('→',' से ').replace('·',', ').replace('—',', ').replace('–',', ').replace('vs','बनाम')
    return re.sub(r'[ \t]+',' ',t).strip()

def chunk_text(text,n=CHUNK):
    parts=re.split(r'(?<=[।\.\?!])\s+',text); out,cur=[],""
    for p in parts:
        if len(cur)+len(p)+1>n and cur: out.append(cur); cur=p
        else: cur=(cur+" "+p).strip()
    if cur: out.append(cur)
    return out or [text]

def build_segments(post_dir,lang):
    blocks=get_blocks(post_dir)
    if not blocks or sum(len(b) for b in blocks)<200: return None
    head=blocks[0]; body=" ".join(blocks[1:])
    sp=speechify_en if lang=="en" else speechify_hi
    intro=sp(head)+("." if lang=="en" else "।")
    if lang=="hi": intro+=" हर्षल दसानी द्वारा।"
    segs=[(intro,HEAD_PAUSE)]
    for c in chunk_text(sp(body)): segs.append((c,SEC_PAUSE))
    segs.append(((EN_DISC if lang=="en" else HI_DISC),0))
    if len(segs)>=2: segs[-2]=(segs[-2][0],PRE_DISC_PAUSE)
    return segs

def _hq_format():
    """Bump edge-tts source to 24kHz/96kbps (2x the 48k default) before it is imported."""
    try:
        import importlib.util
        spec=importlib.util.find_spec("edge_tts")
        cf=os.path.join(os.path.dirname(spec.origin),"communicate.py")
        s=open(cf,encoding="utf-8").read()
        if "audio-24khz-96kbitrate-mono-mp3" not in s and "audio-24khz-48kbitrate-mono-mp3" in s:
            open(cf,"w",encoding="utf-8").write(s.replace("audio-24khz-48kbitrate-mono-mp3","audio-24khz-96kbitrate-mono-mp3"))
    except Exception as e: print("  [hq] note:",repr(e)[:90])

async def synth_missing(missing,files,voice,rate):
    _hq_format()
    import edge_tts
    sem=asyncio.Semaphore(4)
    async def one(i,text):
        async with sem:
            part=files[i]+".part"
            await edge_tts.Communicate(text,voice,rate=rate).save(part)
            os.replace(part,files[i])
    await asyncio.gather(*[one(i,t) for i,t in missing])

def master(files,pauses,out):
    inp=[]; order=[]; idx=0
    for i,f in enumerate(files):
        inp+=["-i",f]; order.append(idx); idx+=1
        if i<len(files)-1 and pauses[i]>0:
            inp+=["-f","lavfi","-t",f"{pauses[i]:.2f}","-i","anullsrc=r=24000:cl=mono"]; order.append(idx); idx+=1
    streams="".join(f"[{k}:a]" for k in order)
    fc=(f"{streams}concat=n={len(order)}:v=0:a=1[c];"
        "[c]highpass=f=70,treble=g=1.5:f=6000,"
        "acompressor=threshold=-18dB:ratio=2.5:attack=10:release=200,"
        "loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    _tmp=out+".tmp.mp3"
    subprocess.run(["ffmpeg","-y","-loglevel","error",*inp,"-filter_complex",fc,"-map","[a]",
                    "-c:a","libmp3lame","-b:a","160k","-ar","48000","-ac","1",_tmp],check=True)
    os.replace(_tmp,out)

def generate(post_dir,lang,voice,out=None,limit=None):
    segs=build_segments(post_dir,lang)
    if not segs: print("  ! no body",post_dir); return False
    if limit: segs=segs[:limit]
    out=out or os.path.join(post_dir,"audio.mp3")
    cache=os.path.join(post_dir,".acache"); os.makedirs(cache,exist_ok=True)
    files=[os.path.join(cache,f"s{i:03d}.mp3") for i in range(len(segs))]
    def have(f): return os.path.exists(f) and os.path.getsize(f)>0
    missing=[(i,segs[i][0]) for i in range(len(segs)) if not have(files[i])]
    if missing: asyncio.run(synth_missing(missing,files,voice,(RATE_EN if lang=="en" else RATE_HI)))
    if not all(have(f) for f in files):
        rem=[i for i,f in enumerate(files) if not have(f)]
        print(f"  ... {len(rem)}/{len(files)} chunks remaining in {post_dir} — re-run"); return False
    master(files,[p for _,p in segs],out)
    shutil.rmtree(cache,ignore_errors=True)
    dur=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",out],
                       capture_output=True,text=True).stdout.strip()
    print(f"  DONE {out}  {os.path.getsize(out)//1024}KB  {float(dur):.0f}s  voice={voice}")
    return True

if __name__=="__main__":
    a=sys.argv[1:]; lang=a[0]; post=a[1]
    voice=a[a.index("--voice")+1] if "--voice" in a else ("en-IN-NeerjaExpressiveNeural" if lang=="en" else "hi-IN-SwaraNeural")
    out=a[a.index("--out")+1] if "--out" in a else None
    limit=int(a[a.index("--limit")+1]) if "--limit" in a else None
    generate(post,lang,voice,out,limit)
