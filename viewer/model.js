import * as T from 'three';
import {Water} from './vendor/objects/Water.js';
import {mergeGeometries} from './vendor/utils/BufferGeometryUtils.js';
import {configureWoodlandGround} from './ground-material.js?v=20261015af';
import {WOODLAND_LIGHT} from './lighting.js?v=20261015af';
import {orientPlantCard} from './plant-cards.js?v=20261015af';

const sceneTextureManager=new T.LoadingManager();
let sceneTexturesLoading=false;
const sceneTextureErrors=[],sceneTextureWaiters=[];
sceneTextureManager.onStart=()=>{sceneTexturesLoading=true;};
sceneTextureManager.onError=url=>{sceneTextureErrors.push(url);};
sceneTextureManager.onLoad=()=>{sceneTexturesLoading=false;while(sceneTextureWaiters.length)sceneTextureWaiters.shift()();};
export async function waitForSceneTextures(){
  if(sceneTexturesLoading)await new Promise(resolve=>sceneTextureWaiters.push(resolve));
  if(sceneTextureErrors.length)throw Error('Bahçe dokuları yüklenemedi: '+sceneTextureErrors.map(url=>url.split('/').pop()).join(', '));
}

// The official plan locates the dome area; the M5 fence and builder dimensions anchor this provisional shell.
const CAGE = {x:-30,y:-64,angle:9*Math.PI/180,length:70,width:40,height:20};
const mat=(color,roughness=1,metalness=0)=>new T.MeshStandardMaterial({color,roughness,metalness,side:T.DoubleSide});
const grass=new T.MeshStandardMaterial({map:sourceTexture('woodland-meadow-v1.png',.2),color:'#e8eddd',roughness:1,side:T.DoubleSide}),waterMat=mat('#387f7b',.48,.03);
const buildingMat=mat('#a98770'),metalMat=mat('#aab9af',.68,.14);
const stoneMat=mat('#c6c4ad'),hedgeMat=mat('#567c54'),reedMat=mat('#789462');
const pavementSideMat=mat('#aa987a');
const penguinGravel=new T.MeshStandardMaterial({map:sourceTexture('penguin-pale-gravel-v1.png',1/1.5),roughness:1});
let bankStoneMaterial;
let habesEarthMaterial;

function grassTexture(){
  // A single mottled ground material gives woodland light variation without
  // layering transparent decals over the terrain or path geometry.
  const size=128,pixels=new Uint8Array(size*size*4),field=[];let seed=5021;
  const random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
  for(let i=0;i<64;i++)field.push(random()*2-1);
  const lerp=(a,b,t)=>a+(b-a)*t;
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    const gx=x/16,gy=y/16,ix=Math.floor(gx),iy=Math.floor(gy),tx=gx-ix,ty=gy-iy;
    const at=(dx,dy)=>field[((iy+dy)&7)*8+((ix+dx)&7)];
    const shade=lerp(lerp(at(0,0),at(1,0),tx),lerp(at(0,1),at(1,1),tx),ty)*21+(random()-.5)*5;
    const p=(y*size+x)*4;
    pixels[p]=Math.max(0,Math.min(255,143+shade));
    pixels[p+1]=Math.max(0,Math.min(255,168+shade));
    pixels[p+2]=Math.max(0,Math.min(255,118+shade*.7));pixels[p+3]=255;
  }
  const texture=new T.DataTexture(pixels,size,size,T.RGBAFormat);
  texture.colorSpace=T.SRGBColorSpace;texture.wrapS=texture.wrapT=T.RepeatWrapping;
  texture.repeat.set(.055,.055);texture.magFilter=T.LinearFilter;texture.minFilter=T.LinearMipmapLinearFilter;
  texture.generateMipmaps=true;texture.anisotropy=4;texture.needsUpdate=true;
  return texture;
}

function pavementTexture(){
  // The selected reference uses warm, compacted gravel rather than a flat grey slab.
  const size=128,pixels=new Uint8Array(size*size*4),coarse=[];let seed=1837;
  const random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
  for(let i=0;i<64;i++)coarse.push(random()*2-1);
  const lerp=(a,b,t)=>a+(b-a)*t;
  const sample=(x,y)=>{
    const gx=x/16,gy=y/16,ix=Math.floor(gx),iy=Math.floor(gy),tx=gx-ix,ty=gy-iy;
    const at=(dx,dy)=>coarse[((iy+dy)&7)*8+((ix+dx)&7)];
    return lerp(lerp(at(0,0),at(1,0),tx),lerp(at(0,1),at(1,1),tx),ty);
  };
  // Subtle irregular stone joints break up the broad gravel without a second mesh.
  const pavers=Array.from({length:64},()=>[.2+random()*.6,.2+random()*.6,(random()-.5)*9]);
  for(let y=0;y<size;y++)for(let x=0;x<size;x++){
    const cx=Math.floor(x/16),cy=Math.floor(y/16),gx=x/16,gy=y/16;
    let first=Infinity,second=Infinity,patch=0;
    for(let oy=-1;oy<=1;oy++)for(let ox=-1;ox<=1;ox++){
      const px=cx+ox,py=cy+oy,site=pavers[((py+8)&7)*8+((px+8)&7)];
      const distance=(gx-px-site[0])**2+(gy-py-site[1])**2;
      if(distance<first){second=first;first=distance;patch=site[2];}
      else if(distance<second)second=distance;
    }
    const joint=second-first<.075?-12:0;
    const p=(y*size+x)*4,grain=sample(x,y)*7+(random()-.5)*8+patch+joint,chip=random()<.025?(random()-.5)*30:0;
    pixels[p]=Math.max(0,Math.min(255,220+grain+chip));
    pixels[p+1]=Math.max(0,Math.min(255,203+grain+chip));
    pixels[p+2]=Math.max(0,Math.min(255,174+grain+chip));pixels[p+3]=255;
  }
  const texture=new T.DataTexture(pixels,size,size,T.RGBAFormat);
  texture.colorSpace=T.SRGBColorSpace;texture.wrapS=texture.wrapT=T.RepeatWrapping;
  texture.repeat.set(.22,.22);texture.magFilter=T.LinearFilter;texture.minFilter=T.LinearMipmapLinearFilter;
  texture.generateMipmaps=true;texture.anisotropy=4;texture.needsUpdate=true;
  return texture;
}
const pavementMat=new T.MeshStandardMaterial({map:sourceTexture('woodland-stone-path-v1.png',.3),roughness:1,side:T.DoubleSide});
// The generated stone image supplies a small illustrative relief signal. It
// is not a measured height map; its UVs exactly follow the sole road surface.
const pavementRelief=new T.TextureLoader(sceneTextureManager).load('./assets/woodland-stone-path-v1.png',()=>window.dispatchEvent(new Event('bursa-assets-ready')));
pavementRelief.colorSpace=T.NoColorSpace;pavementRelief.wrapS=pavementRelief.wrapT=T.RepeatWrapping;
pavementRelief.repeat.set(.3,.3);pavementRelief.anisotropy=4;
pavementMat.bumpMap=pavementRelief;pavementMat.bumpScale=.035;

function pondSurface(polygons,height){
  // All current partitioned ponds lie at this one water level. One merged
  // surface owns every pond and performs one shared reflection render.
  const geometries=polygons.map(p=>{
    const result=new T.ShapeGeometry(shape(p.outer,p.holes));
    const tint=new T.Color(p.waterPresentationColor||'#358f86');
    const colors=new Float32Array(result.getAttribute('position').count*3);
    for(let i=0;i<colors.length;i+=3){colors[i]=tint.r;colors[i+1]=tint.g;colors[i+2]=tint.b;}
    const attribute=new T.BufferAttribute(colors,3);
    result.setAttribute('pondTint',attribute);result.setAttribute('color',attribute);
    return result;
  });
  const geometry=mergeGeometries(geometries);
  for(const source of geometries)source.dispose();
  const area=ring=>ring.reduce((sum,p,i)=>{const q=ring[(i+1)%ring.length];return sum+p[0]*q[1]-q[0]*p[1];},0)/2;
  const sourceArea=polygons.reduce((sum,p)=>sum+Math.abs(area(p.outer))-(p.holes||[]).reduce((s,h)=>s+Math.abs(area(h)),0),0);
  const vertices=geometry.getAttribute('position'),indices=geometry.getIndex();let renderedArea=0;
  for(let i=0;i<indices.count;i+=3){
    const a=indices.getX(i),b=indices.getX(i+1),c=indices.getX(i+2);
    renderedArea+=Math.abs((vertices.getX(b)-vertices.getX(a))*(vertices.getY(c)-vertices.getY(a))-(vertices.getY(b)-vertices.getY(a))*(vertices.getX(c)-vertices.getX(a)))/2;
  }
  if(Math.abs(renderedArea-sourceArea)>.02)throw Error('Su yüzeyinin alanı kaynak bölümüyle uyuşmuyor');
  console.info('Water geometry audit',JSON.stringify({sourcePonds:polygons.length,renderMeshes:1,triangles:indices.count/3,sourceAreaM2:sourceArea,renderedAreaM2:renderedArea}));
  const normal=new T.TextureLoader(sceneTextureManager).load('./assets/three-water-normals-r186.jpg',()=>window.dispatchEvent(new Event('bursa-assets-ready')));
  normal.wrapS=normal.wrapT=T.RepeatWrapping;normal.colorSpace=T.NoColorSpace;
  const surface=new Water(geometry,{textureWidth:512,textureHeight:512,waterNormals:normal,
    sunDirection:new T.Vector3(...WOODLAND_LIGHT.direction).normalize(),sunColor:WOODLAND_LIGHT.sun,waterColor:'#358f86',
    distortionScale:1.2,clipBias:.003,side:T.FrontSide});
  const shader=surface.material;
  shader.vertexShader='attribute vec3 pondTint;\nvarying vec3 waterColor;\n'+shader.vertexShader.replace('void main() {','void main() {\nwaterColor = pondTint;');
  // The official addon shades XZ water; this atlas uses XY water with Z up.
  shader.fragmentShader=shader.fragmentShader
    .replace('uniform vec3 waterColor;','varying vec3 waterColor;')
    .replace('worldPosition.xz * size','worldPosition.xy * size')
    .replace('noise.xzy * vec3( 1.5, 1.0, 1.5 )','noise.xyz * vec3( 0.4, 0.4, 1.0 )')
    .replace('surfaceNormal.xz *','surfaceNormal.xy *')
    .replace('float rf0 = 0.3;','float rf0 = 0.025;')
    .replace('( sunColor * diffuseLight * 0.3 + scatter )','( scatter * 1.4 + waterColor * diffuseLight * 0.18 )');
  shader.uniforms.size.value=12;
  surface.position.z=height;surface.receiveShadow=true;
  surface.name='Tekil gölet yüzeyleri · ortak yansıma ve ince dalga normalleri';
  surface.userData.sourceKey='surfacePartition';
  const before=surface.onBeforeRender;
  surface.onBeforeRender=function(renderer,scene,camera,...rest){
    if(this.material===shader)before.call(this,renderer,scene,camera,...rest);
  };
  const reflections=new URLSearchParams(location.search).get('water')!=='0';
  const planMaterial=waterMat.clone();planMaterial.color.set('#ffffff');planMaterial.vertexColors=true;
  return {surface,prepare(camera){
    // The stock oblique reflection camera is perspective-only. Flat plan
    // inspection keeps the same sole geometry and uses its matte water material.
    surface.material=reflections&&camera.isPerspectiveCamera?shader:planMaterial;
  }};
}

