"""Preserve the licensed animal's skin and walk while correcting GLB packaging."""
from pathlib import Path
import hashlib,json,struct
from PIL import Image
from io import BytesIO

HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source=HERE/'source/absol-white-rhinoceros-1k-original.glb'
    assert sha(source)=='2d2dfedb813b1eb6f3437bb1769df30661e90649396219bcd63a3423cd59c9de'
    blob=source.read_bytes();length=struct.unpack_from('<I',blob,12)[0]
    tree=json.loads(blob[20:20+length]);binary=bytearray(blob[20+length:])
    rig=json.loads((HERE/'rig-inspection.json').read_text(encoding='utf-8'))
    low,high=rig['rest'];scale=.97
    centre=[(low[i]+high[i])*.5 for i in range(3)]
    tree['nodes'].append({'name':'WhiteRhino_Metres','scale':[scale]*3,
       'translation':[-centre[0]*scale,-low[1]*scale,-centre[2]*scale],
       'children':tree['scenes'][tree.get('scene',0)]['nodes']})
    tree['scenes'][tree.get('scene',0)]['nodes']=[len(tree['nodes'])-1]
    skinned=[i for i,node in enumerate(tree['nodes']) if 'skin' in node]
    for node in tree['nodes']:
        if 'children' in node:node['children']=[i for i in node['children'] if i not in skinned]
    tree['scenes'][tree.get('scene',0)]['nodes'].extend(skinned)
    vertex_views={tree['accessors'][a]['bufferView'] for mesh in tree['meshes'] for p in mesh['primitives'] for a in p['attributes'].values()}
    for animation in tree['animations']:
        for sampler in animation['samplers']:
            for key in ['input','output']:
                a=tree['accessors'][sampler[key]];view=tree['bufferViews'][a['bufferView']]
                if 'byteStride' in view:
                    assert a['componentType']==5126 and view['byteStride']=={'SCALAR':4,'VEC3':12,'VEC4':16}[a['type']] and a['bufferView'] not in vertex_views
                    del view['byteStride']
    cleared=0
    for mesh in tree['meshes']:
        for p in mesh['primitives']:
            joints=tree['accessors'][p['attributes']['JOINTS_0']];weights=tree['accessors'][p['attributes']['WEIGHTS_0']]
            jv=tree['bufferViews'][joints['bufferView']];wv=tree['bufferViews'][weights['bufferView']]
            js={5121:1,5123:2}[joints['componentType']];assert weights['componentType']==5126
            for i in range(joints['count']):
                jo=8+jv.get('byteOffset',0)+joints.get('byteOffset',0)+i*jv.get('byteStride',js*4)
                wo=8+wv.get('byteOffset',0)+weights.get('byteOffset',0)+i*wv.get('byteStride',16)
                for k in range(4):
                    if struct.unpack_from('<f',binary,wo+4*k)[0]==0 and any(binary[jo+k*js:jo+(k+1)*js]):
                        binary[jo+k*js:jo+(k+1)*js]=b'\0'*js;cleared+=1
            for key in ['TEXCOORD_1','TEXCOORD_2']:p['attributes'].pop(key,None)
    for material in tree['materials']:
        material['pbrMetallicRoughness'].update(metallicFactor=0,roughnessFactor=.92)
        material['normalTexture']['scale']=.7
    modifications='Uniform 0.97 metric interpretation, grounded and centred origin, rough nonmetallic hide and 0.7 normal intensity. Removed redundant animation byteStride and unused UV references, cleared only zero-weight joint indices, moved skinned node to scene root. Shape, active weights, walk keyframes and original 1K texture pixels preserved.'
    tree['asset']['extras']['modifications']=modifications
    encoded=json.dumps(tree,separators=(',',':')).encode();encoded+=b' '*(-len(encoded)%4)
    output=struct.pack('<4sII',b'glTF',2,20+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+binary
    target=HERE/'white-rhinoceros.glb';target.write_bytes(output)
    images=[]
    for item in tree['images']:
        v=tree['bufferViews'][item['bufferView']];offset=8+v.get('byteOffset',0)
        with Image.open(BytesIO(binary[offset:offset+v['byteLength']])) as image:images.append({'pixels':list(image.size),'mode':image.mode})
    meta={'schema':'bursa-zoo-white-rhino-asset/v1','author':'absol','license':'CC BY 4.0',
      'sourceUrl':tree['asset']['extras']['source'],'licenseUrl':'https://creativecommons.org/licenses/by/4.0/',
      'retrievedAt':'2026-10-15','method':'Official Sketchfab Download buttons: original Blender ZIP and converted 1K GLB',
      'originals':[{'file':p.relative_to(HERE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted((HERE/'source').rglob('*')) if p.is_file()],
      'delivery':{'file':target.name,'sha256':sha(target),'bytes':len(output),'triangles':9310,'skinnedMeshDraws':1,'joints':46,
        'images':images,'nominalRgbaMipBytes':sum(i['pixels'][0]*i['pixels'][1]*4*4/3 for i in images),
        'restBoundsXYZGlTF':[[(-.5*(high[0]-low[0]))*scale,0,(-.5*(high[2]-low[2]))*scale],[.5*(high[0]-low[0])*scale,(high[1]-low[1])*scale,.5*(high[2]-low[2])*scale]],
        'scaleIsMeasuredAtBursa':False,'modifications':modifications,'clearedZeroWeightIndices':cleared},
      'clips':[{'name':c['name'],'duration':c['duration'],'groundOffsetMetres':[(low[1]-s['bounds'][0][1])*scale for s in c['samples']]} for c in rig['clips']],
      'status':'Local first asset study; natural behaviour, contact quality and final habitat placement still under review'}
    (HERE/'source-manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (HERE/'ATTRIBUTION.txt').write_text('White rhinoceros by absol\n'+meta['sourceUrl']+'\nCC BY 4.0: '+meta['licenseUrl']+'\n'+modifications+'\n',encoding='utf-8')
    print(json.dumps(meta['delivery']))

if __name__=='__main__':main()
