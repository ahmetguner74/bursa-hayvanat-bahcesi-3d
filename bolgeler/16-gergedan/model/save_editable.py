"""Editable metric habitat and two independent rigs; browser controls remain JS."""
from pathlib import Path
import json,math
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
meta=json.loads((HERE/'colony-layout.json').read_text(encoding='utf-8'))
origin=Vector((*meta['originM5LocalXY'],0))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['M5_origin_XY']=list(origin[:2]);scene['scope']='Illustration-registered region 16; dimensions approximate, not surveyed'
scene['animal_source']='https://sketchfab.com/3d-models/white-rhinoceros-939baeb6d62a4824b8edb3c7f7ef54c7'
scene['browser_controller']='viewer/rhinos.js and viewer/rhino-motion.js; walking routes, rest and grounding remain editable there'
habitat_collection=bpy.data.collections.new('16 - editable curved stable and yard');scene.collection.children.link(habitat_collection)
helper_collection=bpy.data.collections.new('Rig helpers - not rendered');scene.collection.children.link(helper_collection)
def move(obj,collection):
    for old in list(obj.users_collection):old.objects.unlink(obj)
    collection.objects.link(obj)
bpy.ops.import_scene.gltf(filepath=str(HERE/'gergedan-yasam-alani.glb'))
habitat=list(scene.objects)
for obj in habitat:move(obj,habitat_collection)
animal_objects=[];rigs=[]
guides=bpy.data.collections.new('Route guides - not rendered');scene.collection.children.link(guides);guides.hide_render=True
for i,spec in enumerate(meta['routes']):
    collection=bpy.data.collections.new(f'Illustrative adult {i+1} - absol CC BY 4.0');scene.collection.children.link(collection)
    previous=set(scene.objects);bpy.ops.import_scene.gltf(filepath=str(HERE/'hayvan/white-rhinoceros.glb'))
    imported=[o for o in scene.objects if o not in previous]
    helpers={bone.custom_shape for obj in imported if obj.type=='ARMATURE' for bone in obj.pose.bones if bone.custom_shape}
    imported=[o for o in imported if o not in helpers]
    for helper in helpers:helper.hide_render=True;helper.hide_set(True);move(helper,helper_collection)
    pts=[Vector((*p,0)) for p in spec['points']];edges=[(pts[(k+1)%len(pts)]-p).length for k,p in enumerate(pts)]
    distance=spec['initialPhase']*sum(edges);j=0
    while distance>edges[j]:distance-=edges[j];j+=1
    tangent=(pts[(j+1)%len(pts)]-pts[j]).normalized()*spec['direction']
    location=pts[j].lerp(pts[(j+1)%len(pts)],distance/edges[j])-origin;location.z=meta['groundZ']
    pivot=bpy.data.objects.new(f'Adult {i+1} placement - local M5',None);collection.objects.link(pivot)
    pivot.location=location;pivot.rotation_euler.z=math.atan2(tangent.y,tangent.x)+math.pi/2;pivot.scale=(spec['scale'],)*3
    for obj in imported:
        if obj.parent not in imported:obj.parent=pivot
        obj['asset_author']='absol';obj['asset_license']='CC BY 4.0';move(obj,collection)
        if obj.type=='ARMATURE':rigs.append(obj)
        if obj.type=='MESH':
            for slot in obj.material_slots:
                material=slot.material
                if not material or not material.use_nodes:continue
                material=material.copy();slot.material=material;nodes=material.node_tree.nodes;links=material.node_tree.links
                bsdf=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
                if bsdf and bsdf.inputs['Base Color'].links:
                    source=bsdf.inputs['Base Color'].links[0].from_socket
                    mix=nodes.new('ShaderNodeMixRGB');mix.label='Dry dust - browser equivalent';mix.blend_type='MIX';mix.inputs[0].default_value=spec['dust'];mix.inputs[2].default_value=(.43,.41,.37,1)
                    links.new(source,mix.inputs[1]);links.new(mix.outputs[0],bsdf.inputs['Base Color'])
    animal_objects+=imported
    curve=bpy.data.curves.new(f'Adult {i+1} route guide','CURVE');curve.dimensions='3D';spline=curve.splines.new('POLY');spline.points.add(len(pts)-1)
    for p,xy in zip(spline.points,pts):p.co=(xy.x-origin.x,xy.y-origin.y,meta['groundZ']+.02,1)
    spline.use_cyclic_u=True;guide=bpy.data.objects.new(curve.name,curve);guides.objects.link(guide);guide.hide_render=True
scene.frame_set(0);scene.render.fps=24;scene.frame_end=115
preview=bpy.data.collections.new('Preview camera and lights');scene.collection.children.link(preview)
target=Vector((-44-origin.x,91-origin.y,.8));bpy.ops.object.camera_add(location=target+Vector((10,-14,6)))
camera=bpy.context.object;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=45;scene.camera=camera;move(camera,preview)
bpy.ops.object.light_add(type='SUN',location=(10,-20,40));lamp=bpy.context.object;lamp.data.energy=2.5;lamp.rotation_euler=(.4,-.4,-.4);move(lamp,preview)
scene.world.color=(.3,.32,.28);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1280;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
bpy.ops.file.pack_all();output=HERE/'gergedan-yasam-alani-editable.blend';bpy.ops.wm.save_as_mainfile(filepath=str(output))
info={'unit':'metre','originM5LocalXY':meta['originM5LocalXY'],'bones':sum(len(o.data.bones) for o in rigs),'rigs':len(rigs),'actions':[a.name for a in bpy.data.actions],'packedImages':sum(bool(i.packed_file) for i in bpy.data.images),'habitatObjects':len(habitat),'animalObjects':len(animal_objects),'sceneFile':output.name,'autoexec':False,'scope':'Editable full habitat and two source walk rigs. Runtime travel, idle and contact controller in JS; route guides retained.'}
(HERE/'blend-report.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8');print(json.dumps(info))
