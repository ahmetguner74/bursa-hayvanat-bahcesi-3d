import * as T from 'three';
import {GLTFLoader} from '../vendor/loaders/GLTFLoader.js';
import {WOODLAND_LIGHT} from '../lighting.js?v=20261015y';

const digest=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
function pngMetadata(png,metadata){
  const text=new TextEncoder().encode(JSON.stringify(metadata)),keyword=new TextEncoder().encode('BursaZooTree');
  const data=new Uint8Array(keyword.length+5+text.length);data.set(keyword);data.set(text,keyword.length+5);
  const chunk=new Uint8Array(data.length+12),view=new DataView(chunk.buffer);
  view.setUint32(0,data.length);chunk.set([105,84,88,116],4);chunk.set(data,8);
  let crc=0xffffffff;
  for(const byte of chunk.subarray(4,8+data.length)){
    crc^=byte;for(let bit=0;bit<8;bit++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);
  }
  view.setUint32(8+data.length,(crc^0xffffffff)>>>0);
  const result=new Uint8Array(png.length+chunk.length);
  result.set(png.subarray(0,png.length-12));result.set(chunk,png.length-12);result.set(png.subarray(png.length-12),png.length-12+chunk.length);
  return result;
}
export async function bakeTreeAtlas(progress){
  if(!crypto.subtle)throw Error('Atlas üretimini bu bilgisayarda 127.0.0.1 adresinden açın.');
  const build=await fetch('../models/tree-model-metadata.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Ağaç kaynak kaydı eksik');return r.json();});
  const file=build.files.find(item=>item.name.endsWith('.glb'));
  const bytes=await fetch('../models/'+file.name+'?v='+file.sha256).then(r=>{if(!r.ok)throw Error('Ağaç modeli yüklenemedi');return r.arrayBuffer();});
  if(await digest(bytes)!==file.sha256)throw Error('Ağaç kaynağı dosya kaydıyla eşleşmiyor.');
  const gltf=await new GLTFLoader().parseAsync(bytes,'../models/');
  const scene=new T.Scene(),root=gltf.scene;root.rotation.x=Math.PI/2;scene.add(root);root.updateMatrixWorld(true);
  const bounds=new T.Box3(),point=new T.Vector3();let radial=0,triangles=0;
  root.traverse(node=>{
    if(!node.isMesh)return;node.visible=node.userData.lod===0;
    if(!node.visible)return;
    node.castShadow=true;node.receiveShadow=true;
    // Render at twice the delivery resolution, then filter once in the atlas.
    // Hard cutouts here avoid squaring alpha coverage on a transparent target.
    node.material.alphaToCoverage=false;
    const positions=node.geometry.getAttribute('position');triangles+=(node.geometry.index?.count||positions.count)/3;
    for(let i=0;i<positions.count;i++){
      point.fromBufferAttribute(positions,i).applyMatrix4(node.matrixWorld);bounds.expandByPoint(point);radial=Math.max(radial,Math.hypot(point.x,point.y));
    }
  });
  if(triangles!==build.lods[0].triangles)throw Error('Yakın ağaç geometrisi eksik.');
  const height=bounds.max.z-bounds.min.z,center=new T.Vector3(0,0,bounds.min.z+height*.5),ortho=Math.max(height*1.45,radial*2.2);
  const renderer=new T.WebGLRenderer({alpha:true,antialias:true,preserveDrawingBuffer:true});renderer.setSize(1024,1024,false);renderer.setPixelRatio(1);
  renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.NoToneMapping;renderer.setClearColor(0,0);
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;
  scene.add(new T.HemisphereLight(WOODLAND_LIGHT.sky,WOODLAND_LIGHT.ground,WOODLAND_LIGHT.hemisphere));
  const sun=new T.DirectionalLight(WOODLAND_LIGHT.sun,WOODLAND_LIGHT.sunIntensity);sun.target.position.copy(center);sun.position.copy(center).add(new T.Vector3(...WOODLAND_LIGHT.direction).normalize().multiplyScalar(100));
  sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.near=.1;sun.shadow.camera.far=250;
  sun.shadow.camera.left=sun.shadow.camera.bottom=-radial*1.5;sun.shadow.camera.right=sun.shadow.camera.top=radial*1.5;
  sun.shadow.bias=-.00018;sun.shadow.normalBias=.06;sun.shadow.intensity=WOODLAND_LIGHT.shadowIntensity;sun.shadow.radius=WOODLAND_LIGHT.shadowRadius;scene.add(sun,sun.target);
  const camera=new T.OrthographicCamera(-ortho/2,ortho/2,ortho/2,-ortho/2,.1,250);camera.up.set(0,0,1);
  const atlas=document.createElement('canvas');atlas.width=atlas.height=2048;const ctx=atlas.getContext('2d');
  const frame=document.createElement('canvas');frame.width=frame.height=512;const frameContext=frame.getContext('2d');frameContext.imageSmoothingQuality='high';
  const meta={schema:'bursa-zoo-tree-impostors/v1',source:build.source.url,license:'CC0',authors:build.source.authors,sourceSha256:build.source.sha256,
    renderSourceGltfSha256:file.sha256,sourceModelLOD:0,sourceTriangles:triangles,leafTintLinear:build.leafTintLinear,artisticShape:build.artisticShape,
    renderEngine:'three-webgl/r'+T.REVISION,renderSize:1024,frameSize:512,
    method:'Exact local GLB with atlas viewer lights. Linear lighting encoded into sRGB PNG; viewer applies ACES once. 2x supersampling; no AI repainting.',
    lighting:{hemisphere:[WOODLAND_LIGHT.sky,WOODLAND_LIGHT.ground,WOODLAND_LIGHT.hemisphere],sun:[WOODLAND_LIGHT.sun,WOODLAND_LIGHT.sunIntensity],direction:WOODLAND_LIGHT.direction,shadowIntensity:WOODLAND_LIGHT.shadowIntensity,shadowRadius:WOODLAND_LIGHT.shadowRadius,toneMapping:'none'},
    sourceHeight:height,sourceBaseZ:bounds.min.z,sourceRadialExtent:radial,center:center.toArray(),orthoScale:ortho,frames:[]};
  try{
    for(let index=0;index<16;index++){
      const azimuth=(index%8)*Math.PI/4,elevation=T.MathUtils.degToRad(index<8?32:60);
      camera.position.copy(center).add(new T.Vector3(Math.cos(azimuth)*Math.cos(elevation),Math.sin(azimuth)*Math.cos(elevation),Math.sin(elevation)).multiplyScalar(70));camera.lookAt(center);
      renderer.render(scene,camera);frameContext.clearRect(0,0,512,512);frameContext.drawImage(renderer.domElement,0,0,512,512);
      ctx.drawImage(frame,(index%4)*512,Math.floor(index/4)*512);
      meta.frames.push({index,azimuthDegrees:(index%8)*45,elevationDegrees:index<8?32:60,rgbaSha256:await digest(frameContext.getImageData(0,0,512,512).data)});
      progress(index+1,16);await new Promise(resolve=>requestAnimationFrame(resolve));
    }
    meta.atlasRgbaSha256=await digest(ctx.getImageData(0,0,2048,2048).data);
    const blob=await new Promise(resolve=>atlas.toBlob(resolve,'image/png'));if(!blob)throw Error('Atlas PNG oluşturulamadı.');
    const png=new Uint8Array(await blob.arrayBuffer());
    // Bind the actual encoded PNG, including its filtered edge colours. Canvas
    // readback and PNG encoding need not use identical unpremultiply rounding.
    meta.encodedPngSha256=await digest(png);
    return new Blob([pngMetadata(png,meta)],{type:'image/png'});
  }finally{
    renderer.dispose();sun.shadow.map?.dispose();
    const geometries=new Set(),materials=new Set(),textures=new Set(),images=new Set();
    root.traverse(node=>{if(node.isMesh){geometries.add(node.geometry);materials.add(node.material);for(const value of Object.values(node.material))if(value?.isTexture){textures.add(value);if(value.image)images.add(value.image);}}});
    for(const geometry of geometries)geometry.dispose();for(const material of materials)material.dispose();for(const texture of textures)texture.dispose();for(const image of images)image.close?.();
  }
}
