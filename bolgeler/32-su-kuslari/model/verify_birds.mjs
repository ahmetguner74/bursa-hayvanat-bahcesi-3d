import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {T,loadGLB} from '../../15-penguen/model/hayvan/load_local_gltf.mjs';
const here=new URL('./',import.meta.url),bytes=await fs.readFile(new URL('hayvan/greater-flamingo.glb',here));
const meta=JSON.parse(await fs.readFile(new URL('aviary-birds-layout.json',here),'utf8'));
assert.equal(createHash('sha256').update(bytes).digest('hex'),meta.assetSha256);
const gltf=await loadGLB(bytes),meshes=[],bones=[];
gltf.scene.traverse(o=>{if(o.isMesh)meshes.push(o);if(o.isBone)bones.push(o);});
assert.equal(bones.length,5);assert.equal(meshes.length,2);assert.equal(meshes.filter(o=>o.isSkinnedMesh).length,1);
assert.equal(meshes.reduce((s,m)=>s+(m.geometry.index?.count??m.geometry.attributes.position.count)/3,0),12040);
const {clone}=await import('../../../vendor/utils/SkeletonUtils.js');
const duplicate=clone(gltf.scene),copyMeshes=[];duplicate.traverse(o=>{if(o.isMesh)copyMeshes.push(o);});
for(let i=0;i<meshes.length;i++){assert.equal(copyMeshes[i].geometry,meshes[i].geometry);assert.equal(copyMeshes[i].material,meshes[i].material);}
assert.notEqual(copyMeshes.find(m=>m.isSkinnedMesh).skeleton.bones[0],meshes.find(m=>m.isSkinnedMesh).skeleton.bones[0]);
const mixer=new T.AnimationMixer(gltf.scene),point=new T.Vector3(),minima={},maximumDisplacement={},loopSeam={};
function pose(){
  gltf.scene.updateMatrixWorld(true);for(const m of meshes)if(m.isSkinnedMesh)m.skeleton.update();
  const points=[];
  for(const mesh of meshes){const position=mesh.geometry.attributes.position;for(let i=0;i<position.count;i++){mesh.getVertexPosition(i,point).applyMatrix4(mesh.matrixWorld);points.push(point.clone());}}
  return points;
}
const rest=pose();const contact=rest.map((p,i)=>p.y<.055?i:-1).filter(i=>i>=0);let groundMin=Infinity,groundMax=-Infinity,maxFootDrift=0;
for(const clip of gltf.animations){
  mixer.stopAllAction();const action=mixer.clipAction(clip);action.reset().play();
  let low=Infinity,high=-Infinity,movement=0;const samples=[];
  for(let i=0;i<=144;i++){
    action.time=clip.duration*i/144;mixer.update(0);const positions=pose();
    const y=Math.min(...positions.map(p=>p.y));low=Math.min(low,y);high=Math.max(high,y);
    for(const index of contact)maxFootDrift=Math.max(maxFootDrift,positions[index].distanceTo(rest[index]));
    for(let j=0;j<positions.length;j++)movement=Math.max(movement,positions[j].distanceTo(rest[j]));
    if(i===0||i===144)samples.push(positions);
  }
  minima[clip.name]=[low,high];maximumDisplacement[clip.name]=movement;loopSeam[clip.name]=Math.max(...samples[0].map((p,i)=>p.distanceTo(samples[1][i])));
  assert.ok(movement>.0005&&movement<.15,clip.name+' restrained real skinned motion');assert.ok(loopSeam[clip.name]<1e-7);
  groundMin=Math.min(groundMin,low);groundMax=Math.max(groundMax,high);
}
assert.ok(Math.abs(groundMin)<.00001&&Math.abs(groundMax)<.00001,'ground contact');assert.ok(maxFootDrift<1e-7,'foot/toes remain anchored');
// Real runtime with the same production loader, file fixtures and real clips.
globalThis.document={hidden:false};globalThis.location={search:''};globalThis.innerWidth=1280;
const nativeFetch=globalThis.fetch;
globalThis.fetch=async input=>{
  const url=typeof input==='string'?input:input.url;
  if(url.includes('aviary-birds-layout.json'))return new Response(JSON.stringify(meta),{headers:{'Content-Type':'application/json'}});
  if(url.includes('greater-flamingo.glb'))return new Response(bytes,{headers:{'Content-Type':'model/gltf-binary','Content-Length':String(bytes.length)}});
  return nativeFetch(input);
};
const {createAviaryBirds}=await import('../../../viewer/aviary-birds.js');
const parent=new T.Group();parent.visible=true;let changes=0;
const birds=createAviaryBirds(parent,()=>changes++,{base:'http://localhost/models/',anchor:meta.anchor});
const focus=birds.focusPoint(),camera=new T.PerspectiveCamera(44,1280/720,.1,1000);camera.up.set(0,0,1);camera.position.set(focus[0],focus[1]-8,3.5);camera.lookAt(focus[0],focus[1],.6);camera.updateMatrixWorld();
birds.update(0,camera,720,32);
for(let i=0;i<100&&birds.status()!=='ready';i++)await new Promise(resolve=>setTimeout(resolve,10));
assert.equal(birds.status(),'ready');
for(let i=1;i<=7200;i++)birds.update(i*1000/60,camera,720,32);
const initial=birds.getDebugSnapshot();assert.ok(initial.actors.some(a=>a.changes>0));assert.ok(new Set(initial.actors.map(a=>a.bones)).size===4);
assert.ok(initial.visible);assert.equal(initial.actors.length,4);
let now=121000;
for(const kind of ['hidden','paused','disabled','parent-hidden','out-of-frame']){
  if(kind==='hidden')document.hidden=true;
  if(kind==='paused')birds.setPaused(true);
  if(kind==='disabled')birds.setEnabled(false);
  if(kind==='parent-hidden')parent.visible=false;
  if(kind==='out-of-frame'){camera.lookAt(focus[0],focus[1]-100,.6);camera.updateMatrixWorld();}
  const before=birds.getDebugSnapshot().actors;
  for(let i=0;i<120;i++){birds.update(now,camera,720,32);now+=1000/60;}
  const after=birds.getDebugSnapshot().actors;
  for(let i=0;i<4;i++){assert.equal(before[i].time,after[i].time,kind+' freezes clip');assert.deepEqual(before[i].position,after[i].position,'no ground drift');}
  document.hidden=false;birds.setPaused(false);birds.setEnabled(true);parent.visible=true;camera.lookAt(focus[0],focus[1],.6);camera.updateMatrixWorld();birds.update(now,camera,720,32);now+=1000/60;
}
const report={assetSha256:meta.assetSha256,animals:4,triangles:48160,jointsPerAnimal:5,sharedGeometry:true,sharedMaterialsAndTextures:true,independentSkeletons:true,groundMinM:groundMin,groundMaxM:groundMax,maxFootDriftM:maxFootDrift,clips:maximumDisplacement,loopSeamM:loopSeam,groundByClip:minima,runtimeSeconds:120,runtimeStateChecks:['hidden','paused','disabled','parent-hidden','out-of-frame'],runtimeNoGroundDrift:true,behaviorChanges:initial.actors.map(a=>a.changes),gpuPerformanceMeasured:false,scope:'CPU actual skinned geometry and runtime behavior; not physical phone FPS or veterinary behavioral validation'};
await fs.writeFile(new URL('bird-verification.json',here),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
