import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {T} from '../bolgeler/15-penguen/model/hayvan/load_local_gltf.mjs';

const base='http://127.0.0.1:8768/',NativeRequest=globalThis.Request,nativeFetch=globalThis.fetch;
globalThis.Request=class extends NativeRequest{constructor(input,options){super(typeof input==='string'?new URL(input,base):input,options);}};
globalThis.fetch=(input,options)=>nativeFetch(typeof input==='string'?new URL(input,base):input,options);
globalThis.document=Object.assign(new EventTarget(),{hidden:false});globalThis.location={search:''};globalThis.innerWidth=1280;
globalThis.matchMedia=()=>({matches:false});
class Canvas extends EventTarget{constructor(){super();this.style={};this.ownerDocument=document;this.clientWidth=1004;this.clientHeight=720;}getRootNode(){return document;}}
const {createPenguins}=await import('../viewer/penguins.js');
const {createExplorerCamera}=await import('../viewer/explorer-camera.js');
const {insideDomain}=await import('../viewer/penguin-motion.js');
const {penguinColonyView,penguinFocusView,penguinTarget}=await import('../viewer/penguin-views.js');
const meta=await fetch(base+'models/penguin-colony.json').then(r=>r.json());
const camera=new T.PerspectiveCamera(44,1004/720,.12,2500),parent=new T.Group();camera.up.set(0,0,1);
const nav=createExplorerCamera(camera,new Canvas(),()=>{},()=>{});
const colony=penguinColonyView(1280);nav.flyTo(colony,{animate:false});
const runtime=createPenguins(parent,()=>{},{touchDevice:true,random:()=>.47});runtime.setInteractive(true);runtime.update(0,camera,720,15);
for(let i=0;i<500&&runtime.status()==='loading';i++)await new Promise(resolve=>setTimeout(resolve,10));
assert.equal(runtime.status(),'ready');runtime.setAutonomous(true);
let now=0,following=null,maxCameraStep=0,maxCentreErrorPixels=0;
function run(seconds,measure=false){
  for(let i=0;i<Math.ceil(seconds*60);i++){
    now+=1000/60;nav.update(now);runtime.update(now,camera,720,15);
    if(following!==null){
      const before=camera.position.clone(),point=penguinTarget(runtime.animals()[following],1280);
      nav.follow(point,1/60);camera.updateMatrixWorld(true);
      if(measure){
        maxCameraStep=Math.max(maxCameraStep,camera.position.distanceTo(before));
        const ndc=new T.Vector3(...point).project(camera);
        maxCentreErrorPixels=Math.max(maxCentreErrorPixels,Math.hypot(ndc.x*1004/2,ndc.y*720/2));
      }
    }
    const snapshot=runtime.getDebugSnapshot();assert(snapshot.stats.maxConcurrentRigs<=2);
    for(const a of snapshot.actors)if(a.water)assert(insideDomain(meta.waterDomain,a.x,a.y));
  }
}
function focus(index){
  const a=runtime.animals()[index];nav.flyTo(penguinFocusView(a,1280),{animate:false});run(.1);
  assert(runtime.observe(index));assert(runtime.tap(index));following=a.water?index:null;
}
run(16);assert.equal(runtime.interaction().selected,null,'colony view does not imply an observed individual');
focus(0);run(6);assert(runtime.getDebugSnapshot().actors.every(a=>!a.visible||!a.active||a.index===0),'other animals settle while one is observed');
focus(3);run(3);
parent.updateMatrixWorld(true);let bodyAbove=0,bodyVertices=0,bodyTop=-Infinity;const vertex=new T.Vector3();
parent.children[0].children[3].traverse(mesh=>{
  if(!mesh.isSkinnedMesh||mesh.name!=='Object_9')return;mesh.skeleton.update();
  for(let i=0;i<mesh.geometry.attributes.position.count;i++){
    const z=mesh.getVertexPosition(i,vertex).applyMatrix4(mesh.matrixWorld).z-meta.waterZ;
    bodyVertices++;if(z>0)bodyAbove++;bodyTop=Math.max(bodyTop,z);
  }
});
assert(bodyAbove>0&&bodyAbove<bodyVertices,'swimming body stays partly submerged and partly visible');
const start=runtime.animals()[3].point.slice();run(3,true);const end=runtime.animals()[3].point;
assert(Math.hypot(end[0]-start[0],end[1]-start[1])>.4,'watched swimmer actually travels');
assert(runtime.getDebugSnapshot().actors.every(a=>!a.visible||!a.active||a.index===3));
const beforeRetap=runtime.animals()[3].point.slice();assert(runtime.tap(3));assert.deepEqual(runtime.animals()[3].point,beforeRetap,'retap does not teleport');
run(8,true);assert.equal(runtime.interaction().detail.activity,'swim','retapping a swimmer extends swimming instead of stopping');
assert(maxCameraStep<.02,'follow movement is continuous per frame');assert(maxCentreErrorPixels<14,'watched swimmer stays near frame centre');
assert.equal(camera.up.z,1);assert(camera.position.z>0,'tracking camera stays above ground');
following=null;runtime.setInteractive(false);run(6);const idle=runtime.getDebugSnapshot().stats.poseUpdates;run(10);assert.equal(runtime.getDebugSnapshot().stats.poseUpdates,idle);
assert.equal(runtime.getDebugSnapshot().observed,false);assert.equal(runtime.interaction().selected,null);
const result={revision:'20261016au',scope:'Production GLB, motion, ExplorerCamera and OrbitControls on CPU with an event-only canvas. Browser screenshots verify rendered UI; no GPU/FPS measurement.',colonyHasNoDefaultSelection:true,onlyObservedAnimalContinues:true,waterRetapExtendsSwimming:true,waterRetapNoTeleport:true,swimmerTravelMetres:Math.hypot(end[0]-start[0],end[1]-start[1]),maximumCameraStepMetres:maxCameraStep,maximumCentreErrorPixels:maxCentreErrorPixels,maximumSampledRigs:runtime.getDebugSnapshot().stats.maxConcurrentRigs,swimmingSkinSample:{bodyVertices,bodyAboveWater:bodyAbove,highestPointAboveWaterMetres:bodyTop},waterInsidePool:true,leavingStopsUpdates:true};
writeFileSync(new URL('./penguin-focus.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
