import * as T from 'three';

/** A single, non-interactive discovery cue; never adds a mesh or render pass. */
export function createTouchCue(element,storage=globalThis.sessionStorage){
  const key='bursa-zoo-animal-touch-v1',point=new T.Vector3(),view=new T.Vector3();
  let consumed=false,shown=false,start=null;
  try{consumed=storage?.getItem(key)==='seen';}catch{}
  function hide(){element.hidden=true;}
  function complete(){consumed=true;hide();try{storage?.setItem(key,'seen');}catch{}}
  function update(animals,camera,width,height,now,eligible){
    if(consumed){hide();return;}
    if(!eligible){if(shown)complete();else hide();return;}
    if(shown&&now-start>=4000){complete();return;}
    camera.updateMatrixWorld();
    const candidates=animals.filter(a=>a.visible).map(animal=>{
      point.set(...animal.point);const depth=-view.copy(point).applyMatrix4(camera.matrixWorldInverse).z;point.project(camera);
      const pixels=animal.height*height/(2*Math.max(.1,depth)*Math.tan(T.MathUtils.degToRad(camera.fov/2)));
      return {x:(point.x+1)*width/2,y:(1-point.y)*height/2,pixels,depth};
    }).filter(p=>p.depth>0&&p.pixels>=24&&p.x>24&&p.x<width-24&&p.y>120&&p.y<height*.68).sort((a,b)=>b.pixels-a.pixels);
    const target=candidates[0];if(!target){hide();return;}
    if(!shown){shown=true;start=now;try{storage?.setItem(key,'seen');}catch{}}
    element.style.left=Math.min(width-80,target.x+8)+'px';element.style.top=(target.y+10)+'px';element.hidden=false;
  }
  return {update,hide,complete};
}