function sourceTexture(name,repeat=1){
  const texture=new T.TextureLoader(sceneTextureManager).load('./assets/'+name,()=>window.dispatchEvent(new Event('bursa-assets-ready')));
  texture.colorSpace=T.SRGBColorSpace;texture.wrapS=texture.wrapT=T.RepeatWrapping;
  texture.repeat.set(repeat,repeat);texture.anisotropy=4;
  return texture;
}
const plantViewportHeight={value:innerHeight};
addEventListener('resize',()=>{plantViewportHeight.value=innerHeight;});
const lowPlantMaterials=new WeakMap();
function stablePlantMaterial(material,fadeSmall=false){
  // A small positive mip bias suppresses sub-pixel leaf sparkle without a new
  // render pass, supersampling, alpha hashing, temporal history or animation.
  material.onBeforeCompile=shader=>{
    shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',
      T.ShaderChunk.map_fragment.replace('texture2D( map, vMapUv )','texture2D( map, vMapUv, 0.65 )'));
    if(fadeSmall){
      shader.uniforms.plantViewportHeight=plantViewportHeight;
      shader.vertexShader='uniform float plantViewportHeight;\nvarying float plantCoverage;\n'+shader.vertexShader;
      shader.vertexShader=shader.vertexShader.replace('#include <project_vertex>',`#include <project_vertex>
        float cardHeight=1.0;
        #ifdef USE_INSTANCING
          cardHeight=length(instanceMatrix[1].xyz);
        #endif
        float viewDepth=projectionMatrix[3][3]>.5?1.0:max(.1,-mvPosition.z);
        float cardPixels=.5*plantViewportHeight*projectionMatrix[1][1]*cardHeight/viewDepth;
        plantCoverage=smoothstep(4.0,11.0,cardPixels);
      `);
      shader.fragmentShader='varying float plantCoverage;\n'+shader.fragmentShader;
      shader.fragmentShader=shader.fragmentShader.replace('#include <alphatest_fragment>',
        'diffuseColor.a *= plantCoverage;\n#include <alphatest_fragment>');
    }
  };
  material.customProgramCacheKey=()=> 'stable-plant-sampling/v2/'+Number(fadeSmall);
  return material;
}
function lowPlantMaterial(base){
  if(!lowPlantMaterials.has(base))lowPlantMaterials.set(base,stablePlantMaterial(base.clone(),true));
  return lowPlantMaterials.get(base);
}
const foliageTexture=sourceTexture('foliage-cluster-web-v1.png');
foliageTexture.wrapS=foliageTexture.wrapT=T.ClampToEdgeWrapping;
// The photographed-style leaf spray already contains diffuse variation.
// Leaf sprays contain their own small-scale shading. Bounded per-card light
// keeps the underside readable; alpha depth casts crowns onto the ground.
const foliageMaterial=stablePlantMaterial(new T.MeshBasicMaterial({map:foliageTexture,alphaTest:.35,
  alphaToCoverage:true,side:T.DoubleSide}));
const foliageDepth=stablePlantMaterial(new T.MeshDepthMaterial({map:foliageTexture,alphaTest:.35,
  side:T.DoubleSide,depthPacking:T.RGBADepthPacking}));
