import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {T} from './load_local_gltf.mjs';

const base='http://127.0.0.1:8768/',NativeRequest=globalThis.Request,nativeFetch=globalThis.fetch;
globalThis.Request=class extends NativeRequest{constructor(input,options){super(typeof input==='string'?new URL(input,base):input,options);}};
globalThis.fetch=(input,options)=>nativeFetch(typeof input==='string'?new URL(input,base):input,options);
globalThis.document={hidden:false};globalThis.location={search:''};globalThis.innerWidth=1280;
const {createPenguins}=await import('../../../../viewer/penguins.js');
const meta=JSON.parse(readFileSync(new URL('./colony-layout.json',import.meta.url)));
const parent=new T.Group(),camera=new T.PerspectiveCamera(56,16/9,.2,1200);camera.up.set(0,0,1);camera.position.set(-3.8,118.8,2.7);camera.lookAt(-7,123.5,.1);camera.updateProjectionMatrix();
let notify;const loaded=new Promise(resolve=>{notify=resolve;});
const controller=createPenguins(parent,()=>{if(['ready','error'].includes(controller.status()))notify();});
controller.setInteractive(true);controller.update(0,camera,720,15);await loaded;assert.equal(controller.status(),'ready');
let now=0,groundMin=Infinity,groundMax=-Infinity,worstGroundPose=null;
const group=parent.children[0],point=new T.Vector3();
const frozenPose=()=>JSON.stringify(controller.getDebugSnapshot().actors.map(a=>({x:a.x,y:a.y,heading:a.heading,pose:a.pose,samples:a.samples})));
function ground(){
  group.updateMatrixWorld(true);const snapshot=controller.getDebugSnapshot();
  for(let index=0;index<meta.landStarts.length;index++){
    const body=group.children[index].getObjectByName('Object_9');assert(body?.isSkinnedMesh);body.skeleton.update();
    let min=Infinity;
    for(let v=0;v<body.geometry.attributes.position.count;v++)min=Math.min(min,body.getVertexPosition(v,point).applyMatrix4(body.matrixWorld).z-meta.groundZ);
    if(Math.abs(min)>Math.max(Math.abs(groundMin===Infinity?0:groundMin),Math.abs(groundMax===-Infinity?0:groundMax)))worstGroundPose=snapshot.actors[index];
    groundMin=Math.min(groundMin,min);groundMax=Math.max(groundMax,min);
  }
}
function run(seconds,inspectGround=false){
  let changed=0;for(let i=0;i<Math.ceil(seconds*60);i++){now+=1000/60;if(controller.update(now,camera,720,15))changed++;if(inspectGround&&i%2===0)ground();}return changed;
}
run(.1);assert.equal(group.children.length,5);assert(group.visible);
const idleUpdates=controller.getDebugSnapshot().stats.poseUpdates;assert.equal(run(20),0);assert.equal(controller.getDebugSnapshot().stats.poseUpdates,idleUpdates);

const hitPoint=new T.Vector3(...meta.landStarts[0],meta.groundZ+.3),ndc=hitPoint.clone().project(camera),ray=new T.Raycaster();ray.setFromCamera(new T.Vector2(ndc.x,ndc.y),camera);
assert.equal(controller.pick(ray,camera,720),0,'Actual skinned bird must be tappable');
assert(controller.select(0));assert(controller.command('sleep'));run(10,true);
assert(controller.interaction().detail.sleeping);const sleepPose=frozenPose(),sleepUpdates=controller.getDebugSnapshot().stats.poseUpdates;
assert.equal(run(40),0);assert.equal(frozenPose(),sleepPose);assert.equal(controller.getDebugSnapshot().stats.poseUpdates,sleepUpdates);
assert(controller.command('look'));run(10,true);assert(!controller.interaction().detail.sleeping);
assert(controller.command('preen'));run(17,true);assert(!controller.getDebugSnapshot().actors[0].active);

