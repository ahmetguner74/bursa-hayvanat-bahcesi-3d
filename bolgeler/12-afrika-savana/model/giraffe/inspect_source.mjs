import {readFileSync,writeFileSync} from 'node:fs';
import {T,loadGLB} from '../../../15-penguen/model/hayvan/load_local_gltf.mjs';
const gltf=await loadGLB(readFileSync(new URL('./source/bluemesh-giraffe-1k-original.glb',import.meta.url)));
const meshes=[];gltf.scene.traverse(n=>{if(n.isSkinnedMesh)meshes.push(n)});
const mix=new T.AnimationMixer(gltf.scene),clip=gltf.animations[0],a=mix.clipAction(clip);a.play();
let p=new T.Vector3();let samples=[];
for(let i=0;i<=96;i++){mix.setTime(i*clip.duration/96);gltf.scene.updateMatrixWorld(true);meshes.forEach(m=>m.skeleton.update());let box=new T.Box3();for(let m of meshes)for(let k=0;k<m.geometry.attributes.position.count;k++)box.expandByPoint(m.getVertexPosition(k,p).applyMatrix4(m.matrixWorld));samples.push({t:i*clip.duration/96,bounds:[box.min.toArray(),box.max.toArray()]});}
const result={meshes:meshes.map(m=>({name:m.name,vertices:m.geometry.attributes.position.count,bones:m.skeleton.bones.map(b=>b.name)})),duration:clip.duration,tracks:clip.tracks.map(t=>({name:t.name,n:t.times.length,first:Array.from(t.values.slice(0,t.getValueSize())),last:Array.from(t.values.slice(-t.getValueSize()))})),samples};
writeFileSync(new URL('./source-inspection.json',import.meta.url),JSON.stringify(result,null,2));console.log(JSON.stringify({duration:clip.duration,meshes:result.meshes,first:samples[0],last:samples.at(-1),pos:result.tracks.filter(t=>t.name.endsWith('.position'))}));
