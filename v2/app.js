const svg=document.getElementById('map');
const surfaces=document.getElementById('road-surfaces');
const byId=id=>document.getElementById(id);
const svgNs='http://www.w3.org/2000/svg';

try{await start();}catch(error){
  console.error(error);
  byId('road-status').textContent='Yol verisi açılamadı: '+error.message;
}

async function start(){
  const [registrationResponse,roadsResponse]=await Promise.all([
    fetch('rectification.json',{cache:'no-store'}),
    fetch('roads-metric.json',{cache:'no-store'}),
  ]);
  if(!registrationResponse.ok||!roadsResponse.ok)throw Error('Yerel rektifikasyon veya yol dosyası bulunamadı');
  const [registration,roads]=await Promise.all([registrationResponse.json(),roadsResponse.json()]);
  const grid=registration.grid;
  if(!grid||![grid.xMin,grid.xMax,grid.yMin,grid.yMax,grid.pixelsPerMetre].every(Number.isFinite))throw Error('Rektifikasyon ızgarası geçersiz');
  if(grid.xMax<=grid.xMin||grid.yMax<=grid.yMin||grid.pixelsPerMetre<=0)throw Error('Rektifikasyon ızgarası boş');
  if(!Array.isArray(roads.features))throw Error('Yol geometrisi bulunamadı');

  const ppm=grid.pixelsPerMetre;
  const width=(grid.xMax-grid.xMin)*ppm,height=(grid.yMax-grid.yMin)*ppm;
  const toCanvas=point=>[(point[0]-grid.xMin)*ppm,(grid.yMax-point[1])*ppm];
  let bounds={minX:Infinity,minY:Infinity,maxX:-Infinity,maxY:-Infinity};
  const counts={pedestrian_surface:0,vehicle_surface:0};
  const vehicleFragment=document.createDocumentFragment();
  const pedestrianFragment=document.createDocumentFragment();

  // GeoJSON outer rings and holes share the same metric frame as the rectified grid.
  function ringPath(ring,id){
    if(!Array.isArray(ring)||ring.length<4)throw Error(`${id}: eksik yol halkası`);
    const parts=[];
    ring.forEach((point,index)=>{
      if(!Array.isArray(point)||point.length<2||!Number.isFinite(point[0])||!Number.isFinite(point[1]))throw Error(`${id}: geçersiz yol noktası`);
      const [x,y]=toCanvas(point);
      bounds.minX=Math.min(bounds.minX,x);bounds.minY=Math.min(bounds.minY,y);
      bounds.maxX=Math.max(bounds.maxX,x);bounds.maxY=Math.max(bounds.maxY,y);
      parts.push(`${index?'L':'M'}${x.toFixed(2)} ${y.toFixed(2)}`);
    });
    return parts.join(' ')+' Z';
  }
  function polygonPath(polygon,id){
    if(!Array.isArray(polygon)||!polygon.length)throw Error(`${id}: boş yol çokgeni`);
    return polygon.map(ring=>ringPath(ring,id)).join(' ');
  }
  for(const feature of roads.features){
    const id=String(feature.id??'adsız yol');
    if(!(feature.kind in counts))throw Error(`${id}: bilinmeyen yol sınıfı`);
    const geometry=feature.geometry;
    if(!geometry)throw Error(`${id}: geometri eksik`);
    let d;
    if(geometry.type==='Polygon')d=polygonPath(geometry.coordinates,id);
    else if(geometry.type==='MultiPolygon')d=geometry.coordinates.map(polygon=>polygonPath(polygon,id)).join(' ');
    else throw Error(`${id}: desteklenmeyen geometri`);
    const path=document.createElementNS(svgNs,'path');
    path.setAttribute('d',d);
    path.setAttribute('class','road '+(feature.kind==='vehicle_surface'?'vehicle':'pedestrian'));
    path.setAttribute('fill-rule','evenodd');
    path.dataset.roadId=id;
    (feature.kind==='vehicle_surface'?vehicleFragment:pedestrianFragment).append(path);
    counts[feature.kind]+=geometry.type==='MultiPolygon'?geometry.coordinates.length:1;
  }
  if(!roads.features.length)throw Error('Henüz çıkarılmış yol yok');
  // Keep pedestrian detail visible where source classes touch at shared junctions.
  surfaces.append(vehicleFragment,pedestrianFragment);

  byId('pedestrian-count').textContent=`${counts.pedestrian_surface} alan`;
  byId('vehicle-count').textContent=`${counts.vehicle_surface} alan`;
  byId('road-status').textContent=`${counts.pedestrian_surface+counts.vehicle_surface} bağlı yol alanı · sürükle, tekerlekle yakınlaş`;

  const padding=48;
  const fit={x:bounds.minX-padding,y:bounds.minY-padding,
    width:Math.max(100,bounds.maxX-bounds.minX+padding*2),
    height:Math.max(100,bounds.maxY-bounds.minY+padding*2)};
  const view={...fit};
  function applyView(){svg.setAttribute('viewBox',`${view.x} ${view.y} ${view.width} ${view.height}`);}
  function reset(){Object.assign(view,fit);applyView();}
  function screenPoint(clientX,clientY){
    const ctm=svg.getScreenCTM();
    if(!ctm)return{x:view.x+view.width/2,y:view.y+view.height/2};
    const point=new DOMPoint(clientX,clientY).matrixTransform(ctm.inverse());
    return{x:point.x,y:point.y};
  }
  function zoom(scale,clientX,clientY){
    const pivot=screenPoint(clientX,clientY);
    const nextWidth=Math.max(fit.width/18,Math.min(fit.width*1.8,view.width*scale));
    const actual=nextWidth/view.width;
    view.x=pivot.x-(pivot.x-view.x)*actual;
    view.y=pivot.y-(pivot.y-view.y)*actual;
    view.width=nextWidth;view.height*=actual;
    applyView();
  }
  function centre(){const rect=svg.getBoundingClientRect();return[rect.left+rect.width/2,rect.top+rect.height/2];}
  byId('zoom-in').addEventListener('click',()=>zoom(.8,...centre()));
  byId('zoom-out').addEventListener('click',()=>zoom(1.25,...centre()));
  byId('reset-view').addEventListener('click',reset);
  svg.addEventListener('wheel',event=>{
    event.preventDefault();
    zoom(Math.exp(event.deltaY*.0012),event.clientX,event.clientY);
  },{passive:false});

  const pointers=new Map();
  svg.addEventListener('pointerdown',event=>{
    pointers.set(event.pointerId,{x:event.clientX,y:event.clientY});
    svg.setPointerCapture(event.pointerId);
    svg.classList.add('dragging');
  });
  svg.addEventListener('pointermove',event=>{
    const before=pointers.get(event.pointerId);
    if(!before)return;
    if(pointers.size===1){
      const from=screenPoint(before.x,before.y),to=screenPoint(event.clientX,event.clientY);
      view.x+=from.x-to.x;view.y+=from.y-to.y;
      applyView();
    }else if(pointers.size===2){
      const other=[...pointers].find(([id])=>id!==event.pointerId)?.[1];
      if(other){
        const oldMid=[(before.x+other.x)/2,(before.y+other.y)/2];
        const newMid=[(event.clientX+other.x)/2,(event.clientY+other.y)/2];
        const oldDistance=Math.hypot(before.x-other.x,before.y-other.y);
        const newDistance=Math.hypot(event.clientX-other.x,event.clientY-other.y);
        const anchor=screenPoint(...oldMid);
        if(oldDistance>2&&newDistance>2)zoom(oldDistance/newDistance,...oldMid);
        const shifted=screenPoint(...newMid);
        view.x+=anchor.x-shifted.x;view.y+=anchor.y-shifted.y;
        applyView();
      }
    }
    pointers.set(event.pointerId,{x:event.clientX,y:event.clientY});
  });
  const endPointer=event=>{
    pointers.delete(event.pointerId);
    if(!pointers.size)svg.classList.remove('dragging');
  };
  svg.addEventListener('pointerup',endPointer);
  svg.addEventListener('pointercancel',endPointer);
  svg.addEventListener('lostpointercapture',endPointer);
  svg.addEventListener('keydown',event=>{
    const [cx,cy]=centre();
    if(event.key==='+'||event.key==='=')zoom(.8,cx,cy);
    else if(event.key==='-')zoom(1.25,cx,cy);
    else if(event.key==='Home')reset();
    else if(event.key.startsWith('Arrow')){
      const step=view.width*.07;
      if(event.key==='ArrowLeft')view.x-=step;
      if(event.key==='ArrowRight')view.x+=step;
      if(event.key==='ArrowUp')view.y-=step;
      if(event.key==='ArrowDown')view.y+=step;
      applyView();
    }else return;
    event.preventDefault();
  });
  applyView();
  await setupOfficialMap(grid,registration.source?.imageUrl);
}

