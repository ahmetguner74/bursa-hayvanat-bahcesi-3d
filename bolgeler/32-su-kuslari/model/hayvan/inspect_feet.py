from pathlib import Path
import bpy,json
HERE=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(HERE/'greater-flamingo-editable.blend'))
body=bpy.data.objects['GreaterFlamingo_body']
vertices=[list(v.co) for v in body.data.vertices if v.co.z<.055]
(HERE/'feet-vertices.json').write_text(json.dumps(vertices))
print('foot_vertices',len(vertices),'bounds',[[min(v[i] for v in vertices),max(v[i] for v in vertices)] for i in range(3)])
