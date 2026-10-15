import * as T from 'three';

function atlasUv(material){
  material.onBeforeCompile=shader=>{
    shader.vertexShader='attribute vec4 atlasRect;\n'+shader.vertexShader;
    shader.vertexShader=shader.vertexShader.replace('#include <uv_vertex>','#include <uv_vertex>\n#ifdef USE_MAP\n vMapUv = vMapUv * atlasRect.zw + atlasRect.xy;\n#endif');
  };
  material.customProgramCacheKey=()=> 'atlas-tree-impostor-uv/v1';
}
export async function createImpostorLayer(capacity,renderer,metadata){
  if(metadata.frames.length!==16)throw Error('Uzak ağaç açıları eksik');
  const texture=await new T.TextureLoader().loadAsync('./assets/forest-impostor-atlas.png?v='+metadata.atlas.sha256.slice(0,16));
  texture.colorSpace=T.SRGBColorSpace;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
  const geometry=new T.PlaneGeometry(1,1);
  const rects=new T.InstancedBufferAttribute(new Float32Array(Math.max(1,capacity)*4),4);rects.setUsage(T.DynamicDrawUsage);geometry.setAttribute('atlasRect',rects);
  // SSAA atlas edges carry fractional coverage. A high cutoff thins the
  // photographed foliage; retain those edges and let MSAA smooth coverage.
  const material=new T.MeshBasicMaterial({map:texture,alphaTest:.14,alphaToCoverage:true,side:T.DoubleSide});atlasUv(material);
  const depth=new T.MeshDepthMaterial({map:texture,alphaTest:.14,side:T.DoubleSide,depthPacking:T.RGBADepthPacking});atlasUv(depth);
  const mesh=new T.InstancedMesh(geometry,material,Math.max(1,capacity));mesh.name='Uzak ağaç · 16 açılı CC0 silüet';
  mesh.customDepthMaterial=depth;mesh.instanceMatrix.setUsage(T.DynamicDrawUsage);mesh.frustumCulled=false;
  mesh.castShadow=true;mesh.receiveShadow=false;mesh.count=0;
  const zUp=new T.Vector3(0,0,1),origin=new T.Vector3(),rotation=new T.Matrix4();
  const direction=new T.Vector3(),localDirection=new T.Vector3(),up=new T.Vector3();
  const tree=new T.Object3D(),plane=new T.Object3D(),matrix=new T.Matrix4(),inverse=new T.Matrix4();
  const color=new T.Color();
  function set(index,entry,camera){
    const {spec}=entry,angle=spec.seed*.381966;
    const xy=spec.r*1.6/metadata.sourceRadialExtent,z=spec.h/metadata.sourceHeight;
    tree.position.set(spec.x,spec.y,-.24-metadata.sourceBaseZ*z);tree.rotation.set(0,0,angle);tree.scale.set(xy,xy,z);tree.updateMatrix();
    if(camera.isOrthographicCamera)direction.set(0,0,1).applyQuaternion(camera.quaternion);
    else direction.copy(camera.position).sub(new T.Vector3(spec.x,spec.y,-.24+spec.h*.5));
    inverse.copy(tree.matrix).invert();localDirection.copy(direction).transformDirection(inverse);
    const azimuth=(Math.atan2(localDirection.y,localDirection.x)+2*Math.PI)%(2*Math.PI);
    const elevation=T.MathUtils.radToDeg(Math.atan2(localDirection.z,Math.hypot(localDirection.x,localDirection.y)));
    // Camera damping must not alternate atlas images around a sector boundary.
    // Hold each direction inside a small dead band; no second tree is drawn.
    let row=entry.impostorRow??(elevation<46?0:1);
    if(row===0&&elevation>50)row=1;else if(row===1&&elevation<42)row=0;
    let sector=entry.impostorSector??Math.round(azimuth/(Math.PI/4))%8;
    const difference=Math.atan2(Math.sin(azimuth-sector*Math.PI/4),Math.cos(azimuth-sector*Math.PI/4));
    if(Math.abs(difference)>Math.PI/8+.09)sector=Math.round(azimuth/(Math.PI/4))%8;
    entry.impostorRow=row;entry.impostorSector=sector;
    const frame=row*8+sector;
    rotation.lookAt(localDirection,origin,zUp);plane.quaternion.setFromRotationMatrix(rotation);
    up.set(0,1,0).applyQuaternion(plane.quaternion);
    const rootY=-metadata.sourceHeight*.5*Math.cos(T.MathUtils.degToRad(row?60:32));
    plane.position.set(0,0,metadata.sourceBaseZ).addScaledVector(up,-rootY);
    plane.scale.set(metadata.orthoScale,metadata.orthoScale,1);plane.updateMatrix();
    matrix.multiplyMatrices(tree.matrix,plane.matrix);mesh.setMatrixAt(index,matrix);
    rects.setXYZW(index,(frame%4)/4,(3-Math.floor(frame/4))/4,.25,.25);
    color.copy(entry.color);mesh.setColorAt(index,color);
  }
  function finish(count){mesh.count=count;mesh.visible=count>0;mesh.instanceMatrix.needsUpdate=true;rects.needsUpdate=true;if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true;}
  return {mesh,set,finish,metadata};
}
