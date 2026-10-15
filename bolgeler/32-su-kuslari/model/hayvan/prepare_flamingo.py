"""Build a small, editable CC BY derivative; no runtime mesh simulation.

Source is AI-assisted and has NO original skeleton or animation, despite its
title. This adds a restrained five-bone rest/looking rig, never locomotion.
"""
from pathlib import Path
import bpy, bmesh, math, json, hashlib, sys, struct
from mathutils import Vector, Matrix

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));from finalize_glb import finalize
SOURCE=HERE/'source/flamingo-original.glb'
EXPECTED='1f84fc62873c83cc148dc15befd304f4efb0d87b01c9f026a9470972ecd2f899'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
meshes=[o for o in scene.objects if o.type=='MESH']
for o in meshes:
    matrix=o.matrix_world.copy();o.parent=None;o.matrix_world=matrix
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();body=bpy.context.object;body.name='GreaterFlamingo_body'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
for o in list(scene.objects):
    if o!=body:bpy.data.objects.remove(o,do_unlink=True)
# Weld only duplicate chunk edges. The diffuse and normal UV sets stay intact.
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.0000003);bm.to_mesh(body.data);bm.free()
before=len(body.data.polygons)
dec=body.modifiers.new('Web derivative - 12000 triangle budget','DECIMATE');dec.ratio=12000/before;dec.use_collapse_triangulate=True
bpy.ops.object.modifier_apply(modifier=dec.name)
coords=[v.co for v in body.data.vertices];zlo=min(v.z for v in coords);zhi=max(v.z for v in coords);factor=1.30/(zhi-zlo)
feet=[v for v in coords if v.z<zlo+.025];footcentre=Vector((sum(v.x for v in feet)/len(feet),sum(v.y for v in feet)/len(feet),zlo))
rotate=Matrix.Rotation(-math.pi/2,3,'Z')
for v in body.data.vertices:v.co=rotate@((v.co-footcentre)*factor)
neckgroup=body.vertex_groups.new(name='NeckSmoothing')
for v in body.data.vertices:
    if v.co.y>.28 and .83<v.co.z<1.18:neckgroup.add([v.index],1,'REPLACE')
smoothmod=body.modifiers.new('Remove source neck surface lumps','SMOOTH');smoothmod.vertex_group=neckgroup.name;smoothmod.factor=.65;smoothmod.iterations=6
bpy.ops.object.modifier_apply(modifier=smoothmod.name);body.vertex_groups.remove(body.vertex_groups['NeckSmoothing'])
for p in body.data.polygons:p.use_smooth=True
body.data.update()
# Keep the real licensed texture pixels and their UVs; technical 1K source.
material=body.data.materials[0]
body.data.materials.clear();body.data.materials.append(material)
for p in body.data.polygons:p.material_index=0
nodes=material.node_tree.nodes
bsdf=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Roughness'].default_value=.87
for n in nodes:
    if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.12
# Bake a documented material colour correction, leaving licensed source pixels
# untouched in the archive. Dark beak/eyes and the red legs keep source colour.
original=bsdf.inputs['Base Color'].links[0].from_socket
links=material.node_tree.links
maskattr=body.data.color_attributes.new(name='PlumageMask',type='FLOAT_COLOR',domain='POINT')
for v in body.data.vertices:
    mask=max(0,min(1,(v.co.z-.66)/.15));maskattr.data[v.index].color=(mask,mask,mask,1)
