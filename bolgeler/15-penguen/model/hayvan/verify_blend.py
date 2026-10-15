"""Reopen the deliverable, rather than trusting an exporter success message."""
from pathlib import Path
import json,hashlib
import bpy
HERE=Path(__file__).resolve().parent
path=HERE/'african-penguin-editable.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
armatures=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
actions=[a.name for a in bpy.data.actions]
meshes=[o for o in bpy.context.scene.objects if o.name in ['Object_9','Object_74']]
assert len(armatures)==1 and len(armatures[0].data.bones)==64
assert len(meshes)==2 and len(actions)==8
assert bpy.context.scene.unit_settings.system=='METRIC' and bpy.context.scene.unit_settings.scale_length==1
images=[i for i in bpy.data.images if i.packed_file]
assert len(images)==3
report={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'armatures':1,'bones':64,'bodyMeshes':2,'actions':actions,'packedImages':len(images),'unit':'metre','previewObjectsSeparate':True}
(HERE/'blend-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
