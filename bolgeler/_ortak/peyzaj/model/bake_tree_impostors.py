"""Render camera impostors from the exact verified near tree; no repainting.

Blender --background --factory-startup --disable-autoexec SOURCE.blend
--python-exit-code 1 --python THIS.py -- [number of frames, default16]
"""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
SOURCE=OUT/'generic-broadleaf-tree.blend'
build=json.loads((OUT/'build-report.json').read_text(encoding='utf-8'))
blend_record=next(r for r in build['files'] if r['name']==SOURCE.name)
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve()
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==blend_record['sha256']
count=int(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else 16
target=OUT/'impostors';target.mkdir(exist_ok=True)
originals=[obj for obj in bpy.data.objects if obj.type=='MESH' and obj.get('lod')==0]
assert len(originals)==3
scene=bpy.data.scenes.new('Atlas near tree impostor bake');bpy.context.window.scene=scene
trees=[]
for original in originals:
    tree=original.copy();tree.data=original.data.copy();tree.hide_render=False
    scene.collection.objects.link(tree);tree.hide_set(False);trees.append(tree)
points=[tree.matrix_world@vertex.co for tree in trees for vertex in tree.data.vertices]
height=max(v.z for v in points)-min(v.z for v in points);base=min(v.z for v in points)
radial=max(math.hypot(v.x,v.y) for v in points);ortho_scale=max(height*1.45,radial*2.2)
center=Vector((0,0,base+height*.5))
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.cycles.max_bounces=3;scene.cycles.transparent_max_bounces=8
scene.render.threads_mode='FIXED';scene.render.threads=12
scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';scene.render.film_transparent=True
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0
world=bpy.data.worlds.new('Atlas tree ambient');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.83,.66,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=1.2;scene.world=world
sun=bpy.data.lights.new('Atlas tree sun','SUN');sun.energy=3;sun.angle=.08
sun_object=bpy.data.objects.new('Atlas tree sun',sun);scene.collection.objects.link(sun_object)
sun_object.rotation_euler=Vector((-.5,.35,.79)).to_track_quat('Z','Y').to_euler()
camera_data=bpy.data.cameras.new('Atlas tree bake camera');camera_data.type='ORTHO';camera_data.ortho_scale=ortho_scale
camera=bpy.data.objects.new('Atlas tree bake camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera
report={'schema':'bursa-zoo-tree-impostors/v1','source':'https://polyhaven.com/a/jacaranda_tree','license':'CC0',
    'authors':['Rico Cilliers','Rob Tuytel'],'sourceSha256':build['source']['sha256'],
    'renderSourceBlendSha256':blend_record['sha256'],
    'renderSourceGltfSha256':next(r['sha256'] for r in build['files'] if r['name'].endswith('.glb')),
    'sourceModelLOD':0,'sourceTriangles':build['lods'][0]['triangles'],'leafTintLinear':build['leafTintLinear'],
    'method':'Cycles12 samples; the exact editable near LOD including its materials and artistic crown profile. Offline generic vegetation, not a botanical survey.',
    'artisticShape':build['artisticShape'],
    'sourceHeight':height,'sourceBaseZ':base,'sourceRadialExtent':radial,'center':list(center),'orthoScale':ortho_scale,'frameSize':512,'frames':[]}
for index in range(count):
    azimuth=math.radians((index%8)*45);elevation=math.radians(32 if index<8 else 60)
    direction=Vector((math.cos(azimuth)*math.cos(elevation),math.sin(azimuth)*math.cos(elevation),math.sin(elevation)))
    camera.location=center+direction*70;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    path=target/f'tree-{index:02d}.png';scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    report['frames'].append({'index':index,'azimuthDegrees':(index%8)*45,'elevationDegrees':32 if index<8 else 60,
        'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':path.stat().st_size})
    (target/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('ATLAS FRAME READY',index,path.stat().st_size,flush=True)
