import * as T from 'three';
import {OrbitControls} from './vendor/OrbitControls.js';
import {createAtlasOrbit,PLAN_TILT} from './atlas-orbit.js?v=20261015ag';
import {createPenguins} from './penguins.js?v=20261015ai';
import {createRegionalModels} from './region-models.js?v=20261015af';
import {createSite,CAGE,waitForSceneTextures} from './model.js?v=20261015af';
import {createSceneFinishing} from './scene-effects.js?v=20261015af';
import {WOODLAND_LIGHT} from './lighting.js?v=20261015af';

const $=id=>document.getElementById(id);
try{await start();}catch(error){console.error(error);$('loading').textContent='Görünüm açılamadı: '+error.message;}

async function start(){
  const [siteResponse,planResponse,surfaceResponse,buildingResponse,landscapeResponse,regionResponse,modelResponse,groundResponse]=await Promise.all([
    fetch('./site-data.json',{cache:'no-store'}),
    fetch('./current-plan-data.json',{cache:'no-store'}),
    fetch('./surface-layers.json',{cache:'no-store'}),
    fetch('./building-shell.json',{cache:'no-store'}),
    fetch('./landscape-layout.json',{cache:'no-store'}),
    fetch('./region-locations.json',{cache:'no-store'}),
    fetch('./scene-model-catalog.json',{cache:'no-store'}),
    fetch('./ground-material-layout.json',{cache:'no-store'}),
  ]);
  if(!siteResponse.ok||!planResponse.ok||!surfaceResponse.ok||!buildingResponse.ok||!landscapeResponse.ok||!regionResponse.ok||!modelResponse.ok||!groundResponse.ok)throw Error('Alan ve güncel plan verisi yüklenemedi');
  const [D,P,S,B,L,R,M,G]=await Promise.all([siteResponse.json(),planResponse.json(),surfaceResponse.json(),buildingResponse.json(),landscapeResponse.json(),regionResponse.json(),modelResponse.json(),groundResponse.json()]);
  if(R.schema!=='bursa-zoo-region-locations/v1'||R.areas.length!==43)throw Error('Bölge envanteri eksik');
  const host=$('stage'),canvas=$('canvas');
  const scene=new T.Scene();scene.background=new T.Color('#d8e3d7');
  const mapCamera=new T.OrthographicCamera(-420,420,300,-300,.1,3000);mapCamera.up.set(0,0,1);
  // Keep the depth range near the actual site scale to avoid distant surface flicker.
  const siteCamera=new T.PerspectiveCamera(30,1,.5,2500);siteCamera.up.set(0,0,1);
  const eyeCamera=new T.PerspectiveCamera(56,1,.2,1200);eyeCamera.up.set(0,0,1);
  let camera=mapCamera;
  const renderer=new T.WebGLRenderer({antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=WOODLAND_LIGHT.exposure;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;canvas.append(renderer.domElement);
  scene.add(new T.HemisphereLight(WOODLAND_LIGHT.sky,WOODLAND_LIGHT.ground,WOODLAND_LIGHT.hemisphere));
  const sun=new T.DirectionalLight(WOODLAND_LIGHT.sun,WOODLAND_LIGHT.sunIntensity);sun.position.set(...WOODLAND_LIGHT.direction);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.near=1;sun.shadow.camera.far=900;sun.shadow.bias=-.00018;sun.shadow.normalBias=.06;sun.shadow.intensity=WOODLAND_LIGHT.shadowIntensity;sun.shadow.radius=WOODLAND_LIGHT.shadowRadius;scene.add(sun,sun.target);
  const {site,cage,trees,footprints,forestCandidates,prepareWater}=createSite(D,P,S,B,L,G);scene.add(site);
  let forest=null;
  const forestMode=new URLSearchParams(location.search).get('forest');
  const finishing=createSceneFinishing(renderer,scene,camera);
  const regionalModels=createRegionalModels(M,footprints,()=>{dirty=true;syncModelStatus();});
  const penguins=createPenguins(footprints,()=>{dirty=true;syncModelStatus();});
  async function loadForest(){
    if(!['1','2'].includes(forestMode))return;
    try{
      const {createForest}=await import('./forest.js?v=20261015af');
      forest=await createForest(forestCandidates,renderer,forestMode==='2'?'impostor':'mesh');trees.add(forest.group);dirty=true;
    }catch(error){console.warn('Dallanan ağaç denemesi yüklenemedi; mevcut bitkiler gösteriliyor.',error);}
  }
  // The September 2026 illustration is displayed from the zoo's own URL.
  // Registration coefficients come from current-plan-registration.json (12 controls).
  const planImageToMetres={x:[.740875564,-.012134839,-349.859305],y:[-.034404068,-.707726837,327.297028]};
  const metresToPlanImage={u:[1.348680483,-.023124771,479.417086],v:[-.065562153,-1.411850395,439.156908]};
  const planOverlay=$('plan-overlay'),planOverlayImage=$('plan-overlay-image');
  const tracedEdge=P.features.find(feature=>feature.id==='illustrated_site_edge')?.pointsXYMetres;
  if(tracedEdge?.length){
    planOverlayImage.style.clipPath='polygon('+tracedEdge.map(([x,y])=>{
      const u=metresToPlanImage.u[0]*x+metresToPlanImage.u[1]*y+metresToPlanImage.u[2];
      const v=metresToPlanImage.v[0]*x+metresToPlanImage.v[1]*y+metresToPlanImage.v[2];
      return `${(u/1600*100).toFixed(4)}% ${(v/864*100).toFixed(4)}%`;
    }).join(',')+')';
  }
  const hotspots={cage:{x:CAGE.x,y:CAGE.y,z:23,label:'Su Kuşları Kafesi',view:'entry',primary:true},
    penguin:{x:-14,y:134,z:4,label:'Penguen',view:'penguin'}};
  let controls=createAtlasOrbit(OrbitControls,camera,renderer.domElement,new T.Vector3(),{onChange:()=>{dirty=true;},onStart:()=>{transition=null;}});
  function bindOrbit(target,eye=false){
    controls.dispose();
    controls=createAtlasOrbit(OrbitControls,camera,renderer.domElement,target,{flat:!eye&&perspective===0,eye,onChange:()=>{dirty=true;},onStart:()=>{transition=null;}});
  }
  const c=Math.cos(CAGE.angle),s=Math.sin(CAGE.angle);
  const cagePoint=(u,v,z)=>[CAGE.x+u*c-v*s,CAGE.y+u*s+v*c,z];
  const viewDefs={
    site:{projection:'site',position:[360,-440,540],target:[18,-6,0],mobilePosition:[-166,0,800],mobileTarget:[6.5,50.7,0],zoom:.82},
    cage:{projection:'map',position:[CAGE.x+44,CAGE.y-118,46],target:[CAGE.x,CAGE.y,9],zoom:4.1},
    entry:{projection:'eye',position:cagePoint(56,-2,1.7),mobilePosition:cagePoint(57,2,1.7),target:cagePoint(12,0,5.6),mobileTarget:cagePoint(12,0,4),zoom:1},
    inside:{projection:'eye',position:cagePoint(13,-8,1.7),mobilePosition:cagePoint(6,-16,3.5),target:cagePoint(0,4,2.7),mobileTarget:cagePoint(7,2,.6),mobileFov:74,zoom:1},
    'cage-top':{projection:'map',position:[CAGE.x-8,CAGE.y-4,130],target:[CAGE.x,CAGE.y,2],zoom:5.1},
    penguin:{projection:'map',position:[48,69,43],target:[-14,134,1],zoom:9.6},
    'penguin-close':{projection:'eye',position:[-6.6,119.8,.9],mobilePosition:[-6.6,120.0,.78],target:[-7.5,123,.08],zoom:1},
  };
  const africanModel=M.models.find(model=>model.key==='africanVillage');
  if(!africanModel)throw Error('Afrika Köyü kamera sınırları eksik');
  const africanBounds=new T.Box3(new T.Vector3(...africanModel.boundsXYZMetres[0]),new T.Vector3(...africanModel.boundsXYZMetres[1]));
  const africanFitPoints=africanModel.fitPointsXYZMetres.map(point=>new T.Vector3(...point));
  for(const area of R.areas){
    const option=document.createElement('option');option.value='region-'+area.number;
    option.textContent=String(area.number).padStart(2,'0')+' · '+area.name+(area.anchors.length?'':' · konumu belirsiz');
    option.disabled=!area.anchors.length;$('region-select').append(option);
    if(!area.anchors.length)continue;
    const framedModel=area.number===14?africanModel:area.number===13?M.models.find(model=>model.key==='africanCafe'):area.number===9?M.models.find(model=>model.key==='habesIsland'):area.number===29?M.models.find(model=>model.key==='bearPool'):null;
    const modelBounds=framedModel?new T.Box3(new T.Vector3(...framedModel.boundsXYZMetres[0]),new T.Vector3(...framedModel.boundsXYZMetres[1])):null;
    const [x0,y0,x1,y1]=modelBounds?[modelBounds.min.x-6,modelBounds.min.y-6,modelBounds.max.x+6,modelBounds.max.y+6]:area.contextBoundsXYMetres;
    const x=(x0+x1)/2,y=(y0+y1)/2;
    viewDefs[option.value]={projection:'map',position:[x+40,y+(area.number===14?110:-110),65],target:[x,y,3],zoom:4,area,bounds:[x0,y0,x1,y1],fitPoints:framedModel?framedModel.fitPointsXYZMetres.map(point=>new T.Vector3(...point)):null};
  }
  let active='site',transition=null,dirty=true,drag=false,down=null,fullscreenFallback=false,initialized=false,viewHintLabel='Genel plan';
  addEventListener('bursa-assets-ready',()=>{dirty=true;});
  const focusedModelRegion=()=>viewDefs[active].area?.number||(['penguin','penguin-close'].includes(active)?15:null);
  function syncModelStatus(){
    const state=regionalModels.statusFor(focusedModelRegion());
    const enabled=footprints.visible,loading=enabled&&state&&['idle','loading'].includes(state.status),failed=enabled&&state?.status==='error';
    $('view-hint').textContent=viewHintLabel+(loading?' · ayrıntılar yükleniyor…':failed?' · ayrıntılar açılamadı':'');
    const status=$('region-load-status');status.hidden=!state;
    status.textContent=!state?'':!enabled?'3B ayrıntıları için Yapılar katmanını açın.':failed?'3B ayrıntıları açılamadı. Tekrar deneyebilirsiniz.':loading?'3B ayrıntıları yükleniyor…':'3B ayrıntıları hazır.';
    $('region-load-retry').hidden=!failed;
    const animalRegion=focusedModelRegion()===15;
    $('penguin-close').hidden=!animalRegion;
    $('penguin-credit').hidden=!animalRegion;
    $('penguin-status').hidden=!animalRegion;
    $('penguin-status').textContent=penguins.status()==='error'?'Penguenler açılamadı. Tekrar yükleyin.':penguins.status()==='ready'?'Afrika penguenleri · yürüyüş, yüzme ve tüy bakımı':'Penguenler hazırlanıyor…';
    $('penguin-retry').hidden=!animalRegion||penguins.status()!=='error';
  }
  $('region-load-retry').onclick=()=>{const region=focusedModelRegion();if(region)regionalModels.retry(region);};
  $('penguin-close').onclick=()=>{go('penguin-close');showLayers(false);};
  $('penguin-retry').onclick=()=>penguins.retry();
  let animalsEnabled=true;
  $('toggle-animals').onclick=()=>{animalsEnabled=!animalsEnabled;penguins.setEnabled(animalsEnabled);$('toggle-animals').setAttribute('aria-pressed',String(animalsEnabled));};
  let planOverlayOn=new URLSearchParams(location.search).get('overlay')==='1',planOpacity=55,planImageFailed=false;
  try{const stored=localStorage.getItem('bursa-zoo-plan-opacity');if(stored!==null){const saved=Number(stored);if(Number.isFinite(saved)&&saved>=0&&saved<=100)planOpacity=saved;}}catch{}
  $('plan-overlay-opacity').value=String(planOpacity);
  $('plan-overlay-opacity-value').value=planOpacity+'%';
  planOverlay.style.opacity=String(planOpacity/100);
  function syncPlanOverlay(){
    planOverlay.hidden=!planOverlayOn||planImageFailed||viewDefs[active].projection==='eye';
    $('toggle-plan-overlay').setAttribute('aria-pressed',String(planOverlayOn));
    $('plan-overlay-opacity').disabled=!planOverlayOn||planImageFailed;
    dirty=true;
  }
  planOverlayImage.addEventListener('error',()=>{
    planImageFailed=true;
    $('plan-overlay-hint').firstChild.textContent='Resmî kroki yüklenemedi. Kaynağı açmayı deneyin. ';
    syncPlanOverlay();
  });
  $('toggle-plan-overlay').addEventListener('click',()=>{planOverlayOn=!planOverlayOn;syncPlanOverlay();});
  $('plan-overlay-opacity').addEventListener('input',event=>{
    planOpacity=Number(event.target.value);
    $('plan-overlay-opacity-value').value=planOpacity+'%';
    planOverlay.style.opacity=String(planOpacity/100);
    try{localStorage.setItem('bursa-zoo-plan-opacity',String(planOpacity));}catch{}
  });
  syncPlanOverlay();
  function updatePlanOverlay(){
    if(planOverlay.hidden)return;
    // A CSS projective plane follows the metric XY frame without duplicating
    // terrain meshes or requiring cross-origin access to the official image.
    camera.updateMatrixWorld();
    const projection=new T.Matrix4().multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);
    const clip=(u,v)=>new T.Vector4(
      planImageToMetres.x[0]*u+planImageToMetres.x[1]*v+planImageToMetres.x[2],
      planImageToMetres.y[0]*u+planImageToMetres.y[1]*v+planImageToMetres.y[2],
      0,1).applyMatrix4(projection);
    const origin=clip(0,0),right=clip(1,0).sub(origin),down=clip(0,1).sub(origin);
    if(Math.abs(origin.w)<1e-8)return;
    const w=host.clientWidth/2,h=host.clientHeight/2,k=1/origin.w;
    const a=w*(right.x+right.w)*k,b=w*(down.x+down.w)*k,c=w*(origin.x+origin.w)*k;
    const d=h*(right.w-right.y)*k,e=h*(down.w-down.y)*k,f=h*(origin.w-origin.y)*k;
    const g=right.w*k,j=down.w*k;
    planOverlayImage.style.transform=`matrix3d(${a},${d},0,${g},${b},${e},0,${j},0,0,1,0,${c},${f},0,1)`;
  }
  let perspective=45;
  try{const stored=localStorage.getItem('bursa-zoo-site-perspective');if(stored!==null){const saved=Number(stored);if(Number.isFinite(saved)&&saved>=0&&saved<=100)perspective=saved;}}catch{}
  const requestedPerspective=Number(new URLSearchParams(location.search).get('perspective'));
  if(new URLSearchParams(location.search).has('perspective')&&Number.isFinite(requestedPerspective)&&requestedPerspective>=0&&requestedPerspective<=100)perspective=requestedPerspective;
  $('perspective').value=String(perspective);
  $('perspective-value').value=perspective+'%';
  const overviewFov=36;
  const overviewTilt=(name,narrow)=>T.MathUtils.degToRad((name==='cage-top'?28:name==='site'?(narrow?38:60):name==='cage'?72:68)*Math.sqrt(perspective/100));
  const overviewFrame=(name,narrow,value)=>name==='site'&&!narrow?1+.3*Math.max(0,1-value/45):1;
  const overviewHeading=(name,narrow)=>{
    const v=viewDefs[name],position=narrow&&v.mobilePosition?v.mobilePosition:v.position,target=narrow&&v.mobileTarget?v.mobileTarget:v.target;
    return new T.Vector3(position[0]-target[0],position[1]-target[1],0).normalize();
  };
  const overviewDirection=(name,narrow,heading)=>{
    // A tiny offset preserves the plan heading without a singular lookAt at Z.
    const tilt=Math.max(PLAN_TILT,overviewTilt(name,narrow));
    return new T.Vector3(heading.x*Math.sin(tilt),heading.y*Math.sin(tilt),Math.cos(tilt));
  };
  const viewSpan=(subject)=>subject.isOrthographicCamera?(subject.top-subject.bottom)/subject.zoom:2*subject.position.distanceTo(controls.target)*Math.tan(T.MathUtils.degToRad(subject.fov)/2)/subject.zoom;
  function setOverviewPerspective(previousPerspective){
    if(viewDefs[active].projection==='eye')return;
    transition=null;
    const narrow=host.clientWidth<760,target=controls.target.clone(),offset=camera.position.clone().sub(target);
    const heading=new T.Vector3(offset.x,offset.y,0);
    if(previousPerspective===0||heading.lengthSq()<Math.pow(offset.length()*1e-4,2))heading.copy(overviewHeading(active,narrow));
    else heading.normalize();
    const direction=overviewDirection(active,narrow,heading);
    const span=viewSpan(camera)*overviewFrame(active,narrow,perspective)/overviewFrame(active,narrow,previousPerspective),next=perspective===0?mapCamera:siteCamera;
    if(next===mapCamera){next.zoom=(next.top-next.bottom)/span;next.position.copy(target).addScaledVector(direction,Math.max(800,span));}
    else{next.fov=overviewFov;next.zoom=1;next.position.copy(target).addScaledVector(direction,span/(2*Math.tan(T.MathUtils.degToRad(next.fov)/2)));}
    next.updateProjectionMatrix();camera=next;bindOrbit(target);dirty=true;
  }
  function resize(){
    const w=host.clientWidth,h=host.clientHeight;
    mapCamera.left=-420;mapCamera.right=420;mapCamera.top=420*h/w;mapCamera.bottom=-420*h/w;mapCamera.updateProjectionMatrix();
    siteCamera.aspect=w/h;siteCamera.updateProjectionMatrix();eyeCamera.aspect=w/h;eyeCamera.updateProjectionMatrix();renderer.setSize(w,h,false);
    if(initialized)go(active,false);dirty=true;
  }
  new ResizeObserver(resize).observe(host);resize();
  function go(name,animate=true){
    const v=viewDefs[name];if(!v)return;
    const shadowExtent=v.bounds?Math.max(65,(v.bounds[2]-v.bounds[0])*.7,(v.bounds[3]-v.bounds[1])*.7):name==='site'?430:name==='penguin-close'?18:name==='penguin'?65:name==='entry'||name==='inside'?85:185;
    const shadowCentre=v.area?new T.Vector3(...v.target):name==='site'?new T.Vector3(40,20,0):['penguin','penguin-close'].includes(name)?new T.Vector3(-14,134,0):new T.Vector3(CAGE.x,CAGE.y,0);
    sun.shadow.normalBias=name==='penguin-close'?.005:.06;
    sun.target.position.copy(shadowCentre);sun.position.copy(shadowCentre).add(new T.Vector3(...WOODLAND_LIGHT.direction));
    sun.shadow.camera.left=-shadowExtent;sun.shadow.camera.right=shadowExtent;
    sun.shadow.camera.top=shadowExtent;sun.shadow.camera.bottom=-shadowExtent;sun.shadow.camera.updateProjectionMatrix();
    const previous=camera;active=name;camera=v.projection==='eye'?eyeCamera:perspective>0?siteCamera:mapCamera;
    const narrow=host.clientWidth<760;
    const heading=v.projection==='eye'?null:overviewHeading(name,narrow);
    document.querySelectorAll('[data-view]').forEach(b=>{const on=b.dataset.view===name;b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on));});
    $('perspective').disabled=v.projection==='eye';
    $('perspective-hint').textContent=name==='penguin-close'?'Penguen yakın görünümünde göz hizası sabittir.':v.projection==='eye'?'Giriş ve İç görünümlerinde göz hizası sabittir.':name==='penguin'?'Penguen alanının bakış açısını değiştirir.':'Alan, Dış ve Üst görünümlerinde uygulanır.';
    if(v.area)$('perspective-hint').textContent='Seçili bölgenin bakış açısını değiştirir.';
    const position=narrow&&v.mobilePosition?v.mobilePosition:v.position;
    const next=new T.Vector3(...position),target=new T.Vector3(...(narrow&&v.mobileTarget?v.mobileTarget:v.target));
    if(camera===eyeCamera){camera.fov=narrow&&v.mobileFov?v.mobileFov:56;camera.updateProjectionMatrix();}
    const factor=narrow?(name==='site'?2:name==='cage'||name==='cage-top'||name==='penguin'?2.2:1):1;
    const frameScale=heading?overviewFrame(name,narrow,perspective):1;
    const regionSpan=v.bounds?Math.max(v.bounds[3]-v.bounds[1]+30,(v.bounds[2]-v.bounds[0]+30)*host.clientHeight/host.clientWidth)*1.25:null;
    let zoom=camera===siteCamera?1:regionSpan?(mapCamera.top-mapCamera.bottom)/regionSpan:v.zoom*factor/frameScale;
    if(heading){
      const span=regionSpan||(mapCamera.top-mapCamera.bottom)/(v.zoom*factor)*frameScale;
      const direction=overviewDirection(name,narrow,heading);
      if(camera===siteCamera){camera.fov=overviewFov;camera.updateProjectionMatrix();next.copy(target).addScaledVector(direction,span/(2*Math.tan(T.MathUtils.degToRad(camera.fov)/2)));}
      else next.copy(target).addScaledVector(direction,Math.max(800,span));
      if(v.fitPoints?.length){
        // A long diagonal hut row occupies much less screen width than the
        // corners of its overall XY box. Fit individual mesh boxes instead.
        const right=new T.Vector3().crossVectors(camera.up,direction).normalize();
        const up=new T.Vector3().crossVectors(direction,right).normalize();
        const tangent=Math.tan(T.MathUtils.degToRad(overviewFov)/2),aspect=host.clientWidth/host.clientHeight;
        let distance=8,screenSpan=1;
        for(const point of v.fitPoints){
          const p=point.clone().sub(target),x=Math.abs(p.dot(right)),y=Math.abs(p.dot(up));
          distance=Math.max(distance,p.dot(direction)+1.2*x/(tangent*aspect),p.dot(direction)+1.5*y/tangent);
          screenSpan=Math.max(screenSpan,2.4*x/aspect,3*y);
        }
        if(camera===siteCamera)next.copy(target).addScaledVector(direction,distance);
        else{zoom=(mapCamera.top-mapCamera.bottom)/screenSpan;next.copy(target).addScaledVector(direction,800);}
      }
    }
    if(!animate||previous!==camera||v.projection==='eye'||matchMedia('(prefers-reduced-motion: reduce)').matches){
      transition=null;camera.position.copy(next);camera.zoom=zoom;camera.updateProjectionMatrix();bindOrbit(target,v.projection==='eye');dirty=true;
    }else{
      // A new control instance discards inertia from the previous view.
      bindOrbit(controls.target.clone(),v.projection==='eye');
      transition={from:camera.position.clone(),to:next,fromTarget:controls.target.clone(),toTarget:target,z0:camera.zoom,z1:zoom,start:performance.now()};
    }
    $('map-guide').hidden=name!=='site';
    syncPlanOverlay();
    const hints={site:'Genel plan',cage:'Su Kuşları Kafesi · dış görünüm',entry:'Su Kuşları Kafesi · giriş',inside:'Su Kuşları Kafesi · iç görünüm','cage-top':'Su Kuşları Kafesi · üstten',penguin:'Penguen · havuz ve kıyı','penguin-close':'Afrika penguenleri · yakından'};
    viewHintLabel=v.area?v.area.number+' · '+v.area.name:hints[name];syncModelStatus();
    $('region-select').value=v.area?name:focusedModelRegion()===15?'region-15':'site';
    $('region-note').textContent=v.area?(v.area.isModelStarted?'3B çalışma başladı. ':'Henüz ayrıntılı model yok. ')+(v.area.anchors.length>1?v.area.anchors.length+' kroki noktası gösteriliyor. ':'')+'Konum krokiye göre yaklaşık; numara alan sınırı değildir.':'43 alan listeleniyor. 40 · Çocuk Oyun Alanı’nın konumu Eylül krokisinde henüz doğrulanamadı.';
    const modelKey=name==='penguin-close'?'penguin-animal':v.area?{9:'habes',11:'lemur',12:'savanna-platform',13:'african-cafe',14:'african-village',15:'penguin',29:'bear-pool',30:'turk-koyu',31:'dome',32:'dome'}[v.area.number]:null;
    $('region-model-link').hidden=!modelKey;
    $('region-model-link').textContent=name==='penguin-close'?'Pengueni ve animasyonlarını incele':'3B modeli yakından incele';
    if(modelKey)$('region-model-link').href='./model-review/?model='+modelKey;
  }
  $('region-select').addEventListener('change',event=>go(event.target.value));
  document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>go(b.dataset.view)));
  $('reset').onclick=()=>go('site');$('zoom-in').onclick=()=>{transition=null;camera.zoom=Math.min(18,camera.zoom*1.25);camera.updateProjectionMatrix();dirty=true;};$('zoom-out').onclick=()=>{transition=null;camera.zoom=Math.max(.55,camera.zoom/1.25);camera.updateProjectionMatrix();dirty=true;};
  $('perspective').addEventListener('input',e=>{
    const previousPerspective=perspective;
    perspective=Number(e.target.value);$('perspective-value').value=perspective+'%';
    try{localStorage.setItem('bursa-zoo-site-perspective',String(perspective));}catch{}
    setOverviewPerspective(previousPerspective);
  });
  const markers=[];for(const [key,h] of Object.entries(hotspots)){const b=document.createElement('button');b.className='marker'+(h.primary?' primary':'');b.textContent=h.label;b.onclick=()=>go(h.view);$('markers').append(b);markers.push({button:b,view:'site',point:new T.Vector3(h.x,h.y,h.z)});}
  for(const area of R.areas)for(const anchor of area.anchors){const b=document.createElement('span');b.className='marker region-pin';b.textContent=area.number;b.setAttribute('aria-label',area.number+' · '+area.name);$('markers').append(b);markers.push({button:b,view:'region-'+area.number,point:new T.Vector3(...anchor.localXYMetres,1)});}
  function updateMarkers(){const w=host.clientWidth,h=host.clientHeight;for(const m of markers){const p=m.point.clone().project(camera);m.button.style.left=((p.x+1)*w/2)+'px';m.button.style.top=((-p.y+1)*h/2)+'px';m.button.hidden=active!==m.view||p.z>1||p.z< -1||p.x>1.1||p.x< -1.1||p.y>1.1||p.y< -1.1;}}
  function updateMapGuide(){
    if(active!=='site')return;
    const at=controls.target.clone().project(camera),north=controls.target.clone().add(new T.Vector3(0,100,0)).project(camera);
    $('north-arrow').style.transform='rotate('+Math.atan2(north.x-at.x,north.y-at.y)*180/Math.PI+'deg)';
    const east=controls.target.clone().add(new T.Vector3(100,0,0)).project(camera);
    const pixelsPerMetre=Math.hypot((east.x-at.x)*host.clientWidth/2,(east.y-at.y)*host.clientHeight/2)/100;
    const scaleMetres=[10,20,25,50,100,200,500,1000].reduce((best,value)=>Math.abs(value*pixelsPerMetre-95)<Math.abs(best*pixelsPerMetre-95)?value:best);
    $('scale-rule').style.width=scaleMetres*pixelsPerMetre+'px';
    $('scale-label').textContent=(perspective?'≈ ':'')+scaleMetres+' m';
  }
  renderer.domElement.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY];drag=false;});
  renderer.domElement.addEventListener('pointermove',e=>{if(down&&Math.hypot(e.clientX-down[0],e.clientY-down[1])>6)drag=true;});
  renderer.domElement.addEventListener('pointerup',e=>{
    if(!down||drag){down=null;return;}down=null;
    const r=renderer.domElement.getBoundingClientRect(),p=new T.Vector2(2*(e.clientX-r.left)/r.width-1,-2*(e.clientY-r.top)/r.height+1);
    const ray=new T.Raycaster();ray.setFromCamera(p,camera);
    if(active==='site'&&ray.intersectObject(cage,true).length)go('entry');
  });
  for(const [id,group] of [['toggle-trees',trees],['toggle-buildings',footprints]])$(id).onclick=()=>{group.visible=!group.visible;$(id).setAttribute('aria-pressed',String(group.visible));syncModelStatus();dirty=true;};
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
  const profileRendering=new URLSearchParams(location.search).get('profile')==='1';
  let captureRequested=false;
  $('capture-scene').hidden=new URLSearchParams(location.search).get('capture')!=='1';
  $('capture-scene').onclick=()=>{captureRequested=true;dirty=true;};
  const renderSamples=[];let profileWarmup=0;
  if(profileRendering)renderer.info.autoReset=false;
  function frame(now){
    requestAnimationFrame(frame);
    if(transition){
      const t=Math.min(1,(now-transition.start)/850),e=t*t*(3-2*t);
      camera.position.lerpVectors(transition.from,transition.to,e);controls.target.lerpVectors(transition.fromTarget,transition.toTarget,e);
      camera.zoom=transition.z0+(transition.z1-transition.z0)*e;camera.updateProjectionMatrix();if(t>=1)transition=null;dirty=true;
    }
    controls.update();
    if(penguins.update(now,camera,host.clientHeight,focusedModelRegion()))dirty=true;
    if(dirty){
      const began=profileRendering?performance.now():0;if(profileRendering)renderer.info.reset();
      regionalModels.update(camera,host.clientHeight,focusedModelRegion());forest?.prepare(camera,host.clientHeight);prepareWater(camera);
      finishing.render(camera);updatePlanOverlay();updateMarkers();updateMapGuide();dirty=false;
      if(captureRequested){
        captureRequested=false;
        renderer.domElement.toBlob(blob=>{if(!blob)return;const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='bursa-penguins-webgl.png';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);},'image/png');
      }
      if(profileRendering&&profileWarmup++>=8&&renderSamples.length<48){
        renderSamples.push({cpuMs:performance.now()-began,calls:renderer.info.render.calls,triangles:renderer.info.render.triangles});
        if(renderSamples.length===24||renderSamples.length===48){
          const sorted=renderSamples.map(s=>s.cpuMs).sort((a,b)=>a-b),average=key=>renderSamples.reduce((sum,s)=>sum+s[key],0)/renderSamples.length;
          console.info('Local render profile',JSON.stringify({view:active,frames:renderSamples.length,p95CpuSubmissionMs:sorted[Math.floor(sorted.length*.95)],meanDrawCalls:average('calls'),meanTriangles:average('triangles'),textures:renderer.info.memory.textures,gpuTimingMeasured:false}));
        }
      }
    }
  }
  const params=new URLSearchParams(location.search),focus=params.get('focus'),region='region-'+params.get('region');
  go(viewDefs[region]?region:viewDefs[focus]?focus:'site',false);
  await waitForSceneTextures();
  initialized=true;$('loading').remove();requestAnimationFrame(frame);void loadForest();
}
