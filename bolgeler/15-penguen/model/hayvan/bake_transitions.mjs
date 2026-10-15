// Offline grounding for the actual blended GLB poses. Runtime performs only
// a bilinear lookup, never a CPU loop over the skinned penguin vertices.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {T,loadGLB} from './load_local_gltf.mjs';

const file=new URL('./penguin-transitions.json',import.meta.url),bytes=readFileSync(new URL('./african-penguin.glb',import.meta.url));
const sha256=createHash('sha256').update(bytes).digest('hex'),phaseSegments=128,weightSegments=16;
const pairs=[['Idle','Idle'],['Idle','Shake'],['Idle','Preen'],['Idle','Sit1'],['Preen','Idle'],['Shake','Idle'],['Sit1','Sleep'],['Sit1','Idle'],['Sleep','Sit1'],['Sleep','Idle']];
if(existsSync(file)){
  const cached=JSON.parse(readFileSync(file));
  if(cached.schema==='bursa-zoo-penguin-transition-ground/v1'&&cached.assetSha256===sha256&&cached.phaseSegments===phaseSegments&&cached.weightSegments===weightSegments&&pairs.every(([a,b])=>cached.tables[a+'>'+b]?.values.length===phaseSegments+1)){
    console.log(JSON.stringify({transitionGround:'cached',bytes:readFileSync(file).length,assetSha256:sha256}));process.exit(0);
  }
}
const gltf=await loadGLB(bytes),mixer=new T.AnimationMixer(gltf.scene),body=gltf.scene.getObjectByName('Object_9'),point=new T.Vector3();
if(!body?.isSkinnedMesh)throw Error('Penguin body skin missing');
const clips=new Map(gltf.animations.map(clip=>[clip.name,clip]));
const result={schema:'bursa-zoo-penguin-transition-ground/v1',assetSha256:sha256,phaseSegments,weightSegments,tables:{},scope:'Actual body skin minimum Y. From-pose phase and blend weight, target-pose phase zero. Original GLB bytes unchanged.'};
for(const [from,to] of pairs){
  mixer.stopAllAction();
  const source=clips.get(from),target=clips.get(to),a=mixer.clipAction(source);
  const b=mixer.clipAction(new T.AnimationClip(to+' blend bake',target.duration,target.tracks));
  a.play();b.play();a.paused=true;b.paused=true;
  const values=[];
  for(let phase=0;phase<=phaseSegments;phase++){
    const row=[];
    for(let weight=0;weight<=weightSegments;weight++){
      a.time=phase===phaseSegments?0:source.duration*phase/phaseSegments;b.time=0;
      a.setEffectiveWeight(1-weight/weightSegments);b.setEffectiveWeight(weight/weightSegments);mixer.update(0);gltf.scene.updateMatrixWorld(true);body.skeleton.update();
      let min=Infinity;
      for(let i=0;i<body.geometry.attributes.position.count;i++)min=Math.min(min,body.getVertexPosition(i,point).applyMatrix4(body.matrixWorld).y);
      row.push(Math.round(-min*1e6)/1e6);
    }
    values.push(row);
  }
  result.tables[from+'>'+to]={duration:source.duration,values};
}
writeFileSync(file,JSON.stringify(result)+'\n');
console.log(JSON.stringify({transitionGround:'baked',pairs:pairs.length,bytes:readFileSync(file).length,assetSha256:sha256}));
