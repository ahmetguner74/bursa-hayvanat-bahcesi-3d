import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {T} from '../bolgeler/15-penguen/model/hayvan/load_local_gltf.mjs';

const base='http://127.0.0.1:8768/',NativeRequest=globalThis.Request,nativeFetch=globalThis.fetch;
globalThis.Request=class extends NativeRequest{constructor(input,options){super(typeof input==='string'?new URL(input,base):input,options);}};
globalThis.fetch=(input,options)=>nativeFetch(typeof input==='string'?new URL(input,base):input,options);
globalThis.document={hidden:false};globalThis.location={search:''};globalThis.innerWidth=390;
const {createPenguins}=await import('../viewer/penguins.js');
const {insideDomain}=await import('../viewer/penguin-motion.js');
const meta=await fetch(base+'models/penguin-colony.json').then(r=>r.json());
const parent=new T.Group(),camera=new T.PerspectiveCamera(56,246/844,.12,2500);
camera.up.set(0,0,1);camera.position.set(.2,115.5,6.7);camera.lookAt(-7.9,124.5,.2);camera.updateMatrixWorld(true);
let seed=138;const random=()=>((seed=(1664525*seed+1013904223)>>>0)/4294967296);
const runtime=createPenguins(parent,()=>{},{touchDevice:true,random});runtime.setInteractive(true);runtime.update(0,camera,844,15);
for(let i=0;i<500&&runtime.status()==='loading';i++)await new Promise(resolve=>setTimeout(resolve,10));
assert.equal(runtime.status(),'ready');
let now=0,maximumActive=0;const seen=new Set(),behaviors=new Set();
function run(seconds){
  for(let frame=0;frame<Math.ceil(seconds*60);frame++){
    now+=1000/60;runtime.update(now,camera,844,15);
    const snapshot=runtime.getDebugSnapshot(),active=snapshot.actors.filter(a=>a.active&&a.visible);
    maximumActive=Math.max(maximumActive,active.length);assert(snapshot.stats.maxConcurrentRigs<=2,'at most two sampled rigs, including orbit/manual taps/blends');
    for(const actor of active){seen.add(actor.index);behaviors.add(actor.activity);}
    for(const actor of snapshot.actors)if(actor.water)assert(insideDomain(meta.waterDomain,actor.x,actor.y),'actual water route remains inside pool');
  }
}
run(5);const idle=runtime.getDebugSnapshot().stats.poseUpdates;run(5);assert.equal(runtime.getDebugSnapshot().stats.poseUpdates,idle);
assert.equal(runtime.animals().filter(a=>a.visible).length,5,'all five animals fit the phone colony camera');
assert(runtime.select(0,{react:false}));runtime.setAutonomous(true);run(180);
assert.equal(seen.size,5,'every penguin gets a turn without a touch');
const firstRound=[...seen].sort();
assert(behaviors.has('swim')&&behaviors.has('preen')&&behaviors.has('sleep'));
seen.clear();run(180);assert([0,1,2].every(i=>seen.has(i)),'visible colony keeps moving after swimmers leave the frame');
camera.position.set(-6.7,113,6);camera.lookAt(-6.7,123,.2);camera.updateMatrixWorld(true);seen.clear();run(180);
assert([0,1,2].every(i=>seen.has(i)),'offscreen swimmers cannot block the visible land colony');
camera.position.set(.2,115.5,6.7);camera.lookAt(-7.9,124.5,.2);camera.updateMatrixWorld(true);run(.1);
for(let tap=0;tap<25;tap++){const index=tap%5;assert(runtime.tap(index));run(.12);assert.equal(runtime.interaction().selected,index);}
run(2.5);
const observed=runtime.interaction().selected;
assert.equal(runtime.interaction().detail.water,runtime.getDebugSnapshot().actors[observed].water,'panel observation follows the touched animal');
document.hidden=true;run(.1);const frozen=JSON.stringify(runtime.getDebugSnapshot());run(40);assert.equal(JSON.stringify(runtime.getDebugSnapshot()),frozen);document.hidden=false;
const positions=runtime.animals().map(a=>a.point);run(1/60);assert(runtime.animals().every((a,i)=>new T.Vector3(...a.point).distanceTo(new T.Vector3(...positions[i]))<.03));
runtime.setAutonomous(false);runtime.setInteractive(false);run(6);const settled=runtime.getDebugSnapshot().stats.poseUpdates;run(30);assert.equal(runtime.getDebugSnapshot().stats.poseUpdates,settled,'leaving colony stops autonomous poses');
runtime.setInteractive(true);runtime.setAutonomous(true);run(5);camera.lookAt(0,-100,0);camera.updateMatrixWorld(true);run(.1);
const offscreen=JSON.stringify(runtime.getDebugSnapshot());run(30);assert.equal(JSON.stringify(runtime.getDebugSnapshot()),offscreen,'offscreen colony freezes');
camera.lookAt(-7.9,124.5,.2);camera.updateMatrixWorld(true);
const reduced=createPenguins(new T.Group(),()=>{},{touchDevice:true,reducedMotion:true,random});reduced.setInteractive(true);reduced.update(0,camera,844,15);
for(let i=0;i<500&&reduced.status()==='loading';i++)await new Promise(resolve=>setTimeout(resolve,10));
assert.equal(reduced.status(),'ready');reduced.select(0,{react:false});reduced.setAutonomous(true);
const reducedIdle=reduced.getDebugSnapshot().stats.poseUpdates;
for(let i=0;i<600;i++)reduced.update(i*1000/60,camera,844,15);
assert.equal(reduced.getDebugSnapshot().stats.poseUpdates,reducedIdle,'reduced motion suppresses autonomous behavior');
assert(reduced.tap(1));for(let i=0;i<60;i++)reduced.update(10001+i*1000/60,camera,844,15);
assert(reduced.getDebugSnapshot().stats.poseUpdates>reducedIdle,'reduced motion still permits an explicit body tap');
const result={revision:'20261016aq',scope:'Actual production runtime and HTTP GLB on CPU; no GPU/FPS claim',phoneViewport:[390,844],renderViewport:[246,844],allFiveFitCamera:true,autonomousAnimals:firstRound,behaviors:[...behaviors].sort(),maximumVisibleActiveStates:maximumActive,maximumSampledRigs:runtime.getDebugSnapshot().stats.maxConcurrentRigs,rapidDirectTaps:25,hiddenAndOffscreenFrozen:true,offscreenSwimmersDoNotBlockLand:true,leavingColonyStopsUpdates:true,swimmersInsidePool:true,reducedMotionNoAutonomyExplicitTapWorks:true};
writeFileSync(new URL('./penguin-discovery.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