const fernTexture=sourceTexture('woodland-fern-clump-web-v1.png');
fernTexture.wrapS=fernTexture.wrapT=T.ClampToEdgeWrapping;
const fernMaterial=stablePlantMaterial(new T.MeshBasicMaterial({map:fernTexture,alphaTest:.35,alphaToCoverage:true,side:T.DoubleSide}));
const fernDepth=stablePlantMaterial(new T.MeshDepthMaterial({map:fernTexture,alphaTest:.35,side:T.DoubleSide,depthPacking:T.RGBADepthPacking}));
const darkFoliageTexture=sourceTexture('foliage-cluster-dark-web-v1.png');
darkFoliageTexture.wrapS=darkFoliageTexture.wrapT=T.ClampToEdgeWrapping;
const darkFoliageMaterial=stablePlantMaterial(new T.MeshBasicMaterial({map:darkFoliageTexture,alphaTest:.35,alphaToCoverage:true,side:T.DoubleSide}));
const darkFoliageDepth=stablePlantMaterial(new T.MeshDepthMaterial({map:darkFoliageTexture,alphaTest:.35,side:T.DoubleSide,depthPacking:T.RGBADepthPacking}));
const broadleafTexture=sourceTexture('woodland-broadleaf-clump-web-v1.png');
broadleafTexture.wrapS=broadleafTexture.wrapT=T.ClampToEdgeWrapping;
const broadleafMaterial=stablePlantMaterial(new T.MeshBasicMaterial({map:broadleafTexture,alphaTest:.35,alphaToCoverage:true,side:T.DoubleSide}));
const broadleafDepth=stablePlantMaterial(new T.MeshDepthMaterial({map:broadleafTexture,alphaTest:.35,side:T.DoubleSide,depthPacking:T.RGBADepthPacking}));
function botanicalCard(name,threshold=.5){
  const texture=sourceTexture(name);texture.wrapS=texture.wrapT=T.ClampToEdgeWrapping;
  return {material:stablePlantMaterial(new T.MeshBasicMaterial({map:texture,alphaTest:threshold,alphaToCoverage:true,side:T.DoubleSide})),
    depth:stablePlantMaterial(new T.MeshDepthMaterial({map:texture,alphaTest:threshold,side:T.DoubleSide,depthPacking:T.RGBADepthPacking}))};
}
const palmCard=botanicalCard('woodland-palm-frond-v1.png');
const grassCard=botanicalCard('woodland-grass-tussock-web-v1.png',.35);
const shrubCard=botanicalCard('woodland-shrub-spray-web-v1.png',.35);
const flowerCard=botanicalCard('woodland-wildflower-clump-web-v1.png',.55);
const barkTexture=sourceTexture('woodland-tree-bark-v1.png');barkTexture.repeat.set(1,6);
const barkMaterial=new T.MeshStandardMaterial({map:barkTexture,color:'#d5cfbd',roughness:1});
function leafCanopies(specs,cardsPerTree=24,dark=false){
  const mesh=new T.InstancedMesh(new T.PlaneGeometry(1,1),dark?darkFoliageMaterial:foliageMaterial,specs.length*cardsPerTree);
  mesh.name=dark?'Koyu sivri yapraklı taç kümeleri — görsel yorum':'Meşe yapraklı taç kümeleri — görsel yorum';
  mesh.customDepthMaterial=dark?darkFoliageDepth:foliageDepth;
  const d=new T.Object3D(),normal=new T.Vector3(),up=new T.Vector3(0,0,1),spin=new T.Quaternion();
  const colors=dark?['#ffffff','#e8eddf','#d3ddcf','#f2f0df']:['#d8e4d7','#e0ead6','#f1f2df','#c5d6c0','#d8e2ce'];
  specs.forEach(({x,y,h,r,seed=0},i)=>{
    for(let k=0;k<cardsPerTree;k++){
      const az=seed*.31+k*2.399963,cos=1-2*(k+.5)/cardsPerTree,sin=Math.sqrt(1-cos*cos);
      const dx=Math.cos(az)*sin,dy=Math.sin(az)*sin;
      const lobes=1+.16*Math.sin(az*3+seed*.7);
      d.position.set(x+dx*r*.85*lobes,y+dy*r*.85*lobes,-.24+h*.76+cos*r*.75);
      normal.set(dx,dy,cos*.72+.3).normalize();
      d.quaternion.setFromUnitVectors(up,normal);
      spin.setFromAxisAngle(up,az*.63);d.quaternion.multiply(spin);
      // The dark asset has larger empty alpha margins; preserve crown coverage.
      const size=r*((dark?2.05:1.55)+.18*Math.sin(k*3.7+seed));
      d.scale.set(size,size*.92,1);d.updateMatrix();mesh.setMatrixAt(i*cardsPerTree+k,d.matrix);
      const light=.72+.28*Math.max(0,normal.dot(new T.Vector3(-.5,.35,.79)));
      mesh.setColorAt(i*cardsPerTree+k,new T.Color(colors[(Math.abs(seed)+k)%colors.length]).multiplyScalar(light));
    }
  });
  mesh.instanceMatrix.needsUpdate=true;if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true;
  mesh.computeBoundingSphere();mesh.castShadow=true;mesh.receiveShadow=false;
  return mesh;
}
function variedCanopies(specs){
  const group=new T.Group();
  const light=specs.filter(p=>Math.abs(p.seed)%3===0),dark=specs.filter(p=>Math.abs(p.seed)%3!==0);
  if(light.length)group.add(leafCanopies(light));
  if(dark.length)group.add(leafCanopies(dark,24,true));
  return group;
}
function treeBranches(specs,material){
  const mesh=new T.InstancedMesh(new T.CylinderGeometry(.055,.13,1,5),material,specs.length*3);
  mesh.name='Taç içindeki üç yönlü ana dallar — görsel yorum';
  const d=new T.Object3D(),a=new T.Vector3(),b=new T.Vector3(),delta=new T.Vector3();
  const axis=new T.Vector3(0,1,0);
  specs.forEach(({x,y,h,r,seed=0},i)=>{
    for(let k=0;k<3;k++){
      const angle=seed*.37+k*2.0944;
      a.set(x,y,-.24+h*.46);
      b.set(x+Math.cos(angle)*r*.78,y+Math.sin(angle)*r*.78,-.24+h*.75+k*.12);
      delta.subVectors(b,a);d.position.copy(a).addScaledVector(delta,.5);
      d.quaternion.setFromUnitVectors(axis,delta.clone().normalize());d.scale.set(1,delta.length(),1);
      d.updateMatrix();mesh.setMatrixAt(i*3+k,d.matrix);
    }
  });
  mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingSphere();mesh.castShadow=true;
  return mesh;
}
function legacyTreeGroup(specs,native=false){
  const group=new T.Group();group.name='Önceki ağaç görünümü · tekil yedek';
  if(!specs.length)return group;
  const trunks=new T.InstancedMesh(new T.CylinderGeometry(native?.18:.14,native?.27:.25,1,native?5:6),barkMaterial,specs.length);
  const d=new T.Object3D();
  specs.forEach(({x,y,h,palm=false},i)=>{
    const trunkHeight=h*(palm?.88:native?.66:.64);
    d.position.set(x,y,-.24+trunkHeight*.5);d.rotation.set(Math.PI/2,0,0);
    const width=palm?.82:native?1.12:1;
    d.scale.set(width,trunkHeight,width);d.updateMatrix();trunks.setMatrixAt(i,d.matrix);
  });
  trunks.instanceMatrix.needsUpdate=true;trunks.castShadow=true;group.add(trunks);
  const broad=specs.filter(s=>!s.palm),palms=specs.filter(s=>s.palm);
  if(broad.length)group.add(treeBranches(broad,barkMaterial),variedCanopies(broad));
  if(palms.length)group.add(palmCrowns(palms));
  return group;
}
function replaceableTreeGroups(specs,parent,candidates,native=false){
  const eligible=specs.filter(s=>!s.palm&&s.h>=5&&!insideCage(s.x,s.y,-1));
  const eligibleSet=new Set(eligible),retained=specs.filter(s=>!eligibleSet.has(s));
  const legacy=legacyTreeGroup(eligible,native);parent.add(legacy,legacyTreeGroup(retained,native));
  candidates.push({specs:eligible,legacy,source:native?'M5 tree symbol':'visual landscape'});
}
function leafyShrubs(specs,kind='oak'){
  const fern=kind==='fern',broad=kind==='broadleaf',tuft=kind==='grass',shrub=kind==='shrub',flower=kind==='flower';
  const card=tuft?grassCard:shrub?shrubCard:flower?flowerCard:null;
  const cardsPerPlant=2;
  const material=lowPlantMaterial(card?card.material:broad?broadleafMaterial:fern?fernMaterial:foliageMaterial);
  const mesh=new T.InstancedMesh(new T.PlaneGeometry(1,1),material,specs.length*cardsPerPlant);
  mesh.name=flower?'Küçük sarı ve beyaz çiçekli alçak ot kümeleri':tuft?'İnce yapraklı alçak ot kümeleri':shrub?'Küçük oval yapraklı çalılar':broad?'Geniş yapraklı alçak rozetler':fern?'Alfa kesimli eğrelti kümeleri':'Yaprak dokulu alçak bitki kümeleri';
  mesh.customDepthMaterial=card?card.depth:broad?broadleafDepth:fern?fernDepth:foliageDepth;
  const d=new T.Object3D();
  const colors=['#d0dfb0','#e4e5b8','#c3d0a1','#f0e9be','#d6e0ad','#b8c798'];
  specs.forEach(([x,y,z,size,variant=0],i)=>{
    for(let k=0;k<cardsPerPlant;k++){
      // Alpha sprite bases are placed at ground level; no floating foliage cap.
      const width=size*(flower?1.35:tuft?1.05:shrub?1.8:broad?2:2.4),height=size*(flower?.95:tuft?1.05:shrub?1.5:broad?1.2:1.8);
      const baseV=flower?.859649:tuft?.949:shrub?.807:0;
      d.position.set(x,y,card?-.24+height*(baseV-.5):broad?size*.35-.18:z);
      orientPlantCard(d,variant*.72+k*Math.PI/2);
      d.scale.set(width,height,1);d.updateMatrix();mesh.setMatrixAt(i*cardsPerPlant+k,d.matrix);
      mesh.setColorAt(i*cardsPerPlant+k,new T.Color(flower?'#f6f0d8':colors[variant%colors.length]));
    }
  });
  mesh.instanceMatrix.needsUpdate=true;if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true;
  // Contact depth is already included by the AO beauty pass. Avoid flickering
  // sub-pixel cutout shadows and extra shadow-map draws for these low sprites.
  mesh.computeBoundingSphere();mesh.castShadow=false;mesh.receiveShadow=false;return mesh;
}

function palmCrowns(specs){
  // A curved strip uses the unchanged horizontal frond PNG. UV bounds omit
  // empty padding; fourteen fronds are radial, with varied elevation/droop.
  const positions=[],uvs=[],indices=[],steps=10;
  for(let i=0;i<=steps;i++){
    const t=i/steps;
    for(const side of [-1,1]){
      positions.push(t,side*.5,.17*Math.sin(Math.PI*t)-.16*t*t);
      uvs.push(.12+.77*t,side<0?.34:.63);
    }
    if(i<steps){const a=i*2;indices.push(a,a+2,a+3,a,a+3,a+1);}
  }
  const geometry=new T.BufferGeometry();geometry.setAttribute('position',new T.Float32BufferAttribute(positions,3));
  geometry.setAttribute('uv',new T.Float32BufferAttribute(uvs,2));geometry.setIndex(indices);geometry.computeVertexNormals();
  const mesh=new T.InstancedMesh(geometry,palmCard.material,specs.length*14);
  mesh.name='Kavisli tek yapraklı palmiye taçları — görsel yorum';mesh.customDepthMaterial=palmCard.depth;
  const d=new T.Object3D();
  specs.forEach(({x,y,h,r,seed},i)=>{
    for(let k=0;k<14;k++){
      const length=r*(1.0+.16*Math.sin(k*2.7+seed));
      d.position.set(x,y,-.24+h*.88+(k%2)*.15);
      d.rotation.set(0,k<7?-.12:.16,k*2.399963+seed*.3);
      d.scale.set(length,length*.31,length);d.updateMatrix();mesh.setMatrixAt(i*14+k,d.matrix);
      mesh.setColorAt(i*14+k,new T.Color(k%3===0?'#e7ebdb':'#ccd9bb').multiplyScalar(.82+(k%4)*.05));
    }
  });
  mesh.instanceMatrix.needsUpdate=true;if(mesh.instanceColor)mesh.instanceColor.needsUpdate=true;
  mesh.computeBoundingSphere();mesh.castShadow=true;return mesh;
}

function cageLocal(x,y){
  const dx=x-CAGE.x,dy=y-CAGE.y,c=Math.cos(CAGE.angle),s=Math.sin(CAGE.angle);
  return [dx*c+dy*s,-dx*s+dy*c];
}
function insideCage(x,y,pad=0){const [u,v]=cageLocal(x,y);return (u/(35+pad))**2+(v/(20+pad))**2<1;}
function box(parent,w,d,h,x,y,z,material){const m=new T.Mesh(new T.BoxGeometry(w,d,h),material);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}

