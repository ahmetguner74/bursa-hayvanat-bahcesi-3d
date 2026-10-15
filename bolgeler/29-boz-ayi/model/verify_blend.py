"""Run in Blender after opening the saved editable asset, not the builder scene."""
import bpy,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
report=json.loads((HERE/'model-report.json').read_text(encoding='utf-8'))
inputs=json.loads((HERE/'model-inputs.json').read_text(encoding='utf-8'))
scene=bpy.context.scene;models=bpy.data.collections['Model · M5 metres'].objects
assert scene.unit_settings.system=='METRIC' and scene.unit_settings.scale_length==1
assert list(scene['origin_m5_local_xy_metres'])==inputs['originM5LocalXY']
assert scene['source_glb_sha256']==hashlib.sha256((HERE/'boz-ayi-havuz-kiyisi.glb').read_bytes()).hexdigest()
triangles=0
for obj in models:
    assert obj.type=='MESH';obj.data.calc_loop_triangles();triangles+=len(obj.data.loop_triangles)
assert triangles==report['triangles'] and len(models)==8
assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
assert all(obj not in list(models) for obj in bpy.data.collections['Preview only · camera lights ground'].objects)
print(json.dumps({'modelObjects':len(models),'modelTriangles':triangles,'packedTextures':True,'m5OriginRetained':True}))
