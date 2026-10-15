import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {T,loadGLB} from '../../15-penguen/model/hayvan/load_local_gltf.mjs';
const {createRhinoMotion,rhinoBlendGround}=await import('../../../viewer/rhino-motion.js');
const {createRhinoIdleClip,createRhinos}=await import('../../../viewer/rhinos.js');
const meta=JSON.parse(readFileSync(new URL('./colony-layout.json',import.meta.url)));
const asset=JSON.parse(readFileSync(new URL('./hayvan/source-manifest.json',import.meta.url)));
const inside=(ring,x,y)=>{let b=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],c=ring[j];if((a[1]>y)!==(c[1]>y)&&x<(c[0]-a[0])*(y-a[1])/(c[1]-a[1])+a[0])b=!b;}return b;};
const allowed=b=>meta.safeDomain.some(p=>inside(p.outer,b.x,b.y)&&!p.holes.some(h=>inside(h,b.x,b.y)));
const birds=meta.routes.map((_,i)=>createRhinoMotion(meta,i));let minDistance=Infinity,maxStep=0,walkSamples=0,idleSamples=0,travel=0;
for(let i=0;i<72000;i++){
  if(i%1000===0)for(const b of birds)b.request(8);
  for(const b of birds){const x=b.x,y=b.y;b.update(1/60,birds);assert.ok(allowed(b),'Rhino left eroded safe floor');const d=Math.hypot(x-b.x,y-b.y);maxStep=Math.max(maxStep,d);travel+=d;if(b.clip==='walk')walkSamples++;else idleSamples++;}
  minDistance=Math.min(minDistance,Math.hypot(birds[0].x-birds[1].x,birds[0].y-birds[1].y));
}
assert.ok(minDistance>=meta.minimumSeparationMetres);assert.ok(maxStep<.01);assert.ok(travel>200&&walkSamples>0&&idleSamples>0);
const gltf=await loadGLB(readFileSync(new URL('./hayvan/white-rhinoceros.glb',import.meta.url))),idle=createRhinoIdleClip(gltf.scene),mixer=new T.AnimationMixer(gltf.scene),walk=mixer.clipAction(gltf.animations[0]),rest=mixer.clipAction(idle),point=new T.Vector3();let mesh;
gltf.scene.traverse(n=>{if(n.isSkinnedMesh)mesh=n;});let blendGroundMin=Infinity,blendGroundMax=-Infinity;
for(const phase of [.2,1.1,2.1,3.1,4.1]){
  mixer.stopAllAction();walk.reset().play();walk.time=phase;mixer.update(0);rest.reset().play();walk.crossFadeTo(rest,1,false);
  for(let i=0;i<64;i++){
    mixer.update(1/60);const w=walk.isRunning()?walk.getEffectiveWeight():0;gltf.scene.position.y=rhinoBlendGround(meta.blendGround,walk.time,w);gltf.scene.updateMatrixWorld(true);mesh.skeleton.update();let low=Infinity;
    for(let v=0;v<mesh.geometry.attributes.position.count;v++)low=Math.min(low,mesh.getVertexPosition(v,point).applyMatrix4(mesh.matrixWorld).y);
    blendGroundMin=Math.min(blendGroundMin,low);blendGroundMax=Math.max(blendGroundMax,low);
  }
}
assert.ok(blendGroundMin>-.004&&blendGroundMax<.004,JSON.stringify({blendGroundMin,blendGroundMax}));
globalThis.location={search:''};globalThis.document={hidden:false};globalThis.innerWidth=1280;
const parent=new T.Group(),runtime=createRhinos(parent,()=>{},{base:'http://127.0.0.1:8768/models/'}),camera=new T.PerspectiveCamera(50,16/9,.1,500);camera.up.set(0,0,1);camera.position.set(-30,65,15);camera.lookAt(-43,94,0);camera.updateMatrixWorld(true);
runtime.update(0,camera,720,16);
for(let i=0;i<500&&runtime.status()==='loading';i++)await new Promise(r=>setTimeout(r,10));
assert.equal(runtime.status(),'ready');for(let i=1;i<=90;i++)runtime.update(i*1000/60,camera,720,16);
const before=runtime.focusPoint();runtime.setPaused(true);runtime.update(60000,camera,720,16);assert.deepEqual(runtime.focusPoint(),before);runtime.setPaused(false);document.hidden=true;runtime.update(90000,camera,720,16);assert.deepEqual(runtime.focusPoint(),before);document.hidden=false;runtime.update(90017,camera,720,16);const resumeJump=Math.hypot(...runtime.focusPoint().map((v,i)=>v-before[i]));assert.ok(resumeJump<.02);
const proof={simulationSeconds:1200,updates:144000,minDistanceMetres:minDistance,maxStepMetres:maxStep,totalTravelMetres:travel,walkSamples,idleSamples,blendGroundMinMetres:blendGroundMin,blendGroundMaxMetres:blendGroundMax,pauseHiddenAndResumePassed:true,resumeJumpMetres:resumeJump,scope:'Actual source skin,controller and runtime loading; no GPU or physical phone benchmark'};
writeFileSync(new URL('./colony-verification.json',import.meta.url),JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify(proof));