function shape(points, holes=[]) {
  const s=new T.Shape();points.forEach(([x,y],i)=>i?s.lineTo(x,y):s.moveTo(x,y));s.closePath();
  for(const ring of holes){const h=new T.Path();ring.forEach(([x,y],i)=>i?h.lineTo(x,y):h.moveTo(x,y));h.closePath();s.holes.push(h);}
  return s;
}
function flat(points,material,z,holes=[]){
  const o=new T.Mesh(new T.ShapeGeometry(shape(points,holes)),material);o.position.z=z;o.receiveShadow=true;return o;
}
function ringArea(points){
  let sum=0;for(let i=0;i<points.length;i++){const a=points[i],b=points[(i+1)%points.length];sum+=a[0]*b[1]-b[0]*a[1];}
  return Math.abs(sum)/2;
}
function riverStoneCurbs(rings){
  // Spatial batches trace the road boundary. Near stones have smooth normals;
  // distant batches use fewer faces. Exactly one LOD is visible in each batch.
  const samples=[],occupied=new Map(),cell=.76,minDistanceSq=cell*cell;
  const key=(x,y)=>`${x},${y}`;
  const free=(x,y)=>{
    const gx=Math.floor(x/cell),gy=Math.floor(y/cell);
    for(let ix=gx-1;ix<=gx+1;ix++)for(let iy=gy-1;iy<=gy+1;iy++)
      for(const p of occupied.get(key(ix,iy))||[])if((p[0]-x)**2+(p[1]-y)**2<minDistanceSq)return false;
    const bucket=key(gx,gy);if(!occupied.has(bucket))occupied.set(bucket,[]);
    occupied.get(bucket).push([x,y]);return true;
  };
  for(let ri=0;ri<rings.length;ri++){
    const ring=rings[ri];let walked=0,next=.65+(ri%4)*.17;
    for(let i=0;i<ring.length;i++){
      const a=ring[i],b=ring[(i+1)%ring.length],dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
      if(length<.001)continue;
      while(next<=walked+length){
        const t=(next-walked)/length,x=a[0]+dx*t,y=a[1]+dy*t;
        if(free(x,y))samples.push([x,y,Math.atan2(dy,dx)]);
        next+=1.07;
      }
      walked+=length;
    }
  }
  const closeGeometry=new T.IcosahedronGeometry(1,1),farGeometry=new T.IcosahedronGeometry(1,0);
  const material=new T.MeshStandardMaterial({color:'#ffffff',roughness:1});
  const group=new T.Group();group.name='QGIS yol sınırı · mesafeye göre dere taşları';
  const palette=['#a79d88','#c0b398','#b2a68e','#d0bea0','#968f7e'];
  const dummy=new T.Object3D(),chunks=new Map(),cellSize=64;
  samples.forEach((p,i)=>{
    const gx=Math.floor(p[0]/cellSize),gy=Math.floor(p[1]/cellSize),key=gx+','+gy;
    if(!chunks.has(key))chunks.set(key,{x:(gx+.5)*cellSize,y:(gy+.5)*cellSize,items:[]});
    chunks.get(key).items.push({p,i});
  });
  for(const chunk of chunks.values()){
    const near=new T.InstancedMesh(closeGeometry,material,chunk.items.length);
    const far=new T.InstancedMesh(farGeometry,material,chunk.items.length);
    chunk.items.forEach(({p:[x,y,angle],i},j)=>{
      const variation=((i*2654435761)>>>0)/4294967296;
      dummy.position.set(x-chunk.x,y-chunk.y,-.125);
      dummy.rotation.set(0,0,angle+(variation-.5)*.45);
      dummy.scale.set(.27+variation*.065,.185+variation*.035,.12+variation*.025);
      dummy.updateMatrix();near.setMatrixAt(j,dummy.matrix);
      near.setColorAt(j,new T.Color(palette[i%palette.length]));
    });
    near.instanceMatrix.needsUpdate=true;near.instanceColor.needsUpdate=true;
    far.instanceMatrix=near.instanceMatrix;far.instanceColor=near.instanceColor;
    for(const mesh of [near,far]){mesh.computeBoundingSphere();mesh.receiveShadow=true;}
    const lod=new T.LOD();lod.position.set(chunk.x,chunk.y,0);
    lod.addLevel(near,0);lod.addLevel(far,90,.12);group.add(lod);
  }
  console.info('Curb LOD audit',JSON.stringify({stones:samples.length,batches:chunks.size,nearFacesPerStone:80,farFacesPerStone:20}));
  return group;
}
function woodlandEdgePlanting(roadRings,pathSurfaces,data,currentPlan){
  // Roadside planting is a single set of instanced low models on terrain.
  // Candidates must stay beyond the paved edge and outside mapped features.
  const containsRing=(ring,x,y)=>{
    let inside=false;
    for(let i=0,j=ring.length-1;i<ring.length;j=i++){
      const a=ring[i],b=ring[j];
      if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;
    }
    return inside;
  };
  const containsSurface=(surface,x,y)=>containsRing(surface.outer,x,y)&&
    !(surface.holes||[]).some(h=>containsRing(h,x,y));
  const forbidden=[];
  for(const f of data.features)if((f.role==='water'||f.role==='building')&&f.closed)
    for(const ring of f.paths)if(ring.length>=4)forbidden.push({outer:ring,holes:[]});
  if(data.alligatorPond?.outer?.length>=4)forbidden.push({outer:data.alligatorPond.outer,holes:[]});
  const entrancePond=currentPlan?.features?.find(f=>f.id==='entrance_pond_5');
  if(entrancePond?.pointsXYMetres?.length>=4)forbidden.push({outer:entrancePond.pointsXYMetres,holes:[]});
  const hash=(x,y,salt=0)=>{
    const n=Math.sin(x*127.1+y*311.7+salt*71.9)*43758.5453;
    return n-Math.floor(n);
  };
  const planted=[],occupied=new Map(),cell=1.05;
  const free=(x,y)=>{
    const gx=Math.floor(x/cell),gy=Math.floor(y/cell);
    for(let ix=gx-1;ix<=gx+1;ix++)for(let iy=gy-1;iy<=gy+1;iy++)
      for(const p of occupied.get(`${ix},${iy}`)||[])if((p[0]-x)**2+(p[1]-y)**2<cell*cell)return false;
    const key=`${gx},${gy}`;if(!occupied.has(key))occupied.set(key,[]);
    occupied.get(key).push([x,y]);return true;
  };
  const suitable=(x,y)=>{
    if(!containsRing(data.outline,x,y)||insideCage(x,y,1.2))return false;
    const [u,v]=cageLocal(x,y);
    if(Math.abs(v)<6.5&&Math.abs(u)>27&&Math.abs(u)<65)return false;
    if(pathSurfaces.some(s=>containsSurface(s,x,y)))return false;
    return !forbidden.some(s=>containsSurface(s,x,y));
  };
  for(let ri=0;ri<roadRings.length;ri++){
    const ring=roadRings[ri];let walked=0,next=2.3+(ri%3)*.57;
    for(let i=0;i<ring.length;i++){
      const a=ring[i],b=ring[(i+1)%ring.length],dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
      if(length<.001)continue;
      while(next<=walked+length){
        const t=(next-walked)/length,x=a[0]+dx*t,y=a[1]+dy*t;
        if(hash(x,y,1)<.78){
          const side=hash(x,y,2)<.5?-1:1,offset=.84+hash(x,y,3)*.42;
          for(const sign of [side,-side]){
            const px=x-sign*dy/length*offset,py=y+sign*dx/length*offset;
            if(suitable(px,py)&&free(px,py)){
              planted.push([px,py,hash(px,py,4),hash(px,py,5)]);
              // Small grouped patches read as undergrowth from a distance.
              for(const direction of [-1,1])if(hash(px,py,7+direction)<.66){
                const distance=1.13+hash(px,py,8+direction)*.25;
                const qx=px+dx/length*direction*distance-sign*dy/length*.18;
                const qy=py+dy/length*direction*distance+sign*dx/length*.18;
                if(suitable(qx,qy)&&free(qx,qy))
                  planted.push([qx,qy,hash(qx,qy,4),hash(qx,qy,5)]);
              }
              break;
            }
          }
        }
        next+=4.45;
      }
      walked+=length;
    }
  }
  const group=new T.Group();group.name='Yol kenarı ot, eğrelti ve oval yapraklı çalılar — görsel yorum';
  group.userData.sourceKey='landscape';
  if(!planted.length)return group;
  const patches=planted.map(([x,y,a,b])=>[x,y,.12+(.55+a*.35)*.55,.55+a*.35,Math.floor(b*6)]);
  group.add(leafyShrubs(patches.filter((p,i)=>i%3===0),'grass'),
    leafyShrubs(patches.filter((p,i)=>i%3===1),'fern'),leafyShrubs(patches.filter((p,i)=>i%3===2),'shrub'));
  return group;
}
function woodlandInteriorPlanting(layout,forestCandidates){
  if(layout?.schema!=='bursa-zoo-woodland-visual-layout/v1')throw Error('Orman görsel yerleşimi eksik');
  const group=new T.Group();group.name='Model hedefi için orman alt dokusu — konumlar görsel yorum';
  group.userData.sourceKey='visualLandscape';
  const canopySpecs=[];
  const d=new T.Object3D();
  layout.trees.forEach(([x,y,h,r,variant],i)=>{
    const seed=variant+i*7,palm=seed%13===0;
    canopySpecs.push({x,y,h,r,seed,palm});
  });
  replaceableTreeGroups(canopySpecs,group,forestCandidates);
  const understory=layout.plants.map(([x,y,size,variant])=>[x,y,.1+size*.55,size,variant]);
  group.add(leafyShrubs(understory.filter(p=>p[4]===0)),leafyShrubs(understory.filter(p=>p[4]===1),'broadleaf'),
    leafyShrubs(understory.filter(p=>p[4]===2),'fern'),leafyShrubs(understory.filter(p=>p[4]===3),'grass'),
    leafyShrubs(understory.filter(p=>p[4]===4||p[4]===5),'shrub'),leafyShrubs(understory.filter(p=>p[4]===6),'flower'));
  const banks=layout.shoreStones||[];
  if(banks.length){
    const stones=new T.InstancedMesh(new T.IcosahedronGeometry(1,1),mat('#ffffff'),banks.length);
    stones.name='Gölet kıyısı doğal taşları — görsel yorum';
    const palette=['#b9ac8e','#d4c7a8','#99967e','#c5bda5','#a6a38b'];
    banks.forEach(([x,y,size,height,angle],i)=>{
      d.position.set(x,y,-.2+height*.35);d.rotation.set(.12*(i%3),.09*(i%4),angle);
      d.scale.set(size,size*.78,height);d.updateMatrix();stones.setMatrixAt(i,d.matrix);
      stones.setColorAt(i,new T.Color(palette[i%palette.length]));
    });
    stones.instanceMatrix.needsUpdate=true;stones.instanceColor.needsUpdate=true;
    stones.computeBoundingSphere();stones.receiveShadow=true;stones.castShadow=true;group.add(stones);
  }
  const waterside=(layout.shorePlants||[]).map(([x,y,size,variant])=>[x,y,.1+size*.55,size,variant]);
  group.add(leafyShrubs(waterside.filter(p=>p[4]%3===0),'grass'),
    leafyShrubs(waterside.filter(p=>p[4]%3===1),'shrub'),leafyShrubs(waterside.filter(p=>p[4]%3===2),'fern'));
  return group;
}
function cylinderBetween(a,b,r,material,parent){
  const delta=b.clone().sub(a);const o=new T.Mesh(new T.CylinderGeometry(r,r,delta.length(),6),material);
  o.position.copy(a).addScaledVector(delta,.5);o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.normalize());parent.add(o);return o;
}

