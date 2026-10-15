// CPU geometry/rig inspection of the actual production loader. Images are
// represented by PNG dimensions here; the browser renders their real pixels.
import {registerHooks} from 'node:module';
const threeUrl=new URL('../../../../vendor/three.module.js',import.meta.url).href;
registerHooks({resolve(specifier,context,next){
  if(specifier==='three')return {url:threeUrl,shortCircuit:true};
  if(specifier.startsWith('./vendor/')&&context.parentURL.includes('/viewer/'))return {url:new URL('../../../../vendor/'+specifier.slice(9),import.meta.url).href,shortCircuit:true};
  return next(specifier,context);
}});
globalThis.self=globalThis;
globalThis.ProgressEvent=class extends Event{constructor(type,details){super(type);Object.assign(this,details);}};
globalThis.createImageBitmap=async blob=>{
  const bytes=new Uint8Array(await blob.arrayBuffer()),view=new DataView(bytes.buffer);
  return {width:view.getUint32(16),height:view.getUint32(20),close(){}};
};
export const T=await import(threeUrl);
const {GLTFLoader}=await import('../../../../vendor/loaders/GLTFLoader.js');
export async function loadGLB(bytes){
  return new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
}
