import bpy,json
from pathlib import Path
H=Path('bolgeler/12-afrika-savana/model/giraffe').resolve();bpy.ops.wm.open_mainfile(filepath=str(H/'savanna-giraffes-editable.blend'),load_ui=False)
rigs=[o for o in bpy.data.objects if o.type=='ARMATURE'];assert len(rigs)==2 and sum(len(o.data.bones)for o in rigs)==98 and rigs[0].data!=rigs[1].data
j=json.loads((H/'editable-scene-verification.json').read_text());j['reopenedFromSavedFile']=True;j['independentArmatureData']=True;j['packedImagesReopened']=sum(bool(im.packed_file)for im in bpy.data.images);(H/'editable-scene-verification.json').write_text(json.dumps(j,indent=2),encoding='utf-8');print('EDITABLE_REOPEN',len(rigs),sum(len(o.data.bones)for o in rigs),j['packedImagesReopened'])
