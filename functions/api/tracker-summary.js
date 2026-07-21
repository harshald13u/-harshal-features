// Cloudflare Pages Function — GET /api/tracker-summary
// Live numbers for the homepage "Media Tracker" spotlight, computed at the edge from
// the SAME data the tracker uses (Harshal_Dasani_Dashboard.html -> EMBEDDED_SNAPSHOT_ROWS).
// This makes the homepage count structurally unable to drift from the tracker: there is
// no separately-maintained number to go stale. Mirrors the homepage's syncTracker() and
// blog/_tools/gen_tracker_summary.py exactly (unique canon-link count, e-paper heuristic,
// latest 3). Edge-cached ~30 min; ?fresh bypasses; static tracker-summary.json is the
// graceful fallback. No recommendations, no PII.

const EPAPER_RE = /news\s?paper|\bepaper\b|e[\s-]?paper|magazine|\bedition\b|\.pdf$|true point news|outlook business december|outlook business november|wall street cn|stcn article|bhopal english edition|cn article|detailnews|\.shtml/i;

function canon(u){
  u = (u || '').toString().trim().toLowerCase()
    .replace(/^https?:\/\//, '').replace(/^(www\.|m\.|amp\.)/, '');
  u = u.replace(/\/+$/, '').replace(/\.+$/, '').split('#')[0];
  return u;
}

async function handle(context){
  const H = { 'content-type':'application/json; charset=utf-8',
              'cache-control':'public, max-age=1800, s-maxage=1800',
              'access-control-allow-origin':'*' };
  try {
    const src = new URL('/Harshal_Dasani_Dashboard.html', context.request.url);
    const r = await fetch(src, { cf:{ cacheTtl:1800, cacheEverything:true } });
    if(!r.ok) throw new Error('dashboard ' + r.status);
    const t = await r.text();
    const m = t.match(/EMBEDDED_SNAPSHOT_ROWS\s*=\s*(\[[\s\S]*?\])\s*;/);
    if(!m) throw new Error('EMBEDDED_SNAPSHOT_ROWS not found');
    const rows = JSON.parse(m[1]);
    const seen = Object.create(null); let count = 0, epaper = 0;
    for(const row of rows){
      const c = canon(row && row.Link);
      if(c && !seen[c]){ seen[c] = 1; count++; }
      if(EPAPER_RE.test(String((row && row.Heading) || ''))) epaper++;
    }
    const latest = rows.filter(x => x && x.Heading && x.Link)
      .sort((a,b) => new Date(b.Date||0) - new Date(a.Date||0))
      .slice(0,3)
      .map(x => ({ Heading:x.Heading, Link:x.Link, Topic:x.Topic, Publication:x.Publication, Date:x.Date }));
    return new Response(JSON.stringify({ count, epaper, latest,
      generated:new Date().toISOString(), source:'live:Harshal_Dasani_Dashboard.html' }), { headers:H });
  } catch(e){
    try {
      const r = await fetch(new URL('/tracker-summary.json', context.request.url), { cf:{ cacheTtl:300 } });
      if(r.ok){ const j = await r.json(); j.stale = true; return new Response(JSON.stringify(j), { headers:H }); }
    } catch(_){}
    return new Response(JSON.stringify({ count:0, epaper:0, latest:[], error:String(e && e.message || e) }), { status:200, headers:H });
  }
}

// Edge-cache the computed JSON so the dashboard is parsed at most once per TTL per edge
// node. Cache key ignores the ?nc= cache-buster. ?fresh bypasses. Invisible to the page.
export async function onRequest(context){
  const url = new URL(context.request.url);
  if(url.searchParams.has('fresh')) return handle(context);
  const cache = caches.default;
  const key = new Request(url.origin + url.pathname);
  const hit = await cache.match(key);
  if(hit) return hit;
  const resp = await handle(context);
  try { if(resp && resp.status===200) context.waitUntil(cache.put(key, resp.clone())); } catch(e){}
  return resp;
}
