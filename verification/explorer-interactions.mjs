import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {T} from '../bolgeler/15-penguen/model/hayvan/load_local_gltf.mjs';

const base='http://127.0.0.1:8768/',NativeRequest=globalThis.Request,nativeFetch=globalThis.fetch;
globalThis.Request=class extends NativeRequest{constructor(input,options){super(typeof input==='string'?new URL(input,base):input,options);}};
globalThis.fetch=(input,options)=>nativeFetch(typeof input==='string'?new URL(input,base):input,options);
globalThis.document={hidden:false};globalThis.location={search:''};globalThis.innerWidth=1280;
const {createPenguins}=await import('../viewer/penguins.js');
const {createRhinos}=await import('../viewer/rhinos.js');
const {createGiraffes}=await import('../viewer/giraffes.js');
const {createAviaryBirds}=await import('../viewer/aviary-birds.js');
const types=[
  ['penguin',createPenguins,15,5,[-7,123.5,.2]],
  ['rhino',createRhinos,16,2,[-43,94,1]],
  ['giraffe',createGiraffes,12,2,[49,41,2.3]],
  ['aviary',createAviaryBirds,32,4,[-35,-76,.6]],
];
const result={revision:'20261016au',scope:'Actual production runtimes + local GLB bytes on CPU. No GPU/physical-phone benchmark.',species:{}};
for(const [key,factory,region,count,at] of types){
  const parent=new T.Group(),camera=new T.PerspectiveCamera(56,16/9,.12,2000);camera.up.set(0,0,1);
  camera.position.set(at[0]+5,at[1]-10,at[2]+4);camera.lookAt(...at);camera.updateMatrixWorld(true);
  const runtime=factory(parent,()=>{},{touchDevice:true});runtime.setInteractive(true);runtime.update(0,camera,720,region);
  for(let i=0;i<500&&runtime.status()==='loading';i++)await new Promise(resolve=>setTimeout(resolve,10));
  assert.equal(runtime.status(),'ready',key+' must load');
  let now=1;
  const run=seconds=>{for(let i=0;i<Math.ceil(seconds*60);i++){now+=1000/60;runtime.update(now,camera,720,region);}};
  run(.1);assert.equal(runtime.animals().length,count);
  const idle=runtime.getDebugSnapshot().stats.poseUpdates;run(5);assert.equal(runtime.getDebugSnapshot().stats.poseUpdates,idle,key+' must freeze at rest');
  const animal=runtime.animals()[0],height=animal.height;
  camera.position.set(animal.point[0]+height,animal.point[1]-height*3,animal.point[2]+height);camera.lookAt(...animal.point);camera.updateMatrixWorld(true);run(.1);
  const ndc=new T.Vector3(...animal.point).project(camera),ray=new T.Raycaster();ray.setFromCamera(new T.Vector2(ndc.x,ndc.y),camera);
  assert.equal(runtime.pick(ray,camera,720),0,key+' real mesh must be tappable');
  assert(runtime.select(0));run(1.5);
  const oldRandom=Math.random;Math.random=()=>.9999;
  assert(runtime.tap(0));Math.random=oldRandom;
  const before=runtime.animals()[0].point.slice(),updates=runtime.getDebugSnapshot().stats.poseUpdates;run(2);
  const after=runtime.animals()[0].point.slice(),poseUpdates=runtime.getDebugSnapshot().stats.poseUpdates-updates;
  assert(poseUpdates>=58&&poseUpdates<=61,key+' near touch pose updates must be 30 Hz');
  const travel=Math.hypot(after[0]-before[0],after[1]-before[1]);
  if(['rhino','giraffe'].includes(key))assert(travel>.05,key+' walk must travel');
  const metadata=runtime.metadata?.()||await fetch(base+'models/penguin-colony.json').then(r=>r.json()),vertex=new T.Vector3();
  let groundMin=Infinity,groundMax=-Infinity;
  for(let sample=0;sample<32;sample++){
    run(.25);parent.updateMatrixWorld(true);
    let low=Infinity;
    parent.children[0].children[0].traverse(mesh=>{
      if(!mesh.isSkinnedMesh)return;mesh.skeleton.update();
      // Source feather cards contain transparent padding below the feet.
      // Match the asset's documented body/foot reference, not their quad bounds.
      if(key==='penguin'&&mesh.name!=='Object_9')return;
      for(let i=0;i<mesh.geometry.attributes.position.count;i++)low=Math.min(low,mesh.getVertexPosition(i,vertex).applyMatrix4(mesh.matrixWorld).z-metadata.groundZ);
    });
    groundMin=Math.min(groundMin,low);groundMax=Math.max(groundMax,low);
  }
  assert(groundMin>-.008&&groundMax<.008,key+' actual skin must stay grounded: '+JSON.stringify({groundMin,groundMax}));
  runtime.tap(0);run(.2);
  const beforeHiddenPoint=runtime.animals()[0].point.slice();
  document.hidden=true;const hidden=JSON.stringify(runtime.getDebugSnapshot().actors);run(30);assert.equal(JSON.stringify(runtime.getDebugSnapshot().actors),hidden);document.hidden=false;
  run(1/60);const resumed=runtime.animals()[0].point;
  assert(Math.hypot(...resumed.map((v,i)=>v-beforeHiddenPoint[i]))<.03,key+' resume must not jump');
  for(let i=0;i<25;i++){runtime.tap(0);run(.12);}
  run(35);assert(!runtime.getDebugSnapshot().actors.some(a=>a.active),key+' rapid taps must settle');
  runtime.clearSelection();run(3);const settled=runtime.getDebugSnapshot().stats.poseUpdates;run(10);assert.equal(runtime.getDebugSnapshot().stats.poseUpdates,settled,key+' settled actors must stop updates');
  runtime.setInteractive(false);assert.equal(runtime.select(0),false);
  const meshes=[];parent.traverse(n=>{if(n.isSkinnedMesh)meshes.push(n);});
  const first=meshes[0],other=meshes.find(n=>n!==first&&n.geometry===first.geometry);
  assert(other&&other.skeleton.bones[0]!==first.skeleton.bones[0],key+' rigs must be independent with shared geometry');
  result.species[key]={animals:count,idlePoseUpdates:0,actualMeshPicking:true,touchUpdatesInTwoSeconds:poseUpdates,travelMetres:travel,actualSkinGrounding:{reference:key==='penguin'?metadata.groundingReference:'Lowest skinned vertex',minimumMetres:groundMin,maximumMetres:groundMax},hiddenFrozen:true,rapidTapsSettle:true,settledPoseUpdates:0,independentRigsSharedGeometry:true};
}
writeFileSync(new URL('./explorer-interactions.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
