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
  // Desktop uses a slightly deeper zoom; tablet/mobile have a perceptible,
  // reduced-scale, native-scroll version with no sticky/gesture interception.
  const canZoom=()=>!reducedMotion.matches;
  let ticking=false;
  const draw=()=>{
    ticking=false;
    const enabled=canZoom();
    const h=window.innerHeight;
    const width=window.innerWidth;
    for(const section of chapters){
      if(!enabled){
        section.style.removeProperty('--photo-scale');
        section.style.removeProperty('--text-shift');
        section.style.removeProperty('--chapter-opacity');
        continue;
      }
      const box=section.getBoundingClientRect();
      if(box.bottom<0||box.top>h)continue;
      const progress=Math.min(1,Math.max(0,(h-box.top)/(h+box.height)));
      const base=width<768?1.014:width<1024?1.019:1.025;
      const distance=width<768?.048:width<1024?.051:.055;
      section.style.setProperty('--photo-scale',(base+distance*progress).toFixed(4));
      if(width<1024){
        section.style.setProperty('--text-shift',(12*(1-progress)).toFixed(2));
        section.style.setProperty('--chapter-opacity',Math.min(1,.94+.06*progress*2).toFixed(3));
      }else{
        section.style.removeProperty('--text-shift');
        section.style.removeProperty('--chapter-opacity');
      }
    }
  };
  const onScroll=()=>{if(!ticking){ticking=true;requestAnimationFrame(draw)}};
  window.addEventListener('scroll',onScroll,{passive:true});
  window.addEventListener('resize',onScroll,{passive:true});
  reducedMotion.addEventListener?.('change',onScroll);
  draw();
})();