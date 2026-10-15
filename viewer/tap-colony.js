import * as T from 'three';
import {GLTFLoader} from './vendor/loaders/GLTFLoader.js';
import {clone} from './vendor/utils/SkeletonUtils.js';
import {chooseDifferent,createClipReaction,pickAnimal,sampleGround,sampleBlendGround} from './animal-interaction.js?v=20261016at';

/** Shared lifecycle and picking; clips/placement/grounding remain species data. */
export function createTapColony(parent,onChange,config,options={}){
  const group=new T.Group();group.name=config.name;group.visible=false;parent.add(group);
  const base=options.base||'./models/',frustum=new T.Frustum(),matrix=new T.Matrix4(),sphere=new T.Sphere(),viewPoint=new T.Vector3();
  const touch=options.touchDevice??(typeof matchMedia!=='undefined'&&matchMedia('(pointer: coarse)').matches);
  let state='idle',meta=null,asset=null,actors=[],selected=null,interactive=false,enabled=true,paused=false,lastTime=null;
  const random=options.random||(()=>Math.random()),reducedMotion=options.reducedMotion??false;
  let autonomous=false,observed=false,colonyTime=0,scheduleTime=null,pendingTap=null,behaviorOrder=0,uiSignature='';
  const stats={poseUpdates:0,maxConcurrentRigs:0};
  const delay=(min,max)=>min+random()*(max-min);
  function focus(actor){return [actor.pivot.position.x,actor.pivot.position.y,actor.pivot.position.z+config.height*actor.spec.scale*.5];}
  function placement(actor){
    if(actor.route){actor.pivot.position.set(actor.route.x,actor.route.y,meta.groundZ);actor.pivot.rotation.z=actor.route.heading+config.headingOffset;}
  }
  function applyPose(actor){
    const samples=actor.reaction.samples(),wanted=[];
    for(let slot=0;slot<samples.length;slot++){
      const sample=samples[slot],key=sample.clip+':'+slot;
      let action=actor.actions.get(key);
      if(!action){const source=actor.clips.get(sample.clip);action=actor.mixer.clipAction(slot?new T.AnimationClip(source.name+' blend',source.duration,source.tracks):source);actor.actions.set(key,action);}
      if(!action.isScheduled())action.play();
      action.enabled=true;action.paused=true;action.time=sample.time;action.setEffectiveWeight(sample.weight);wanted.push(action);
    }
    for(const action of actor.scheduled)if(!wanted.includes(action))action.stop();
    actor.scheduled=wanted;actor.mixer.update(0);
    const walk=samples.find(s=>s.clip===config.walkClip);
    actor.rig.position.y=walk&&meta.blendGround?sampleBlendGround(meta.blendGround,walk.time,walk.weight):samples.reduce((sum,s)=>sum+sampleGround(asset?.clips.find(c=>c.name===s.clip),s.time)*s.weight,0);
    stats.poseUpdates++;
  }
  async function json(file){const r=await fetch(base+file,{cache:'no-store'});if(!r.ok)throw Error(file+' yüklenemedi');return r.json();}
  async function load(){
    state='loading';onChange();
    try{
      [meta,asset]=await Promise.all([json(config.layout),config.assetMeta?json(config.assetMeta):null]);
      const gltf=await new GLTFLoader().loadAsync(base+config.file+'?v='+meta.assetSha256.slice(0,16));
      const clips=new Map([...gltf.animations,...(config.extraClips?.(gltf.scene,gltf.animations)||[])].map(c=>[c.name,c]));
      for(const name of [config.restClip,...config.choices.filter(c=>c!=='walk'),...(config.walkClip?[config.walkClip]:[])])if(!clips.has(name))throw Error('Hayvan klibi eksik: '+name);
      const specs=config.specs(meta);
      actors=specs.map((spec,index)=>{
        const rig=clone(gltf.scene),pivot=new T.Group(),axis=new T.Group();axis.rotation.x=Math.PI/2;axis.add(rig);pivot.add(axis);pivot.scale.setScalar(spec.scale);pivot.userData.animalIndex=index;
        rig.traverse(n=>{if(n.isMesh){n.frustumCulled=false;n.castShadow=true;n.receiveShadow=true;n.material=n.material.clone();if(n.material.map)n.material.map.anisotropy=4;config.material?.(n.material,spec);}});
        const route=config.route?.(meta,index);if(route)route.rate=meta.walkSpeedAtClipRateOne;
        const reaction=createClipReaction(clips,config.restClip,route,config.walkClip);
        const actor={spec,rig,pivot,route,reaction,clips,mixer:new T.AnimationMixer(rig),actions:new Map(),scheduled:[],previous:null,nextBehaviorAt:autonomous?delay(.8,3.8):Infinity,behaviorOrder:0};
        if(!route)config.place(pivot,spec,meta,options);
        placement(actor);applyPose(actor);return actor;
      });
      group.clear();group.add(...actors.map(a=>a.pivot));state='ready';lastTime=null;onChange();
    }catch(error){state='error';console.warn(config.name+' yüklenemedi.',error);onChange();}
  }
  function notifyState(){
    const signature=[selected,actors[selected]?.reaction.activity()].join('|');
    if(signature!==uiSignature){uiSignature=signature;onChange();}
  }
  function requestBehavior(actor,name){
    const accepted=actor.reaction.request(name);
    if(accepted){actor.previous=name;actor.nextBehaviorAt=Infinity;actor.behaviorOrder=++behaviorOrder;lastTime=null;notifyState();}
    return accepted;
  }
  function schedule(now){
    if(!autonomous||!interactive||reducedMotion){scheduleTime=null;return;}
    colonyTime+=scheduleTime===null?0:Math.min((now-scheduleTime)/1000,.08);scheduleTime=now;
    let active=actors.filter(a=>a.pivot.visible&&a.reaction.active()).length;
    if(pendingTap){
      const actor=actors[pendingTap.index];
      if(actor?.pivot.visible&&(actor.reaction.active()||active<2)){
        requestBehavior(actor,pendingTap.name);pendingTap=null;
        active=actors.filter(a=>a.pivot.visible&&a.reaction.active()).length;
      }
    }
    for(const actor of actors){
      if(actor.reaction.active())actor.nextBehaviorAt=Infinity;
      else if(actor.nextBehaviorAt===Infinity)actor.nextBehaviorAt=colonyTime+delay(8,18);
    }
    if(pendingTap)return;
    const due=actors.filter(a=>a.pivot.visible&&(!observed||actors[selected]===a)&&!a.reaction.active()&&a.nextBehaviorAt<=colonyTime).sort((a,b)=>a.nextBehaviorAt-b.nextBehaviorAt);
    for(const actor of due){
      if(active>=2)break;
      if(requestBehavior(actor,actor.previous===null&&config.firstBehavior?config.firstBehavior:chooseDifferent(config.choices,actor.previous,random)))active++;
    }
  }
  function update(now,camera,height,region){
    camera.updateMatrixWorld();matrix.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);frustum.setFromProjectionMatrix(matrix);
    const centre=config.centre;viewPoint.set(...centre);sphere.center.copy(viewPoint);sphere.radius=config.radius;
    let visible=frustum.intersectsSphere(sphere);
    if(actors.length){visible=false;for(const actor of actors){sphere.center.set(...focus(actor));sphere.radius=config.height*.75;actor.pivot.visible=frustum.intersectsSphere(sphere);visible||=actor.pivot.visible;}}
    const depth=Math.max(.5,-viewPoint.applyMatrix4(camera.matrixWorldInverse).z),pixels=config.height*height*camera.zoom/(2*depth*Math.tan(T.MathUtils.degToRad(camera.fov)/2));
    const wanted=enabled&&parent.visible&&!document.hidden&&visible&&(config.regions.includes(region)||pixels>=4)&&(!options.requireHabitat||options.requireHabitat());
    const shown=wanted&&state==='ready',changed=shown!==group.visible;group.visible=shown;
    if(!wanted){lastTime=null;scheduleTime=null;return changed;}
    if(state==='idle'){void load();return changed;}if(state!=='ready')return changed;
    if(paused){lastTime=null;scheduleTime=null;return changed;}
    schedule(now);
    const active=actors.filter(a=>a.pivot.visible&&a.reaction.active()).sort((a,b)=>Number(actors[selected]===b)-Number(actors[selected]===a)||a.behaviorOrder-b.behaviorOrder).slice(0,2);
    if(!active.length){lastTime=null;return changed;}
    const interval=pixels>=20?(touch||innerWidth<760?1000/30:1000/60):1000/12;
    if(lastTime!==null&&now-lastTime<interval-.5)return changed;
    const dt=lastTime===null?1/60:Math.min(.08,(now-lastTime)/1000);lastTime=now;
    const neighbors=actors.map(a=>a.route).filter(Boolean);
    stats.maxConcurrentRigs=Math.max(stats.maxConcurrentRigs,active.length);
    for(const actor of active){const wasActive=actor.reaction.active();actor.reaction.update(dt,neighbors);placement(actor);applyPose(actor);if(wasActive&&!actor.reaction.active())onChange();}
    notifyState();
    return true;
  }
  function select(index,{react=true}={}){
    if(!interactive||!group.visible||!actors[index])return false;
    if(selected!==index){
      if(!autonomous)for(const a of actors)a.reaction.cancel();
      selected=index;
      if(react&&!reducedMotion)requestBehavior(actors[index],config.notice);
    }
    lastTime=null;onChange();return true;
  }
  function observe(index){
    if(!select(index,{react:false}))return false;
    observed=true;pendingTap=null;
    for(let i=0;i<actors.length;i++)if(i!==index)actors[i].reaction.cancel();
    onChange();return true;
  }
  function tap(index){
    if(index!==selected)return select(index);
    if(!interactive||!actors[index])return false;
    const actor=actors[index],name=chooseDifferent(config.tapChoices||config.choices,actor.previous,random);
    const active=actors.filter(a=>a.pivot.visible&&a.reaction.active());
    if(autonomous&&!actor.reaction.active()&&active.length>=2){
      pendingTap={index,name};for(const a of active)a.reaction.cancel();onChange();return true;
    }
    return requestBehavior(actor,name);
  }
  function clearSelection(){observed=false;pendingTap=null;for(const actor of actors)actor.reaction.cancel();selected=null;lastTime=null;notifyState();}
  function setAutonomous(value){
    value=Boolean(value);if(autonomous===value)return;
    autonomous=value;colonyTime=0;scheduleTime=null;pendingTap=null;
    for(const actor of actors){actor.nextBehaviorAt=value?delay(.8,3.8):Infinity;if(!value)actor.reaction.cancel();}
    onChange();
  }
  function interaction(){
    const actor=actors[selected];
    return {state,selected,detail:actor?{label:config.label+' '+(selected+1),activity:actor.reaction.activity()}:null};
  }
  function animals(){
    const bounds=asset?.delivery?.restBoundsXYZGlTF||asset?.restBounds;
    return actors.map((a,index)=>({index,label:config.label,point:focus(a),height:config.height*a.spec.scale,width:config.width*a.spec.scale,
      frame:bounds?{length:(bounds[1][2]-bounds[0][2])*a.spec.scale,depth:(bounds[1][0]-bounds[0][0])*a.spec.scale,height:(bounds[1][1]-bounds[0][1])*a.spec.scale}:null,
      heading:a.route?.heading??a.pivot.rotation.z,activity:a.reaction.activity(),selected:index===selected,visible:group.visible&&a.pivot.visible}));
  }
  return {update,select,observe,tap,clearSelection,setAutonomous,interaction,animals,status:()=>state,metadata:()=>meta,
    pick:(ray,camera,height,settings)=>interactive?pickAnimal(actors,group,ray,camera,height,focus,settings):null,
    setInteractive(value){if(interactive===value)return;interactive=value;if(!value){setAutonomous(false);clearSelection();}},
    setEnabled(value){enabled=value;lastTime=null;onChange();},
    setPaused(value){paused=value;lastTime=null;onChange();},
    retry(){if(state==='error'){state='idle';onChange();}},
    focusPoint(){const actor=actors[selected??0];return actor?focus(actor):null;},
    getDebugSnapshot(){return {state,visible:group.visible,selected,autonomous,observed,stats:{...stats},actors:actors.map(a=>({position:a.pivot.position.toArray(),visible:a.pivot.visible,active:a.reaction.active(),activity:a.reaction.activity(),samples:a.reaction.samples()}))};}
  };
}
