"""Author a slow lateral-sequence walk on the licensed rig; preserve source idle."""
import bpy, math,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
H=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(H/'giraffe-prepared.blend'),load_ui=False)
s=bpy.context.scene;s.render.fps=30;s.frame_start=0;s.frame_end=120
arm=next(o for o in s.objects if o.type=='ARMATURE');body=max((o for o in s.objects if o.type=='MESH'),key=lambda o:len(o.data.vertices))
# Use a derivative of the downloaded albedo; no Bursa photograph pixels are copied.
img=bpy.data.images.load(str(H/'baringo-basecolor.png'),check_existing=True);img.pack()
for mat in body.data.materials:
 bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Alpha'].default_value=1
 for link in list(mat.node_tree.links):
  if link.to_node==bs and link.to_socket.name in ['Alpha','Metallic','Roughness']:mat.node_tree.links.remove(link)
 tex=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image.name=='Image_0');tex.image=img
 bs.inputs['Roughness'].default_value=.88;bs.inputs['Metallic'].default_value=0
# Sample the original idle before making a new animation action.
source=arm.animation_data.action;source.name='Idle_Source_BlueMesh'
for tr in list(arm.animation_data.nla_tracks):arm.animation_data.nla_tracks.remove(tr)
poses=[]
base=None
for i in range(121):
 s.frame_set(1+int(i*95/120),subframe=(i*95/120)%1);bpy.context.view_layer.update()
 if base is None:base={p.name:(arm.matrix_world@p.matrix).copy() for p in arm.pose.bones}
 poses.append({p.name:p.matrix_basis.copy() for p in arm.pose.bones})
# A neutral stance uses the immutable original idle leg pose. All four feet plant.
aw=arm.matrix_world.copy();inv=aw.inverted()
legs=[('fore_right',['Bone.017_Armature','Bone.018_Armature','Bone.019_Armature'],.12,1),('fore_left',['Bone.020_Armature','Bone.021_Armature','Bone.022_Armature'],.62,1),('hind_right',['Bone.023_Armature','Bone.024_Armature','Bone.025_Armature'],0,-1),('hind_left',['Bone.026_Armature','Bone.027_Armature','Bone.028_Armature'],.5,-1)]
# Target ground velocity .48m/s, stride period4s; 70%stance gives1.344m travel.
period=4.;speed=.48;stance=.70;travel=speed*period*stance
sole_indices={};sole_weights={}
for label,names,offset,bend in legs:
 vg=body.vertex_groups[names[2]].index;items=[]
 for v in body.data.vertices:
  w=next((q.weight for q in v.groups if q.group==vg),0)
  if w>.70 and (body.matrix_world@v.co).z<.22:items.append((v.index,w))
 sole_indices[names[2]]=[i for i,w in items];sole_weights[names[2]]={i:w for i,w in items}
max_sole_correction=0
walk=bpy.data.actions.new('Walk_Authored_LateralSequence');arm.animation_data.action=walk
if hasattr(arm.animation_data,'action_slot'):arm.animation_data.action_slot=walk.slots.new(id_type='OBJECT',name=arm.name)
for i in range(121):
 s.frame_set(i);phase=i/120;old=poses[i]
 # Very small body/neck sway. All limb targets remain in world units.
 bodyshift=Vector((.018*math.sin(math.tau*phase),0,-.18+.014*math.cos(math.tau*phase*2)))
 for p in arm.pose.bones:
  p.matrix_basis=old[p.name].copy()
 bpy.context.view_layer.update()
 rootbone=arm.pose.bones['Armature_rootJoint'];m=(aw@rootbone.matrix).copy();m.translation+=bodyshift;rootbone.matrix=inv@m
 bpy.context.view_layer.update()
 target_lifts={}
 for label,names,offset,bend in legs:
  ps=[base[n].translation.copy() for n in names];a,b,c=ps;A=a+bodyshift
  u=(phase-offset)%1
  if u<stance:dy=travel*(.5-u/stance);lift=0
  else:
   v=(u-stance)/(1-stance);smooth=v*v*(3-2*v);dy=travel*(-.5+smooth);lift=.16*math.sin(math.pi*v)**2
  target_lifts[names[2]]=lift
  C=c+Vector((0,dy,lift));v=C-A;D=v.length;L1=(b-a).length;L2=(c-b).length
  if D>=L1+L2-.0005:C=A+v.normalized()*(L1+L2-.0005);v=C-A;D=v.length
  along=(L1*L1-L2*L2+D*D)/(2*D);height=math.sqrt(max(0,L1*L1-along*along))
  unit=v.normalized();perp=Vector((0,-unit.z,unit.y))*bend;K=A+unit*along+perp*height
  for n,P,Q,oldP,oldQ in [(names[0],A,K,a,b),(names[1],K,C,b,c)]:
   oldM=base[n];delta=(oldQ-oldP).rotation_difference(Q-P);_,q,sc=oldM.decompose();m=Matrix.LocRotScale(P,delta@q,sc);arm.pose.bones[n].matrix=inv@m
  m=base[names[2]].copy();m.translation=C;arm.pose.bones[names[2]].matrix=inv@m
 bpy.context.view_layer.update()
 # Project the authored toe support onto the actual skinned sole. This fixes
 # the last1–3cm caused by mixed hoof/ankle weights, entirely offline.
 for correction_pass in range(3):
  deps=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(deps);mesh=ev.to_mesh()
  positions=[(ev.matrix_world@v.co).z for v in mesh.vertices];ev.to_mesh_clear()
  for n,indices in sole_indices.items():
   vi=min(indices,key=lambda k:positions[k]);delta=(target_lifts[n]-positions[vi])/sole_weights[n][vi]
   max_sole_correction=max(max_sole_correction,abs(delta));p=arm.pose.bones[n];m=aw@p.matrix;m.translation.z+=delta;p.matrix=inv@m
  bpy.context.view_layer.update()
 for p in arm.pose.bones:
  p.rotation_mode='QUATERNION';p.keyframe_insert(data_path='location',frame=i,group=p.name);p.keyframe_insert(data_path='rotation_quaternion',frame=i,group=p.name);p.keyframe_insert(data_path='scale',frame=i,group=p.name)
