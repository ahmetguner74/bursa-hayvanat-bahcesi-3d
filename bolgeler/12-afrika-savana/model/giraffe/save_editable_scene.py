"""Save two independently editable rigs plus the reference-informed habitat."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.fps=30;s.frame_start=0;s.frame_end=120
bpy.ops.import_scene.gltf(filepath=str(H/'zurafa-acik-yasam-alani.glb'))
root=bpy.data.objects.new('Savanna_M5_origin_60_48',None);s.collection.objects.link(root)
for o in list(s.objects):
 if o!=root and o.parent is None:o.parent=root
root.location=(60,48,0);root['coordinateFrame']='M5 local ED50/TM30,metres';root['originEd50']=[418823,4454491];root['surveyed']=False
meta=json.loads((H/'giraffe-colony.json').read_text());placements=json.loads((H/'editable-placement.json').read_text())
rigs=[]
for i,p in enumerate(placements):
 before=set(s.objects);bpy.ops.import_scene.gltf(filepath=str(H/'baringo-giraffe.glb'));new=set(s.objects)-before
 pivot=bpy.data.objects.new('IllustrativeBaringo_'+str(i+1),None);s.collection.objects.link(pivot)
 support=bpy.data.objects.new('SoleSupport_'+str(i+1),None);s.collection.objects.link(support);support.parent=pivot
 for o in new:
  if o.parent is None:o.parent=support
  if 'Icosphere'in o.name:o.hide_render=True;o.hide_viewport=True
 pivot.location=(p['x'],p['y'],meta['groundZ']);pivot.rotation_euler.z=p['heading']-math.pi/2;pivot.scale=(p['scale'],)*3
 support.location.z=meta['blendGround']['values'][0][16 if i==0 else 0]
 rig=next(o for o in new if o.type=='ARMATURE');rigs.append(rig)
 wanted='Walk_Authored_LateralSequence'if i==0 else'Idle_Source_BlueMesh';candidate=next(a for a in bpy.data.actions if a.name.startswith(wanted)and a.name.endswith('.001')==bool(i))
 for tr in rig.animation_data.nla_tracks:tr.mute=True
 rig.animation_data.action=candidate
 pivot['visualInterpretation']='Baringo-style CC BY derivative,not an exact individual portrait';pivot['runtimeMotion']='viewer/giraffes.js and giraffe-motion.js;scene pose is preview,paths remain editable in JSON'
for im in bpy.data.images:
 if im.source=='FILE':im.pack()
s.world=bpy.data.worlds.new('SavannaPreviewWorld');s.world.color=(.45,.51,.55)
bpy.ops.object.light_add(type='SUN',location=(60,48,20));sun=bpy.context.object;sun.name='PreviewSun';sun.data.energy=2.2;sun.rotation_euler=(.45,-.4,-.6);sun.data.angle=.04
bpy.ops.object.light_add(type='AREA',location=(40,35,20));fill=bpy.context.object;fill.name='PreviewFill';fill.data.energy=3000;fill.data.size=30
bpy.ops.object.camera_add(location=(94,10,16));cam=bpy.context.object;cam.rotation_euler=(Vector((59,44,3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=43;s.camera=cam
s.frame_set(0)
text=bpy.data.texts.new('MODEL_SOURCES_AND_LIMITS');text.write((H/'ATTRIBUTION.txt').read_text(encoding='utf-8-sig')+'\n\n'+(H/'habitat-inputs.json').read_text(encoding='utf-8'))
bpy.ops.wm.save_as_mainfile(filepath=str(H/'savanna-giraffes-editable.blend'))
assert len(rigs)==2 and sum(len(r.data.bones)for r in rigs)==98
(H/'editable-scene-verification.json').write_text(json.dumps({'file':'savanna-giraffes-editable.blend','independentRigs':2,'bones':98,'metric':True,'habitatOriginM5XY':[60,48],'imagesPacked':all(im.packed_file for im in bpy.data.images if im.source=='FILE'),'sourcePhotoPixelsUsedAsTextures':False,'runtimeRoutes':'giraffe-colony.json','surveyed':False},indent=2),encoding='utf-8')
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(H/'savanna-giraffes-preview.png');bpy.ops.render.render(write_still=True)
