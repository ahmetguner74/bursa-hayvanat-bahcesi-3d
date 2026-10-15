import {createTapColony} from './tap-colony.js?v=20261016au';
import {createGiraffeMotion} from './giraffe-motion.js?v=20261016at';

export function createGiraffes(parent,onChange,options={}){
  return createTapColony(parent,onChange,{
    name:'Baringo zürafaları · BlueMesh · CC BY 4.0',label:'Zürafa',
    layout:'giraffe-colony.json',assetMeta:'giraffe-asset.json',file:'baringo-giraffe.glb',
    restClip:'Idle_Source_BlueMesh',walkClip:'Walk_Authored_LateralSequence',
    notice:'Idle_Source_BlueMesh',choices:['Idle_Source_BlueMesh','walk'],
    height:5,width:2.8,centre:[60,46,2.4],radius:32,regions:[12],headingOffset:-Math.PI/2,
    specs:meta=>meta.routes,route:createGiraffeMotion,
  },options);
}
