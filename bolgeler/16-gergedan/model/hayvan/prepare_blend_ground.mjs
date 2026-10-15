// Offline contact lookup from the actual skinned animation; no vertex loop at runtime.
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {T,loadGLB} from '../../../15-penguen/model/hayvan/load_local_gltf.mjs';
const {createRhinoIdleClip}=await import('../../../../viewer/rhinos.js');
const bytes=readFileSync(new URL('./white-rhinoceros.glb',import.meta.url)),g=await loadGLB(bytes),mixer=new T.AnimationMixer(g.scene),walk=mixer.clipAction(g.animations[0]).play(),idle=mixer.clipAction(createRhinoIdleClip(g.scene)).play(),point=new T.Vector3();let mesh;g.scene.traverse(n=>{if(n.isSkinnedMesh)mesh=n;});
const values=[],phaseSegments=512,weightSegments=16;
for(let phase=0;phase<=phaseSegments;phase++){
  const row=[];
  for(let weight=0;weight<=weightSegments;weight++){
    walk.time=(phase%phaseSegments)/phaseSegments*g.animations[0].duration;idle.time=2;
    walk.setEffectiveWeight(weight/weightSegments);idle.setEffectiveWeight(1-weight/weightSegments);mixer.update(0);g.scene.updateMatrixWorld(true);mesh.skeleton.update();let low=Infinity;
    for(let v=0;v<mesh.geometry.attributes.position.count;v++)low=Math.min(low,mesh.getVertexPosition(v,point).applyMatrix4(mesh.matrixWorld).y);
    row.push(-low);
  }values.push(row);
}
const result={assetSha256:createHash('sha256').update(bytes).digest('hex'),duration:g.animations[0].duration,phaseSegments,weightSegments,values,scope:'Actual skin ground height while blending source walk and generated neutral idle. Precomputed to avoid per-frame vertex skinning.'};
writeFileSync(new URL('./blend-ground.json',import.meta.url),JSON.stringify(result)+'\n');console.log(JSON.stringify({poses:values.length*(weightSegments+1),phaseSegments,weightSegments}));