async function setupOfficialMap(grid,sourceUrl){
  const image=byId('official-map');
  const checkbox=byId('show-official-map');
  const slider=byId('official-map-opacity');
  const value=byId('official-map-opacity-value');
  const status=byId('official-map-status');
  const workspace=document.querySelector('.workspace');
  let available=false;

  function update(){
    const transparency=Math.max(0,Math.min(100,Number(slider.value)));
    value.textContent=`${transparency}%`;
    const opacity=checkbox.checked&&available?(100-transparency)/100:0;
    image.style.opacity=String(opacity);
    workspace.classList.toggle('overlay-visible',opacity>0);
    slider.disabled=!available||!checkbox.checked;
  }
  checkbox.addEventListener('change',update);
  slider.addEventListener('input',update);
  update();

  function unavailable(reason,url){
    checkbox.checked=false;
    checkbox.disabled=true;
    available=false;
    update();
    status.replaceChildren(document.createTextNode(`${reason} `));
    if(typeof url==='string'&&/^https:\/\//.test(url)){
      const link=document.createElement('a');
      link.href=url;
      link.target='_blank';
      link.rel='noopener noreferrer';
      link.textContent='Resmi krokiyi aç';
      status.append(link);
    }
  }

  try{
    const response=await fetch('official-map.json',{cache:'no-store'});
    if(!response.ok)throw Error('katman bildirimi bulunamadı');
    const manifest=await response.json();
    sourceUrl=manifest.sourceUrl||sourceUrl;
    if(!manifest.available||typeof manifest.path!=='string'){
      unavailable('Yerel kroki dosyası bulunamadı.',sourceUrl);
      return;
    }
    const expectedWidth=(grid.xMax-grid.xMin)*grid.pixelsPerMetre;
    const expectedHeight=(grid.yMax-grid.yMin)*grid.pixelsPerMetre;
    if(manifest.width!==expectedWidth||manifest.height!==expectedHeight)throw Error('kroki ve yol ızgaraları uyuşmuyor');
    const preloaded=new Image();
    await new Promise((resolve,reject)=>{
      preloaded.onload=resolve;
      preloaded.onerror=()=>reject(Error('resmi kroki görseli yüklenemedi'));
      preloaded.src=manifest.path;
    });
    image.setAttribute('x','0');
    image.setAttribute('y','0');
    image.setAttribute('width',String(expectedWidth));
    image.setAttribute('height',String(expectedHeight));
    image.setAttribute('href',manifest.path);
    available=true;
    update();
    status.textContent='Eylül 2026 resmi krokisi · konumlar yaklaşık';
  }catch(error){
    console.error('Resmi kroki katmanı:',error);
    unavailable('Kroki gösterilemedi.',sourceUrl);
  }
}
