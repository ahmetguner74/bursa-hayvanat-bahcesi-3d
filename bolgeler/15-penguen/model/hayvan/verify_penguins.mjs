import {readFileSync,writeFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {T,loadGLB} from './load_local_gltf.mjs';
import {createPenguinBehavior,insideDomain,groundOffset} from '../../../../viewer/penguin-motion.js';
const require=createRequire(import.meta.url),validator=require('../../../_qa/gltf-check/node_modules/gltf-validator');
const file=new URL('./african-penguin.glb',import.meta.url),bytes=readFileSync(file),meta=JSON.parse(readFileSync(new URL('./colony-layout.json',import.meta.url)));
const validation=await validator.validateBytes(new Uint8Array(bytes),{uri:'african-penguin.glb',maxIssues:100});
writeFileSync(new URL('./gltf-validation.json',import.meta.url),JSON.stringify(validation,null,2)+'\n');
if(validation.issues.numErrors||validation.issues.numWarnings)throw Error('GLB errors/warnings');
const birds=[...meta.landStarts,...meta.waterStarts].map((_,i)=>createPenguinBehavior(meta,i));
const states=new Set();let maximumMove=0,minimumSeparation=Infinity;
for(let frame=0;frame<18000;frame++)for(const bird of birds){
  const [x,y]=[bird.x,bird.y];bird.update(1/30,birds);states.add(bird.clip);
  maximumMove=Math.max(maximumMove,Math.hypot(bird.x-x,bird.y-y));
  if(!insideDomain(bird.water?meta.waterDomain:meta.groundDomain,bird.x,bird.y))throw Error('Bird left its safe domain');
  if(bird.dive<0||bird.dive>.501)throw Error('Dive outside basin depth');
  for(const other of birds)if(other!==bird&&other.water===bird.water)minimumSeparation=Math.min(minimumSeparation,Math.hypot(bird.x-other.x,bird.y-other.y));
}
if(!['Walk','Idle','Preen','Shake','Penguin swim'].every(name=>states.has(name)))throw Error('Behavior states missing');
if(maximumMove>.025||minimumSeparation<.63)throw Error('Motion continuity or separation failed');
const gltf=await loadGLB(bytes),mixer=new T.AnimationMixer(gltf.scene),meshes=[];
gltf.scene.traverse(n=>{if(n.isSkinnedMesh)meshes.push(n);});
let minimumGround=Infinity,maximumGround=-Infinity,maximumHeight=0;
const point=new T.Vector3(),clipProof=[];
for(const clip of gltf.animations){
  if(clip.name==='Penguin swim')continue;
  mixer.stopAllAction();mixer.clipAction(clip).play();let min=Infinity,max=-Infinity;
  for(let step=0;step<96;step++){
    const time=clip.duration*step/96;mixer.setTime(time);gltf.scene.position.y=groundOffset(meta.clips,clip.name,time);gltf.scene.updateMatrixWorld(true);
    let y=Infinity,top=-Infinity;
    for(const mesh of meshes){mesh.skeleton.update();for(let i=0;i<mesh.geometry.attributes.position.count;i++){mesh.getVertexPosition(i,point).applyMatrix4(mesh.matrixWorld);if(!Number.isFinite(point.lengthSq()))throw Error('Nonfinite animated vertex');if(mesh.name==='Object_9')y=Math.min(y,point.y);top=Math.max(top,point.y);}}
    min=Math.min(min,y);max=Math.max(max,y);maximumHeight=Math.max(maximumHeight,top);
  }
  minimumGround=Math.min(minimumGround,min);maximumGround=Math.max(maximumGround,max);clipProof.push({clip:clip.name,minFootMetres:min,maxFootMetres:max});
}
if(minimumGround<-.025||maximumGround>.025)throw Error('Grounding error exceeds 2.5cm');
const {clone}=await import('../../../../vendor/utils/SkeletonUtils.js');
const copy=clone(gltf.scene),copyMeshes=[];copy.traverse(n=>{if(n.isSkinnedMesh)copyMeshes.push(n);});
for(let i=0;i<meshes.length;i++)if(copyMeshes[i].skeleton.bones[0]===meshes[i].skeleton.bones[0]||copyMeshes[i].geometry!==meshes[i].geometry||copyMeshes[i].material!==meshes[i].material)throw Error('Skeleton/geometry sharing failed');
const proof={revision:'20261015ai',simulationSeconds:600,samples:18000*birds.length,states:[...states],maximumMovementPer30HzStepMetres:maximumMove,minimumSameDomainSeparationMetres:minimumSeparation,grounding:{minimumGround,maximumGround,clipProof},maximumAnimatedHeightMetres:maximumHeight,independentSkeletons:true,sharedGeometryAndMaterials:true,trianglesPerBird:meta.trianglesPerBird,colonyTriangles:meta.trianglesPerBird*birds.length,gltfIssues:validation.issues};
writeFileSync(new URL('./verification.json',import.meta.url),JSON.stringify(proof,null,2)+'\n');
console.log(JSON.stringify({...proof,gltfIssues:{errors:validation.issues.numErrors,warnings:validation.issues.numWarnings},grounding:{minimumGround,maximumGround}}));
