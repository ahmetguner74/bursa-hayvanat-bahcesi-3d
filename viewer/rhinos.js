import * as T from 'three';
import {createTapColony} from './tap-colony.js?v=20261016au';
import {createRhinoMotion} from './rhino-motion.js?v=20261016at';

export function createRhinoIdleClip(root,name='Idle'){
  const tracks=[],times=[0,1.5,3,4.5,6],wave=[0,1,0,-.65,0];
  root.traverse(bone=>{
    if(!bone.isBone)return;
    const values=[];
    for(let i=0;i<times.length;i++){
      const q=bone.quaternion.clone();
      if(bone.name.startsWith('ear001'))q.multiply(new T.Quaternion().setFromAxisAngle(new T.Vector3(0,0,1),wave[i]*(name==='Ears'?.13:.06)*(bone.name.includes('L')?1:-1)));
      if(bone.name==='head_9')q.multiply(new T.Quaternion().setFromAxisAngle(new T.Vector3(0,0,1),wave[i]*(name==='Look'?.035:.012)));
      if(bone.name==='tail001_4')q.multiply(new T.Quaternion().setFromAxisAngle(new T.Vector3(1,0,0),wave[i]*.04));
      values.push(...q.toArray());
    }
    tracks.push(new T.QuaternionKeyframeTrack(bone.name+'.quaternion',times,values));
    tracks.push(new T.VectorKeyframeTrack(bone.name+'.position',[0,6],[...bone.position.toArray(),...bone.position.toArray()]));
  });
  return new T.AnimationClip(name,6,tracks);
}
export function createRhinos(parent,onChange,options={}){
  return createTapColony(parent,onChange,{
    name:'Beyaz gergedanlar · absol · CC BY 4.0',label:'Beyaz gergedan',
    layout:'rhino-colony.json',assetMeta:'rhino-asset.json',file:'white-rhinoceros.glb',
    restClip:'Idle',walkClip:'walk',notice:'Look',choices:['Look','Ears','walk'],
    extraClips:root=>['Idle','Look','Ears'].map(name=>createRhinoIdleClip(root,name)),
    height:1.9,width:4.6,centre:[-43,94,1],radius:28,regions:[16],headingOffset:Math.PI/2,
    specs:meta=>meta.routes,route:createRhinoMotion,
    material(material,spec){
      material.normalScale?.set(.55,.55);
      material.onBeforeCompile=shader=>{
        shader.uniforms.rhinoDust={value:spec.dust};
        shader.fragmentShader='uniform float rhinoDust;\n'+shader.fragmentShader.replace('#include <map_fragment>','#include <map_fragment>\ndiffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.43,0.41,0.37), rhinoDust);');
      };
      material.customProgramCacheKey=()=> 'rhino-dust-v1';
    },
  },options);
}
