(()=>{
  const menuToggle=document.querySelector('.menu-toggle');
  const mobileNav=document.querySelector('.mobile-nav');
  const setMenu=open=>{
    if(!menuToggle||!mobileNav)return;
    menuToggle.setAttribute('aria-expanded',String(open));
    menuToggle.setAttribute('aria-label',open?'Close navigation':'Open navigation');
    mobileNav.hidden=!open;
  };
  if(menuToggle&&mobileNav){
    menuToggle.addEventListener('click',()=>setMenu(menuToggle.getAttribute('aria-expanded')!=='true'));
    mobileNav.addEventListener('click',event=>{if(event.target.closest('a'))setMenu(false)});
    document.addEventListener('keydown',event=>{if(event.key==='Escape'&&menuToggle.getAttribute('aria-expanded')==='true'){setMenu(false);menuToggle.focus()}});
    window.addEventListener('resize',()=>{if(window.innerWidth>=1024)setMenu(false)},{passive:true});
  }
  const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
  if('IntersectionObserver' in window&&!reducedMotion.matches){
    const revealNodes=[...document.querySelectorAll('.reveal')];
    const observer=new IntersectionObserver(entries=>{
      for(const entry of entries)if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target)}
    },{threshold:0.08,rootMargin:'0px 0px 35px 0px'});
    document.documentElement.classList.add('enhanced');
    revealNodes.forEach(node=>observer.observe(node));
  }
  // Native scrolling is never intercepted; photo transforms are enhancement only.
  const chapters=[...document.querySelectorAll('[data-zoom]')];
  if(!chapters.length)return;
  const canZoom=()=>!reducedMotion.matches&&window.matchMedia('(min-width: 1024px)').matches;
  let ticking=false;
  const draw=()=>{
    ticking=false;
    if(!canZoom()){chapters.forEach(section=>section.style.removeProperty('--photo-scale'));return}
    const h=window.innerHeight;
    for(const section of chapters){
      const box=section.getBoundingClientRect();
      if(box.bottom<0||box.top>h)continue;
      const progress=Math.min(1,Math.max(0,(h-box.top)/(h+box.height)));
      section.style.setProperty('--photo-scale',(1.025+0.055*progress).toFixed(4));
    }
  };
  const onScroll=()=>{if(!ticking){ticking=true;requestAnimationFrame(draw)}};
  window.addEventListener('scroll',onScroll,{passive:true});
  window.addEventListener('resize',onScroll,{passive:true});
  reducedMotion.addEventListener?.('change',onScroll);
  draw();
})();