function pointInBox(p,box){
  return p.x>=box.minX&&p.x<=box.maxX&&p.y>=box.minY&&p.y<=box.maxY&&p.z>=box.minZ&&p.z<=box.maxZ;
}
function triangleTouchesBox(a,b,c,box){
  return Math.max(a.x,b.x,c.x)>=box.minX&&Math.min(a.x,b.x,c.x)<=box.maxX&&
    Math.max(a.y,b.y,c.y)>=box.minY&&Math.min(a.y,b.y,c.y)<=box.maxY&&
    Math.max(a.z,b.z,c.z)>=box.minZ&&Math.min(a.z,b.z,c.z)<=box.maxZ;
}
function barOutsideBox(a,b,box){
  let enter=0,leave=1;
  for(const axis of ['x','y','z']){
    const delta=b[axis]-a[axis],low=box['min'+axis.toUpperCase()],high=box['max'+axis.toUpperCase()];
    if(Math.abs(delta)<1e-9){if(a[axis]<low||a[axis]>high)return [[a,b]];continue;}
    const t0=(low-a[axis])/delta,t1=(high-a[axis])/delta;
    enter=Math.max(enter,Math.min(t0,t1));leave=Math.min(leave,Math.max(t0,t1));
    if(enter>=leave)return [[a,b]];
  }
  const parts=[];
  if(enter>1e-5)parts.push([a,a.clone().lerp(b,enter)]);
  if(leave<1-1e-5)parts.push([a.clone().lerp(b,leave),b]);
  return parts;
}
function splitPolygonAtPlane(poly,axis,limit,keepGreater){
  const inside=[],outside=[];
  const signed=p=>keepGreater?p[axis]-limit:limit-p[axis];
  let prev=poly[poly.length-1],prevDistance=signed(prev);
  for(const point of poly){
    const distance=signed(point);
    if((prevDistance>=0)!==(distance>=0)){
      const crossing=prev.clone().lerp(point,prevDistance/(prevDistance-distance));
      inside.push(crossing);outside.push(crossing);
    }
    (distance>=0?inside:outside).push(point);
    prev=point;prevDistance=distance;
  }
  return [inside,outside];
}
function polygonOutsideBox(poly,box){
  // Partition the triangle at each portal plane. Every emitted polygon lies
  // outside at least one plane; only the portion inside all six is discarded.
  const planes=[['x',box.minX,true],['x',box.maxX,false],
    ['y',box.minY,true],['y',box.maxY,false],
    ['z',box.minZ,true],['z',box.maxZ,false]];
  let pending=[poly];const outside=[];
  for(const [axis,limit,keepGreater] of planes){
    const next=[];
    for(const piece of pending){
      const [inside,cut]=splitPolygonAtPlane(piece,axis,limit,keepGreater);
      if(cut.length>=3)outside.push(cut);
      if(inside.length>=3)next.push(inside);
    }
    pending=next;
    if(!pending.length)break;
  }
  return outside;
}

