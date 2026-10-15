import bpy,bmesh,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
HERE=Path(__file__).resolve().parent
assert hashlib.sha256((HERE/'source/bluemesh-giraffe-1k-original.glb').read_bytes()).hexdigest()=='67ab7005ba6828b32ca900ebc97b01699c030a11b68c1c66f7442f2c8be87bee','Original animal source changed'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(HERE/'source/bluemesh-giraffe-1k-original.glb'))
for o in list(bpy.data.objects):
 if o.type=='LIGHT' or any(s in o.name for s in ['Circle','Icosphere','Lamp']): bpy.data.objects.remove(o,do_unlink=True)
scene=bpy.context.scene;scene.frame_set(1)
meshes=[o for o in scene.objects if o.type=='MESH'];arm=[o for o in scene.objects if o.type=='ARMATURE'][0]
print('OBJECTS',[(o.name,o.type,len(o.data.vertices) if o.type=='MESH' else None) for o in scene.objects]); print('ACTIONS',[(a.name,list(a.frame_range)) for a in bpy.data.actions]);print('BONEMAP',[(b.name, list(arm.matrix_world@b.head_local),list(arm.matrix_world@b.tail_local)) for b in arm.data.bones])
# Evaluate actual initial geometry, then add a metric root without touching rig animation.
deps=bpy.context.evaluated_depsgraph_get();pts=[]
for o in meshes:
 e=o.evaluated_get(deps);m=e.to_mesh();pts.extend(e.matrix_world@v.co for v in m.vertices);e.to_mesh_clear()
lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)])
scale=5.0/(hi.z-lo.z);root=bpy.data.objects.new('BaringoGiraffe_Metres_Interpretation',None);scene.collection.objects.link(root)
for o in [o for o in scene.objects if o.parent is None and o!=root]:o.parent=root
root.scale=(scale,scale,scale);root.location=(-.5*(lo.x+hi.x)*scale,-.5*(lo.y+hi.y)*scale,-lo.z*scale)
bpy.context.view_layer.update()
# Technical UV mask: remove lower-leg spotting while preserving the original map elsewhere.
body=max(meshes,key=lambda o:len(o.data.vertices));uv=body.data.uv_layers.active
# glTF splits vertices at UV islands; subdivision must see a welded geometric
# surface, while loop UVs keep their seams. Otherwise neck/back seams shrink
# into visible holes. Only coincident positions are welded.
bm=bmesh.new();bm.from_mesh(body.data);before=len(bm.verts)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00002);bm.to_mesh(body.data);bm.free();body.data.update()
print('UV_SEAM_WELD',before,len(body.data.vertices))
triangles=[];body.data.calc_loop_triangles()
for tr in body.data.loop_triangles:
 triangles.append({'uv':[list(uv.data[i].uv) for i in tr.loops],'height':[(body.matrix_world@body.data.vertices[i].co).z for i in tr.vertices]})
(HERE/'uv-height-mask.json').write_text(json.dumps(triangles),encoding='utf-8')
for o in meshes:
 for poly in o.data.polygons:poly.use_smooth=True
 if o!=body:continue
 # One Catmull–Clark level before the skin: better long-neck outline, still 15.6k triangles.
 sub=o.modifiers.new('SilhouetteRefinement','SUBSURF');sub.levels=1;sub.render_levels=1;sub.uv_smooth='PRESERVE_BOUNDARIES'
 while list(o.modifiers).index(sub)>0:
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_move_up(modifier=sub.name)
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=sub.name)
 dec=o.modifiers.new('MobileSilhouetteBudget','DECIMATE');dec.ratio=.70
 while list(o.modifiers).index(dec)>0:bpy.ops.object.modifier_move_up(modifier=dec.name)
 bpy.ops.object.modifier_apply(modifier=dec.name)
for mat in bpy.data.materials:
 mat.diffuse_color=(.8,.8,.8,1);mat.surface_render_method='DITHERED'
 if not mat.use_nodes:continue
 bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if bs:bs.inputs['Roughness'].default_value=.88;bs.inputs['Metallic'].default_value=0
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image:
   print('IMAGE',n.image.name,n.image.size[:],n.image.filepath)
   if n.image.name=='Image_0':n.image.filepath_raw=str(HERE/'source-texture.png');n.image.file_format='PNG';n.image.save()
# No source script runs. Save intermediate for technical texture repack/render/export.
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'giraffe-prepared.blend'))
(HERE/'blender-inspection.json').write_text(json.dumps({'sourceBoundsZUp':[list(lo),list(hi)],'scale':scale,'heightInterpretationMetres':5,'bones':len(arm.data.bones),'meshes':[(o.name,len(o.data.polygons))for o in meshes]}),encoding='utf-8')
