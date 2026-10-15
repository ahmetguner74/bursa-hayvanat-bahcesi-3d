import * as T from 'three';

const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const smooth=x=>x*x*(3-2*x);

export function chooseDifferent(choices,previous,random=Math.random){
  const pool=choices.filter(choice=>choice!==previous);
  return (pool.length?pool:choices)[Math.floor(random()*(pool.length||choices.length))];
}

// Finite travel on the validated habitat paths. Clip phase follows distance,
// including acceleration and braking; the colony controls when it is requested.
export function createRouteMotion(meta,index){
  const spec=meta.routes[index];
  const curve=new T.CatmullRomCurve3(spec.points.map(p=>new T.Vector3(...p,0)),true,'centripetal');
  curve.arcLengthDivisions=1024;curve.updateArcLengths();
  const length=curve.getLength(),point=new T.Vector3(),tangent=new T.Vector3();
  const state={x:0,y:0,heading:0,speed:0,scale:spec.scale,distance:spec.initialPhase*length,walking:false,clip:'Idle',curve,length};
  let remaining=0;
  function sample(){
    const u=((state.distance/length)%1+1)%1;
    curve.getPointAt(u,point);curve.getTangentAt(u,tangent).multiplyScalar(spec.direction);
    state.x=point.x;state.y=point.y;state.heading=Math.atan2(tangent.y,tangent.x);
  }
  sample();
  state.request=(seconds=8)=>{remaining=seconds;state.walking=true;};
  state.stop=()=>{remaining=0;state.walking=false;};
  state.active=()=>remaining>0||state.speed>1e-6;
  state.update=(dt,neighbors=[])=>{
    dt=clamp(dt,0,.08);remaining=Math.max(0,remaining-dt);state.walking=remaining>0;
    let target=remaining>1.8?meta.walkSpeedAtClipRateOne*spec.scale:0;
    for(const other of neighbors){
      if(other===state)continue;
      const dx=other.x-state.x,dy=other.y-state.y;
      if(Math.hypot(dx,dy)<meta.minimumSeparationMetres+1.2&&dx*Math.cos(state.heading)+dy*Math.sin(state.heading)>0)target=0;
    }
    state.speed+=clamp(target-state.speed,-.30*dt,.22*dt);
    state.distance+=state.speed*dt*spec.direction;sample();
    state.clip=state.active()?'walk':'Idle';return state;
  };
  return state;
}

