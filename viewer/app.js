import * as T from 'three';
import {createExplorerCamera} from './explorer-camera.js?v=20261016au';
import {createExplorerLabels} from './explorer-labels.js?v=20261016aq';
import {createTouchCue} from './touch-cue.js?v=20261016au';
import {createAnimalInfo} from './animal-info.js?v=20261016au';
import {ANIMAL_PROFILES} from './animal-profiles.js?v=20261016au';
import {colonyView,animalFocusView,animalTarget as targetForAnimal} from './animal-views.js?v=20261016au';
import {createPenguins} from './penguins.js?v=20261016aq';
import {createRhinos} from './rhinos.js?v=20261016au';
import {createGiraffes} from './giraffes.js?v=20261016au';
import {createAviaryBirds} from './aviary-birds.js?v=20261016au';
import {createRegionalModels} from './region-models.js?v=20261016aq';
import {createSite,CAGE,waitForSceneTextures} from './model.js?v=20261015al';
import {createSceneFinishing} from './scene-effects.js?v=20261015af';
import {WOODLAND_LIGHT} from './lighting.js?v=20261015af';

const $=id=>document.getElementById(id);
try{await start();}catch(error){
  console.error(error);
  const loading=$('loading'),retry=$('load-retry');
  loading.textContent='Hayvanat bahçesi yüklenemedi.';loading.classList.add('load-error');
  retry.hidden=false;retry.onclick=()=>location.reload();loading.append(retry);
}

