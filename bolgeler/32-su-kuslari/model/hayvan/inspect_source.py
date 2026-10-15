from pathlib import Path
import bpy,json,sys
from mathutils import Vector
HERE=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
name=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'stork'
bpy.ops.import_scene.gltf(filepath=str(HERE/f'source/{name}-original.glb'))
scene=bpy.context.scene;scene.frame_set(0)
meshes=[o for o in scene.objects if o.type=='MESH' and o.hide_render==False]
info=[];pts=[]
for o in meshes:
    coords=[o.matrix_world@v.co for v in o.data.vertices];pts+=coords
    info.append({'name':o.name,'vertices':len(coords),'bounds':[[min(v[i] for v in coords) for i in range(3)],[max(v[i] for v in coords) for i in range(3)]],'materials':[m.name for m in o.data.materials]})
print(json.dumps(info));(HERE/f'{name}-source-inspection.json').write_text(json.dumps(info,indent=2))
lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);target=(lo+hi)/2
scene.world.color=(.45,.45,.45);scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=800;scene.render.resolution_percentage=100
bpy.ops.object.light_add(type='SUN',location=(10,-20,30));bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.5,-.4,-.3)
bpy.ops.object.camera_add(location=target+Vector((5,-6,3)));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=max(hi-lo)*1.35;scene.camera=cam
for name,off in [('front',(5,-7,2)),('side',(-7,1,1)),('top',(0,-1,9))]:
    cam.location=target+Vector(off);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(HERE/(sys.argv[-1]+'-source-'+name+'.png'));bpy.ops.render.render(write_still=True)
