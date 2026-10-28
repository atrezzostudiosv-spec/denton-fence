(()=>{
  const filters=[...document.querySelectorAll('[data-filter]')];
  const projects=[...document.querySelectorAll('.project[data-category]')];
  const live=document.querySelector('.filter-live');
  filters.forEach(button=>button.addEventListener('click',()=>{
    const type=button.dataset.filter;
    filters.forEach(item=>{const active=item===button;item.classList.toggle('is-active',active);item.setAttribute('aria-pressed',String(active))});
    let count=0;
    projects.forEach(project=>{project.hidden=type!=='all'&&project.dataset.category!==type;if(!project.hidden)count++});
    if(live)live.textContent=`Showing ${count} ${type==='all'?'project':type} photograph${count===1?'':'s'}.`;
  }));
  const dialog=document.querySelector('.gallery-dialog');
  if(!dialog||typeof dialog.showModal!=='function')return;
  const img=dialog.querySelector('img');const caption=dialog.querySelector('.dialog-inner p');
  document.querySelectorAll('.project-open').forEach(button=>button.addEventListener('click',()=>{
    img.src=button.dataset.image;
    img.alt=button.dataset.caption;
    caption.textContent=button.dataset.caption;
    dialog.showModal();
  }));
  dialog.querySelector('.dialog-close')?.addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close()});
  dialog.addEventListener('close',()=>{img.removeAttribute('src');img.alt='';caption.textContent=''});
})();
