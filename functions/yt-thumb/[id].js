// Cloudflare Pages Function — GET /yt-thumb/<videoId>
// Serves a YouTube video thumbnail FROM THIS DOMAIN so Google Images credits it to
// harshaldasani.pages.dev (and it loads same-origin on the page). Proxies i.ytimg.com
// at the edge (maxres -> hq -> mq), validates the 11-char id, long-cached/immutable.
export async function onRequest(context){
  const id = (context.params.id || '').toString();
  if(!/^[\w-]{11}$/.test(id)) return new Response('bad id', { status:400 });
  const H = { 'content-type':'image/jpeg', 'cache-control':'public, max-age=604800, immutable', 'access-control-allow-origin':'*' };
  const cache = caches.default;
  const key = new Request(new URL(context.request.url).origin + '/yt-thumb/' + id);
  const hit = await cache.match(key);
  if(hit) return hit;
  for(const q of ['maxresdefault','hqdefault','mqdefault']){
    try{
      const r = await fetch('https://i.ytimg.com/vi/' + id + '/' + q + '.jpg', { cf:{ cacheTtl:604800, cacheEverything:true } });
      if(r.ok){ const resp = new Response(r.body, { headers:H }); context.waitUntil(cache.put(key, resp.clone())); return resp; }
    }catch(e){}
  }
  return new Response('not found', { status:404 });
}
