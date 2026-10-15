import * as T from 'three';
import {GTAOPass} from './vendor/postprocessing/GTAOPass.js';
import {OutputPass} from './vendor/postprocessing/OutputPass.js';

// Depth comes from the beauty render, so the real alpha cutouts are respected.
// An override normal material would turn leaf cards into opaque rectangles.
export function createSceneFinishing(renderer,scene,initialCamera){
  if(!renderer.extensions.has('EXT_color_buffer_float')||new URLSearchParams(location.search).get('finish')==='0'){
    console.info('Scene finishing: direct renderer fallback');
    return {render(camera){renderer.setRenderTarget(null);renderer.render(scene,camera);}};
  }
  const gl=renderer.getContext();
  const colorSamples=Array.from(gl.getInternalformatParameter(gl.RENDERBUFFER,gl.RGBA16F,gl.SAMPLES)||[]);
  const depthSamples=Array.from(gl.getInternalformatParameter(gl.RENDERBUFFER,gl.DEPTH_COMPONENT24,gl.SAMPLES)||[]);
  const samples=Math.max(0,...colorSamples.filter(n=>n<=4&&depthSamples.includes(n)));
  console.info('Scene finishing targets',JSON.stringify({color:'RGBA16F',samples,aoMaxEdge:768}));
  const color=new T.WebGLRenderTarget(1,1,{type:T.HalfFloatType,samples,
    depthTexture:new T.DepthTexture(1,1,T.UnsignedIntType)});
  color.texture.name='Atlas linear beauty and alpha-tested depth';
  const composite=new T.WebGLRenderTarget(1,1,{type:T.HalfFloatType,depthBuffer:false});
  const ao=new GTAOPass(scene,initialCamera,1,1);
  ao.setGBuffer(color.depthTexture);
  ao.blendIntensity=.55;
  ao.updateGtaoMaterial({radius:2.2,thickness:.5,distanceFallOff:1,scale:.75,samples:12});
  ao.updatePdMaterial({samples:8,radius:4,depthPhi:2,normalPhi:3});
  const output=new OutputPass();output.renderToScreen=true;
  const size=new T.Vector2();
  let width=0,height=0;
  const enabled=new URLSearchParams(location.search).get('ao')!=='0';
  function render(camera){
    renderer.getDrawingBufferSize(size);
    if(size.x!==width||size.y!==height){
      width=size.x;height=size.y;color.setSize(width,height);composite.setSize(width,height);
      const scale=Math.min(.7,768/Math.max(width,height));
      ao.setSize(Math.max(1,Math.round(width*scale)),Math.max(1,Math.round(height*scale)));
    }
    ao.camera=camera;
    const perspective=camera.isPerspectiveCamera?1:0;
    if(ao.gtaoMaterial.defines.PERSPECTIVE_CAMERA!==perspective){
      ao.gtaoMaterial.defines.PERSPECTIVE_CAMERA=perspective;ao.gtaoMaterial.needsUpdate=true;
    }
    renderer.setRenderTarget(color);renderer.render(scene,camera);
    if(enabled){ao.render(renderer,composite,color);output.render(renderer,null,composite);}
    else output.render(renderer,null,color);
    renderer.setRenderTarget(null);
  }
  return {render};
}