attribute=nodes.new('ShaderNodeVertexColor');attribute.layer_name='PlumageMask'
bw=nodes.new('ShaderNodeRGBToBW');links.new(original,bw.inputs[0])
remap=nodes.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=.12;remap.inputs['From Max'].default_value=.28;links.new(bw.outputs[0],remap.inputs['Value'])
multiply=nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY';links.new(attribute.outputs['Color'],multiply.inputs[0]);links.new(remap.outputs[0],multiply.inputs[1])
hue=nodes.new('ShaderNodeHueSaturation');hue.inputs['Saturation'].default_value=.35;links.new(original,hue.inputs['Color'])
light=nodes.new('ShaderNodeMixRGB');light.inputs[0].default_value=.28;light.inputs[2].default_value=(.83,.78,.75,1);links.new(hue.outputs['Color'],light.inputs[1])
colour=nodes.new('ShaderNodeMixRGB');links.new(multiply.outputs[0],colour.inputs[0]);links.new(original,colour.inputs[1]);links.new(light.outputs[0],colour.inputs[2])
emission=nodes.new('ShaderNodeEmission');links.new(colour.outputs[0],emission.inputs[0]);output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');links.new(emission.outputs[0],output.inputs['Surface'])
image=bpy.data.images.new('Greater flamingo - pale plumage material bake',width=1024,height=1024,alpha=False);image.colorspace_settings.name='sRGB'
texture=nodes.new('ShaderNodeTexImage');texture.image=image;nodes.active=texture;texture.select=True
scene.render.engine='CYCLES';scene.cycles.samples=1;scene.render.bake.margin=8
body.data.uv_layers.active_index=0;bpy.ops.object.bake(type='EMIT')
image.filepath_raw=str(HERE/'derived-plumage.png');image.file_format='PNG';image.save();links.new(bsdf.outputs[0],output.inputs['Surface']);links.new(texture.outputs['Color'],bsdf.inputs['Base Color'])
body.data.color_attributes.remove(maskattr)
# Add the missing thin interdigital membranes. Original source toes and ankle
# remain; the outer web edge is concave between toes, not a solid square pad.
footmat=bpy.data.materials.new('Flamingo interdigital skin');footmat.use_nodes=True;footbsdf=footmat.node_tree.nodes.get('Principled BSDF');footbsdf.inputs['Base Color'].default_value=(.34,.14,.17,1);footbsdf.inputs['Roughness'].default_value=.9
left=[(-.101,-.035),(-.209,-.015),(-.161,-.004),(-.173,.052),(-.125,.018),(-.095,.070)]
verts=[];faces=[]
for side in [0,1]:
    points=left if side==0 else [(-x-.012,y) for x,y in left]
    start=len(verts);verts += [(x,y,z) for z in [.013,.017] for x,y in points]
    # Fan triangulation follows this star-shaped footprint from the ankle.
    for i in range(1,len(points)-1):faces += [(start,start+i+1,start+i),(start+6,start+6+i,start+6+i+1)]
    for i in range(6):j=(i+1)%6;faces += [(start+i,start+j,start+6+j,start+6+i)]
mesh=bpy.data.meshes.new('Corrected webbed feet');mesh.from_pydata(verts,[],faces)
# Mirroring reverses handedness. Orient each closed membrane outwards rather
# than leaving one foot inside out; this also gives positive signed volumes.
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
mesh.materials.append(footmat);web=bpy.data.objects.new('Flamingo_webbed_feet',mesh);scene.collection.objects.link(web)
rigdata=bpy.data.armatures.new('Flamingo_rest_rig');rig=bpy.data.objects.new('FlamingoRig',rigdata);scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;body.select_set(False);rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
specs=[('Root',(0,0,0),(0,0,.25),None),('Body',(0,0,.72),(0,0,1.04),'Root'),('NeckBase',(0,.24,.84),(0,.40,.98),'Body'),('NeckUpper',(0,.40,.98),(0,.43,1.18),'NeckBase'),('Head',(0,.43,1.18),(0,.43,1.29),'NeckUpper')]
for name,head,tail,parent in specs:
    b=rigdata.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=rigdata.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT')
