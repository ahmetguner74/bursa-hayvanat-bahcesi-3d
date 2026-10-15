import * as T from 'three';
import {OrbitControls} from './vendor/OrbitControls.js';
import {createAtlasOrbit} from './atlas-orbit.js?v=20261015ag';

const smooth=t=>t*t*(3-2*t);
export function createExplorerCamera(camera,element,onChange,onUserStart,onFlight=()=>{}){
  let controls,flight=null;
  function bind(target){
    controls?.dispose();
    controls=createAtlasOrbit(OrbitControls,camera,element,target,{onChange,onStart(){flight=null;onFlight(false);onUserStart();}});
    controls.minDistance=.85;controls.maxDistance=2200;
    controls.maxPolarAngle=Math.PI*.495;
  }
  bind(new T.Vector3());
  function flyTo(pose,{animate=true,waypoints=[]}={}){
    const start={position:camera.position.clone(),target:controls.target.clone(),fov:camera.fov};
    bind(start.target);
    const end={position:new T.Vector3(...pose.position),target:new T.Vector3(...pose.target),fov:pose.fov||56};
    const frames=[start,...waypoints.map(p=>({position:new T.Vector3(...p.position),target:new T.Vector3(...p.target),fov:p.fov||56})),end];
    if(!animate||matchMedia('(prefers-reduced-motion: reduce)').matches){camera.position.copy(end.position);controls.target.copy(end.target);camera.fov=end.fov;camera.updateProjectionMatrix();controls.update();flight=null;onFlight(false);onChange();return;}
    flight={frames,index:0,start:performance.now(),duration:waypoints.length?850:1800};onFlight(true);onChange();
  }
  function update(now){
    if(flight){
      const {frames,index,start,duration}=flight,t=Math.min(1,(now-start)/duration),e=smooth(t),a=frames[index],b=frames[index+1];
      camera.position.lerpVectors(a.position,b.position,e);controls.target.lerpVectors(a.target,b.target,e);
      camera.fov=a.fov+(b.fov-a.fov)*e;camera.updateProjectionMatrix();onChange();
      if(t===1){if(index+2<frames.length){flight.index++;flight.start=now;}else{flight=null;onFlight(false);}}
    }
    controls.update();
  }
  function follow(point,dt){
    if(flight||!point)return false;
    const delta=new T.Vector3(...point).sub(controls.target).multiplyScalar(1-Math.exp(-12*Math.min(dt,.08)));
    if(delta.lengthSq()<1e-8)return false;
    camera.position.add(delta);controls.target.add(delta);controls.update();onChange();return true;
  }
  return {flyTo,update,follow,inFlight:()=>Boolean(flight)};
}
