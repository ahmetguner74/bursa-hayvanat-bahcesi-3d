"""Keep every vertex/keyframe; put skinned meshes at scene root per glTF."""
from pathlib import Path
import json,struct
H=Path(__file__).resolve().parent;p=H/'baringo-giraffe.glb';b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);binary=b[20+n:]
skinned=[i for i,node in enumerate(j['nodes'])if'skin'in node]
for node in j['nodes']:
 if'children'in node:node['children']=[i for i in node['children']if i not in skinned]
j['scenes'][j.get('scene',0)]['nodes'].extend(i for i in skinned if i not in j['scenes'][j.get('scene',0)]['nodes'])
j['asset']['extras']={'author':'BlueMesh','source':'https://sketchfab.com/3d-models/giraffe-522c042aad9f4348a74c2985ec3f99f9','license':'CC BY4.0','modifications':'Metric5m interpretation; welded coincident UV-seam vertices before subdivision/decimation; new authored lateral-sequence walk, original idle retained; plain lower-leg albedo adaptation. Skinned nodes moved to scene root; active joint weights,UV and animation data unchanged by this packaging step.'}
e=json.dumps(j,separators=(',',':')).encode();e+=b' '*(-len(e)%4);p.write_bytes(struct.pack('<4sII',b'glTF',2,20+len(e)+len(binary))+struct.pack('<II',len(e),0x4e4f534a)+e+binary)
