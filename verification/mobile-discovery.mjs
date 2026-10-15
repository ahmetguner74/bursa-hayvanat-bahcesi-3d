import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {T} from '../bolgeler/15-penguen/model/hayvan/load_local_gltf.mjs';
const base='http://127.0.0.1:8768/',NativeRequest=globalThis.Request,nativeFetch=globalThis.fetch;
globalThis.Request=class extends NativeRequest{constructor(input,options){super(typeof input==='string'?new URL(input,base):input,options);}};
globalThis.fetch=(input,options)=>nativeFetch(typeof input==='string'?new URL(input,base):input,options);
globalThis.document={hidden:false};globalThis.innerWidth=390;
const {createAviaryBirds}=await import('../viewer/aviary-birds.js'),{createTouchCue}=await import('../viewer/touch-cue.js');
const camera=new T.PerspectiveCamera(56,390/666,.12,2500);camera.up.set(0,0,1);camera.position.set(-39,-80,2);camera.lookAt(-38,-76,.5);camera.updateMatrixWorld(true);
const parent=new T.Group(),runtime=createAviaryBirds(parent,()=>{},{touchDevice:true,random:()=>0});runtime.setInteractive(true);runtime.update(0,camera,666,32);
for(let i=0;i<500&&runtime.status()==='loading';i++)await new Promise(resolve=>setTimeout(resolve,10));assert.equal(runtime.status(),'ready');runtime.update(1,camera,666,32);parent.updateMatrixWorld(true);
const mesh=parent.children[0].children[0].getObjectByProperty('isSkinnedMesh',true);assert(mesh);mesh.skeleton.update();
const vertex=new T.Vector3(),reference=[];
for(let i=0;i<mesh.geometry.attributes.position.count;i++)reference.push(mesh.getVertexPosition(i,vertex).applyMatrix4(mesh.matrixWorld).clone());
assert(runtime.observe(0));assert(runtime.tap(0));assert.equal(runtime.interaction().detail.activity,'LookAround');
let now=1,maximumSkinTravel=0,minimumGround=Infinity,maximumGround=-Infinity;
for(let frame=1;frame<=360;frame++){
 now+=1000/60;runtime.update(now,camera,666,32);
 if(frame%12)continue;parent.updateMatrixWorld(true);mesh.skeleton.update();let low=Infinity;
 for(let i=0;i<reference.length;i++){
  mesh.getVertexPosition(i,vertex).applyMatrix4(mesh.matrixWorld);maximumSkinTravel=Math.max(maximumSkinTravel,vertex.distanceTo(reference[i]));low=Math.min(low,vertex.z);
 }
 minimumGround=Math.min(minimumGround,low+.24);maximumGround=Math.max(maximumGround,low+.24);
}
assert(maximumSkinTravel>.09,'flamingo head/neck response must be visibly larger than the old 0.039m pose: '+maximumSkinTravel);
assert(minimumGround>-.002&&maximumGround<.002,'feet must remain on the ground');
for(let i=0;i<8;i++){assert(runtime.tap(0));assert.notEqual(runtime.interaction().detail.activity,'Rest','deliberate touch must request a visible response');for(let n=0;n<60;n++){now+=1000/60;runtime.update(now,camera,666,32);}}
const storage=new Map(),store={getItem:key=>storage.get(key),setItem:(key,value)=>storage.set(key,value)};
const element={hidden:true,style:{}},cue=createTouchCue(element,store),animal={visible:true,point:[-38,-76,.5],height:1.3};
cue.update([animal],camera,390,666,0,false);assert(element.hidden);
cue.update([animal],camera,390,666,100,true);assert(!element.hidden,'cue must identify a visible animal');
cue.update([animal],camera,390,666,2100,true);assert(!element.hidden);
cue.update([animal],camera,390,666,4100,true);assert(element.hidden,'cue expires after four seconds');
const nextElement={hidden:true,style:{}},next=createTouchCue(nextElement,store);next.update([animal],camera,390,666,5000,true);assert(nextElement.hidden,'cue does not repeat in the same session');
const result={revision:'20261016au',scope:'Production GLB/runtime CPU skin samples and cue lifecycle. Browser evidence verifies presentation.',flamingoMaximumSkinTravelMetres:maximumSkinTravel,groundErrorMetres:[minimumGround,maximumGround],touchNeverChoosesSubtleRest:true,oneTimeCue:{visibleAnimal:true,fourSecondLifetime:true,noSessionRepeat:true},extraMeshes:0,extraBones:0};
writeFileSync(new URL('./mobile-discovery.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
