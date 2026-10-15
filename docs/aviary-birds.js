import * as T from 'three';
import {createTapColony} from './tap-colony.js?v=20261016au';

/** Refine the authored neck poses once at load; feet and body placement stay put. */
export function createFlamingoReactions(animations){
  const identity=new T.Quaternion();
  return animations.filter(clip=>['LookAround','Settle'].includes(clip.name)).map(source=>{
    const clip=source.clone(),factor=source.name==='LookAround'?3.2:2.4;
    for(const track of clip.tracks){
      for(let i=0;i<track.times.length;i++)track.times[i]*=.8;
      if(!track.name.endsWith('.quaternion')||!['NeckBase','NeckUpper','Head'].some(name=>track.name.startsWith(name+'.')))continue;
      const base=new T.Quaternion().fromArray(track.values,0),inverse=base.clone().invert();
      for(let i=0;i<track.values.length;i+=4){
        const delta=inverse.clone().multiply(new T.Quaternion().fromArray(track.values,i));
        const angle=2*Math.acos(T.MathUtils.clamp(delta.w,-1,1));
        const scaled=identity.clone().slerp(delta,angle>1e-6?Math.min(factor,.6/angle):1);
        base.clone().multiply(scaled).normalize().toArray(track.values,i);
      }
    }
    clip.duration*=.8;return clip;
  });
}

// This resting rig supports restrained reactions, not flight or swimming.
export function createAviaryBirds(parent,onChange,options={}){
  const anchor=options.anchor||{x:-30,y:-64,angle:9*Math.PI/180};
  const toWorld=(x,y)=>[anchor.x+x*Math.cos(anchor.angle)-y*Math.sin(anchor.angle),anchor.y+x*Math.sin(anchor.angle)+y*Math.cos(anchor.angle)];
  return createTapColony(parent,onChange,{
    name:'Flamingolar · Pigcraft · CC BY 4.0',label:'Flamingo',layout:'aviary-birds-layout.json',file:'greater-flamingo.glb',
    restClip:'Rest',notice:'LookAround',choices:['LookAround','Settle','Rest'],tapChoices:['LookAround','Settle'],firstBehavior:'LookAround',
    extraClips:(_root,animations)=>createFlamingoReactions(animations),
    height:1.3,width:.85,centre:[...toWorld(-7,-11.1),.45],radius:8,regions:[31,32],
    specs:meta=>meta.animals,
    place(pivot,spec,meta){pivot.position.set(...toWorld(...spec.localXY),options.surfaceData?.renderLevels?.terrainZ??meta.groundZ);pivot.rotation.z=anchor.angle+spec.heading;},
    material(material){material.normalScale?.set(.12,.12);},
  },options);
}
