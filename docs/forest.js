import * as T from 'three';
import {GLTFLoader} from './vendor/loaders/GLTFLoader.js';
import {WOODLAND_LIGHT} from './lighting.js?v=20261015af';

// Offline CC0 derivative. A single source asset supplies six instanced draws;
// each tree appears in exactly one LOD. Original source XY is never changed.
export async function createForest(candidates,renderer,mode='mesh'){
  const specs=candidates.flatMap(batch=>batch.specs);
  const metadata=mode==='impostor'?await fetch('./assets/forest-impostor-metadata.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Uzak ağaç verisi eksik');return r.json();}):null;
  if(metadata){
    const expected={hemisphere:[WOODLAND_LIGHT.sky,WOODLAND_LIGHT.ground,WOODLAND_LIGHT.hemisphere],sun:[WOODLAND_LIGHT.sun,WOODLAND_LIGHT.sunIntensity],direction:WOODLAND_LIGHT.direction,shadowIntensity:WOODLAND_LIGHT.shadowIntensity,shadowRadius:WOODLAND_LIGHT.shadowRadius,toneMapping:'none'};
    if(JSON.stringify(metadata.lighting)!==JSON.stringify(expected))throw Error('Uzak ağaç ışığı güncel sahneyle eşleşmiyor; yerel atlas yeniden üretilmeli');
  }
  const assetVersion=metadata?.renderSourceGltfSha256?.slice(0,16)||'20261015af';
  const [asset,impostors]=await Promise.all([
    new GLTFLoader().loadAsync('./models/generic-broadleaf-tree.glb?v='+assetVersion),
    metadata?(await import('./forest-impostors.js?v=20261015af')).createImpostorLayer(specs.length,renderer,metadata):null,
  ]);
  asset.scene.updateMatrixWorld(true);
  const parts=[[],[]],zUp=new T.Matrix4().makeRotationX(Math.PI/2);
  const bounds=new T.Box3(),nearBounds=new T.Box3();let radialExtent=0,nearRadialExtent=0;
  asset.scene.traverse(node=>{
    if(!node.isMesh)return;
    const lod=node.userData.lod;
    if(lod!==0&&lod!==1)throw Error('Ağaç ayrıntı düzeyi eksik');
    const geometry=node.geometry.clone().applyMatrix4(node.matrixWorld).applyMatrix4(zUp);
    geometry.computeBoundingBox();bounds.union(geometry.boundingBox);if(lod===0)nearBounds.union(geometry.boundingBox);
    const position=geometry.getAttribute('position');
    for(let i=0;i<position.count;i++){
      const radius=Math.hypot(position.getX(i),position.getY(i));radialExtent=Math.max(radialExtent,radius);
      if(lod===0)nearRadialExtent=Math.max(nearRadialExtent,radius);
    }
    const material=node.material;
    for(const texture of [material.map,material.normalMap,material.roughnessMap])if(texture)texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
    if(material.alphaTest>0)material.alphaToCoverage=true;
    parts[lod].push({geometry,material,leaf:node.name.endsWith('leaves')});
  });
  if(parts.some(lod=>lod.length!==3)||radialExtent<=0)throw Error('Ağaç modeli tamamlanamadı');
  const group=new T.Group();group.name='CC0 dallanan ağaçlar · görsel yorum';
  group.userData.source='https://polyhaven.com/a/jacaranda_tree';
  group.userData.license='CC0';
  if(impostors)group.add(impostors.mesh);
  const meshes=parts.map((lod,level)=>lod.map(part=>{
    const mesh=new T.InstancedMesh(part.geometry,part.material,Math.max(1,specs.length));
    mesh.name=`Peyzaj ağacı · LOD${level} · ${part.leaf?'yaprak':'gövde/dal'}`;
    mesh.instanceMatrix.setUsage(T.DynamicDrawUsage);mesh.count=0;
    mesh.castShadow=true;mesh.receiveShadow=true;mesh.frustumCulled=false;group.add(mesh);return mesh;
  }));
  const canonicalBounds=impostors?nearBounds:bounds,canonicalRadius=impostors?nearRadialExtent:radialExtent;
  const height=canonicalBounds.max.z-canonicalBounds.min.z;
  if(impostors&&(Math.abs(impostors.metadata.sourceHeight-height)>1e-4||Math.abs(impostors.metadata.sourceRadialExtent-canonicalRadius)>1e-4))throw Error('Yakın ve uzak ağaç kaynakları eşleşmiyor');
  const d=new T.Object3D(),matrix=new T.Matrix4(),frustum=new T.Frustum();
  const sphere=new T.Sphere(),tint=new T.Color(),cameraPoint=new T.Vector3();
  const entries=specs.map(spec=>{
    // Existing r positions the old canopy lobes; its full silhouette reached
    // about1.6r. Preserve that visual span rather than shrinking it to r.
    const xy=spec.r*1.6/canonicalRadius,z=spec.h/height;
    d.position.set(spec.x,spec.y,-.24-canonicalBounds.min.z*z);
    d.rotation.set(0,0,spec.seed*.381966);d.scale.set(xy,xy,z);d.updateMatrix();
    // Both LODs use the same bounded green tint for this tree.
    const variation=.93+(Math.abs(spec.seed)%13)/130;
    const warmth=((Math.abs(spec.seed>>>4)%11)-5)/50;
    tint.setRGB(variation*(1+warmth*.5),variation*(1+warmth*.15),variation*(1-warmth*.8));
    return {spec,matrix:d.matrix.clone(),color:tint.clone(),level:1};
  });
  group.userData.treeCount=entries.length;
  // Hide fallback geometry only after the complete replacement is available.
  for(const candidate of candidates)candidate.legacy.visible=false;
  function prepare(camera,viewportHeight){
    camera.updateMatrixWorld();
    matrix.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);frustum.setFromProjectionMatrix(matrix);
    const counts=[0,0];
    for(const entry of entries){
      const {x,y,h,r}=entry.spec;
      sphere.center.set(x,y,-.24+h*.5);sphere.radius=Math.hypot(r*1.6,h*.5)+6;
      if(!frustum.intersectsSphere(sphere))continue;
      const depth=Math.max(.5,cameraPoint.copy(sphere.center).applyMatrix4(camera.matrixWorldInverse).z*-1);
      const pixels=camera.isOrthographicCamera?h*viewportHeight*camera.zoom/(camera.top-camera.bottom):h*viewportHeight*camera.zoom/(2*depth*Math.tan(T.MathUtils.degToRad(camera.fov)/2));
      const threshold=entry.level===0?96:120;entry.level=pixels>threshold?0:1;
      const index=counts[entry.level]++;
      if(entry.level===1&&impostors){impostors.set(index,entry,camera);continue;}
      meshes[entry.level].forEach(mesh=>{mesh.setMatrixAt(index,entry.matrix);mesh.setColorAt(index,entry.color);});
    }
    meshes.forEach((lod,level)=>lod.forEach(mesh=>{
      mesh.count=level===1&&impostors?0:counts[level];mesh.visible=mesh.count>0;mesh.instanceMatrix.needsUpdate=true;
      if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true;
    }));
    group.userData.visibleNearCount=counts[0];group.userData.visibleFarCount=counts[1];
    if(impostors)impostors.finish(counts[1]);
  }
  return {group,prepare};
}
