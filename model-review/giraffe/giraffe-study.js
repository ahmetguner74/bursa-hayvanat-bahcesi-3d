import * as T from 'three';
import {OrbitControls} from '../../vendor/OrbitControls.js';
import {GLTFLoader} from '../../vendor/loaders/GLTFLoader.js';
import {createGiraffes} from '../../giraffes.js?v=20261015am';
const host=document.getElementById('scene'),status=document.getElementById('status');
const scene=new T.Scene();scene.background=new T.Color('#dbe5d6');
const camera=new T.PerspectiveCamera(39,1,.1,240);camera.up.set(0,0,1);
const renderer=new T.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<700?1.25:1.35));
renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;host.append(renderer.domElement);
const fill=new T.HemisphereLight('#fff9eb','#9f9a81',1.9);fill.position.set(0,0,1);scene.add(fill);
const sun=new T.DirectionalLight('#fff0d2',3.15);sun.position.set(110,-15,75);sun.castShadow=true;scene.add(sun,sun.target);sun.target.position.set(60,48,0);
sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-38;sun.shadow.camera.right=38;sun.shadow.camera.top=38;sun.shadow.camera.bottom=-38;sun.shadow.camera.far=200;sun.shadow.normalBias=.008;sun.shadow.intensity=.78;
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.screenSpacePanning=false;controls.minDistance=6;controls.maxDistance=160;controls.maxPolarAngle=Math.PI*.48;
let dirty=true,capture=false,mode=new URLSearchParams(location.search).get('view')==='animal'?'animal':'habitat',paused=false,buildingReady=false,follow=false,framedAnimal=false,lastWidth=0;
const delta=new T.Vector3(),target=new T.Vector3(),parent=new T.Group();scene.add(parent);
controls.addEventListener('change',()=>{dirty=true;});controls.addEventListener('start',()=>{follow=false;});
const giraffes=createGiraffes(parent,()=>{
  dirty=true;status.textContent=giraffes.status()==='ready'?'İki zürafa · yürüme ve dinlenme':giraffes.status()==='error'?'Zürafalar açılamadı':'Zürafalar hazırlanıyor…';
  if(mode==='animal'&&!framedAnimal&&giraffes.status()==='ready'){frame();framedAnimal=true;}
},{base:'../../models/',requireHabitat:()=>buildingReady});
try{
  const [gltf,report]=await Promise.all([new GLTFLoader().loadAsync('../../models/zurafa-acik-yasam-alani.glb?v=20261015am'),fetch('../../models/giraffe-habitat.json').then(r=>r.json())]);
  gltf.scene.rotation.x=Math.PI/2;gltf.scene.position.set(...report.originM5LocalXY,0);parent.add(gltf.scene);
  gltf.scene.traverse(node=>{if(node.isMesh){node.castShadow=node.name!=='savanna_owned_sand';node.receiveShadow=true;for(const material of Array.isArray(node.material)?node.material:[node.material])if(material.map)material.map.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());}});buildingReady=true;
}catch(error){status.textContent='Yaşam alanı açılamadı';console.error(error);}
function frame(){
  const mobile=innerWidth<700;
  if(mode==='animal'){controls.target.set(...(giraffes.focusPoint()||[49,41,2.3]));camera.position.copy(controls.target).add(new T.Vector3(11,-15,mobile?3.5:3));follow=true;}
  else{controls.target.set(60,48,1.5);camera.position.copy(controls.target).add(new T.Vector3(mobile?59:38,mobile?-75:-48,mobile?62:38));follow=false;}
  controls.update();dirty=true;
}
function resize(){camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight,false);if(lastWidth===0||(lastWidth<700)!==(innerWidth<700))frame();lastWidth=innerWidth;dirty=true;}
function choose(next){mode=next;document.getElementById('animal').setAttribute('aria-pressed',String(mode==='animal'));document.getElementById('habitat').setAttribute('aria-pressed',String(mode==='habitat'));frame();}
document.getElementById('animal').onclick=()=>choose('animal');document.getElementById('habitat').onclick=()=>choose('habitat');
document.getElementById('pause').onclick=()=>{paused=!paused;giraffes.setPaused(paused);document.getElementById('pause').setAttribute('aria-pressed',String(paused));document.getElementById('pause').textContent=paused?'Devam et':'Duraklat';};
document.addEventListener('visibilitychange',()=>{dirty=true;});
if(new URLSearchParams(location.search).get('capture')==='1')document.getElementById('capture').hidden=false;
document.getElementById('capture').onclick=()=>{capture=true;dirty=true;};
function tick(now){
  requestAnimationFrame(tick);if(document.hidden)return;
  controls.update();if(giraffes.update(now,camera,innerHeight,12))dirty=true;
  if(follow&&mode==='animal'&&giraffes.focusPoint()){target.set(...giraffes.focusPoint());delta.copy(target).sub(controls.target).multiplyScalar(.12);controls.target.add(delta);camera.position.add(delta);controls.update();dirty=true;}
  if(!dirty)return;renderer.render(scene,camera);dirty=false;
  if(capture){capture=false;renderer.domElement.toBlob(blob=>{if(!blob)return;const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='bursa-baringo-giraffes-v1.png';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);},'image/png');}
}
window.addEventListener('resize',resize);resize();choose(mode);
for(const id of ['animal','habitat','pause'])document.getElementById(id).disabled=false;
requestAnimationFrame(tick);