async function start(){
  const files=['site-data','current-plan-data','surface-layers','building-shell','landscape-layout','scene-model-catalog','ground-material-layout'];
  const data=await Promise.all(files.map(async file=>{const r=await fetch('./'+file+'.json',{cache:'no-store'});if(!r.ok)throw Error(file+' yüklenemedi');return r.json();}));
  const [D,P,S,B,L,M,G]=data,host=$('stage'),scene=new T.Scene();
  scene.background=new T.Color('#d8e3d7');
  const camera=new T.PerspectiveCamera(36,1,.12,2500);camera.up.set(0,0,1);
  const renderer=new T.WebGLRenderer({antialias:true,alpha:false});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=WOODLAND_LIGHT.exposure;
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;$('canvas').append(renderer.domElement);
  scene.add(new T.HemisphereLight(WOODLAND_LIGHT.sky,WOODLAND_LIGHT.ground,WOODLAND_LIGHT.hemisphere));
  const sun=new T.DirectionalLight(WOODLAND_LIGHT.sun,WOODLAND_LIGHT.sunIntensity);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
  sun.shadow.camera.near=1;sun.shadow.camera.far=900;sun.shadow.bias=-.00018;sun.shadow.intensity=WOODLAND_LIGHT.shadowIntensity;sun.shadow.radius=WOODLAND_LIGHT.shadowRadius;scene.add(sun,sun.target);
  const {site,cage,trees,footprints,forestCandidates,prepareWater}=createSite(D,P,S,B,L,G);scene.add(site);
  const finishing=createSceneFinishing(renderer,scene,camera);
  let dirty=true,mode='overview',habitat=null,selected=null,follow=false,forest=null,previousFrame=0,frames=0,initialized=false,autoFrame=true;
  const params=new URLSearchParams(location.search),debug=params.get('profile')==='1';
  const changed=()=>{dirty=true;};
  const regionalModels=createRegionalModels(M,footprints,()=>{dirty=true;syncStatus();});
  const runtimes={
    penguin:createPenguins(footprints,changed,{reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,requireHabitat:()=>regionalModels.statusForKey('penguinPool')?.status==='ready'}),
    rhino:createRhinos(footprints,changed,{reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,requireHabitat:()=>regionalModels.statusForKey('rhinoHabitat')?.status==='ready'}),
    giraffe:createGiraffes(footprints,changed,{reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,requireHabitat:()=>regionalModels.statusForKey('giraffeHabitat')?.status==='ready'}),
    aviary:createAviaryBirds(footprints,changed,{reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,anchor:CAGE,surfaceData:S}),
  };
  const animalKeys={penguinPool:'penguin',rhinoHabitat:'rhino',giraffeHabitat:'giraffe'};
  const titles={penguinPool:'Penguenler',rhinoHabitat:'Gergedanlar',giraffeHabitat:'Zürafalar',bearPool:'Boz Ayı Havuzu',habesIsland:'Habeş Maymunu Adası',turkishVillage:'Türk Köyü',savannaPlatform:'Savanna Ahşap Yapı',lemurIsland:'Lemur Adası',africanVillage:'Afrika Köyü',africanCafe:'Afrika Kafe'};
  const habitats=M.models.map(model=>{
    const [min,max]=model.boundsXYZMetres;
    return {key:model.key,label:titles[model.key]||model.name,region:model.regions[0],animal:animalKeys[model.key],bounds:[min,max],
      point:[(min[0]+max[0])/2,(min[1]+max[1])/2,max[2]+1.5],priority:animalKeys[model.key]?3:1};
  });
  habitats.unshift({key:'aviary',label:'Su Kuşları Kafesi',region:32,animal:'aviary',point:[CAGE.x,CAGE.y,CAGE.height+2],priority:4});
  const navigation=createExplorerCamera(camera,renderer.domElement,changed,()=>{setFollow(false);autoFrame=false;dismissHint();clearHover();},moving=>{host.dataset.cameraState=moving?'moving':'resting';});
  const labels=createExplorerLabels($('scene-labels'),item=>item.kind==='habitat'?openHabitat(item.habitat):openAnimal(item.index));
  const animalInfo=createAnimalInfo($('animal-info'),$('animal-announcement'));
  const touchCue=createTouchCue($('touch-cue'));
  const renderWidth=()=>$('canvas').clientWidth;
  function showAnimalInfo(key){host.classList.toggle('animal-discovery',Boolean(ANIMAL_PROFILES[key]));animalInfo.show(key);resize(false);}
  function currentRuntime(){return habitat?.animal?runtimes[habitat.animal]:null;}
  function setFollow(value){follow=value;host.dataset.cameraTracking=value?habitat.animal:'off';}
  function region(){return habitat?.region||null;}
  function dismissHint(){$('interaction-hint').hidden=true;}
  function positionHint(){
    const bar=document.querySelector('.topbar').getBoundingClientRect();
    $('interaction-hint').style.top=(host.clientWidth>1000?bar.top+24:bar.bottom+10)+'px';
    $('animal-info').style.top=host.clientWidth<=760||host.clientHeight<=450?'':bar.bottom+18+'px';
  }
  function hint(text){$('interaction-hint').textContent=text;$('interaction-hint').hidden=false;positionHint();}
  function syncStatus(){
    const state=habitat&&habitat.key!=='aviary'?regionalModels.statusForKey(habitat.key):null,runtime=currentRuntime();
    const loading=state&&['idle','loading'].includes(state.status)||runtime&&['idle','loading'].includes(runtime.status());
    const failed=state?.status==='error'||runtime?.status()==='error';
    const text=(selected?currentRuntime().animals()[selected.index]?.label||habitat.label:habitat?.label||'Genel plan')+(loading?' · hazırlanıyor…':failed?' · yüklenemedi':'');
    if($('view-hint').textContent!==text)$('view-hint').textContent=text;
    $('load-retry').hidden=!failed;
  }
  function refreshLabels(){
    const animals=mode!=='overview'?(currentRuntime()?.animals()||[]):[];
    let items=[];
    if(mode==='overview')items=habitats.filter(h=>h.animal).map(h=>({id:h.key,label:h.label,accessibleLabel:h.label+' yaşam alanına yaklaş',point:h.point,priority:h.priority,kind:'habitat',habitat:h}));
    else items=animals.map(a=>({
      id:'animal-'+a.index,index:a.index,label:'',silent:true,
      accessibleLabel:a.label+' '+(a.index+1)+(a.selected?' · davranışını değiştir':' · yakından izle'),
      point:a.point,height:a.height,selected:a.selected,visible:a.visible,kind:'animal',
    }));
    labels.sync(items);
    const topInset=Math.max(document.querySelector('.topbar').getBoundingClientRect().bottom,$('interaction-hint').hidden?0:$('interaction-hint').getBoundingClientRect().bottom)+8;
    labels.update(camera,renderWidth(),host.clientHeight,topInset);
  }
  function shadowAt(target,extent,close=false){
    sun.shadow.normalBias=close?.005:.06;sun.target.position.set(...target);sun.position.copy(sun.target.position).add(new T.Vector3(...WOODLAND_LIGHT.direction));
    Object.assign(sun.shadow.camera,{left:-extent,right:extent,top:extent,bottom:-extent});sun.shadow.camera.updateProjectionMatrix();
  }
  function sitePose(){
    const narrow=host.clientWidth<760,target=narrow?[6.5,50.7,0]:[18,-6,0],heading=new T.Vector3(...(narrow?[-172.5,-50.7,0]:[.25,-1,0])).normalize();
    const tilt=T.MathUtils.degToRad(narrow?25.5:40.25),span=840*host.clientHeight/host.clientWidth/(.82*(narrow?2:1)),distance=span/(2*Math.tan(T.MathUtils.degToRad(18)))*(narrow?1:.85);
    return {position:[target[0]+heading.x*Math.sin(tilt)*distance,target[1]+heading.y*Math.sin(tilt)*distance,Math.cos(tilt)*distance],target,fov:36};
  }
  function habitatPose(h){
    const [min,max]=h.bounds,target=[(min[0]+max[0])/2,(min[1]+max[1])/2,1.5],direction=new T.Vector3(.42,-.8,.62).normalize();
    const right=new T.Vector3().crossVectors(camera.up,direction).normalize(),up=new T.Vector3().crossVectors(direction,right),aspect=host.clientWidth/host.clientHeight,tan=Math.tan(T.MathUtils.degToRad(21));
    let distance=15;
    for(const x of [min[0],max[0]])for(const y of [min[1],max[1]])for(const z of [0,max[2]]){
      const p=new T.Vector3(x-target[0],y-target[1],z-target[2]);distance=Math.max(distance,p.dot(direction)+1.2*Math.abs(p.dot(right))/(tan*aspect),p.dot(direction)+1.35*Math.abs(p.dot(up))/tan);
    }
    return {position:new T.Vector3(...target).addScaledVector(direction,distance).toArray(),target,fov:42};
  }
  function clearAnimals(){touchCue.hide();for(const runtime of Object.values(runtimes))runtime.setInteractive(false);selected=null;setFollow(false);$('animal-announcement').textContent='';showAnimalInfo(null);}
  function overview(animate=true){
    clearAnimals();mode='overview';habitat=null;autoFrame=true;
    $('back').hidden=true;hint('Bir yaşam alanına dokun.');shadowAt([40,20,0],430);
    navigation.flyTo(sitePose(),{animate});syncStatus();dirty=true;
  }
  function openHabitat(h,animate=true){
    clearAnimals();habitat=h;mode='habitat';autoFrame=true;
    currentRuntime()?.setInteractive(true);
    $('back').hidden=false;$('back-label').textContent='Genel plana dön';$('back').setAttribute('aria-label','Genel plana dön');
    if(h.animal){
      showAnimalInfo(h.animal);animalInfo.update(null);dismissHint();
      currentRuntime().setAutonomous(true);shadowAt(h.point,h.animal==='aviary'?50:h.animal==='giraffe'?55:35,true);
      navigation.flyTo(colonyPose(),{animate});syncStatus();dirty=true;return;
    }
    hint('Sürükleyerek yaşam alanını keşfet.');
    shadowAt(h.point,h.key==='aviary'?95:Math.max(35,(h.bounds[1][0]-h.bounds[0][0])*.7,(h.bounds[1][1]-h.bounds[0][1])*.7));
    navigation.flyTo(habitatPose(h),{animate});syncStatus();dirty=true;
  }
  function animalTarget(animal){return targetForAnimal(habitat.animal,animal,host.clientWidth);}
  function colonyPose(){return colonyView(habitat.animal,currentRuntime().animals(),renderWidth(),host.clientHeight,host.clientWidth<760,CAGE);}
  function animalPose(animal){return animalFocusView(habitat.animal,animal,renderWidth(),host.clientHeight,host.clientWidth<760,CAGE);}
  function openAnimal(index,animate=true){
    const runtime=currentRuntime();if(!runtime)return;
    const animal=runtime.animals().find(a=>a.index===index);if(!animal)return;autoFrame=true;
    if(!runtime.observe(index)||!runtime.tap(index))return;
    touchCue.complete();
    mode='animal';selected={index};setFollow(animal.water||['rhino','giraffe'].includes(habitat.animal));dismissHint();
    const profile=ANIMAL_PROFILES[habitat.animal],detail=runtime.interaction().detail;
    $('back-label').textContent=profile.back;$('back').setAttribute('aria-label',profile.backLabel);positionHint();
    animalInfo.update(detail);
    shadowAt(animal.point,habitat.animal==='giraffe'?55:habitat.animal==='aviary'?50:habitat.animal==='rhino'?42:20,true);
    navigation.flyTo(animalPose(animal),{animate});syncStatus();dirty=true;
  }
  $('back').onclick=()=>{dismissHint();if(mode==='animal')openHabitat(habitat);else overview();};
  $('load-retry').onclick=()=>{if(habitat){regionalModels.retry(habitat.region);currentRuntime()?.retry();dirty=true;}};
  let down=null,dragging=false,hoverAt=0;
  const pointer=new T.Vector2(),ray=new T.Raycaster();
  function cast(event){const r=renderer.domElement.getBoundingClientRect();pointer.set(2*(event.clientX-r.left)/r.width-1,1-2*(event.clientY-r.top)/r.height);ray.setFromCamera(pointer,camera);}
  function clearHover(){renderer.domElement.style.cursor='grab';labels.hover(null);}
  renderer.domElement.addEventListener('pointerdown',event=>{
    if(event.isPrimary&&event.button===0&&!down){down={id:event.pointerId,x:event.clientX,y:event.clientY};dragging=false;}else{down=null;dragging=true;}
  });
  renderer.domElement.addEventListener('pointermove',event=>{
    if(down&&Math.hypot(event.clientX-down.x,event.clientY-down.y)>6){dragging=true;clearHover();}
    if(down||event.pointerType!=='mouse'||performance.now()-hoverAt<100||mode==='overview')return;
    hoverAt=performance.now();cast(event);const index=currentRuntime()?.pick(ray,camera,host.clientHeight,{precise:false})??null;
    renderer.domElement.style.cursor=index===null?'grab':'pointer';labels.hover(index===null?null:'animal-'+index);
  });
  renderer.domElement.addEventListener('pointerleave',clearHover);
  renderer.domElement.addEventListener('pointercancel',()=>{down=null;dragging=false;clearHover();});
  renderer.domElement.addEventListener('pointerup',event=>{
    const tap=down&&!dragging&&event.pointerId===down.id&&event.button===0;down=null;if(!tap)return;
    cast(event);
    if(mode!=='overview'){const index=currentRuntime()?.pick(ray,camera,host.clientHeight);if(index!==null&&index!==undefined)openAnimal(index);return;}
    if(ray.intersectObject(cage,true).length){openHabitat(habitats[0]);return;}
    const key=regionalModels.pick(ray);if(key){const h=habitats.find(h=>h.key===key&&h.animal);if(h)openHabitat(h);}
  });
  document.addEventListener('keydown',event=>{
    if(event.key!=='Escape'||document.fullscreenElement||fullscreenFallback)return;
    if(mode==='animal')openHabitat(habitat);else if(mode==='habitat')overview();
  });
  let fullscreenFallback=false;
  function syncFull(on){$('fullscreen').setAttribute('aria-pressed',String(on));$('fullscreen').setAttribute('aria-label',on?'Tam ekrandan çık':'Tam ekran');dirty=true;}
  $('fullscreen').onclick=async()=>{
    if(document.fullscreenElement===host){await document.exitFullscreen();return;}
    if(fullscreenFallback){host.classList.remove('fallback-fullscreen');fullscreenFallback=false;syncFull(false);return;}
    try{await host.requestFullscreen();syncFull(true);}catch{host.classList.add('fallback-fullscreen');fullscreenFallback=true;syncFull(true);}
  };
  document.addEventListener('fullscreenchange',()=>syncFull(document.fullscreenElement===host));
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&fullscreenFallback){host.classList.remove('fallback-fullscreen');fullscreenFallback=false;syncFull(false);}});
  function resize(reframe=true){
    const w=renderWidth(),h=host.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false);
    positionHint();
    if(reframe&&initialized&&autoFrame&&!navigation.inFlight()){
      const animal=selected&&currentRuntime()?.animals().find(a=>a.index===selected.index);
      navigation.flyTo(animal?animalPose(animal):habitat?.animal?colonyPose():habitat?habitatPose(habitat):sitePose(),{animate:false});
    }
    dirty=true;
  }
  new ResizeObserver(()=>resize()).observe(host);resize();
  const forestMode=params.get('forest');
  if(['1','2'].includes(forestMode))import('./forest.js?v=20261015af').then(async({createForest})=>{forest=await createForest(forestCandidates,renderer,forestMode==='2'?'impostor':'mesh');trees.add(forest.group);dirty=true;}).catch(error=>console.warn('Ağaç denemesi açılamadı.',error));
  addEventListener('bursa-assets-ready',changed);
  let captureRequested=false;
  $('capture-scene').hidden=params.get('capture')!=='1';$('capture-scene').onclick=()=>{captureRequested=true;dirty=true;};
  let lastProfile=0,lastFrames=0,lastPoses=0;
  function frame(now){
    requestAnimationFrame(frame);const dt=previousFrame?(now-previousFrame)/1000:1/60;previousFrame=now;
    navigation.update(now);
    if(dirty)regionalModels.update(camera,host.clientHeight,region());
    for(const runtime of Object.values(runtimes))if(runtime.update(now,camera,host.clientHeight,region()))dirty=true;
    touchCue.update(currentRuntime()?.animals()||[],camera,renderWidth(),host.clientHeight,now,mode==='habitat'&&!navigation.inFlight()&&(host.clientWidth<760||host.clientHeight<450)&&!document.hidden);
    if(follow&&selected&&!navigation.inFlight()&&!document.hidden){
      const animal=currentRuntime().animals().find(a=>a.index===selected.index);
      if(animal)navigation.follow(animalTarget(animal),dt);
    }
    if(dirty){
      forest?.prepare(camera,host.clientHeight);prepareWater(camera);finishing.render(camera);camera.updateMatrixWorld();refreshLabels();syncStatus();animalInfo.update(currentRuntime()?.interaction().detail);dirty=false;frames++;
      if(captureRequested){captureRequested=false;renderer.domElement.toBlob(blob=>{if(!blob)return;const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='bursa-atlas-explore-'+mode+'.png';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);},'image/png');}
    }
    if(debug&&now-lastProfile>=5000){const snapshots=Object.fromEntries(Object.entries(runtimes).map(([key,runtime])=>[key,runtime.getDebugSnapshot()])),poses=Object.values(snapshots).reduce((n,s)=>n+s.stats.poseUpdates,0);
      console.info('Local explorer profile',JSON.stringify({mode,habitat:habitat?.key,renderedFrames:frames-lastFrames,poseUpdates:poses-lastPoses,activeAnimals:Object.values(snapshots).flatMap(s=>s.actors).filter(a=>a.active).length,intervalMs:now-lastProfile,gpuTimingMeasured:false}));
      lastFrames=frames;lastPoses=poses;lastProfile=now;
    }
  }
  const focus=params.get('focus'),aliases={cage:'aviary',entry:'aviary',inside:'aviary','cage-top':'aviary','aviary-close':'aviary',penguin:'penguinPool','penguin-close':'penguinPool','rhino-close':'rhinoHabitat','giraffe-close':'giraffeHabitat'};
  const requested=habitats.find(h=>h.key===(params.get('area')||aliases[focus]))||habitats.find(h=>h.region===Number(params.get('region')));
  if(requested)openHabitat(requested,false);else overview(false);
  await waitForSceneTextures();initialized=true;resize();$('loading').remove();requestAnimationFrame(frame);
}
