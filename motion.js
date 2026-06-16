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
    var dur=parseInt(el.getAttribute('data-dur')||'1200',10);
    var t0=performance.now();
    function step(now){
      if(document.hidden){ el.textContent=pre+fmtNum(target,el)+suf; return; }
      var p=Math.min(1,(now-t0)/dur);
      var e=1-Math.pow(1-p,3);
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
