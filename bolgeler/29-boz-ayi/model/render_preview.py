"""Import the actual GLB into an editable Blender file and render that asset."""
import bpy,hashlib,json,math
from pathlib import Path
from mathutils import Vector

HERE=Path(__file__).resolve().parent
inputs=json.loads((HERE/'model-inputs.json').read_text(encoding='utf-8'))
asset=HERE/'boz-ayi-havuz-kiyisi.glb'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(asset))
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene['source_glb_sha256']=hashlib.sha256(asset.read_bytes()).hexdigest()
scene['origin_m5_local_xy_metres']=inputs['originM5LocalXY']
scene['source_id']=inputs['poolSourceId']
scene['interpretation']='Candidate region29 pool component. Native XY retained; bank/rocks/plants/heights are visual estimates. Region28/29 boundary unverified.'
model_objects=[o for o in scene.objects if o.type=='MESH']
model_collection=bpy.data.collections.new('Model · M5 metres');scene.collection.children.link(model_collection)
for o in model_objects:
    for collection in list(o.users_collection):collection.objects.unlink(o)
    model_collection.objects.link(o)
preview_collection=bpy.data.collections.new('Preview only · camera lights ground');scene.collection.children.link(preview_collection)
def preview_object(o):
    for collection in list(o.users_collection):collection.objects.unlink(o)
    preview_collection.objects.link(o)

points=[o.matrix_world@Vector(p) for o in model_objects for p in o.bound_box]
low=Vector(tuple(min(p[i] for p in points) for i in range(3)))
high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
target=(low+high)*.5
bpy.ops.object.camera_add(location=target+Vector((58,-77,59)))
camera=bpy.context.object;camera.name='Preview camera';preview_object(camera)
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=max(high.x-low.x,high.y-low.y)*1.23
scene.camera=camera
bpy.ops.object.light_add(type='SUN',location=(0,0,60))
sun=bpy.context.object;sun.name='Preview warm sun';sun.data.energy=2.2
sun.rotation_euler=(math.radians(24),math.radians(-28),math.radians(-35));sun.data.angle=.10;preview_object(sun)
bpy.ops.object.light_add(type='AREA',location=target+Vector((-18,12,32)))
fill=bpy.context.object;fill.name='Preview soft fill';fill.data.energy=4500;fill.data.shape='DISK';fill.data.size=40
fill.rotation_euler=(target-fill.location).to_track_quat('-Z','Y').to_euler();preview_object(fill)
bpy.ops.mesh.primitive_plane_add(size=220,location=(0,0,-1.72))
ground=bpy.context.object;ground.name='Preview background only';preview_object(ground)
mat=bpy.data.materials.new('Preview pale background');mat.diffuse_color=(.62,.70,.57,1);ground.data.materials.append(mat)
world=bpy.data.worlds.new('Preview world');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.55,.62,.49,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;scene.world=world
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(HERE/'preview.png')
scene.view_settings.view_transform='AgX'
for image in bpy.data.images:
    if image.source=='FILE' and not image.packed_file:image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'boz-ayi-havuz-kiyisi.blend'))
bpy.ops.render.render(write_still=True)
(HERE/'preview-source.json').write_text(json.dumps({'renderSourceGlbSha256':scene['source_glb_sha256'],
    'blendSha256':hashlib.sha256((HERE/'boz-ayi-havuz-kiyisi.blend').read_bytes()).hexdigest(),
    'imageSha256':hashlib.sha256((HERE/'preview.png').read_bytes()).hexdigest(),'blenderVersion':bpy.app.version_string,
    'renderEngine':'Cycles','samples':32,'sizePixels':[1200,800],
    'note':'Offline render of the actual GLB; not a browser screenshot or new concept image.'},indent=2)+'\n',encoding='utf-8')
