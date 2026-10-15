import {readFileSync,writeFileSync} from 'node:fs';
import {T,loadGLB} from './load_local_gltf.mjs';
const gltf=await loadGLB(readFileSync(new URL('./source/major-african-penguin-original.glb',import.meta.url)));
const mixer=new T.AnimationMixer(gltf.scene),meshes=[];
gltf.scene.traverse(node=>{if(node.isSkinnedMesh)meshes.push(node);});
const point=new T.Vector3(),bounds=new T.Box3();
function poseBounds(){
  gltf.scene.updateMatrixWorld(true);for(const mesh of meshes)mesh.skeleton.update();bounds.makeEmpty();
  for(const mesh of meshes)for(let i=0;i<mesh.geometry.attributes.position.count;i++)bounds.expandByPoint(mesh.getVertexPosition(i,point).applyMatrix4(mesh.matrixWorld));
  return [bounds.min.toArray(),bounds.max.toArray()];
}
const clips=[];
for(const clip of gltf.animations){
  mixer.stopAllAction();const action=mixer.clipAction(clip).play();const samples=[];
  for(let i=0;i<=20;i++){
    mixer.setTime(clip.duration*i/20);const box=poseBounds();
    const bones={};for(const name of ['Root_01','Penguin_02','Toe_R_08','Toe_L_017','AnimalHead_027'])bones[name]=gltf.scene.getObjectByName(name)?.getWorldPosition(new T.Vector3()).toArray();
    let bodyGround=Infinity;
    for(let vertex=0;vertex<meshes[0].geometry.attributes.position.count;vertex++)bodyGround=Math.min(bodyGround,meshes[0].getVertexPosition(vertex,point).applyMatrix4(meshes[0].matrixWorld).y);
    samples.push({time:clip.duration*i/20,bounds:box,bodyGround,bones});
  }
  clips.push({name:clip.name,duration:clip.duration,samples});
}
const proof={meshes:meshes.map(m=>({name:m.name,triangles:(m.geometry.index?.count||m.geometry.attributes.position.count)/3,bones:m.skeleton.bones.length})),clips};
writeFileSync(new URL('./rig-inspection.json',import.meta.url),JSON.stringify(proof,null,2)+'\n');
console.log(JSON.stringify({meshes:proof.meshes,clips:clips.map(c=>({name:c.name,duration:c.duration,firstBounds:c.samples[0].bounds,bodyGround:c.samples[0].bodyGround}))}));
