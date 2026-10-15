import * as T from 'three';
import {penguinColonyView,penguinFocusView,penguinTarget} from './penguin-views.js?v=20261016au';

const initial={
  rhino:[[-43.13,89.74,.71,1.9,4.6],[-53.35,100.7,.67,1.824,4.416]],
  giraffe:[[43.54,41.5,2.26,5,2.8],[71.6,45.4,2.035,4.55,2.548]],
};
function fit(animals,direction,width,height,fov,margin){
  const target=animals.reduce((sum,a)=>sum.add(new T.Vector3(...a.point)),new T.Vector3()).multiplyScalar(1/animals.length);
  const right=new T.Vector3().crossVectors(new T.Vector3(0,0,1),direction).normalize(),up=new T.Vector3().crossVectors(direction,right);
  const tan=Math.tan(T.MathUtils.degToRad(fov/2)),aspect=width/height;
  let distance=2;
  for(const a of animals)for(const x of [-1,1])for(const y of [-1,1])for(const z of [-1,1]){
    const length=(a.frame?.length||a.width)*.55,depth=(a.frame?.depth||a.width)*.55,c=Math.cos(a.heading||0),s=Math.sin(a.heading||0);
    const p=new T.Vector3(a.point[0]+x*length*c-y*depth*s,a.point[1]+x*length*s+y*depth*c,a.point[2]+z*(a.frame?.height||a.height)*.55).sub(target);
    distance=Math.max(distance,p.dot(direction)+margin*Math.abs(p.dot(right))/(tan*aspect),p.dot(direction)+margin*Math.abs(p.dot(up))/tan);
  }
  return {position:target.clone().addScaledVector(direction,distance).toArray(),target:target.toArray(),fov};
}
function aviaryDirection(anchor,narrow=false){
  const c=Math.cos(anchor.angle),s=Math.sin(anchor.angle);
  // Shore-side camera remains inside the dome and looks along the colony.
  const v=narrow?-.04:-.15;
  return new T.Vector3(-c-v*s,-s+v*c,.18).normalize();
}
export function animalTarget(key,animal,width){return key==='penguin'?penguinTarget(animal,width):animal.point;}
export function colonyView(key,animals,width,height,narrow,anchor){
  if(key==='penguin')return penguinColonyView(narrow?390:1280);
  if(!animals.length){
    if(key==='aviary'){
      const c=Math.cos(anchor.angle),s=Math.sin(anchor.angle);
      animals=[[-10.4,-11.4],[-8.3,-10.9],[-5.9,-11.7],[-1.6,-11.1]].map(([u,v])=>({point:[anchor.x+u*c-v*s,anchor.y+u*s+v*c,.41],height:1.3,width:.85}));
    }else animals=initial[key].map(([x,y,z,h,w])=>({point:[x,y,z],height:h,width:w}));
  }
  const direction=key==='aviary'?aviaryDirection(anchor,narrow):new T.Vector3(...(key==='giraffe'?(narrow?[1,-.18,.48]:[.4,-1,.55]):[.85,-1,.65])).normalize();
  return fit(animals,direction,width,height,narrow?56:46,1.25);
}
export function animalFocusView(key,animal,width,height,narrow,anchor){
  if(key==='penguin')return penguinFocusView(animal,narrow?390:1280);
  let direction=new T.Vector3(.4,-1,.3);
  if(key==='rhino'){
    const left=animal.heading-Math.PI/3,right=animal.heading+Math.PI/3,angle=Math.sin(left)<Math.sin(right)?left:right;
    direction.set(Math.cos(angle),Math.sin(angle),.25);
  }else if(key==='aviary')direction=aviaryDirection(anchor,narrow);
  return fit([animal],direction.normalize(),width,height,narrow?56:50,1.28);
}
