import * as T from 'three';
import {GLTFLoader} from './vendor/loaders/GLTFLoader.js';
import {clone} from './vendor/utils/SkeletonUtils.js';
import {createPenguinInteraction,groundOffset,transitionGround} from './penguin-motion.js?v=20261016aq';
import {chooseDifferent} from './animal-interaction.js?v=20261015ao';

export function createPenguins(parent,onChange,options={}){
  const base=options.base||'./models/',group=new T.Group();group.name='Afrika penguenleri · Major · CC BY 4.0';group.visible=false;parent.add(group);
  const frustum=new T.Frustum(),matrix=new T.Matrix4(),centre=new T.Vector3(-10,129,0),viewCentre=new T.Vector3(),sphere=new T.Sphere();
  const box=new T.Box3(new T.Vector3(-29,120,-1.4),new T.Vector3(1,146,1));
  const debug=typeof location!=='undefined'&&new URLSearchParams(location.search).get('animaldebug')==='1';
  const reducedMotion=options.reducedMotion??false;
  const touchDevice=options.touchDevice??(typeof matchMedia!=='undefined'&&matchMedia('(pointer: coarse)').matches);
  const random=options.random||Math.random;
  let state='idle',meta=null,transitionData=null,actors=[],selected=null,enabled=true,interactive=false,lastTime=null,uiSignature='';
  let autonomous=false,observed=false,colonyTime=0,scheduleTime=null,pendingTap=null,behaviorOrder=0;
  const stats={poseUpdates:0,animatedUpdates:0,cpuMs:0,maxCpuMs:0,maxConcurrentRigs:0};

  function actorLabel(actor){return actor.bird.water?'Havuz '+(actor.bird.index-meta.landStarts.length+1):'Kıyı '+(actor.bird.index+1);}
  function focusFor(actor){
    const b=actor.bird,samples=b.samples();
    if(b.water){const height=samples.reduce((sum,s)=>sum+(s.clip==='Penguin swim'?.08:.12)*s.weight,0);return [b.x,b.y,meta.waterZ+height];}
    const height=samples.reduce((sum,s)=>sum+(s.clip==='Sleep'?.12:s.clip==='Sit1'?.24:.3)*s.weight,0);
    return [b.x,b.y,meta.groundZ+height*b.scale];
  }
  function updatePlacement(actor){
    const b=actor.bird;
    const waterOffset=b.water?b.samples().reduce((sum,s)=>sum+(s.clip==='Penguin swim'?meta.swimAnchorOffsetMetres:meta.floatAnchorOffsetMetres)*s.weight,0):0;
    actor.pivot.position.set(b.x,b.y,b.water?meta.waterZ+waterOffset*b.scale:meta.groundZ);
    actor.pivot.rotation.z=b.heading+Math.PI/2;
  }
  function applyPose(actor){
    const samples=actor.bird.samples(),wanted=[];
    let lift=0;
    for(let slot=0;slot<samples.length;slot++){
      const sample=samples[slot],key=sample.clip+':'+slot;
      let action=actor.actions.get(key);
      if(!action){
        const source=actor.clips.get(sample.clip);
        const clip=slot===0?source:new T.AnimationClip(source.name+' blend',source.duration,source.tracks);
        action=actor.mixer.clipAction(clip);actor.actions.set(key,action);
      }
      if(!action.isScheduled())action.play();
      action.enabled=true;action.paused=true;action.time=sample.time;action.setEffectiveWeight(sample.weight);wanted.push(action);
      if(!actor.bird.water)lift+=groundOffset(meta.clips,sample.clip,sample.time)*sample.weight;
    }
    for(const action of actor.scheduled)if(!wanted.includes(action))action.stop();
    if(!actor.bird.water&&samples.length===2)lift=transitionGround(transitionData,samples[0].clip,samples[1].clip,samples[0].time,samples[1].weight);
    actor.scheduled=wanted;actor.mixer.update(0);actor.rig.position.y=lift;stats.poseUpdates++;
  }
  async function load(){
    state='loading';onChange();
    try{
      const response=await fetch(base+'penguin-colony.json',{cache:'no-store'});
      if(!response.ok)throw Error('Penguen yerleşimi yüklenemedi');meta=await response.json();
      if(meta.schema!=='bursa-zoo-penguin-colony/v2'||meta.waterRoutes?.length!==meta.waterStarts.length||!Number.isFinite(meta.floatAnchorOffsetMetres))throw Error('Penguen etkileşim verisi uyumsuz');
      const [gltf,groundResponse]=await Promise.all([new GLTFLoader().loadAsync(base+meta.asset+'?v='+meta.assetSha256.slice(0,16)),fetch(base+'penguin-transitions.json',{cache:'no-store'})]);
      if(!groundResponse.ok)throw Error('Penguen geçiş verisi yüklenemedi');transitionData=await groundResponse.json();
      if(transitionData.schema!=='bursa-zoo-penguin-transition-ground/v1'||transitionData.assetSha256!==meta.assetSha256)throw Error('Penguen geçiş verisi uyumsuz');
      const clips=new Map(gltf.animations.map(clip=>[clip.name,clip]));
      for(const name of ['Idle','Shake','Preen','Sit1','Sleep','Penguin swim'])if(!clips.has(name))throw Error('Penguen klibi eksik: '+name);
      const next=[...meta.landStarts,...meta.waterStarts].map((_,index)=>{
        const rig=clone(gltf.scene),pivot=new T.Group(),axis=new T.Group(),bird=createPenguinInteraction(meta,index);
        axis.rotation.x=Math.PI/2;axis.add(rig);pivot.add(axis);pivot.scale.setScalar(bird.scale);pivot.userData.penguinIndex=index;
        rig.traverse(node=>{if(node.isMesh){node.castShadow=!bird.water;node.receiveShadow=true;node.frustumCulled=false;if(node.material.map)node.material.map.anisotropy=4;}});
        const actor={rig,pivot,bird,clips,mixer:new T.AnimationMixer(rig),actions:new Map(),scheduled:[],visible:false,previous:null,nextBehaviorAt:Infinity,behaviorOrder:0};
        updatePlacement(actor);applyPose(actor);return actor;
      });
      actors=next;group.clear();group.add(...actors.map(actor=>actor.pivot));state='ready';lastTime=null;onChange();
      if(debug)console.info('Penguin interaction asset',JSON.stringify({birds:actors.length,triangles:meta.trianglesPerBird*actors.length,independentRigs:true,sharedGeometry:true,sharedTextures:true,nearViewAutonomy:true}));
    }catch(error){state='error';console.warn('Penguen modeli yüklenemedi.',error);onChange();}
  }
  function notifyState(){
    const actor=actors[selected],signature=[selected,actor?.bird.label(),actor?.bird.activity(),actor?.bird.sleeping()].join('|');
    if(signature!==uiSignature){uiSignature=signature;onChange();}
  }
  function delay(min,max){return min+random()*(max-min);}
  function nextBehavior(actor){
    const b=actor.bird;
    if(b.water)return b.activity()==='swim'?'rest':'swim';
    if(b.sleeping())return 'look';
    const choices=['look','look','preen','notice','sleep'].filter(name=>name!==(b.activity()||actor.previous));
    return choices[Math.min(choices.length-1,Math.floor(random()*choices.length))];
  }
  function requestBehavior(actor,name){
    const accepted=actor.bird.request(name);
    if(accepted){actor.previous=name;actor.nextBehaviorAt=Infinity;actor.behaviorOrder=++behaviorOrder;lastTime=null;notifyState();}
    return accepted;
  }
  function schedule(now){
    if(!autonomous||!interactive||reducedMotion){scheduleTime=null;return;}
    colonyTime+=scheduleTime===null?0:Math.min((now-scheduleTime)/1000,.08);scheduleTime=now;
    let active=actors.filter(a=>a.visible&&a.bird.active()).length;
    // A tap takes the next available slot. At most two rigs animate together,
    // including their blend-out; a new touch never resets another rig's pose.
    if(pendingTap){
      const actor=actors[pendingTap.index];
      if(actor?.visible&&(actor.bird.active()||active<2)){
        requestBehavior(actor,pendingTap.name);
        pendingTap=null;active=actors.filter(a=>a.visible&&a.bird.active()).length;
      }
    }
    for(const actor of actors){
      if(actor.bird.active())actor.nextBehaviorAt=Infinity;
      else if(actor.nextBehaviorAt===Infinity)actor.nextBehaviorAt=colonyTime+(actor.bird.sleeping()?delay(20,40):actor.bird.water?delay(10,20):delay(6,14));
    }
    if(pendingTap)return;
    const due=actors.filter(a=>a.visible&&(!observed||a.bird.index===selected)&&!a.bird.active()&&a.nextBehaviorAt<=colonyTime).sort((a,b)=>a.nextBehaviorAt-b.nextBehaviorAt);
    for(const actor of due){if(active>=2)break;if(requestBehavior(actor,nextBehavior(actor)))active++;}
  }
  function update(now,camera,viewportHeight,region){
    camera.updateMatrixWorld();matrix.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);frustum.setFromProjectionMatrix(matrix);
    const depth=Math.max(.5,-viewCentre.copy(centre).applyMatrix4(camera.matrixWorldInverse).z);
    const pixels=camera.isOrthographicCamera?.62*viewportHeight*camera.zoom/(camera.top-camera.bottom):.62*viewportHeight*camera.zoom/(2*depth*Math.tan(T.MathUtils.degToRad(camera.fov)/2));
    let inFrame=frustum.intersectsBox(box);
    if(actors.length){
      inFrame=false;
      for(const actor of actors){
        const b=actor.bird;sphere.center.set(b.x,b.y,b.water?meta.waterZ+.03:meta.groundZ+.3*b.scale);sphere.radius=.65*b.scale;
        actor.visible=frustum.intersectsSphere(sphere);actor.pivot.visible=actor.visible;inFrame||=actor.visible;
      }
    }
    const visible=enabled&&parent.visible&&!document.hidden&&inFrame&&(region===15||pixels>=3);
    const habitat=!options.requireHabitat||options.requireHabitat();
    const nextVisible=visible&&habitat&&state==='ready',changed=group.visible!==nextVisible;group.visible=nextVisible;
    if(!visible||!habitat){lastTime=null;scheduleTime=null;return changed;}
    if(state==='idle'){void load();return changed;}if(state!=='ready')return changed;
    schedule(now);
    // Offscreen poses freeze without occupying a visible animation slot. If an
    // orbit reveals several paused rigs, resume two at a time with no catch-up.
    const active=actors.filter(actor=>actor.visible&&actor.bird.active()).sort((a,b)=>Number(b.bird.index===selected)-Number(a.bird.index===selected)||a.behaviorOrder-b.behaviorOrder).slice(0,2);
    if(!active.length){lastTime=null;return changed;}
    const interval=pixels>=24?(touchDevice||innerWidth<760?1000/30:1000/60):1000/12;
    if(lastTime!==null&&now-lastTime<interval-.5)return changed;
    const dt=lastTime===null?1/60:Math.min((now-lastTime)/1000,.08);lastTime=now;
    const began=debug?performance.now():0;
    stats.maxConcurrentRigs=Math.max(stats.maxConcurrentRigs,active.length);
    for(const actor of active){actor.bird.update(dt);updatePlacement(actor);applyPose(actor);}
    if(debug){
      const cpu=performance.now()-began;stats.cpuMs+=cpu;stats.maxCpuMs=Math.max(stats.maxCpuMs,cpu);stats.animatedUpdates++;
      if(stats.animatedUpdates===180)console.info('Penguin interaction animation profile',JSON.stringify({updates:180,meanCpuMs:stats.cpuMs/180,maxCpuMs:stats.maxCpuMs,visibleActiveRigs:active.length,gpuTimingMeasured:false}));
    }
    notifyState();return true;
  }
  function select(index,{react=true}={}){
    if(!interactive||state!=='ready'||!enabled||!parent.visible||!Number.isInteger(index)||!actors[index])return false;
    if(!autonomous&&selected!==index)for(const actor of actors)if(actor.bird.index!==index)actor.bird.cancel();
    selected=index;lastTime=null;
    const bird=actors[index].bird;
    if(react&&!reducedMotion)bird.request(bird.water?'swim':bird.sleeping()?'look':'notice');
    notifyState();return true;
  }
  function clearSelection(){
    observed=false;pendingTap=null;
    if(selected===null)return;
    actors[selected]?.bird.cancel();selected=null;lastTime=null;notifyState();
  }
  function observe(index){
    if(!select(index,{react:false}))return false;
    observed=true;pendingTap=null;
    for(const actor of actors)if(actor.bird.index!==index)actor.bird.cancel();
    onChange();return true;
  }
  function command(name){
    const actor=actors[selected];if(!interactive||!enabled||!parent.visible||!actor)return false;
    const accepted=actor.bird.request(name);
    if(accepted){lastTime=null;notifyState();}return accepted;
  }
  function pick(raycaster,camera,viewportHeight,{precise=true}={}){
    if(!interactive||!group.visible)return null;
    // Refit animated bounds only on an actual tap, never in the frame loop.
    if(precise){
      group.updateMatrixWorld(true);
      group.traverse(node=>{if(node.isSkinnedMesh){node.skeleton.update();node.computeBoundingSphere();node.computeBoundingBox();}});
      for(const hit of raycaster.intersectObject(group,true)){
        let node=hit.object;while(node&&node!==group){const index=node.userData.penguinIndex;if(Number.isInteger(index)&&actors[index].visible)return index;node=node.parent;}
      }
    }
    let nearest=null,best=18;
    for(const actor of actors){
      if(!actor.visible)continue;
      sphere.center.set(...focusFor(actor));
      const z=-viewCentre.copy(sphere.center).applyMatrix4(camera.matrixWorldInverse).z;if(z<=0)continue;
      const scale=camera.isOrthographicCamera?viewportHeight*camera.zoom/(camera.top-camera.bottom):viewportHeight*camera.zoom/(2*z*Math.tan(T.MathUtils.degToRad(camera.fov)/2));
      const distance=Math.sqrt(raycaster.ray.distanceSqToPoint(sphere.center))*scale;
      if(distance<best){best=distance;nearest=actor.bird.index;}
    }
    return nearest;
  }
  function interaction(){
    const actor=actors[selected];
    return {state,enabled:enabled&&parent.visible,selected,animals:actors.map(a=>({index:a.bird.index,label:actorLabel(a),water:a.bird.water})),
      detail:actor?{label:actorLabel(actor),water:actor.bird.water,status:actor.bird.label(),sleeping:actor.bird.sleeping(),activity:actor.bird.activity()}:null};
  }
  function tap(index){
    if(autonomous){
      if(!select(index,{react:false}))return false;
      const actor=actors[index],name=observed&&actor.bird.water?'swim':nextBehavior(actor),active=actors.filter(a=>a.visible&&a.bird.active());
      if(actor.bird.active()||active.length<2)return requestBehavior(actor,name);
      pendingTap={index,name};
      active.find(a=>a.bird.index!==index)?.bird.cancel();notifyState();return true;
    }
    if(index!==selected)return select(index);
    const actor=actors[index];if(!actor)return false;
    const b=actor.bird,name=b.water?(b.active()?'rest':'swim'):b.sleeping()?'look':chooseDifferent(['look','notice','preen','sleep'],actor.previous||b.activity());
    actor.previous=name;return command(name);
  }
  function animals(){return actors.map((a,index)=>({index,label:'Afrika pengueni',point:focusFor(a),height:.62*a.bird.scale,width:.65*a.bird.scale,heading:a.bird.heading,water:a.bird.water,activity:a.bird.activity(),selected:index===selected,visible:group.visible&&a.visible}));}
  function setAutonomous(value){
    value=Boolean(value);if(autonomous===value)return;
    autonomous=value;colonyTime=0;scheduleTime=null;pendingTap=null;
    for(const actor of actors){actor.nextBehaviorAt=value?delay(.2,2.8):Infinity;if(!value)actor.bird.cancel();}
    onChange();
  }
  return {update,status:()=>state,interaction,select,observe,tap,animals,clearSelection,command,pick,
    setAutonomous,
    setInteractive(value){if(interactive===value)return;interactive=value;if(!value){setAutonomous(false);clearSelection();}else onChange();},
    setEnabled(value){enabled=value;lastTime=null;onChange();},
    retry(){if(state==='error'){state='idle';onChange();}},
    focusPoint(){const actor=actors[selected];return actor?focusFor(actor):null;},
    getDebugSnapshot(){return {state,visible:group.visible,selected,autonomous,observed,stats:{...stats},actors:actors.map(a=>({...a.bird.snapshot(),visible:a.visible}))};}};
}
