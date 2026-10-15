import {readFileSync,writeFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {T,loadGLB} from '../../15-penguen/model/hayvan/load_local_gltf.mjs';
const asset=await loadGLB(readFileSync(new URL('./hayvan/white-rhinoceros.glb',import.meta.url)));
const meta=JSON.parse(readFileSync(new URL('./hayvan/source-manifest.json',import.meta.url)));
const mixer=new T.AnimationMixer(asset.scene),clip=asset.animations[0],action=mixer.clipAction(clip).play();
const point=new T.Vector3(),meshes=[];asset.scene.traverse(node=>{if(node.isSkinnedMesh)meshes.push(node);});
assert.equal(meshes.length,1);assert.equal(meshes[0].skeleton.bones.length,46);assert.equal(meshes[0].geometry.index.count/3,9310);
const lut=meta.clips[0].groundOffsetMetres;let minimum=Infinity,maximum=-Infinity;
let first=null,last=null;
for(let i=0;i<=240;i++){
  const t=clip.duration*i/240;mixer.setTime(t);
  const phase=(t%clip.duration)/clip.duration*(lut.length-1),index=Math.floor(phase),fraction=phase-index;
  asset.scene.position.y=lut[index]*(1-fraction)+lut[Math.min(index+1,lut.length-1)]*fraction;
  asset.scene.updateMatrixWorld(true);let low=Infinity;const positions=[];
  for(const mesh of meshes){mesh.skeleton.update();for(let j=0;j<mesh.geometry.attributes.position.count;j++){
    mesh.getVertexPosition(j,point).applyMatrix4(mesh.matrixWorld);low=Math.min(low,point.y);
    if(i===0||i===240)positions.push(...point.toArray());
  }}
  minimum=Math.min(minimum,low);maximum=Math.max(maximum,low);if(i===0)first=positions;if(i===240)last=positions;
}
const seam=Math.max(...first.map((v,i)=>Math.abs(v-last[i])));
assert.ok(minimum>-.004&&maximum<.004,JSON.stringify({minimum,maximum}));assert.ok(seam<1e-5);
const habitat=JSON.parse(readFileSync(new URL('./model-report.json',import.meta.url)));
assert.equal(habitat.groundPartition.overlapM2,0);assert.ok(habitat.groundPartition.uncoveredM2<1e-7);
const proof={samples:241,triangles:9310,joints:46,groundMinMetres:minimum,groundMaxMetres:maximum,loopSeamMaxMetres:seam,
  groundPartition:habitat.groundPartition,scope:'Actual skinned geometry and loop seam; not a natural locomotion/foot-slip certification or GPU benchmark'};
writeFileSync(new URL('./verification.json',import.meta.url),JSON.stringify(proof,null,2)+'\n');console.log(JSON.stringify(proof));