function makeCage(cageLocalSurfaces,isTerrain){
  const root=new T.Group();root.name='Su Kuşları Kafesi — 70 × 40 × 20 m';root.position.set(CAGE.x,CAGE.y,-.09);root.rotation.z=CAGE.angle;
  const N=36,M=18,L=CAGE.length/2,R=CAGE.width/2,H=CAGE.height;
  // Leave the full walk-through volume clear at both portal ends, with a small
  // margin for the thickness of the steel members and their joint spheres.
  const portalBoxes=[-1,1].map(sign=>({
    minX:sign<0?-L-.5:29.5,maxX:sign<0?-29.5:L+.5,
    minY:-1.75,maxY:1.75,minZ:-.2,maxZ:2.8
  }));
  const nodes=[];for(let i=0;i<=N;i++){
    const u=-L+.02+(CAGE.length-.04)*i/N;
    const k=Math.sqrt(Math.max(0,1-(u/L)**2));const row=[];
    for(let j=0;j<=M;j++){
      const a=Math.PI*j/M;row.push(new T.Vector3(u,R*k*Math.cos(a),H*k*Math.sin(a)));
    }nodes.push(row);
  }
  const bars=[];const add=(a,b)=>{
    let parts=[[a,b]];
    for(const box of portalBoxes)parts=parts.flatMap(([start,end])=>barOutsideBox(start,end,box));
    for(const [start,end] of parts)if(start.distanceTo(end)>.08)bars.push([start,end]);
  };
  for(let i=0;i<=N;i++)for(let j=0;j<=M;j++){
    if(i<N)add(nodes[i][j],nodes[i+1][j]);
    if(j<M)add(nodes[i][j],nodes[i][j+1]);
    if(i<N&&j<M)add(nodes[i][j],nodes[i+1][j+1]);
  }
  const nearSteel=new T.Group();nearSteel.name='yakın görünüm — tam tek katlı çelik örgü ve ağ';
  const rodGeo=new T.CylinderGeometry(.052,.052,1,6),nodeGeo=new T.SphereGeometry(.078,6,5);
  const rods=new T.InstancedMesh(rodGeo,metalMat,bars.length);rods.name='çelik üçgen kafes — yaklaşık örgü';
  const visibleNodes=nodes.flat().filter(p=>!portalBoxes.some(box=>pointInBox(p,box)));
  const ball=new T.InstancedMesh(nodeGeo,metalMat,visibleNodes.length);ball.name='çelik birleşim düğümleri';
  const dummy=new T.Object3D();let bi=0;
  for(const [a,b] of bars){const d=b.clone().sub(a);dummy.position.copy(a).addScaledVector(d,.5);dummy.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.clone().normalize());dummy.scale.set(1,d.length(),1);dummy.updateMatrix();rods.setMatrixAt(bi++,dummy.matrix);}
  let ni=0;for(const p of visibleNodes){dummy.position.copy(p);dummy.quaternion.identity();dummy.scale.setScalar(1);dummy.updateMatrix();ball.setMatrixAt(ni++,dummy.matrix);}
  rods.instanceMatrix.needsUpdate=true;ball.instanceMatrix.needsUpdate=true;
  rods.computeBoundingSphere();ball.computeBoundingSphere();
  rods.castShadow=true;ball.castShadow=true;nearSteel.add(rods,ball);
  // The translucent mesh suggests the nylon net without copying a source photo.
  const verts=[];
  for(let i=0;i<N;i++)for(let j=0;j<M;j++){
    for(const triangle of [[nodes[i][j],nodes[i+1][j],nodes[i][j+1]],
      [nodes[i+1][j],nodes[i+1][j+1],nodes[i][j+1]]]){
      let pieces=[triangle];
      for(const portal of portalBoxes){
        if(triangleTouchesBox(...triangle,portal))
          pieces=pieces.flatMap(piece=>polygonOutsideBox(piece,portal));
      }
      for(const piece of pieces)for(let k=1;k<piece.length-1;k++){
        const [a,b,c]=[piece[0],piece[k],piece[k+1]];
        if(new T.Vector3().subVectors(b,a).cross(new T.Vector3().subVectors(c,a)).lengthSq()<1e-10)continue;
        verts.push(a.x,a.y,a.z,b.x,b.y,b.z,c.x,c.y,c.z);
      }
    }
  }
  const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(verts,3));geo.computeVertexNormals();
  const net=new T.Mesh(geo,new T.MeshBasicMaterial({color:'#d1ded9',transparent:true,opacity:.025,side:T.DoubleSide,forceSinglePass:true,depthWrite:false}));
  net.name='tek katlı yarı saydam ağ yorumu';net.raycast=()=>{};nearSteel.add(net);
  // At map scale, the measured tube diameter projects to less than a pixel.
  // Keep the full near structure; show only selected, more contrasted ribs at
  // distance so the open, single-wall dome reads as a cage rather than haze.
  const farSteel=new T.Group();farSteel.name='uzak görünüm — seçilmiş ana kirişler';
  const farBars=[];
  const farDisplayRadius=.09;
  const farPortalClearance=farDisplayRadius+.02;
  // Clip the simplified tubes with their display radius in mind, so even the
  // thick far LOD leaves the same actual walk-through portal volume clear.
  const farPortalBoxes=portalBoxes.map(box=>({
    minX:box.minX-farPortalClearance,maxX:box.maxX+farPortalClearance,
    minY:box.minY-farPortalClearance,maxY:box.maxY+farPortalClearance,
    minZ:box.minZ-farPortalClearance,maxZ:box.maxZ+farPortalClearance
  }));
  const addFar=(a,b)=>{
    let parts=[[a,b]];
    for(const box of farPortalBoxes)parts=parts.flatMap(([start,end])=>barOutsideBox(start,end,box));
    for(const [start,end] of parts)if(start.distanceTo(end)>.2)farBars.push([start,end]);
  };
  const step=3;
  for(let i=0;i<=N;i+=step)for(let j=0;j<=M;j+=step){
    if(i+step<=N)addFar(nodes[i][j],nodes[i+step][j]);
    if(i>0&&i<N&&j+step<=M)addFar(nodes[i][j],nodes[i][j+step]);
    if(i+step<=N&&j+step<=M&&(i/step+j/step)%2===0)
      addFar(nodes[i][j],nodes[i+step][j+step]);
  }
  // 0.09 m is a screen-legibility radius for the sparse far LOD, not a
  // measured pipe size; its 180 mm diameter exceeds the builder's published
  // 42.4–139.7 mm pipe range. The near geometry retains its 0.052 m radius.
  const farRodGeo=new T.CylinderGeometry(farDisplayRadius,farDisplayRadius,1,6);
  // Both LODs share one steel finish. The far silhouette comes from the
  // selected ribs and their screen-space thickness, not a darker substitute.
  const farRods=new T.InstancedMesh(farRodGeo,metalMat,farBars.length);
  farRods.name='uzaktan okunur tek katlı kafes kirişleri';
  for(let i=0;i<farBars.length;i++){
    const [a,b]=farBars[i],delta=b.clone().sub(a);
    dummy.position.copy(a).addScaledVector(delta,.5);
    dummy.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.clone().normalize());
    dummy.scale.set(1,delta.length(),1);dummy.updateMatrix();farRods.setMatrixAt(i,dummy.matrix);
  }
  farRods.instanceMatrix.needsUpdate=true;farRods.computeBoundingSphere();farRods.castShadow=true;farSteel.add(farRods);
  // Tubes retain the sparse, thick silhouette requested for distance. The
  // original triangulation is a one-pixel line proxy between them, rather
  // than a second opaque/transparent shell surface. WebGL line width is
  // deliberately one pixel (not a world-space or fabrication diameter).
  const proxyPositions=[];
  for(const [a,b] of bars){
    let pieces=[[a,b]];
    for(const portal of farPortalBoxes)pieces=pieces.flatMap(([start,end])=>barOutsideBox(start,end,portal));
    for(const [start,end] of pieces)if(start.distanceTo(end)>.08)
      proxyPositions.push(start.x,start.y,start.z,end.x,end.y,end.z);
  }
  const proxyGeometry=new T.BufferGeometry();
  proxyGeometry.setAttribute('position',new T.Float32BufferAttribute(proxyPositions,3));
  const proxyMaterial=new T.LineBasicMaterial({color:metalMat.color,transparent:true,opacity:.28,depthWrite:false});
  const fineProxy=new T.LineSegments(proxyGeometry,proxyMaterial);
  fineProxy.name='Uzak kafes ince örgü çizgileri — tek piksel sunum';fineProxy.raycast=()=>{};
  farSteel.add(fineProxy);
  // The near and far alternatives are mutually exclusive.
  const cageLod=new T.LOD();cageLod.name='kafes detay düzeyleri';
  cageLod.addLevel(nearSteel,0);cageLod.addLevel(farSteel,85);
  const eye=new T.Vector3(),center=new T.Vector3();let showingFar=false;
  cageLod.update=function(camera){
    const distance=camera.getWorldPosition(eye).distanceTo(this.getWorldPosition(center));
    // Initial desktop and mobile map presets both use the far presentation.
    // Switch back to full detail only after the visitor zooms in explicitly.
    const zoomFactor=camera.isOrthographicCamera?Math.max(1,camera.zoom/11):camera.zoom;
    const apparent=distance/zoomFactor;
    if(showingFar ? apparent<85 : apparent>92)showingFar=!showingFar;
    nearSteel.visible=!showingFar;farSteel.visible=showingFar;
    this._currentLevel=showingFar?1:0;
  };
  root.add(cageLod);
  const portalMat=mat('#535c59'),portalEdge=mat('#8e9892'),gateMat=mat('#273a35');
  for(const sign of [-1,1]){
    const x=sign*32.4;
    const porch=new T.Group();porch.name='İki uçtaki beşik çatılı giriş — fotoğraf eşleştirmesi';root.add(porch);
    porch.userData.sourceKey='entrance';
    // The mutually exclusive path partition owns the walk-through floor.
    for(const side of [-1,1]){
      box(porch,5.6,.18,3.25,x,side*2.57,1.62,portalMat);
      const slope=box(porch,5.9,3.04,.19,x,side*1.25,3.94,portalEdge);slope.rotation.x=-side*.54;
      cylinderBetween(new T.Vector3(x-sign*2.75,side*2.57,0),new T.Vector3(x-sign*2.75,side*2.57,3.25),.11,portalEdge,porch);
    }
    const face=x+sign*2.91;
    box(porch,.14,1.0,3.15,face,-2.05,1.56,portalMat);
    box(porch,.14,1.0,3.15,face,2.05,1.56,portalMat);
    box(porch,.14,3.2,.5,face,0,2.9,portalMat);
    const gable=new T.BufferGeometry();gable.setAttribute('position',new T.Float32BufferAttribute([
      face,-2.62,3.12,face,2.62,3.12,face,0,4.72
    ],3));gable.computeVertexNormals();porch.add(new T.Mesh(gable,portalMat));
    const inner=face-sign*5.55;
    // The two inner gate leaves are shown swung toward the side walls, so they
    // retain their bars without closing the walk-through opening.
    for(const side of [-1,1]){
      for(const offset of [.14,.48,.82,1.16,1.5])
        box(porch,.06,.045,2.7,inner+sign*offset,side*1.45,1.35,gateMat);
      for(const z of [.22,2.5])box(porch,1.52,.05,.07,inner+sign*.82,side*1.45,z,gateMat);
    }
    box(porch,.07,1.6,.12,face+sign*.02,0,2.78,portalEdge);
  }
  // A three-dimensional perimeter member replaces the coplanar footing ring.
  const foot=new T.InstancedMesh(new T.CylinderGeometry(.09,.09,1,6),metalMat,96);
  foot.name='Kafes çevresi — tek instanslı 3B taban kirişi';foot.castShadow=true;root.add(foot);
  const footing=new T.Object3D();
  for(let i=0;i<96;i++){
    const a=2*Math.PI*i/96,b=2*Math.PI*(i+1)/96;
    const start=new T.Vector3(35*Math.cos(a),20*Math.sin(a),-.015),
      end=new T.Vector3(35*Math.cos(b),20*Math.sin(b),-.015),delta=end.sub(start);
    footing.position.copy(start).addScaledVector(delta,.5);
    footing.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.clone().normalize());
    footing.scale.set(1,delta.length(),1);footing.updateMatrix();foot.setMatrixAt(i,footing.matrix);
  }
  foot.instanceMatrix.needsUpdate=true;foot.computeBoundingSphere();
  const benchWood=mat('#665243'),benchMetal=mat('#31594d');
  const bench=new T.Group();bench.name='Giriş önündeki bank — fotoğraf eşleştirmesi';bench.position.set(48,-8.1,0);root.add(bench);
  box(bench,2.2,.48,.1,0,0,.53,benchWood);box(bench,2.2,.1,.75,0,-.23,.91,benchWood);
  for(const x of [-.85,.85])for(const y of [-.16,.16])box(bench,.07,.07,.48,x,y,.26,benchMetal);
  decorateCage(root,cageLocalSurfaces,isTerrain);
  root.userData.sourceKey='shell';
  root.userData.landmark='cage';
  return root;
}

