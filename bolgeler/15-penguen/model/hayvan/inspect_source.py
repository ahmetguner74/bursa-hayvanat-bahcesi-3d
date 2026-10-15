"""Inspect the licensed GLB and render its actual rig in Blender; no autoexec."""
from pathlib import Path
import json, math
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(HERE/'african-penguin.glb'))
model=list(bpy.context.scene.objects)
info={'objects':[], 'actions':[]}
for obj in model:
    info['objects'].append({'name':obj.name,'type':obj.type,'scale':list(obj.scale),'dimensions':list(obj.dimensions),'location':list(obj.location),'animation':obj.animation_data.action.name if obj.animation_data and obj.animation_data.action else None,'nla':[{'name':t.name,'strips':[s.action.name for s in t.strips]} for t in obj.animation_data.nla_tracks] if obj.animation_data else []})
    if obj.animation_data:
        for track in obj.animation_data.nla_tracks: track.mute=True
        idle=next((s for t in obj.animation_data.nla_tracks for s in t.strips if 'Idle' in s.action.name),None)
        if idle:
            obj.animation_data.action=idle.action
            obj.animation_data.action_slot=idle.action_slot
for action in bpy.data.actions:
    info['actions'].append({'name':action.name,'frames':list(action.frame_range),'slots':[s.identifier for s in action.slots]})
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
depsgraph=bpy.context.evaluated_depsgraph_get()
points=[]
for obj in model:
    if obj.type!='MESH' or obj.name!='Object_9': continue
    evaluated=obj.evaluated_get(depsgraph);mesh=evaluated.to_mesh()
    points.extend(evaluated.matrix_world@v.co for v in mesh.vertices);evaluated.to_mesh_clear()
lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)));centre=(lo+hi)*.5
info['idleBoundsXYZ']=[list(lo),list(hi)]
(HERE/'source-inspection.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
print(json.dumps({'bounds':info['idleBoundsXYZ'],'actions':info['actions']}))
height=hi.z-lo.z
bpy.ops.mesh.primitive_plane_add(size=height*12,location=(centre.x,centre.y,lo.z-.002))
plane=bpy.context.object;plane.name='Preview ground';material=bpy.data.materials.new('Sand');material.diffuse_color=(.32,.30,.25,1);plane.data.materials.append(material)
bpy.ops.object.camera_add(location=centre+Vector((height*1.55,-height*2.5,height*.55)))
camera=bpy.context.object;camera.rotation_euler=(centre-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=height*1.4;bpy.context.scene.camera=camera
for offset,power,size in [((height*2,-height*2,height*3),80,2),((-height*2,height,height*2),40,2)]:
    bpy.ops.object.light_add(type='AREA',location=centre+Vector(offset));lamp=bpy.context.object;lamp.data.energy=power;lamp.data.shape='DISK';lamp.data.size=height*size;lamp.rotation_euler=(centre-lamp.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.world.color=(.22,.22,.22);scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(HERE/'source-preview.png')
scene.view_settings.view_transform='AgX';bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'african-penguin-editable.blend'));bpy.ops.render.render(write_still=True)
