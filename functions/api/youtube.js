// Cloudflare Pages Function — GET /api/youtube
// Latest REGULAR videos (no Shorts) from the "Markets with Harshal" Videos tab.
// Scrapes ytInitialData from the channel's /videos page (which already excludes Shorts),
// edge-cached ~6h; falls back to the committed /youtube-snapshot.json if the scrape fails.
// No API key, no cost. Returns [{id,title,views,date}]; the page builds thumb/link from id.

const CH = 'https://www.youtube.com/@marketswitharshal/videos?gl=US&hl=en';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

function extract(html){
  const m = html.match(/ytInitialData\s*=\s*(\{.+?\});<\/script>/s);
  if(!m) return [];
  let data; try{ data = JSON.parse(m[1]); }catch(e){ return []; }
  const out=[], seen=new Set();
  (function walk(o){
    if(!o || typeof o!=='object') return;
    const lv = o.lockupViewModel;
    if(lv && lv.contentType==='LOCKUP_CONTENT_TYPE_VIDEO' && lv.contentId && /^[\w-]{11}$/.test(lv.contentId) && !seen.has(lv.contentId)){
      seen.add(lv.contentId);
      let title=''; try{ title = lv.metadata.lockupMetadataViewModel.title.content; }catch(e){}
      const parts=[]; try{ lv.metadata.lockupMetadataViewModel.metadata.contentMetadataViewModel.metadataRows
        .forEach(r=> r.metadataParts && r.metadataParts.forEach(p=> p.text && p.text.content && parts.push(p.text.content))); }catch(e){}
      const views = parts.find(x=>/view/i.test(x)) || '';
      const date  = parts.find(x=>/ago|hour|day|week|month|year/i.test(x)) || '';
      if(title) out.push({ id:lv.contentId, title, views, date });
    }
    const vr = o.videoRenderer;
    if(vr && vr.videoId && /^[\w-]{11}$/.test(vr.videoId) && !seen.has(vr.videoId)){
      seen.add(vr.videoId);
      const title=(vr.title&&vr.title.runs&&vr.title.runs[0]&&vr.title.runs[0].text)||'';
      const views=(vr.viewCountText&&vr.viewCountText.simpleText)||'';
      const date=(vr.publishedTimeText&&vr.publishedTimeText.simpleText)||'';
      if(title) out.push({ id:vr.videoId, title, views, date });
    }
    for(const k in o) walk(o[k]);
  })(data);
  return out;
}

async function handle(context){
  const H = { 'content-type':'application/json; charset=utf-8', 'cache-control':'public, max-age=21600', 'access-control-allow-origin':'*' };
  try{
    const r = await fetch(CH, { headers:{ 'User-Agent':UA, 'Accept-Language':'en-US,en;q=0.9', 'Cookie':'SOCS=CAI; CONSENT=YES+1' }, cf:{ cacheTtl:21600, cacheEverything:true } });
    if(r.ok){
      const vids = extract(await r.text()).slice(0,24);
      if(vids.length>=3) return new Response(JSON.stringify({ videos:vids, channel:'@marketswitharshal', generated:new Date().toISOString(), source:'live' }), { headers:H });
    }
  }catch(e){}
  try{
    const r = await fetch(new URL('/youtube-snapshot.json', context.request.url), { cf:{ cacheTtl:600 } });
    if(r.ok){ const j = await r.json(); j.source='snapshot'; return new Response(JSON.stringify(j), { headers:H }); }
  }catch(e){}
  return new Response(JSON.stringify({ videos:[], error:'unavailable' }), { status:200, headers:H });
}

export async function onRequest(context){
  const url = new URL(context.request.url);
  if(url.searchParams.has('fresh')) return handle(context);
  const cache = caches.default;
  const key = new Request(url.origin + url.pathname);
  const hit = await cache.match(key);
  if(hit) return hit;
  const resp = await handle(context);
  try{ if(resp && resp.status===200) context.waitUntil(cache.put(key, resp.clone())); }catch(e){}
  return resp;
}
