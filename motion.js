/* Shared motion engine — Harshal Dasani.
   Reveal (data-reveal), count-up (data-count), bar/fill grow,
   SVG line-draw (data-draw). Plays regardless of OS reduce-motion
   (owner decision). rAF counters stop when the tab is hidden. */
(function(){
  var H=document.documentElement;
  try{ H.classList.add('motion-ready'); }catch(e){}
  function ready(fn){ if(document.readyState!=='loading'){ fn(); } else { document.addEventListener('DOMContentLoaded',fn); } }
  function fmtNum(n,el){
    var dec=el.getAttribute('data-decimals');
    if(dec!==null){ return Number(n).toFixed(parseInt(dec,10)); }
    return Math.round(n).toLocaleString('en-IN');
  }
  function countUp(el){
    if(el.dataset.mDone) return; el.dataset.mDone='1';
    var target=parseFloat(el.getAttribute('data-count')||'0');
    var pre=el.getAttribute('data-prefix')||'';
    var suf=el.getAttribute('data-suffix')||'';
    var dur=parseInt(el.getAttribute('data-dur')||'1600',10);
    var t0=performance.now();
    function step(now){
      if(document.hidden){ el.textContent=pre+fmtNum(target,el)+suf; return; }
      var p=Math.min(1,(now-t0)/dur);
      var e=1-Math.pow(1-p,4);
      el.textContent=pre+fmtNum(target*e,el)+suf;
      if(p<1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  ready(function(){
    var sel='[data-reveal],[data-bar],[data-fill],[data-draw],[data-count]';
    var els=Array.prototype.slice.call(document.querySelectorAll(sel));
    if(!('IntersectionObserver' in window)){
      els.forEach(function(el){ el.classList.add('in'); if(el.hasAttribute('data-count')) countUp(el); });
      return;
    }
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(!e.isIntersecting) return;
        var t=e.target; t.classList.add('in');
        if(t.hasAttribute('data-count')) countUp(t);
        io.unobserve(t);
      });
    },{threshold:0.15, rootMargin:'0px 0px -8% 0px'});
    els.forEach(function(el){ io.observe(el); });
  });
})();

/* v4: cursor 3D tilt + gold gloss + magnetic buttons (fine pointers only). */
(function(){
  if(!window.matchMedia || !matchMedia('(hover:hover) and (pointer:fine)').matches) return;
  var TILT='.lens-card,.latest-card,.tile,.post-card,.ipo-card,.snap-card,.snap-feature,.sf-card,.sf-img-card,.photo,.tool-card,.stat-card,.wl-card,.r-tile,.ts-kpi,.snap-kpi,.ipo-stat,.ts-sf,.soc';
  var MAG='.ts-cta,.btn,.btn-gold,.kit-btn,.dl-btn';
  function tilt(el){
    el.classList.add('hd-tilt');
    el.addEventListener('pointermove',function(e){
      var r=el.getBoundingClientRect(); if(!r.width) return;
      var px=(e.clientX-r.left)/r.width, py=(e.clientY-r.top)/r.height;
      el.style.setProperty('transform','perspective(700px) rotateX('+((0.5-py)*7).toFixed(2)+'deg) rotateY('+((px-0.5)*9).toFixed(2)+'deg) translateY(-3px)','important');
      el.style.setProperty('--gx',(px*100).toFixed(1)+'%');
      el.style.setProperty('--gy',(py*100).toFixed(1)+'%');
      el.style.setProperty('--gloss','1');
    });
    el.addEventListener('pointerleave',function(){ el.style.removeProperty('transform'); el.style.setProperty('--gloss','0'); });
  }
  function mag(el){
    el.classList.add('hd-magnetic');
    el.addEventListener('pointermove',function(e){
      var r=el.getBoundingClientRect(); if(!r.width) return;
      el.style.setProperty('transform','translate('+((e.clientX-r.left-r.width/2)*0.3).toFixed(1)+'px,'+((e.clientY-r.top-r.height/2)*0.4).toFixed(1)+'px)','important');
    });
    el.addEventListener('pointerleave',function(){ el.style.removeProperty('transform'); });
  }
  function scan(){
    document.querySelectorAll(TILT).forEach(function(el){ if(!el.__hdt){ el.__hdt=1; tilt(el); } });
    document.querySelectorAll(MAG).forEach(function(el){ if(!el.__hdm){ el.__hdm=1; mag(el); } });
  }
  if(document.readyState!=='loading') scan(); else document.addEventListener('DOMContentLoaded',scan);
  window.addEventListener('load',function(){ setTimeout(scan,400); setTimeout(scan,1500); });
  window.hdScanInteractive=scan;
})();
