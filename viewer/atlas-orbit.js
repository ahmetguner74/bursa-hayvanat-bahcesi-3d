// All atlas cameras share M5's vertical Z axis. Never change camera.up after
// OrbitControls has cached its spherical coordinate frame.
export const PLAN_TILT = 1e-4;

export function createAtlasOrbit(OrbitControls, camera, element, target, {flat=false, eye=false, onChange, onStart}={}) {
  camera.up.set(0,0,1);
  const position=camera.position.clone();
  const controls=new OrbitControls(camera);
  // The constructor looks at its default target; restore the requested pose.
  camera.position.copy(position);
  controls.target.copy(target);
  controls.enableDamping=true;
  controls.dampingFactor=.09;
  controls.screenSpacePanning=false;
  controls.minZoom=.55;
  controls.maxZoom=18;
  controls.minDistance=2;
  controls.maxDistance=30000;
  controls.minPolarAngle=PLAN_TILT;
  controls.maxPolarAngle=flat?PLAN_TILT:eye?Math.PI*.78:Math.PI*.475;
  controls.enableRotate=!flat;
  if(flat){
    // MOUSE.PAN=2, TOUCH.PAN=1: a flat plan behaves like a map.
    controls.mouseButtons.LEFT=2;
    controls.touches.ONE=1;
  }
  controls.update();
  if(element)controls.connect(element);
  if(onChange)controls.addEventListener('change',onChange);
  if(onStart)controls.addEventListener('start',onStart);
  return controls;
}
