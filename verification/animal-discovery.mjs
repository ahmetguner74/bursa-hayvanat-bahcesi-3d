import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {T} from '../bolgeler/15-penguen/model/hayvan/load_local_gltf.mjs';

const base='http://127.0.0.1:8768/',NativeRequest=globalThis.Request,nativeFetch=globalThis.fetch;
globalThis.Request=class extends NativeRequest{constructor(input,options){super(typeof input==='string'?new URL(input,base):input,options);}};
globalThis.fetch=(input,options)=>nativeFetch(typeof input==='string'?new URL(input,base):input,options);
globalThis.document=Object.assign(new EventTarget(),{hidden:false});globalThis.innerWidth=1280;globalThis.matchMedia=()=>({matches:false});
class Canvas extends EventTarget{constructor(){super();this.style={};this.ownerDocument=document;this.clientWidth=1004;this.clientHeight=720;}getRootNode(){return document;}}
const {createExplorerCamera}=await import('../viewer/explorer-camera.js');
const {createRhinos}=await import('../viewer/rhinos.js'),{createGiraffes}=await import('../viewer/giraffes.js'),{createAviaryBirds}=await import('../viewer/aviary-birds.js');
const {colonyView,animalFocusView,animalTarget}=await import('../viewer/animal-views.js');
const {describeBehavior}=await import('../viewer/animal-profiles.js');
const anchor={x:-30,y:-64,angle:9*Math.PI/180,length:70,width:40,height:20};
const types=[['rhino',createRhinos,16,[-43,94,1]],['giraffe',createGiraffes,12,[60,41,2.4]],['aviary',createAviaryBirds,32,[-35,-76,.6]]];
const result={revision:'20261016au',scope:'Actual production GLB/rigs, scheduling and OrbitControls on CPU. Not a physical device FPS/GPU benchmark.',species:{}};
for(const [key,create,region,centre] of types){
  const parent=new T.Group(),camera=new T.PerspectiveCamera(46,1004/720,.12,2500);camera.up.set(0,0,1);
  const nav=createExplorerCamera(camera,new Canvas(),()=>{},()=>{});let randomValue=.37,following=false;
  const runtime=create(parent,()=>{},{touchDevice:true,random:()=>randomValue,anchor});runtime.setInteractive(true);
  camera.position.set(centre[0]+15,centre[1]-25,centre[2]+18);camera.lookAt(...centre);camera.updateMatrixWorld(true);runtime.update(0,camera,720,region);
  for(let i=0;i<500&&runtime.status()==='loading';i++)await new Promise(resolve=>setTimeout(resolve,10));assert.equal(runtime.status(),'ready',key);
  nav.flyTo(colonyView(key,runtime.animals(),1004,720,false,anchor),{animate:false});
  let now=0,maxStep=0,maxError=0;const seen=new Set();
  function run(seconds,measure=false){
    for(let i=0;i<Math.ceil(seconds*60);i++){
      now+=1000/60;runtime.update(now,camera,720,region);
      const snapshot=runtime.getDebugSnapshot();assert(snapshot.stats.maxConcurrentRigs<=2,key+' must sample at most two rigs');
      snapshot.actors.forEach((a,index)=>{if(a.active&&a.visible)seen.add(index);});
      if(following){
        const before=camera.position.clone(),target=animalTarget(key,runtime.animals()[0],1280);nav.follow(target,1/60);camera.updateMatrixWorld(true);
        if(measure){const ndc=new T.Vector3(...target).project(camera);maxStep=Math.max(maxStep,camera.position.distanceTo(before));maxError=Math.max(maxError,Math.hypot(ndc.x*1004/2,ndc.y*720/2));}
      }
    }
  }
  run(.1);runtime.setAutonomous(true);run(70);
  assert.equal(runtime.interaction().selected,null,key+' colony must not imply a selected animal');
  assert.equal(seen.size,runtime.animals().length,key+' all visible individuals must receive a turn');
  assert(runtime.observe(0));assert(runtime.tap(0));run(10);
  assert(runtime.getDebugSnapshot().actors.every((a,i)=>!a.active||i===0),key+' other individuals must settle');
  assert.equal(runtime.interaction().detail.label,runtime.animals()[0].label+' 1');assert(describeBehavior(key,runtime.interaction().detail)[0]);
  const animals=runtime.animals();
  for(const [width,height,narrow] of [[1004,720,false],[246,844,true]]){
    const pose=colonyView(key,animals,width,height,narrow,anchor);camera.aspect=width/height;nav.flyTo(pose,{animate:false});camera.updateMatrixWorld(true);
    for(const animal of animals){const p=new T.Vector3(...animal.point).project(camera);assert(Math.abs(p.x)<1&&Math.abs(p.y)<1,key+' colony bodies must fit '+width);}
    if(key==='aviary'){
      const dx=pose.position[0]-anchor.x,dy=pose.position[1]-anchor.y,c=Math.cos(anchor.angle),s=Math.sin(anchor.angle),u=dx*c+dy*s,v=-dx*s+dy*c;
      assert((u/35)**2+(v/20)**2+(pose.position[2]/20)**2<.96,'aviary colony camera must stay inside dome');
    }
    const focus=animalFocusView(key,animals[0],width,height,narrow,anchor);nav.flyTo(focus,{animate:false});camera.updateMatrixWorld(true);
    for(const z of [-.45,.45]){const p=new T.Vector3(...animals[0].point);p.z+=z*animals[0].height;p.project(camera);assert(Math.abs(p.y)<.9,key+' head and feet must fit '+width);}
  }
  camera.aspect=1004/720;nav.flyTo(animalFocusView(key,runtime.animals()[0],1004,720,false,anchor),{animate:false});
  let travel=0;
  if(key!=='aviary'){
    runtime.setAutonomous(false);runtime.clearSelection();run(20);assert(runtime.select(0));run(1);assert(runtime.observe(0));randomValue=.999;assert(runtime.tap(0));
    const start=runtime.animals()[0].point.slice();following=true;run(3,true);following=false;
    travel=Math.hypot(runtime.animals()[0].point[0]-start[0],runtime.animals()[0].point[1]-start[1]);
    assert(travel>.3,key+' walk must move through space '+JSON.stringify({travel,detail:runtime.interaction().detail,actors:runtime.getDebugSnapshot().actors}));assert(maxStep<.02&&maxError<14,key+' tracking must be smooth');
  }
  document.hidden=true;const hidden=JSON.stringify(runtime.getDebugSnapshot().actors);run(30);assert.equal(JSON.stringify(runtime.getDebugSnapshot().actors),hidden,key+' hidden actors freeze');document.hidden=false;
  camera.position.set(5000,5000,100);camera.lookAt(5000,6000,100);camera.updateMatrixWorld(true);const offscreen=runtime.getDebugSnapshot().stats.poseUpdates;run(20);assert.equal(runtime.getDebugSnapshot().stats.poseUpdates,offscreen,key+' offscreen poses freeze');
  nav.flyTo(colonyView(key,runtime.animals(),1004,720,false,anchor),{animate:false});run(.1);
  for(let i=0;i<25;i++){assert(runtime.observe(i%runtime.animals().length));runtime.tap(i%runtime.animals().length);run(.12);}
  runtime.setInteractive(false);run(30);const idle=runtime.getDebugSnapshot().stats.poseUpdates;run(10);assert.equal(runtime.getDebugSnapshot().stats.poseUpdates,idle,key+' leaving must settle');
  assert.equal(runtime.getDebugSnapshot().observed,false);assert.equal(runtime.interaction().selected,null);
  const quiet=create(new T.Group(),()=>{},{reducedMotion:true,anchor});quiet.setInteractive(true);camera.position.set(centre[0]+15,centre[1]-25,centre[2]+18);camera.lookAt(...centre);camera.updateMatrixWorld(true);quiet.update(0,camera,720,region);
  for(let i=0;i<500&&quiet.status()==='loading';i++)await new Promise(resolve=>setTimeout(resolve,10));assert.equal(quiet.status(),'ready');quiet.setAutonomous(true);quiet.update(1,camera,720,region);
  const before=quiet.getDebugSnapshot().stats.poseUpdates;for(let i=1;i<600;i++)quiet.update(i*1000/60,camera,720,region);assert.equal(quiet.getDebugSnapshot().stats.poseUpdates,before,key+' reduced motion suppresses automatic behavior');
  assert(quiet.observe(0));assert(quiet.tap(0),key+' deliberate tap remains available');
  result.species[key]={individuals:animals.length,everyVisibleAnimalGetsTurn:true,noDefaultSelection:true,onlyObservedAnimalContinues:true,maxSampledRigs:runtime.getDebugSnapshot().stats.maxConcurrentRigs,desktopAndPortraitFraming:true,walkTravelMetres:travel,maxCameraStepMetres:maxStep,maxCentreErrorPixels:maxError,hiddenAndOffscreenFreeze:true,rapidSwitchesSettle:true,leavingStopsPoseUpdates:true,reducedMotion:true};
}
writeFileSync(new URL('./animal-discovery.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