assert(controller.select(3));run(2);
const moving=controller.getDebugSnapshot().actors[3];assert(Math.hypot(moving.x-meta.waterStarts[0][0],moving.y-meta.waterStarts[0][1])>.1);
const beforeHidden=frozenPose(),beforeHiddenUpdates=controller.getDebugSnapshot().stats.poseUpdates;
camera.lookAt(200,0,100);run(20);assert(!group.visible);assert.equal(frozenPose(),beforeHidden);assert.equal(controller.getDebugSnapshot().stats.poseUpdates,beforeHiddenUpdates);
camera.lookAt(-7,123.5,.1);document.hidden=true;run(20);assert.equal(frozenPose(),beforeHidden);
document.hidden=false;controller.setEnabled(false);run(20);assert(!group.visible);assert.equal(frozenPose(),beforeHidden);
controller.setEnabled(true);const beforeResume=controller.getDebugSnapshot().actors[3];run(1/60);const afterResume=controller.getDebugSnapshot().actors[3];
const resumeDistance=Math.hypot(afterResume.x-beforeResume.x,afterResume.y-beforeResume.y);assert(resumeDistance<.02);
run(12);assert(!controller.getDebugSnapshot().actors[3].active);controller.clearSelection();run(3);assert.equal(run(20),0);

controller.select(1);run(.2);controller.command('preen');controller.command('sleep');controller.command('look');run(20,true);
assert(!controller.getDebugSnapshot().actors.some(a=>a.active),'Interrupted requests must settle');
controller.clearSelection();assert.equal(controller.command('sleep'),false);
controller.setInteractive(false);assert.equal(controller.select(0),false);
let reducedNotify;const reducedLoaded=new Promise(resolve=>{reducedNotify=resolve;});
const reduced=createPenguins(new T.Group(),()=>{if(['ready','error'].includes(reduced.status()))reducedNotify();},{reducedMotion:true,touchDevice:true});
reduced.setInteractive(true);reduced.update(0,camera,720,15);await reducedLoaded;assert.equal(reduced.status(),'ready');
reduced.update(1,camera,720,15);assert(reduced.select(0));assert(!reduced.getDebugSnapshot().actors[0].active,'Reduced-motion selection must not auto-play');
const reducedPoseUpdates=reduced.getDebugSnapshot().stats.poseUpdates;
for(let frame=1;frame<=240;frame++)reduced.update(frame*1000/60,camera,720,15);
assert.equal(reduced.getDebugSnapshot().stats.poseUpdates,reducedPoseUpdates);
assert(reduced.command('preen'));const beforeTouchUpdates=reduced.getDebugSnapshot().stats.poseUpdates;
for(let frame=241;frame<=360;frame++)reduced.update(frame*1000/60,camera,720,15);
const touchUpdates=reduced.getDebugSnapshot().stats.poseUpdates-beforeTouchUpdates;
assert(touchUpdates>=58&&touchUpdates<=61,'Coarse pointer must cap near animation at30Hz even in a wide viewport');
const meshes=[];group.traverse(n=>{if(n.isSkinnedMesh)meshes.push(n);});
assert.notEqual(meshes[0].skeleton.bones[0],meshes[2].skeleton.bones[0]);assert.equal(meshes[0].geometry,meshes[2].geometry);assert.equal(meshes[0].material,meshes[2].material);
const proof={revision:'20261016aq',actualRuntimeModule:true,birds:5,idlePoseUpdates:0,sleepPoseUpdates:0,actualMeshPicking:true,waterTravel:true,offscreenFrozen:true,hiddenDocumentFrozen:true,toggleWorks:true,interruptedCommandsSettle:true,reducedMotionRespected:true,coarsePointer30Hz:true,resumeDistanceMetres:resumeDistance,grounding:{minimum:groundMin,maximum:groundMax,worstPose:worstGroundPose},independentSkeletons:true,sharedGeometry:true,physicalGpuOrPhoneTest:false};
writeFileSync(new URL('./runtime-verification.json',import.meta.url),JSON.stringify(proof,null,2)+'\n');
console.log(JSON.stringify({...proof,grounding:{minimum:groundMin,maximum:groundMax}}));
assert(groundMin>-.005&&groundMax<.005,'Blended source poses must remain within5mm of the ground');
