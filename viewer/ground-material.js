import * as T from 'three';

// Numeric weights alter the one existing terrain material. No extra ground
// cap, decal mesh, path polygon or water surface is created here.
export function configureWoodlandGround(material,metadata,manager){
  if(metadata?.schema!=='bursa-zoo-ground-material-weights/v1')throw Error('Zemin malzeme verisi eksik');
  const load=(url,colorSpace)=>{
    const texture=new T.TextureLoader(manager).load(url,()=>window.dispatchEvent(new Event('bursa-assets-ready')));
    texture.colorSpace=colorSpace;texture.anisotropy=4;return texture;
  };
  const weights=load('./'+metadata.image+'?v='+metadata.sha256.slice(0,16),T.NoColorSpace);
  weights.wrapS=weights.wrapT=T.ClampToEdgeWrapping;
  const litter=load('./'+metadata.litterTexture.file+'?v='+metadata.litterTexture.sha256.slice(0,16),T.SRGBColorSpace);
  litter.wrapS=litter.wrapT=T.RepeatWrapping;
  const [x0,y0,x1,y1]=metadata.boundsXYMetres;
  material.onBeforeCompile=shader=>{
    shader.uniforms.groundWeights={value:weights};shader.uniforms.leafLitter={value:litter};
    shader.uniforms.groundBounds={value:new T.Vector4(x0,y0,x1-x0,y1-y0)};
    shader.vertexShader='varying vec2 groundXY;\n'+shader.vertexShader;
    shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>',
      '#include <begin_vertex>\ngroundXY=(modelMatrix*vec4(transformed,1.0)).xy;');
    shader.fragmentShader='uniform sampler2D groundWeights;\nuniform sampler2D leafLitter;\nuniform vec4 groundBounds;\nvarying vec2 groundXY;\n'+shader.fragmentShader;
    shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`#include <map_fragment>
      vec2 groundUv=(groundXY-groundBounds.xy)/groundBounds.zw;
      vec3 weights=texture2D(groundWeights,groundUv).rgb;
      vec3 earth=texture2D(leafLitter,groundXY/3.0).rgb;
      // The generated meadow map supplies broad albedo variation as well as
      // close detail. Lighting still comes from the real scene lights.
      vec3 macro=texture2D(map,groundXY/65.0).rgb;
      float macroValue=dot(macro,vec3(.2126,.7152,.0722));
      diffuseColor.rgb*=mix(.82,1.18,smoothstep(.055,.24,macroValue));
      diffuseColor.rgb=mix(diffuseColor.rgb,earth,weights.r);
      diffuseColor.rgb*=mix(vec3(1.0),vec3(.82,.94,.86),weights.g*.4);
      diffuseColor.rgb=mix(diffuseColor.rgb,diffuseColor.rgb*vec3(1.13,1.035,.88),weights.b*.38);
    `);
  };
  material.customProgramCacheKey=()=> 'woodland-ground-context/v1';
  material.userData.groundWeightsSha256=metadata.sha256;
  material.needsUpdate=true;
}