function decorateCage(root,cageLocalSurfaces,isTerrain){
  const wood=mat('#725341'),woodLight=mat('#977052'),tile=mat('#a75f46');
  // The plan confirms water inside the dome but does not delineate its shore.
  // Keep this lagoon an explicitly interpreted shape beneath the footbridge.
  const lagoon=cageLocalSurfaces.lagoonOutline;
  // The visible lagoon top is produced once by the partitioned site water layer.
  // Rounded individual stones mark the bank without adding another surface.
  const shorePoints=[];
  const bankPlants=[];
  const signedArea=lagoon.slice(1).reduce((sum,p,i)=>sum+lagoon[i][0]*p[1]-p[0]*lagoon[i][1],0);
  const orientation=Math.sign(signedArea)||1;
  for(let i=0;i<lagoon.length-1;i++){
    const a=lagoon[i],b=lagoon[i+1],length=Math.hypot(b[0]-a[0],b[1]-a[1]);
    const count=Math.max(1,Math.round(length/.72));
    for(let j=0;j<count;j++){
      const t=(j+.5)/count;
      const x=a[0]+(b[0]-a[0])*t,y=a[1]+(b[1]-a[1])*t;
      const nx=(b[1]-a[1])/length*orientation,ny=-(b[0]-a[0])/length*orientation;
      shorePoints.push([x,y,nx,ny]);
      if((i*11+j)%3===0){
        const size=.38+((i*7+j*3)%9)*.045,offset=.85+((i*3+j)%5)*.19;
        const px=x+nx*offset,py=y+ny*offset,c=Math.cos(CAGE.angle),s=Math.sin(CAGE.angle);
        const radius=size*1.05;
        const dry=[[0,0],[radius,0],[-radius,0],[0,radius],[0,-radius]].every(([u,v])=>
          isTerrain([CAGE.x+(px+u)*c-(py+v)*s,CAGE.y+(px+u)*s+(py+v)*c]));
        if(dry)bankPlants.push([px,py,.1+size*.55,size,(i+j)%6]);
      }
    }
  }
  const stoneGeometry=new T.IcosahedronGeometry(.33,2),rockPositions=stoneGeometry.getAttribute('position');
  for(let i=0;i<rockPositions.count;i++){
    const x=rockPositions.getX(i),y=rockPositions.getY(i),z=rockPositions.getZ(i);
    const scale=1+.13*Math.sin(x*17+y*9)*Math.cos(z*13-y*5)+.06*Math.sin(x*29-z*19);
    rockPositions.setXYZ(i,x*scale,y*scale,z*scale);
  }
  stoneGeometry.computeVertexNormals();stoneGeometry.computeBoundingSphere();
  const stones=new T.InstancedMesh(stoneGeometry,bankStoneMaterial,shorePoints.length);
  stones.name='İç gölet kıyısı — tekil 3B taşlar';stones.castShadow=true;stones.receiveShadow=true;
  const stone=new T.Object3D();
  for(let i=0;i<shorePoints.length;i++){
    const [x,y,nx,ny]=shorePoints[i],variation=.5+.5*Math.sin(i*2.399963);
    stone.position.set(x+nx*(variation-.35)*.18,y+ny*(variation-.35)*.18,-.07+variation*.05);
    stone.rotation.set((i%7)*.19,(i%5)*.23,(i%11)*.31);
    stone.scale.set(.85+variation*.58,.68+variation*.37,.48+variation*.28);
    stone.updateMatrix();stones.setMatrixAt(i,stone.matrix);
    stones.setColorAt(i,new T.Color(['#bbb49a','#c7bfa5','#a6a18a','#d1c8ad'][i%4]));
  }
  stones.instanceMatrix.needsUpdate=true;stones.instanceColor.needsUpdate=true;stones.computeBoundingSphere();root.add(stones);
  const bank=new T.Group();bank.name='İç gölet kuru kıyısında karma bitki kümeleri — görsel yorum';
  bank.position.z=.09;bank.userData.sourceKey='landscape';
  bank.add(leafyShrubs(bankPlants.filter((p,i)=>i%3===0),'grass'),
    leafyShrubs(bankPlants.filter((p,i)=>i%3===1),'fern'),leafyShrubs(bankPlants.filter((p,i)=>i%3===2),'shrub'));
  root.add(bank);
  console.info('Cage bank planting audit',JSON.stringify({stones:shorePoints.length,plants:bankPlants.length,sampledDryGround:true,samplesPerPlant:5}));
  // The entrance, loop, exit and bridge leads are part of surface-layers.path.
  // Both ends of the crossing extend onto dry ground beyond the pond shore.
  const bridge=new T.Group();bridge.name='Gölet üzerindeki ahşap köprü — görsel yorum';root.add(bridge);
  bridge.userData.sourceKey='landscape';
  const x0=-18.8,x1=10.0,by=2.2,bw=2.35,n=25;
  for(let i=0;i<n;i++){
    const x=x0+(x1-x0)*(i+.5)/n,raise=.23+.43*Math.sin(Math.PI*(i+.5)/n);
    box(bridge,(x1-x0)/n-.03,bw,.14,x,by,raise,woodLight);
    if(i%3===0)for(const side of [-1,1])box(bridge,.12,.12,.9,x,by+side*(bw/2+.07),raise+.48,wood);
  }
  for(const side of [-1,1]){
    const rail=[];for(let i=0;i<=n;i++){
      const x=x0+(x1-x0)*i/n,z=.23+.43*Math.sin(Math.PI*i/n)+.95;
      rail.push(new T.Vector3(x,by+side*(bw/2+.07),z));
    }
    for(let i=1;i<rail.length;i++)cylinderBetween(rail[i-1],rail[i],.055,wood,bridge);
  }
  // The west bank path enters the lagoon before the straight crossing. A
  // raised timber ramp covers only that water crossing, as an actual 3D deck.
  const [rampStart,rampEnd]=cageLocalSurfaces.westernBridgeRamp;
  const rdx=rampEnd[0]-rampStart[0],rdy=rampEnd[1]-rampStart[1],rl=Math.hypot(rdx,rdy);
  const rangle=Math.atan2(rdy,rdx),rnx=-rdy/rl,rny=rdx/rl,rn=11;
  const rampHeight=t=>-.035+.265*t;
  for(let i=0;i<rn;i++){
    const t=(i+.5)/rn;
    const plank=box(bridge,rl/rn-.03,2.2,.14,
      rampStart[0]+rdx*t,rampStart[1]+rdy*t,rampHeight(t),woodLight);
    plank.rotation.z=rangle;
  }
  for(const side of [-1,1]){
    const rail=[];
    for(let i=0;i<=5;i++){
      const t=i/5,x=rampStart[0]+rdx*t+side*rnx*(bw/2+.07),
        y=rampStart[1]+rdy*t+side*rny*(bw/2+.07),z=rampHeight(t);
      box(bridge,.1,.1,.85,x,y,z+.45,wood);
      rail.push(new T.Vector3(x,y,z+.94));
    }
    for(let i=1;i<rail.length;i++)cylinderBetween(rail[i-1],rail[i],.055,wood,bridge);
    cylinderBetween(rail.at(-1),new T.Vector3(x0,by+side*(bw/2+.07),.23+.95),.055,wood,bridge);
  }
  const mill=new T.Group();mill.name='Ahşap kuş evi / değirmen silueti — fotoğraf eşleştirmesi';mill.position.set(13,5,0);root.add(mill);mill.userData.sourceKey='mill';
  box(mill,7.4,5.5,.22,0,0,.16,wood);
  const timberWall=mat('#594638');
  box(mill,6.65,4.68,4.75,0,0,3.05,timberWall);
  for(const side of [-1,1]){
    for(let b=-14;b<=14;b++)box(mill,.075,.085,4.55,b*.215,side*2.4,3.06,woodLight);
    box(mill,1.55,.09,1.65,-1.55,side*2.48,3.55,mat('#26302a'));
    box(mill,1.55,.09,1.65,1.55,side*2.48,3.55,mat('#26302a'));
  }
  for(const sx of [-1,1])for(const sy of [-1,1]){
    const x=sx*3.25,y=sy*2.3;
    box(mill,.23,.23,6.15,x,y,3.2,wood);
    cylinderBetween(new T.Vector3(x,y,.48),new T.Vector3(x-sx*1.5,y,3.1),.07,wood,mill);
  }
  for(const z of [2.85,5.55]){
    box(mill,7.25,5.4,.22,0,0,z,woodLight);
    for(const sy of [-1,1]){
      box(mill,7.3,.1,.12,0,sy*2.66,z+1.0,wood);
      for(let i=-3;i<=3;i++)box(mill,.08,.08,.95,i*1.05,sy*2.66,z+.55,wood);
    }
  }
  for(const sy of [-1,1]){
    const roof=box(mill,8.0,3.5,.19,0,sy*1.45,6.8,tile);roof.rotation.x=-sy*.55;
  }
  for(let step=0;step<14;step++){
    const y=-4.25+step*.57,z=.42+step*.34;
    box(mill,1.28,.42,.13,-4.08,y,z,woodLight);
  }
  for(const x of [-4.75,-3.42])cylinderBetween(new T.Vector3(x,-4.55,.6),new T.Vector3(x,3.35,5.35),.06,wood,mill);
  const wheel=new T.Mesh(new T.TorusGeometry(1.15,.12,6,18),wood);wheel.position.set(-3.85,-.6,1.55);wheel.rotation.y=Math.PI/2;mill.add(wheel);
  for(let i=0;i<8;i++){
    const a=2*Math.PI*i/8;
    cylinderBetween(new T.Vector3(-3.85,-.6,1.55),new T.Vector3(-3.85,-.6+Math.cos(a)*1.13,1.55+Math.sin(a)*1.13),.052,wood,mill);
  }

  // A low planted rim keeps the dome grounded, leaving both entrance axes open.
  const shrubs=new T.Group();shrubs.name='Kafes çevresi ve içindeki çalı kütleleri — görsel yorum';root.add(shrubs);
  shrubs.userData.sourceKey='landscape';
  const bushes=[];
  for(let i=0;i<94;i++){
    const a=2*Math.PI*i/94,jitter=.72*Math.sin(i*2.33)+.42*Math.cos(i*.81),u=(36.1+jitter)*Math.cos(a),v=(21.1+jitter)*Math.sin(a);
    if(Math.abs(v)<3.4&&Math.abs(u)>31)continue;
    const r=.62+(i%8)*.11; bushes.push([u,v,r*.62,r]);
  }
  for(const [x,y] of [[-22,9],[-18,11],[-5,12],[0,13],[18,-8],[21,8],[-20,-10],[22,-4],[-4,-13],[9,-11]])
    for(let k=0;k<4;k++)bushes.push([x+(k%2)*1.1,y+Math.floor(k/2)*.95,.42,.65+(k%3)*.13]);
  for(const [x,y] of [[28,7],[29,-7],[43,7],[45,-8],[-29,6]])for(let k=0;k<4;k++){
    const r=1.05+.19*k;bushes.push([x+(k%2)*1.2,y+Math.floor(k/2)*1.2,r*.75,r]);
  }
  const c=Math.cos(CAGE.angle),s=Math.sin(CAGE.angle);
  const cagePlants=bushes.map(([x,y,z,r],i)=>[x,y,.1+r*.55,r,i%6]).filter(([u,v])=>isTerrain([CAGE.x+u*c-v*s,CAGE.y+u*s+v*c]));
  const garden=cagePlants.filter((p,i)=>i%9!==0),flowers=cagePlants.filter((p,i)=>i%9===0);
  shrubs.add(leafyShrubs(garden.filter((p,i)=>i%4===0),'shrub'),leafyShrubs(garden.filter((p,i)=>i%4===1),'grass'),
    leafyShrubs(garden.filter((p,i)=>i%4===2),'fern'),leafyShrubs(garden.filter((p,i)=>i%4===3),'broadleaf'),leafyShrubs(flowers,'flower'));
  const interiorTrees=legacyTreeGroup([[-23,8,5.6],[-18,10,6.1],[-11,12,4.8],[17,-10,5.9],[21,7,6.6],[9,12,5.4]]
    .map(([x,y,h],i)=>({x,y,h,r:1.08+(i%3)*.13,seed:502+i*7})),true);
  interiorTrees.name='Kafes içi yapraklı küçük ağaçlar — görsel yorum';interiorTrees.position.z=.09;
  interiorTrees.userData.sourceKey='landscape';root.add(interiorTrees);
}

