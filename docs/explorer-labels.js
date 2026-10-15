import * as T from 'three';

/** Scene-anchored DOM targets: no per-frame DOM rebuild or extra render pass. */
export function createExplorerLabels(container,onActivate){
  const entries=new Map(),point=new T.Vector3(),view=new T.Vector3();
  function sync(items){
    const wanted=new Set(items.map(item=>item.id));
    const restoreFocus=[...entries].some(([id,entry])=>!wanted.has(id)&&document.activeElement===entry.button);
    for(const [id,entry] of entries)if(!wanted.has(id)){entry.button.remove();entries.delete(id);}
    for(const item of items){
      let entry=entries.get(item.id);
      if(!entry){
        const button=document.createElement('button');button.type='button';button.className='scene-label';button.textContent=item.label;
        button.addEventListener('click',()=>onActivate(entry.item));container.append(button);entry={button,item};entries.set(item.id,entry);
      }
      entry.item=item;
      if(entry.button.textContent!==item.label)entry.button.textContent=item.label;
      const accessibleLabel=item.accessibleLabel||item.label;
      if(entry.button.getAttribute('aria-label')!==accessibleLabel)entry.button.setAttribute('aria-label',accessibleLabel);
      entry.button.classList.toggle('selected',Boolean(item.selected));
      entry.button.classList.toggle('silent',Boolean(item.silent));
      entry.button.dataset.kind=item.kind;
    }
    if(restoreFocus)[...entries.values()].find(entry=>entry.item.selected)?.button.focus({preventScroll:true});
  }
  function update(camera,width,height,topInset=82){
    const candidates=[];
    for(const entry of entries.values()){
      const item=entry.item;point.set(...item.point);const depth=-view.copy(point).applyMatrix4(camera.matrixWorldInverse).z;point.project(camera);
      const pixels=item.height?item.height*height/(2*Math.max(.1,depth)*Math.tan(T.MathUtils.degToRad(camera.fov)/2)):Infinity;
      entry.button.hidden=item.visible===false||pixels<9||depth<=0||point.z>1||point.z< -1||Math.abs(point.x)>1||Math.abs(point.y)>1;
      if(entry.button.hidden)continue;
      if(item.silent){
        entry.button.style.left=(point.x+1)*width/2+'px';entry.button.style.top=(1-point.y)*height/2+'px';
        const size=Math.max(44,Math.min(96,pixels+12));entry.button.style.width=size+'px';entry.button.style.height=size+'px';
        entry.button.hidden=(1-point.y)*height/2<topInset;continue;
      }
      candidates.push({entry,depth,x:(point.x+1)*width/2,y:(1-point.y)*height/2});
    }
    candidates.sort((a,b)=>Number(b.entry.item.selected)-Number(a.entry.item.selected)||(b.entry.item.priority||0)-(a.entry.item.priority||0)||a.depth-b.depth);
    const placed=[],headerBottom=topInset;
    for(const candidate of candidates){
      const {entry}=candidate,w=entry.button.offsetWidth,h=entry.button.offsetHeight;
      const initialX=Math.max(w/2+8,Math.min(width-w/2-8,candidate.x));
      const initialY=Math.max(headerBottom+h/2,Math.min(height-h/2-12,candidate.y));
      const offsets=entry.item.kind==='animal'
        ?[[0,0],[0,-h-7],[w*.45,-h-7],[-w*.45,-h-7],[0,-2*(h+7)]]
        :[[0,0],[0,-h-7],[0,h+7],[w*.45,-h-7],[-w*.45,-h-7],[w*.45,h+7],[-w*.45,h+7]];
      let x=initialX,y=initialY,fits=false;
      for(const [dx,dy] of offsets){
        x=Math.max(w/2+8,Math.min(width-w/2-8,initialX+dx));y=Math.max(headerBottom+h/2,initialY+dy);
        const rect={left:x-w/2-4,right:x+w/2+4,top:y-h/2-3,bottom:y+h/2+3};
        if(!placed.some(r=>rect.left<r.right&&rect.right>r.left&&rect.top<r.bottom&&rect.bottom>r.top)&&rect.bottom<height-8){placed.push(rect);fits=true;break;}
      }
      entry.button.hidden=!fits;
      if(fits){entry.button.style.left=x+'px';entry.button.style.top=y+'px';}
    }
  }
  function hover(id){for(const [key,entry] of entries)entry.button.classList.toggle('hovered',key===id);}
  return {sync,update,hover};
}
