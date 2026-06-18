/* GUARANTEE: every page that includes this script shows a dark/light toggle + EN/HI dropdown at the top-right.
   - If the page already has a theme toggle, the dropdown is placed beside it (pushed to the extreme right).
   - If the page has NO toggle, this creates a working one (flips html[data-theme] + persists hd-theme) in a
     fixed top-right cluster alongside the dropdown.
   Idempotent. Extend HI_PAGES as more /hi/ pages are built so HI links to the exact twin (else /hi/ home). */
(function(){

  /* === Site-wide page transitions (View Transitions API) === */
  function injectVT(){
    if (document.getElementById('hd-vt-css')) return;
    var st = document.createElement('style');
    st.id = 'hd-vt-css';
    st.textContent =
      '@view-transition { navigation: auto; }' +
      '::view-transition-old(root) { animation: hd-vt-out 200ms cubic-bezier(.4,0,.2,1) both; }' +
      '::view-transition-new(root) { animation: hd-vt-in 280ms cubic-bezier(.4,0,.2,1) both; }' +
      '@keyframes hd-vt-out { to { opacity: 0; } }' +
      '@keyframes hd-vt-in  { from { opacity: 0; } }' +
      '@media (prefers-reduced-motion: reduce) {' +
        '::view-transition-old(root), ::view-transition-new(root) { animation: none !important; }' +
      '}';
    (document.head || document.documentElement).appendChild(st);
  }
  injectVT();
  /* === Skip-to-content link (WCAG 2.4.1 Bypass Blocks) — injected on every page === */
  function injectSkipLink(){
    if (document.getElementById('hd-skip-link')) return;
    if (!document.body) return;
    var st = document.createElement('style');
    st.id = 'hd-skip-css';
    st.textContent =
      '.hd-skip-link{position:absolute;left:-9999px;top:0;z-index:9999;padding:10px 16px;' +
      'background:var(--accent,#d4a64a);color:#1a1530;text-decoration:none;font-weight:700;' +
      'font:700 14px/1 Inter,system-ui,sans-serif;border-radius:0 0 8px 0;}' +
      '.hd-skip-link:focus{left:0;outline:2px solid #fff;outline-offset:2px;}';
    document.head.appendChild(st);
    var a = document.createElement('a');
    a.id = 'hd-skip-link';
    a.className = 'hd-skip-link';
    a.href = '#main';
    a.textContent = 'Skip to content';
    a.addEventListener('click', function(e){
      var target = document.getElementById('main') || document.querySelector('main') || document.querySelector('.page');
      if (target) { 
        e.preventDefault();
        target.setAttribute('tabindex','-1');
        target.focus();
        try { target.scrollIntoView(); } catch(_) {}
      }
    });
    document.body.insertBefore(a, document.body.firstChild);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectSkipLink);
  } else {
    injectSkipLink();
  }
  /* === Footer bar on every page: Home (left) | Legal (center) | Socials (right) === */
  function injectLegalLinks(){
    if (document.getElementById('hd-legal-strip')) return;
    if (!document.body) return;
    var st = document.createElement('style');
    st.id = 'hd-legal-css';
    st.textContent =
      '.hd-legal-strip{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;margin:36px 0 18px;padding:14px 0 0;border-top:1px solid var(--rule,rgba(128,128,128,.18));font:500 11px/1.5 Inter,system-ui,sans-serif;color:var(--muted,#8a8273);letter-spacing:.04em}' +
      '.hd-legal-strip a{color:var(--ink-2,#c9c0ad);text-decoration:none}' +
      '.hd-foot-home{display:inline-flex;align-items:center;gap:6px;padding:4px 6px;white-space:nowrap}' +
      '.hd-foot-home:hover{color:var(--accent,#d4a64a);text-decoration:underline}' +
      '.hd-foot-legal a{margin:0 6px;padding:4px 4px}.hd-foot-legal a:hover{color:var(--accent,#d4a64a);text-decoration:underline}' +
      '.hd-legal-sep{opacity:.5;margin:0 2px}' +
      '.hd-foot-social{display:inline-flex;align-items:center;gap:16px}' +
      '.hd-foot-social a{display:inline-flex;color:var(--ink-2,#c9c0ad)}.hd-foot-social a:hover{color:var(--accent,#d4a64a)}' +
      '.hd-foot-social svg{width:18px;height:18px;fill:currentColor;display:block}' +
      '@media(max-width:600px){.hd-legal-strip{justify-content:center;row-gap:10px}}';
    document.head.appendChild(st);
    var hi = location.pathname.indexOf('/hi/')===0;
    var p = location.pathname.replace(/index\.html$/,'');
    var isHome = (p==='/'||p==='/hi/');
    var homeHref = hi ? '/hi/' : '/';
    var homeTxt = hi ? 'मुख्य पृष्ठ' : 'Home';
    var LI='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.22.79 24 1.77 24h20.45c.98 0 1.78-.78 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/></svg>';
    var XI='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.9 1.15h3.68l-8.04 9.19L24 22.85h-7.41l-5.8-7.58-6.64 7.58H.47l8.6-9.83L0 1.15h7.59l5.24 6.93zM17.61 20.64h2.04L6.49 3.24H4.3z"/></svg>';
    var YT='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23.5 6.19a3.02 3.02 0 0 0-2.12-2.14C19.5 3.55 12 3.55 12 3.55s-7.5 0-9.38.5A3.02 3.02 0 0 0 .5 6.2 31.4 31.4 0 0 0 0 12a31.4 31.4 0 0 0 .5 5.81 3.02 3.02 0 0 0 2.12 2.14c1.88.5 9.38.5 9.38.5s7.5 0 9.38-.5a3.02 3.02 0 0 0 2.12-2.14A31.4 31.4 0 0 0 24 12a31.4 31.4 0 0 0-.5-5.81zM9.55 15.57V8.43L15.82 12z"/></svg>';
    var d = document.createElement('div');
    d.id = 'hd-legal-strip'; d.className = 'hd-legal-strip';
    var home = isHome ? '<span></span>' : '<a class="hd-foot-home" href="'+homeHref+'" aria-label="'+homeTxt+'"><span aria-hidden="true">←</span> '+homeTxt+'</a>';
    d.innerHTML = home +
      '<div class="hd-foot-legal"><a href="/legal/disclaimer/">Disclaimer</a><span class="hd-legal-sep">·</span><a href="/legal/privacy/">Privacy</a><span class="hd-legal-sep">·</span><a href="/legal/terms/">Terms</a></div>' +
      '<div class="hd-foot-social">' +
        '<a href="https://www.linkedin.com/in/harshal-dasani-/" target="_blank" rel="noopener" aria-label="LinkedIn" title="LinkedIn">'+LI+'</a>' +
        '<a href="https://x.com/HarshalDasanii" target="_blank" rel="noopener" aria-label="X (Twitter)" title="X (Twitter)">'+XI+'</a>' +
        '<a href="https://www.youtube.com/@marketswitharshal" target="_blank" rel="noopener" aria-label="YouTube" title="YouTube">'+YT+'</a>' +
      '</div>';
    var mount = document.querySelector('main.page') || document.querySelector('.page') || document.querySelector('main') || document.body;
    (mount && mount.tagName !== 'BODY' ? mount : document.body).appendChild(d);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectLegalLinks);
  } else {
    injectLegalLinks();
  }
  /* === Tablist arrow-key navigation (WAI-ARIA pattern) === */
  function bindTablistArrows(){
    var lists = document.querySelectorAll('[role="tablist"]');
    Array.prototype.forEach.call(lists, function(list){
      if (list.dataset.hdArrowsBound) return;
      list.dataset.hdArrowsBound = '1';
      var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]'));
      if (!tabs.length) return;
      list.addEventListener('keydown', function(e){
        var idx = tabs.indexOf(document.activeElement);
        if (idx < 0) return;
        var next = idx;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = (idx + 1) % tabs.length;
        else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = (idx - 1 + tabs.length) % tabs.length;
        else if (e.key === 'Home') next = 0;
        else if (e.key === 'End') next = tabs.length - 1;
        else return;
        e.preventDefault();
        tabs[next].focus();
        tabs[next].click();
      });
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindTablistArrows);
  } else {
    bindTablistArrows();
  }



  function injectCSS(){
    if (document.getElementById('lang-dd-css')) return;
    var st=document.createElement('style'); st.id='lang-dd-css';
    st.textContent=
      '.lang-dd{position:relative;display:inline-flex;vertical-align:middle;margin-left:8px;line-height:1}'+
      '.lang-dd *{box-sizing:border-box}'+
      '.lang-dd a::before,.lang-dd a::after{content:none !important;margin:0 !important}'+
      '.lang-dd-btn{display:inline-flex;align-items:center;gap:5px;min-height:44px;min-width:44px;height:44px;padding:0 14px;border:1px solid var(--accent,var(--gold,#c69a4a));border-radius:999px;background:transparent;color:var(--accent,var(--gold,#c69a4a));font:700 11px/1 "Inter",system-ui,sans-serif;letter-spacing:.8px;text-transform:none;cursor:pointer}'+
      '.lang-dd-btn:hover{background:rgba(198,154,74,.12)}'+
      '.lang-dd-cv{font-size:9px;opacity:.75}'+
      '.lang-dd-menu{position:absolute;top:calc(100% + 6px);right:0;min-width:70px;background:var(--bg-2,var(--cream,#ffffff));border:1px solid var(--rule,rgba(128,128,128,.4));border-radius:10px;padding:5px;box-shadow:0 12px 28px rgba(0,0,0,.22);z-index:1002;display:flex;flex-direction:column;gap:2px}'+
      '.lang-dd-menu[hidden]{display:none}'+
      '.lang-dd-menu a{display:block !important;padding:7px 12px !important;margin:0 !important;border:0 !important;border-radius:7px;background:transparent !important;color:var(--ink,var(--espresso,#222)) !important;text-decoration:none !important;font:700 12px/1 "Inter",system-ui,sans-serif !important;letter-spacing:.6px !important;text-transform:none !important;text-align:left}'+
      '.lang-dd-menu a:hover{background:var(--bg,rgba(128,128,128,.12)) !important;color:var(--accent,var(--gold,#c69a4a)) !important}'+
      '.lang-dd-menu a.on{color:var(--accent,var(--gold,#c69a4a)) !important}'+
      '.hd-mk-toggle{width:32px;height:32px;border-radius:50%;border:1px solid var(--accent,var(--gold,#c69a4a));background:transparent;color:var(--accent,var(--gold,#c69a4a));font-size:14px;line-height:1;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;padding:0;vertical-align:middle}'+
      '.hd-mk-toggle:hover{background:rgba(198,154,74,.12)}';
    document.head.appendChild(st);
  }
  function makeToggle(){
    var b=document.createElement('button'); b.type='button'; b.className='hd-mk-toggle';
    b.setAttribute('aria-label','Toggle light/dark theme'); b.title='Toggle light/dark theme';
    function cur(){ return document.documentElement.getAttribute('data-theme')||'dark'; }
    function paint(){ b.textContent = cur()==='light' ? '☾' : '☀'; }   // ☾ in light, ☀ in dark
    paint();
    b.addEventListener('click', function(){
      var n = cur()==='light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', n);
      try{ localStorage.setItem('hd-theme', n); }catch(e){}
      paint();
    });
    return b;
  }
  function makeDropdown(){
    var path = location.pathname || '/';
    var isHi = (path === '/hi' || path.indexOf('/hi/') === 0);
    var HI_PAGES = ['/', '/tools/', '/ipo/', '/fii-dii/', '/tools/oil-impact-estimator/', '/tools/sip-calculator/', '/tools/returns-calculator/', '/tools/capital-gains-tax-calculator/', '/blog/', '/blog/posts/rupee-usd-inr-2026-why-falling-where-it-stops/', '/blog/posts/gold-2026-structural-bull-case/', '/blog/posts/silver-2026-deficit-bull-case/', '/blog/posts/copper-2026-electrification-deficit/', '/blog/posts/kospi-2026-korea-rally-reform-explained/', '/blog/posts/spacex-ipo-1-75-trillion-explained/', '/blog/posts/iran-israel-us-war-2026-explained/', '/blog/posts/rbi-mpc-june-2026-rate-pause/', '/blog/posts/crude-oil-india-markets-rupee-inflation/', '/blog/posts/indian-it-stocks-whats-breaking/', '/blog/posts/first-millionaire-billionaire-trillionaire/', '/tracker/', '/tools/fii-flows/', '/blog/posts/harshal-dasani-interviews/', '/blog/posts/harshal-dasani-media-features/', '/blog/posts/markets-with-harshal/', '/photos/', '/legal/disclaimer/', '/legal/privacy/', '/legal/terms/'];
    var enPath, hiPath;
    if (isHi){ enPath = path.replace(/^\/hi/, '') || '/'; hiPath = path; }
    else { enPath = path; hiPath = (HI_PAGES.indexOf(path) !== -1) ? ('/hi'+path) : '/hi/'; }
    var cur = isHi ? 'HI' : 'EN';
    var dd = document.createElement('div'); dd.className='lang-dd';
    dd.innerHTML =
      '<button class="lang-dd-btn" type="button" aria-haspopup="true" aria-expanded="false" aria-label="Choose language">'+
        '<span>'+cur+'</span><span class="lang-dd-cv" aria-hidden="true">▾</span></button>'+
      '<div class="lang-dd-menu" role="menu" hidden>'+
        '<a role="menuitem" href="'+enPath+'" hreflang="en" lang="en"'+(!isHi?' class="on" aria-current="true"':'')+'>EN</a>'+
        '<a role="menuitem" href="'+hiPath+'" hreflang="hi" lang="hi"'+(isHi?' class="on" aria-current="true"':'')+'>HI</a>'+
      '</div>';
    var btn=dd.querySelector('.lang-dd-btn'), menu=dd.querySelector('.lang-dd-menu');
    function close(){ menu.hidden=true; btn.setAttribute('aria-expanded','false'); }
    function open(){ menu.hidden=false; btn.setAttribute('aria-expanded','true'); }
    btn.addEventListener('click', function(e){ e.stopPropagation(); menu.hidden?open():close(); });
    document.addEventListener('click', function(e){ if(!dd.contains(e.target)) close(); });
    document.addEventListener('keydown', function(e){ if(e.key==='Escape') close(); });
    dd.querySelectorAll('a').forEach(function(a){ a.addEventListener('click', function(){ try{ localStorage.setItem('hd-lang', this.getAttribute('lang')); }catch(e){} }); });
    return dd;
  }
  function build(){
    if (document.querySelector('.lang-dd')) return;
    injectCSS();
    var dd = makeDropdown();
    var tog = document.querySelector('.mast-theme-toggle, .theme-toggle, .theme-toggle-btn, button[onclick*="oggleTheme"], button[aria-label*="heme"]');
    if (tog && tog.parentNode){
      var pos = (window.getComputedStyle(tog).position || '');
      if (pos === 'fixed'){
        var r = tog.getBoundingClientRect();
        dd.style.position='fixed'; dd.style.top=Math.round(r.top+r.height/2)+'px';
        dd.style.transform='translateY(-50%)'; dd.style.right=Math.round(window.innerWidth-r.left+8)+'px';
        dd.style.zIndex='1001'; dd.style.marginLeft='0';
        document.body.appendChild(dd);
      } else {
        var p=tog.parentNode, cluster=document.createElement('span');
        cluster.style.cssText='display:inline-flex;align-items:center;gap:12px;margin-left:18px;vertical-align:middle';
        p.appendChild(cluster); tog.style.margin='0'; dd.style.marginLeft='0';
        cluster.appendChild(tog); cluster.appendChild(dd);
      }
    } else {
      // no theme toggle on this page — create one + dropdown in a fixed top-right cluster
      var corner=document.createElement('div');
      corner.style.cssText='position:fixed;top:14px;right:16px;z-index:1001;display:inline-flex;align-items:center;gap:10px';
      var mk=makeToggle(); dd.style.marginLeft='0';
      corner.appendChild(mk); corner.appendChild(dd);
      document.body.appendChild(corner);
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
