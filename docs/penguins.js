import * as T from 'three';
import {GLTFLoader} from './vendor/loaders/GLTFLoader.js';
import {clone} from './vendor/utils/SkeletonUtils.js';
import {createPenguinBehavior,groundOffset} from './penguin-motion.js?v=20261015ai';

export function createPenguins(parent,onChange){
  const group=new T.Group();group.name='Afrika penguenleri · Major · CC BY 4.0';group.visible=false;parent.add(group);
  const frustum=new T.Frustum(),matrix=new T.Matrix4(),centre=new T.Vector3(-10,129,0),viewCentre=new T.Vector3(),sphere=new T.Sphere(),box=new T.Box3(new T.Vector3(-29,120,-1.4),new T.Vector3(1,146,1));
  let state='idle',meta=null,actors=[],neighbors=[],lastTime=null,enabled=true;
  const debug=new URLSearchParams(location.search).get('animaldebug')==='1';
  let updates=0,updateMs=0,maxUpdateMs=0,reported=false;const cadence=[];
  async function load(){
    state='loading';onChange();
    try{
      const response=await fetch('./models/penguin-colony.json',{cache:'no-store'});
      if(!response.ok)throw Error('Penguen yerleşimi yüklenemedi');meta=await response.json();
      const gltf=await new GLTFLoader().loadAsync('./'+meta.asset+'?v='+meta.assetSha256.slice(0,16));
      // SkeletonUtils clones independent bones while retaining shared geometry,
      // materials and textures. Only ten small skinned meshes are added.
      actors=[...meta.landStarts,...meta.waterStarts].map((_,index)=>{
        const rig=clone(gltf.scene),pivot=new T.Group(),axis=new T.Group();axis.rotation.x=Math.PI/2;axis.add(rig);pivot.add(axis);group.add(pivot);
        const behavior=createPenguinBehavior(meta,index);pivot.scale.setScalar(behavior.scale);
        rig.traverse(node=>{if(node.isMesh){node.castShadow=!behavior.water;node.receiveShadow=true;node.frustumCulled=false;if(node.material.map)node.material.map.anisotropy=4;}});
        const mixer=new T.AnimationMixer(rig),actions=Object.fromEntries(gltf.animations.map(clip=>[clip.name,mixer.clipAction(clip)]));
        const action=actions[behavior.clip];action.play();action.time=index*.731%action.getClip().duration;
        return {rig,pivot,behavior,mixer,actions,actionList:Object.entries(actions),current:action};
      });
      neighbors=actors.map(actor=>actor.behavior);
      state='ready';lastTime=null;onChange();
      if(debug)console.info('Penguin asset',JSON.stringify({birds:actors.length,triangles:meta.trianglesPerBird*actors.length,skinDraws:meta.meshDrawsPerBird*actors.length,sharedGeometry:true,sharedTextures:true,clips:Object.keys(meta.clips)}));
    }catch(error){state='error';console.warn('Penguen modeli yüklenemedi.',error);onChange();}
  }
  function update(now,camera,viewportHeight,region){
    camera.updateMatrixWorld();matrix.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);frustum.setFromProjectionMatrix(matrix);
    const depth=Math.max(.5,-viewCentre.copy(centre).applyMatrix4(camera.matrixWorldInverse).z);
    const pixels=camera.isOrthographicCamera?.62*viewportHeight*camera.zoom/(camera.top-camera.bottom):.62*viewportHeight*camera.zoom/(2*depth*Math.tan(T.MathUtils.degToRad(camera.fov)/2));
    let inFrame=frustum.intersectsBox(box);
    if(actors.length){
      inFrame=false;
      for(const actor of actors){
        const b=actor.behavior;sphere.center.set(b.x,b.y,b.water?meta.waterZ+(.03-b.dive)*b.scale:meta.groundZ+.32*b.scale);sphere.radius=.62*b.scale;
        actor.pivot.visible=frustum.intersectsSphere(sphere);inFrame||=actor.pivot.visible;
      }
    }
    const visible=enabled&&parent.visible&&!document.hidden&&inFrame&&(region===15||pixels>=3);
    const changed=group.visible!==(visible&&state==='ready');group.visible=visible&&state==='ready';
    if(!visible){lastTime=null;return changed;}
    if(state==='idle'){void load();return changed;}
    if(state!=='ready')return changed;
    const interval=pixels>=24?(innerWidth<760?1000/30:1000/60):1000/12;
    if(lastTime!==null&&now-lastTime<interval-.5)return changed;
    // Resume without catching up hours of hidden motion or jumping after a stall.
    if(debug&&lastTime!==null&&cadence.length<180)cadence.push(now-lastTime);
    const dt=lastTime===null?1/60:Math.min((now-lastTime)/1000,.08);lastTime=now;
    const began=debug?performance.now():0;
    for(const actor of actors){
      const bird=actor.behavior.update(dt,neighbors);
      actor.pivot.position.set(bird.x,bird.y,bird.water?meta.waterZ+(meta.swimAnchorOffsetMetres-bird.dive)*bird.scale:meta.groundZ);
      actor.pivot.rotation.z=bird.heading+Math.PI/2;
      if(!actor.pivot.visible)continue;
      const action=actor.actions[bird.clip];
      if(action!==actor.current){
        action.reset().setEffectiveWeight(1).setEffectiveTimeScale(1).play();actor.current.crossFadeTo(action,.55,false);actor.current=action;
      }
      action.setEffectiveTimeScale(bird.pace);actor.mixer.update(dt);
      let lift=0,weight=0;
      if(!bird.water)for(const [name,a] of actor.actionList){
        const w=a.getEffectiveWeight();if(!a.isRunning()||w<=0)continue;lift+=groundOffset(meta.clips,name,a.time)*w;weight+=w;
      }
      actor.rig.position.y=weight?lift/weight:0;
    }
    if(debug){
      const elapsed=performance.now()-began;updates++;updateMs+=elapsed;maxUpdateMs=Math.max(maxUpdateMs,elapsed);
      if(!reported&&updates>=180){
        const sorted=cadence.slice().sort((a,b)=>a-b),mean=cadence.reduce((sum,n)=>sum+n,0)/cadence.length;
        console.info('Penguin animation profile',JSON.stringify({updates,meanCpuMs:updateMs/updates,maxCpuMs:maxUpdateMs,targetHz:1000/interval,observedUpdateHz:1000/mean,p95UpdateIntervalMs:sorted[Math.floor(sorted.length*.95)],colonyBirds:actors.length,visibleSkeletons:actors.reduce((sum,a)=>sum+Number(a.pivot.visible),0),wholeSceneGpuMeasured:false}));reported=true;
      }
    }
    return true;
  }
  return {update,status:()=>state,setEnabled(value){enabled=value;lastTime=null;onChange();},retry(){if(state==='error'){state='idle';onChange();}}};
}