export function createSite(data,currentPlan,surfaceData,buildingShellData,visualLandscape,groundMaterial){
  if(surfaceData?.schema!=='bursa-zoo-planar-surface-partition/v1')throw Error('Bölünmüş zemin verisi eksik veya uyumsuz');
  if(buildingShellData?.schema!=='bursa-zoo-building-shell/v1')throw Error('Birleşik bina kabuğu verisi eksik veya uyumsuz');
  const anchor=currentPlan?.features?.find(f=>f.id==='waterbird_aviary_dome_candidate')?.modelAnchor;
  const centre=anchor?.provisionalShellCentreXYMetres;
  const dimensions=anchor?.independentMajorMinorDimensionsMetres;
  if(centre?.length===2&&centre.every(Number.isFinite)&&Number.isFinite(anchor.provisionalShellAngleDegreesCounterclockwiseFromEast)&&dimensions?.length===2&&dimensions.every(n=>Number.isFinite(n)&&n>0)){
    CAGE.x=centre[0];CAGE.y=centre[1];CAGE.angle=anchor.provisionalShellAngleDegreesCounterclockwiseFromEast*Math.PI/180;
    CAGE.length=dimensions[0];CAGE.width=dimensions[1];
  }
  const site=new T.Group();site.name='Bursa Hayvanat Bahçesi — 2026 kroki ve M5 yerleşimi';
  configureWoodlandGround(grass,groundMaterial,sceneTextureManager);
  bankStoneMaterial=new T.MeshStandardMaterial({map:sourceTexture(groundMaterial.rockTexture.file.split('/').pop()+'?v='+groundMaterial.rockTexture.sha256.slice(0,16)),roughness:.95});
  habesEarthMaterial=new T.MeshStandardMaterial({map:sourceTexture(groundMaterial.litterTexture.file.split('/').pop()+'?v='+groundMaterial.litterTexture.sha256.slice(0,16),1/3),color:new T.Color().setRGB(.96,.9,.72),roughness:1});
  const surfaceLayers=surfaceData.layers;
  for(const p of surfaceLayers.terrain){
    const gravel=p.surfaceStyle==='penguin-gravel';
    const habes=p.surfaceStyle==='habes-earth';
    const ground=flat(p.outer,gravel?penguinGravel:habes?habesEarthMaterial:grass,-.24,p.holes);
    ground.name=gravel?'Penguen alanı · tekil çakıl yüzeyi':habes?'Habeş Maymunu adası · tekil toprak yüzeyi':'OSM sınırı içi · çakışmasız çim yüzey';site.add(ground);
  }
  const roadBoundaryRings=[];
  for(const p of surfaceLayers.path){
    // The provisional path caps own their XY regions; no water or building cap is below them.
    roadBoundaryRings.push(p.outer,...p.holes);
    const geometry=new T.ExtrudeGeometry(shape(p.outer,p.holes),{depth:.135,steps:1,bevelEnabled:false,curveSegments:1});
    const m=new T.Mesh(geometry,[pavementMat,pavementSideMat]);
    m.position.z=-.24;m.receiveShadow=true;
    m.name='Manuel QGIS yollarından alçak kaplama · yaklaşık genişlik';site.add(m);
  }
  site.add(riverStoneCurbs(roadBoundaryRings));
  if(!(surfaceData.renderLevels.waterZ<surfaceData.renderLevels.terrainZ))throw Error('Sunum su kotu arazi altında olmalı');
  const water=pondSurface(surfaceLayers.water,surfaceData.renderLevels.waterZ);site.add(water.surface);
  // DGN curb and other survey lines remain in site-data.json for later plan alignment.
  const footprints=new T.Group();footprints.name='M5 yapı izlerinden tekil dış kabuk · aşamalı modelleme';site.add(footprints);
  // Roof polygons partition the footprint by its highest source elevation.
  // One wall is emitted at each outside edge or roof-height step; there are no
  // overlapping closed building extrusions or internal coplanar wall faces.
  for(const p of buildingShellData.bases){
    const base=flat(p.outer,buildingMat,buildingShellData.baseZ,p.holes);
    const indices=base.geometry.getIndex()?.array;
    if(indices){for(let i=0;i<indices.length;i+=3){const swap=indices[i+1];indices[i+1]=indices[i+2];indices[i+2]=swap;}
      base.geometry.getIndex().needsUpdate=true;base.geometry.computeVertexNormals();}
    base.name='M5 yapı kabuğu · tekil alt kapak';footprints.add(base);
  }
  for(const p of buildingShellData.roofs){
    const roof=flat(p.outer,buildingMat,p.z,p.holes);
    roof.castShadow=true;roof.name=p.sourceId+' · tekil çatı';footprints.add(roof);
  }
  const wallVertices=[];
  for(const wall of buildingShellData.walls){
    const [ax,ay]=wall.a,[bx,by]=wall.b,z0=wall.bottom,z1=wall.top;
    wallVertices.push(ax,ay,z0,bx,by,z0,bx,by,z1,ax,ay,z0,bx,by,z1,ax,ay,z1);
  }
  if(wallVertices.length){
    const geometry=new T.BufferGeometry();
    geometry.setAttribute('position',new T.Float32BufferAttribute(wallVertices,3));
    geometry.computeVertexNormals();
    const walls=new T.Mesh(geometry,buildingMat);
    walls.castShadow=true;walls.receiveShadow=true;walls.name='M5 yapı dış duvarları · tekil kot geçişleri';footprints.add(walls);
  }
  const trees=new T.Group();trees.name='M5 ağaç sembollerinden temsili bitki örtüsü';site.add(trees);
  const forestCandidates=[];
  const containsRing=(ring,x,y)=>{
    let inside=false;
    for(let i=0,j=ring.length-1;i<ring.length;j=i++){
      const a=ring[i],b=ring[j];
      if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;
    }
    return inside;
  };
  const onTerrain=([x,y])=>surfaceLayers.terrain.some(s=>
    !['penguin-gravel','habes-earth'].includes(s.surfaceStyle)&&containsRing(s.outer,x,y)&&!(s.holes||[]).some(h=>containsRing(h,x,y)));
  // Old tree symbols are retained in site-data.json. The 2026-derived paving
  // and water own their regions, so their 59 conflicting tree models are culled.
  const positions=(data.treeClusters||[]).filter(c=>onTerrain(c.xy)).map(c=>({p:c.xy,id:c.sourceIds[0]}));
  trees.userData.culledSourceTreeCount=(data.treeClusters||[]).length-positions.length;
  const canopySpecs=[];
  for(const {p,id} of positions){let seed=0;for(const c of id)seed=(seed*31+c.charCodeAt(0))>>>0;
    const within=insideCage(p[0],p[1],-1),[u,v]=cageLocal(p[0],p[1]);
    const dome=20*Math.sqrt(Math.max(0,1-(u/35)**2-(v/20)**2));
    const entranceClearing=u>38&&u<50&&Math.abs(v)<4;
    const h=entranceClearing?1.8:within?Math.min(11.4,Math.max(2.6,dome-2.2),8.7+(seed%36)/10):6+(seed%63)/10;
    const r=entranceClearing?.65:within?1.7+(seed%19)/12:2.1+(seed%23)/10;
    canopySpecs.push({x:p[0],y:p[1],h,r,seed});
  }
  replaceableTreeGroups(canopySpecs,trees,forestCandidates,true);
  trees.add(woodlandEdgePlanting(roadBoundaryRings,surfaceLayers.path,data,currentPlan));
  trees.add(woodlandInteriorPlanting(visualLandscape,forestCandidates));
  const cage=makeCage(surfaceData.cageLocal,onTerrain);site.add(cage);
  return {site,cage,trees,footprints,forestCandidates,prepareWater:water.prepare};
}

export {CAGE};
