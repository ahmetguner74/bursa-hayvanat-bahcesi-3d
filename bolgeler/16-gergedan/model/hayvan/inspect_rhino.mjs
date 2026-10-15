import {readFileSync,writeFileSync} from 'node:fs';
import {T,loadGLB} from '../../../15-penguen/model/hayvan/load_local_gltf.mjs';
const gltf=await loadGLB(readFileSync(new URL('./source/absol-white-rhinoceros-1k-original.glb',import.meta.url)));
const mixer=new T.AnimationMixer(gltf.scene),meshes=[],bones=[];
gltf.scene.traverse(node=>{if(node.isSkinnedMesh)meshes.push(node);if(node.isBone)bones.push(node.name);});
const point=new T.Vector3(),box=new T.Box3();
function bounds(){
  gltf.scene.updateMatrixWorld(true);for(const mesh of meshes)mesh.skeleton.update();box.makeEmpty();
  for(const mesh of meshes)for(let i=0;i<mesh.geometry.attributes.position.count;i++)box.expandByPoint(mesh.getVertexPosition(i,point).applyMatrix4(mesh.matrixWorld));
  return [box.min.toArray(),box.max.toArray()];
}
const rest=bounds(),clips=[];
for(const clip of gltf.animations){
  mixer.stopAllAction();mixer.clipAction(clip).play();const samples=[];
  for(let i=0;i<=512;i++){mixer.setTime(clip.duration*i/512);samples.push({time:clip.duration*i/512,bounds:bounds()});}
  const translations=clip.tracks.filter(t=>t.name.endsWith('.position')).map(t=>({name:t.name,first:Array.from(t.values.slice(0,3)),last:Array.from(t.values.slice(-3))}));
  clips.push({name:clip.name,duration:clip.duration,samples,translations});
}
const result={meshes:meshes.map(m=>({name:m.name,vertices:m.geometry.attributes.position.count,triangles:(m.geometry.index?.count||m.geometry.attributes.position.count)/3,joints:m.skeleton.bones.length})),bones,rest,clips};
writeFileSync(new URL('./rig-inspection.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({meshes:result.meshes,rest,clips:clips.map(c=>({name:c.name,duration:c.duration,first:c.samples[0].bounds,last:c.samples.at(-1).bounds,translations:c.translations.slice(0,8)})),bones}));
