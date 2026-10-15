import * as T from 'three';
import {GLTFLoader} from './vendor/loaders/GLTFLoader.js';

// Load actual visible detail without blocking cameras, roads or the plan.
// Loaded models outside the view form a bounded cache; visible models stay.
export function createRegionalModels(catalog,parent,onChange){
  if(catalog.schema!=='bursa-zoo-scene-models/v1')throw Error('3B model kataloğu uyumsuz');
  const loader=new GLTFLoader(),frustum=new T.Frustum(),matrix=new T.Matrix4(),point=new T.Vector3();
  const entries=catalog.models.map(meta=>{
    const box=new T.Box3(new T.Vector3(...meta.boundsXYZMetres[0]),new T.Vector3(...meta.boundsXYZMetres[1]));
    return {meta,box,sphere:box.getBoundingSphere(new T.Sphere()),status:'idle',scene:null,wanted:false,forced:false,priority:0,lastUsed:0,gpuBytes:0};
  });
  let pending=0,tick=0;
  function resources(root){
    const geometries=new Set(),materials=new Set(),textures=new Set(),images=new Set();
    root.traverse(node=>{
      if(!node.isMesh)return;geometries.add(node.geometry);
      for(const material of Array.isArray(node.material)?node.material:[node.material]){
        materials.add(material);
        for(const value of Object.values(material))if(value?.isTexture){textures.add(value);if(value.image)images.add(value.image);}
      }
    });
    let bytes=0;
    for(const geometry of geometries){
      for(const attribute of Object.values(geometry.attributes))bytes+=attribute.array?.byteLength||0;
      bytes+=geometry.index?.array?.byteLength||0;
    }
    // Conservative decoded RGBA plus mip levels; several maps can share an image.
    for(const image of images)bytes+=(image.width||0)*(image.height||0)*4*4/3;
    return {geometries,materials,textures,images,bytes};
  }
  function evict(entry){
    parent.remove(entry.scene);
    const asset=resources(entry.scene);
    for(const geometry of asset.geometries)geometry.dispose();
    for(const material of asset.materials)material.dispose();
    for(const texture of asset.textures)texture.dispose();
    for(const image of asset.images)image.close?.();
    entry.scene=null;entry.status='idle';entry.gpuBytes=0;
  }
  function trim(){
    let loaded=entries.filter(entry=>entry.scene);
    while(loaded.length>4||loaded.reduce((sum,entry)=>sum+entry.gpuBytes,0)>96*1024*1024){
      const unused=loaded.filter(entry=>!entry.wanted).sort((a,b)=>a.lastUsed-b.lastUsed)[0];
      if(!unused)break;evict(unused);loaded=loaded.filter(entry=>entry!==unused);
    }
  }
  async function load(entry){
    entry.status='loading';pending++;onChange();
    try{
      const gltf=await loader.loadAsync('./'+entry.meta.file+'?v='+entry.meta.sha256.slice(0,16));
      const root=gltf.scene;root.name=entry.meta.name+' · kaynaklı 3B ayrıntı';
      root.rotation.x=Math.PI/2;root.position.set(...entry.meta.originXYZMetres);root.userData.sourceKey=entry.meta.key;
      const hidden=new Set(entry.meta.hiddenNodes);
      root.traverse(node=>{
        if(hidden.has(node.name))node.visible=false;
        if(node.isMesh){node.castShadow=true;node.receiveShadow=true;}
      });
      entry.scene=root;entry.status='ready';entry.gpuBytes=resources(root).bytes;
      root.visible=entry.wanted;parent.add(root);
    }catch(error){
      entry.status='error';console.warn(entry.meta.name+' 3B ayrıntısı yüklenemedi.',error);
    }finally{pending--;trim();pump();onChange();}
  }
  function pump(){
    const queue=entries.filter(entry=>entry.wanted&&entry.status==='idle')
      .sort((a,b)=>Number(b.forced)-Number(a.forced)||b.priority-a.priority);
    while(pending<2&&queue.length)void load(queue.shift());
  }
  function update(camera,viewportHeight,forcedRegion=null){
    tick++;camera.updateMatrixWorld();matrix.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);frustum.setFromProjectionMatrix(matrix);
    for(const entry of entries){
      entry.forced=entry.meta.regions.includes(forcedRegion);
      const depth=Math.max(.5,-point.copy(entry.sphere.center).applyMatrix4(camera.matrixWorldInverse).z);
      entry.priority=camera.isOrthographicCamera?2*entry.sphere.radius*viewportHeight*camera.zoom/(camera.top-camera.bottom):
        entry.sphere.radius*viewportHeight*camera.zoom/(depth*Math.tan(T.MathUtils.degToRad(camera.fov)/2));
      entry.wanted=parent.visible&&(entry.forced||(frustum.intersectsBox(entry.box)&&entry.priority>=18));
      if(entry.wanted)entry.lastUsed=tick;
      if(entry.scene)entry.scene.visible=entry.wanted;
    }
    trim();pump();
  }
  function statusFor(region){const entry=entries.find(entry=>entry.meta.regions.includes(region));return entry?{status:entry.status,name:entry.meta.name}:null;}
  function retry(region){
    const entry=entries.find(entry=>entry.meta.regions.includes(region));
    if(parent.visible&&entry?.status==='error'){entry.status='idle';entry.wanted=true;entry.forced=true;pump();onChange();}
  }
  return {update,statusFor,retry};
}