// At most two manually sampled clip poses, with one last requested reaction.
// This avoids accumulating AnimationAction fades after repeated taps.
export function createClipReaction(clips,restClip,route=null,walkClip=null){
  let step=null,elapsed=0,from={clip:restClip,time:0},pose={...from},pending=null,activity=null;
  let walkTime=0,walkWeight=0,cancelRequested=false;
  const duration=name=>clips.get(name).duration;
  function begin(name){
    activity=name;pending=null;cancelRequested=false;elapsed=0;from={...pose};
    if(name==='walk'){route.request();step='walk';return;}
    step='in';pose={clip:name,time:0};
  }
  function request(name){
    if(name!=='walk'&&!clips.has(name))return false;
    if(name==='walk'&&!route)return false;
    if(activity===name){
      if(step==='walk'){pending=null;route.request();}
      else if(step==='out')pending=name;
      else{pending=null;cancelRequested=false;}
      return true;
    }
    if(step){
      pending=name;
      if(step==='walk')route.stop();
      else if(step==='play'){from={...pose};step='out';elapsed=0;}
      return true;
    }
    begin(name);return true;
  }
  function finish(){
    pose={clip:restClip,time:0};step=null;activity=null;walkWeight=0;cancelRequested=false;
    if(pending){const name=pending;pending=null;begin(name);}
  }
  function update(dt,neighbors){
    if(!step)return false;
    dt=clamp(dt,0,.08);elapsed+=dt;
    if(step==='walk'){
      route.update(dt,neighbors);
      const rate=route.speed/(route.scale*route.rate);
      walkTime=(walkTime+dt*rate)%duration(walkClip);
      walkWeight=clamp(rate,0,1);
      if(!route.active())finish();
    }else if(step==='in'){
      if(elapsed>=.5){from={...pose};step=pending||cancelRequested?'out':'play';elapsed=0;}
    }else if(step==='play'){
      pose.time=elapsed%duration(pose.clip);
      if(elapsed>=duration(pose.clip)){from={...pose};step='out';elapsed=0;}
    }else if(step==='out'){
      if(elapsed>=.65)finish();
    }
    return true;
  }
  function samples(){
    if(step==='walk')return [{clip:restClip,time:0,weight:1-walkWeight},{clip:walkClip,time:walkTime,weight:walkWeight}];
    if(step==='in')return [{...from,weight:1-smooth(clamp(elapsed/.5,0,1))},{...pose,weight:smooth(clamp(elapsed/.5,0,1))}];
    if(step==='out')return [{...from,weight:1-smooth(clamp(elapsed/.65,0,1))},{clip:restClip,time:0,weight:smooth(clamp(elapsed/.65,0,1))}];
    return [{...pose,weight:1}];
  }
  function cancel(){
    pending=null;if(!step)return;
    if(step==='walk'){route.stop();return;}
    // Finish the current blend, then return; never blend three poses.
    if(step==='in'){cancelRequested=true;return;}
    if(step==='out')return;
    from={...pose};step='out';elapsed=0;
  }
  return {request,update,samples,cancel,active:()=>Boolean(step),activity:()=>activity};
}

export function sampleGround(clip,time){
  if(!clip)return 0;
  const values=clip.groundOffsetMetres,p=((time%clip.duration)+clip.duration)%clip.duration/clip.duration*(values.length-1),i=Math.floor(p);
  return values[i]+(values[Math.min(i+1,values.length-1)]-values[i])*(p-i);
}
export function sampleBlendGround(table,time,weight){
  const p=((time%table.duration)+table.duration)%table.duration/table.duration*table.phaseSegments,w=clamp(weight,0,1)*table.weightSegments;
  const i=Math.floor(p),j=Math.floor(w),pt=p-i,wt=w-j,ii=Math.min(i+1,table.phaseSegments),jj=Math.min(j+1,table.weightSegments);
  return (table.values[i][j]*(1-wt)+table.values[i][jj]*wt)*(1-pt)+(table.values[ii][j]*(1-wt)+table.values[ii][jj]*wt)*pt;
}

export function pickAnimal(actors,group,raycaster,camera,height,focus,{precise=true}={}){
  if(!group.visible)return null;
  if(precise){
    group.updateMatrixWorld(true);
    for(const actor of actors)if(actor.pivot.visible)actor.pivot.traverse(node=>{if(node.isSkinnedMesh){node.skeleton.update();node.computeBoundingSphere();node.computeBoundingBox();}});
    for(const hit of raycaster.intersectObject(group,true)){
      let node=hit.object;
      while(node&&node!==group){const index=node.userData.animalIndex;if(Number.isInteger(index)&&actors[index].pivot.visible)return index;node=node.parent;}
    }
  }
  let nearest=null,best=22;
  const p=new T.Vector3(),v=new T.Vector3();
  for(let index=0;index<actors.length;index++){
    if(!actors[index].pivot.visible)continue;
    p.set(...focus(actors[index]));const depth=-v.copy(p).applyMatrix4(camera.matrixWorldInverse).z;
    if(depth<=0)continue;
    const scale=height*camera.zoom/(2*depth*Math.tan(T.MathUtils.degToRad(camera.fov)/2));
    const distance=Math.sqrt(raycaster.ray.distanceSqToPoint(p))*scale;
    if(distance<best){best=distance;nearest=index;}
  }
  return nearest;
}
