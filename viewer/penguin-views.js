import * as T from 'three';

export function penguinColonyView(width){
  return width<760
    ?{position:[-1.2,117.2,5.6],target:[-7.9,124.5,.2],fov:56}
    :{position:[-2.988,116.52,5.49],target:[-7.7,124.5,.55],fov:44};
}
export function penguinTarget(animal,width){
  return [animal.point[0],animal.point[1],animal.point[2]+animal.height*(width<600?.12:.03)];
}
export function penguinFocusView(animal,width){
  const colony=penguinColonyView(width),target=penguinTarget(animal,width);
  const offset=new T.Vector3(...colony.position).sub(new T.Vector3(...colony.target)).normalize().multiplyScalar(animal.water?2.8:3.7);
  return {position:new T.Vector3(...target).add(offset).toArray(),target,fov:colony.fov};
}
