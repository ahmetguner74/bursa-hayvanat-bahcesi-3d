"""Make Blender's skinned scene hierarchy portable and preserve provenance."""
import json,struct
from pathlib import Path

def finalize(path):
    data=Path(path).read_bytes();length=struct.unpack_from('<I',data,12)[0]
    tree=json.loads(data[20:20+length]);binary=data[20+length:]
    skinned=[i for i,node in enumerate(tree['nodes']) if 'skin' in node]
    for node in tree['nodes']:
        if 'children' in node:node['children']=[i for i in node['children'] if i not in skinned]
    roots=tree['scenes'][tree.get('scene',0)]['nodes']
    for i in skinned:
        if i not in roots:roots.append(i)
    for mesh in tree['meshes']:
        for primitive in mesh['primitives']:primitive['attributes'].pop('TEXCOORD_2',None)
    tree['asset']['extras']={'author':'Pigcraft (https://sketchfab.com/s8819296)','license':'CC BY4.0 (https://creativecommons.org/licenses/by/4.0/)','source':'https://sketchfab.com/3d-models/greater-flamingo-resting-rigged-bird-1c54310c3877422497d37512f0ba33dc','modifications':'12k metric derivative; masked neck smoothing; interdigital webs; pale-plumage material bake; original five-bone rest/looking clips authored locally. Source is AI-assisted, had no rig/clips. Not a scan or individually identified animal at Bursa Zoo.'}
    encoded=json.dumps(tree,separators=(',',':'),ensure_ascii=True).encode();encoded+=b' '*(-len(encoded)%4)
    Path(path).write_bytes(struct.pack('<4sII',b'glTF',2,20+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+binary)

if __name__=='__main__':finalize(Path(__file__).parent/'greater-flamingo.glb')