groups={name:body.vertex_groups.new(name=name) for name,*_ in specs}
def smooth(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
for v in body.data.vertices:
    x,y,z=v.co
    upper=smooth(.65,.83,z)
    front=smooth(.17,.33,y)
    neck=upper*front
    high=smooth(.99,1.10,z);head=smooth(1.14,1.21,z)
    weights={'Root':1-upper,'Body':upper-neck,'NeckBase':neck*(1-high),'NeckUpper':neck*high*(1-head),'Head':neck*high*head}
    for name,w in weights.items():
        if w>1e-6:groups[name].add([v.index],w,'REPLACE')
modifier=body.modifiers.new('Resting five-bone skin','ARMATURE');modifier.object=rig;body.parent=rig
web.parent=rig
scene.render.fps=24;scene.frame_start=0;scene.frame_end=144
rig.animation_data_create()
def make_action(name,keys):
    action=bpy.data.actions.new(name);rig.animation_data.action=action
    for bone in rig.pose.bones:bone.rotation_mode='XYZ'
    for frame,yaw,pitch,breathe in keys:
        for bone in rig.pose.bones:bone.rotation_euler=(0,0,0);bone.location=(0,0,0)
        rig.pose.bones['Body'].location.y=breathe
        rig.pose.bones['NeckBase'].rotation_euler.z=yaw*.35
        rig.pose.bones['NeckUpper'].rotation_euler.z=yaw*.35
        rig.pose.bones['Head'].rotation_euler.z=yaw*.30
        rig.pose.bones['Head'].rotation_euler.x=pitch
        for bone in rig.pose.bones:
            bone.keyframe_insert(data_path='rotation_euler',frame=frame,group=bone.name)
            bone.keyframe_insert(data_path='location',frame=frame,group=bone.name)
    rig.animation_data.action=None
    track=rig.animation_data.nla_tracks.new();track.name=name;strip=track.strips.new(name,0,action);strip.action_frame_start=0;strip.action_frame_end=144
    return action
actions=[]
actions.append(make_action('Rest',[(0,0,0,0),(36,.01,.006,.0012),(72,0,0,0),(108,-.008,-.004,.001),(144,0,0,0)]))
actions.append(make_action('LookAround',[(0,0,0,0),(24,.10,-.018,.001),(60,.14,.015,0),(84,0,0,.001),(120,-.10,-.015,0),(144,0,0,0)]))
actions.append(make_action('Settle',[(0,0,0,0),(24,-.035,.07,.001),(48,-.065,.11,0),(72,-.045,.065,.001),(96,.025,.02,0),(120,.015,-.015,.001),(144,0,0,0)]))
# Pack a metric editable source with the exact local rig and custom clips.
for track in rig.animation_data.nla_tracks:track.mute=True
scene.frame_set(0)
scene['scope']='Illustrative resting greater flamingo, not a surveyed or individually identified Bursa animal'
scene['source']='Pigcraft CC BY4.0; AI-assisted original; no source animation. Local rest/looking clips authored in prepare_flamingo.py.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'greater-flamingo-editable.blend'))
# Export only the animal; cameras/helpers are excluded.
for track in rig.animation_data.nla_tracks:track.mute=False
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);web.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
destination=HERE/'greater-flamingo.glb'
bpy.ops.export_scene.gltf(filepath=str(destination),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_frame_range=False,export_force_sampling=True,export_skins=True,export_yup=True,export_image_format='AUTO',export_tangents=True,export_extras=True)
finalize(destination)
body.data.calc_loop_triangles();web.data.calc_loop_triangles()
report={'schema':'bursa-zoo-flamingo-derivative/v1','sourceSha256':EXPECTED,'sourceBytes':SOURCE.stat().st_size,'sourceTriangleCount':before,'deliveryBytes':destination.stat().st_size,'deliverySha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'triangles':len(body.data.loop_triangles)+len(web.data.loop_triangles),'joints':5,'heightM':1.30,'heightEvidence':'Illustrative adult size within San Diego Zoo greater flamingo120–145cm range','sourceHadSkeleton':False,'sourceHadAnimation':False,'clips':[a.name for a in actions],'clipOrigin':'Locally authored limited rest and looking; no source walk/swim/fly/preen','forwardAxis':'Canonical Blender +Y; glTF Y-up','modifications':['weld duplicate chunk boundaries','12k collapse derivative, smooth normals','source neck bumps smoothed in masked six-iteration pass','missing interdigital webbing added between original toes','1024px pale plumage material bake: saturation.35/light mix.28, mask preserves legs and dark beak/eyes','metric grounding/1.30m illustrative adult','five-bone rest rig and three restrained clips','normal strength.12/roughness.87'], 'sourceUrl':'https://sketchfab.com/3d-models/greater-flamingo-resting-rigged-bird-1c54310c3877422497d37512f0ba33dc','author':'Pigcraft','authorUrl':'https://sketchfab.com/s8819296','license':'CC BY4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/','provenance':'Source author discloses AI-assisted3D generation; not a scan of Bursa Zoo.'}
data=destination.read_bytes();jsonlength=struct.unpack_from('<I',data,12)[0];tree=json.loads(data[20:20+jsonlength]);binary=data[28+jsonlength:]
report['images']=[]
for gltfimage in tree.get('images',[]):
    view=tree['bufferViews'][gltfimage['bufferView']];payload=binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
    width,height=struct.unpack_from('>II',payload,16)
    report['images'].append({'width':width,'height':height,'mimeType':gltfimage['mimeType'],'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
report.update({'nominalTextureRgbaWithMipsMiB':sum(i['width']*i['height']*4*4/3 for i in report['images'])/1048576,'nominalTextureScope':'Texture set only; not complete GPU memory','editableSha256':hashlib.sha256((HERE/'greater-flamingo-editable.blend').read_bytes()).hexdigest(),'primaryDrawsPerAnimal':2,'independentRuntimeMaterials':False,'footGeometryAudit':'foot-geometry-verification.json; two locally added membranes are closed/outward after welding normal splits. Original feather/body topology is not a watertight fabrication mesh.'})
(HERE/'asset-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report))
# Two proof views of the optimized, rigged delivery geometry.
for track in rig.animation_data.nla_tracks:track.mute=True
scene.frame_set(0);target=Vector((0,0,.7))
scene.world.color=(.45,.45,.45);scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=True
scene.render.resolution_x=1000;scene.render.resolution_y=900;scene.render.resolution_percentage=100
bpy.ops.object.light_add(type='SUN',location=(10,-20,30));bpy.context.object.data.energy=2.5;bpy.context.object.rotation_euler=(.5,-.4,-.3)
bpy.ops.object.camera_add(location=(2,3,1.2));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=1.65;scene.camera=cam
for name,off in [('front',(1.8,3.2,.6)),('side',(-3.2,.3,.4))]:
    cam.location=target+Vector(off);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(HERE/f'flamingo-delivery-{name}.png');bpy.ops.render.render(write_still=True)