# Original4s action is rescaled from its24fps frame domain to30fps duration4.
for slot in source.slots:
 for layer in source.layers:
  for strip in layer.strips:
   bag=strip.channelbag(slot)
   if bag:
    for fc in bag.fcurves:
     for kp in fc.keyframe_points:kp.co.x=(kp.co.x-1)*120/95
# NLA tracks make both actions exportable, with explicit descriptive clip names.
arm.animation_data.action=None
for act in [source,walk]:
 tr=arm.animation_data.nla_tracks.new();tr.name=act.name;st=tr.strips.new(act.name,0,act);st.frame_end=120
# When previewing select the authored walk alone.
for tr in arm.animation_data.nla_tracks:tr.mute=tr.name!=walk.name
arm.animation_data.action=walk
s.frame_set(0)
for o in s.objects:o.select_set(o.type not in ['LIGHT','CAMERA'])
bpy.context.view_layer.objects.active=arm
# Save metric editable animation source and export selected animal only.
for image in bpy.data.images:
 if image.source=='FILE':image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(H/'baringo-giraffe-editable.blend'))
for tr in arm.animation_data.nla_tracks:tr.mute=False
arm.animation_data.action=None
bpy.ops.export_scene.gltf(filepath=str(H/'baringo-giraffe.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_nla_strips=True,export_frame_range=True,export_force_sampling=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True,export_yup=True)
(H/'authored-gait.json').write_text(json.dumps({'clip':walk.name,'method':'Offline two-segment IK targets baked onto the original49-joint rig; sibling limb joints explicitly solved. Actual skin sole support projected offline with3 iterations.','durationSeconds':period,'travelSpeedMetresPerSecondAtRate1':speed,'stanceFraction':stance,'phaseOffsets':{x[0]:x[2] for x in legs},'maxSwingLiftMetres':.16,'bodyDropMetres':.18,'maxSoleCorrectionPerIterationMetres':max_sole_correction,'motionCapture':False,'reference':'https://pmc.ncbi.nlm.nih.gov/articles/PMC6376938/','sourceClipRole':'Source BlueMesh clip is idle neck/tail motion, NOT a walking clip.'},indent=2),encoding='utf-8')
# Preview studio only, excluded from delivered GLB and editable animal scene.
arm.animation_data.action=walk;s.frame_set(16)
for tr in arm.animation_data.nla_tracks:tr.mute=True
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));floor=bpy.context.object;mat=bpy.data.materials.new('PreviewFloor');mat.diffuse_color=(.20,.18,.13,1);floor.data.materials.append(mat)
s.world=bpy.data.worlds.new('PreviewWorld');s.world.color=(.32,.35,.38)
for name,loc,power,size in [('Key',(4,-2,9),1900,5),('Fill',(-5,3,6),1300,6)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,2.5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(8,-8,5.0));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,2.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=52;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(H/'giraffe-preview.png');bpy.ops.render.render(write_still=True)
