import * as T from 'three';
import {OrbitControls} from './vendor/OrbitControls.js';
import {createSite,CAGE} from './model.js?v=20261014i';

const $=id=>document.getElementById(id);
const hotspots={
  cage:{x:CAGE.x,y:CAGE.y,z:23,label:'Su Kuşları Kafesi',view:'entry',primary:true},
};
try{await start();}catch(error){console.error(error);$('loading').textContent='Görünüm açılamadı: '+error.message;}

async function start(){
  const response=await fetch('./site-data.json',{cache:'no-store'});if(!response.ok)throw Error('Alan verisi yüklenemedi');
  const D=await response.json();const host=$('stage'),canvas=$('canvas');
  const scene=new T.Scene();scene.background=new T.Color('#d8e3d7');
  const mapCamera=new T.OrthographicCamera(-420,420,300,-300,.1,3000);mapCamera.up.set(0,0,1);
  const eyeCamera=new T.PerspectiveCamera(56,1,.1,3000);eyeCamera.up.set(0,0,1);
  let camera=mapCamera;
  const renderer=new T.WebGLRenderer({antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.38;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;canvas.append(renderer.domElement);
  scene.add(new T.HemisphereLight('#eff8e8','#76917a',2.0));const sun=new T.DirectionalLight('#fff1d5',2.4);sun.position.set(-230,160,350);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-420;sun.shadow.camera.right=420;sun.shadow.camera.top=300;sun.shadow.camera.bottom=-300;sun.shadow.camera.near=1;sun.shadow.camera.far=900;sun.shadow.bias=-.0003;scene.add(sun);
  const {site,cage,trees,footprints,canopy}=createSite(D);scene.add(site);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.09;controls.screenSpacePanning=true;controls.minZoom=.55;controls.maxZoom=18;controls.minDistance=2;controls.maxDistance=1200;controls.maxPolarAngle=Math.PI*.495;
  const c=Math.cos(CAGE.angle),s=Math.sin(CAGE.angle);
  const cagePoint=(u,v,z)=>[CAGE.x+u*c-v*s,CAGE.y+u*s+v*c,z];
  const viewDefs={
    site:{projection:'map',position:[360,-440,540],target:[18,-6,0],mobilePosition:[6.5,50.7,800],mobileTarget:[6.5,50.7,0],zoom:1.27},
    cage:{projection:'map',position:[-132,-215,46],target:[CAGE.x,CAGE.y,9],zoom:4.45},
    entry:{projection:'eye',position:cagePoint(56,-2,1.7),mobilePosition:cagePoint(60,2,1.7),target:cagePoint(12,0,7.1),zoom:1},
    inside:{projection:'eye',position:cagePoint(23,-9,1.65),mobilePosition:cagePoint(25,-10,1.65),target:cagePoint(-4,1,3.2),zoom:1},
    'cage-top':{projection:'map',position:[CAGE.x-8,CAGE.y-4,130],target:[CAGE.x,CAGE.y,2],zoom:5.1},
  };
  let active='site',transition=null,dirty=true,drag=false,down=null,fullscreenFallback=false,initialized=false;
  function resize(){
    const w=host.clientWidth,h=host.clientHeight;
    mapCamera.left=-420;mapCamera.right=420;mapCamera.top=420*h/w;mapCamera.bottom=-420*h/w;mapCamera.updateProjectionMatrix();
    eyeCamera.aspect=w/h;eyeCamera.updateProjectionMatrix();renderer.setSize(w,h,false);
    if(initialized)go(active,false);dirty=true;
  }
  new ResizeObserver(resize).observe(host);resize();
  function go(name,animate=true){
    const v=viewDefs[name];if(!v)return;
    const previous=camera;active=name;camera=v.projection==='eye'?eyeCamera:mapCamera;
    const narrow=host.clientWidth<760;
    mapCamera.up.set(name==='site'&&narrow?-.95845:0,name==='site'&&narrow?-.28527:0,name==='site'&&narrow?0:1);
    controls.object=camera;controls.enableRotate=!(name==='site'&&narrow);
    controls.maxPolarAngle=name==='site'&&narrow?Math.PI*.95:v.projection==='eye'?Math.PI*.78:Math.PI*.475;
    document.querySelectorAll('[data-view]').forEach(b=>{const on=b.dataset.view===name;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
    const position=narrow&&v.mobilePosition?v.mobilePosition:v.position;
    const next=new T.Vector3(...position),target=new T.Vector3(...(narrow&&v.mobileTarget?v.mobileTarget:v.target));
    const factor=narrow?(name==='site'?1.35:name==='cage'||name==='cage-top'?2.35:1):1;
    const zoom=v.zoom*factor;
    if(!animate||previous!==camera||v.projection==='eye'||matchMedia('(prefers-reduced-motion: reduce)').matches){
      transition=null;camera.position.copy(next);controls.target.copy(target);camera.zoom=zoom;camera.updateProjectionMatrix();controls.update();dirty=true;
    }else transition={from:camera.position.clone(),to:next,fromTarget:controls.target.clone(),toTarget:target,z0:camera.zoom,z1:zoom,start:performance.now()};
    $('map-guide').hidden=name!=='site';
    const hints={site:'Genel plan',cage:'Su Kuşları Kafesi · dış görünüm',entry:'Su Kuşları Kafesi · giriş',inside:'Su Kuşları Kafesi · iç görünüm','cage-top':'Su Kuşları Kafesi · üstten'};
    $('view-hint').textContent=hints[name];
  }
  document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>go(b.dataset.view)));
  $('reset').onclick=()=>go('site');$('zoom-in').onclick=()=>{camera.zoom=Math.min(18,camera.zoom*1.25);camera.updateProjectionMatrix();dirty=true;};$('zoom-out').onclick=()=>{camera.zoom=Math.max(.55,camera.zoom/1.25);camera.updateProjectionMatrix();dirty=true;};
  const markers=[];for(const [key,h] of Object.entries(hotspots)){const b=document.createElement('button');b.className='marker'+(h.primary?' primary':'');b.textContent=h.label;b.onclick=()=>go(h.view);$('markers').append(b);markers.push({button:b,point:new T.Vector3(h.x,h.y,h.z)});}
  function updateMarkers(){const w=host.clientWidth,h=host.clientHeight;for(const m of markers){const p=m.point.clone().project(camera);m.button.style.left=((p.x+1)*w/2)+'px';m.button.style.top=((-p.y+1)*h/2)+'px';m.button.hidden=active!=='site'||p.z>1||p.z< -1||p.x>1.1||p.x< -1.1||p.y>1.1||p.y< -1.1;}}
  function updateMapGuide(){
    if(active!=='site')return;
    const at=controls.target.clone().project(mapCamera),north=controls.target.clone().add(new T.Vector3(0,100,0)).project(mapCamera);
    $('north-arrow').style.transform='rotate('+Math.atan2(north.x-at.x,north.y-at.y)*180/Math.PI+'deg)';
    const pixelsPerMetre=host.clientWidth*mapCamera.zoom/840;
    const scaleMetres=[10,20,25,50,100,200,500,1000].reduce((best,value)=>Math.abs(value*pixelsPerMetre-95)<Math.abs(best*pixelsPerMetre-95)?value:best);
    $('scale-rule').style.width=scaleMetres*pixelsPerMetre+'px';
    $('scale-label').textContent=scaleMetres+' m';
  }
  controls.addEventListener('change',()=>{dirty=true;});
  renderer.domElement.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY];drag=false;});
  renderer.domElement.addEventListener('pointermove',e=>{if(down&&Math.hypot(e.clientX-down[0],e.clientY-down[1])>6)drag=true;});
  renderer.domElement.addEventListener('pointerup',e=>{
    if(!down||drag){down=null;return;}down=null;
    const r=renderer.domElement.getBoundingClientRect(),p=new T.Vector2(2*(e.clientX-r.left)/r.width-1,-2*(e.clientY-r.top)/r.height+1);
    const ray=new T.Raycaster();ray.setFromCamera(p,camera);
    if(active==='site'&&ray.intersectObject(cage,true).length)go('entry');
  });
  for(const [id,group] of [['toggle-trees',trees],['toggle-buildings',footprints],['toggle-canopies',canopy]])$(id).onclick=()=>{group.visible=!group.visible;$(id).setAttribute('aria-pressed',String(group.visible));dirty=true;};
  function showLayers(on){$('layers-panel').hidden=!on;$('layers-toggle').setAttribute('aria-expanded',String(on));}
  $('layers-toggle').onclick=()=>showLayers($('layers-panel').hidden);
  $('layers-close').onclick=()=>showLayers(false);
  function syncFull(on){$('fullscreen').setAttribute('aria-pressed',String(on));$('fullscreen').setAttribute('aria-label',on?'Tam ekrandan çık':'Tam ekran');$('fullscreen').title=on?'Tam ekrandan çık':'Tam ekran';$('fullscreen').querySelector('.action-label').textContent=on?'Çık':'Tam ekran';dirty=true;}
  $('fullscreen').onclick=async()=>{
    if(document.fullscreenElement===host){await document.exitFullscreen();return;}
    if(fullscreenFallback){host.classList.remove('fallback-fullscreen');fullscreenFallback=false;syncFull(false);return;}
    try{await host.requestFullscreen();syncFull(true);}catch{host.classList.add('fallback-fullscreen');fullscreenFallback=true;syncFull(true);}
  };
  document.addEventListener('fullscreenchange',()=>syncFull(document.fullscreenElement===host));
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&fullscreenFallback){host.classList.remove('fallback-fullscreen');fullscreenFallback=false;syncFull(false);}});
  function frame(now){requestAnimationFrame(frame);if(transition){const t=Math.min(1,(now-transition.start)/850),e=t*t*(3-2*t);camera.position.lerpVectors(transition.from,transition.to,e);controls.target.lerpVectors(transition.fromTarget,transition.toTarget,e);camera.zoom=transition.z0+(transition.z1-transition.z0)*e;camera.updateProjectionMatrix();if(t>=1)transition=null;dirty=true;}controls.update();if(dirty){renderer.render(scene,camera);updateMarkers();updateMapGuide();dirty=false;}}
  const focus=new URLSearchParams(location.search).get('focus');
  go(focus==='cage'?'entry':viewDefs[focus]?focus:'site',false);
  initialized=true;$('loading').remove();requestAnimationFrame(frame);
}
