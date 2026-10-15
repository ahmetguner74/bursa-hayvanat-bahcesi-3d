"""Build offline, editable tree LODs from the CC0 Poly Haven Jacaranda asset.

Run Blender 5.2+ in background with --factory-startup --disable-autoexec and
the original verified jacaranda_tree_1k.blend open. The source file is never
saved over. This is generic visual vegetation, not a Bursa species record.
"""
import bpy
import bmesh
import hashlib
import json
import struct
import numpy as np
from pathlib import Path
from mathutils import Matrix, Vector

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
SOURCE=ROOT/'bolgeler/_qa/tree-assets/jacaranda-source'
EXPECTED_SOURCE='e28e9ea0deb782a830420126b3c5536bde44d1b532cbfb4dccbcc0e46119a0ce'
assert Path(bpy.data.filepath).resolve()==(SOURCE/'jacaranda_tree_1k.blend').resolve()
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==EXPECTED_SOURCE
OUT.mkdir(parents=True,exist_ok=True)
SHAPE=json.loads((OUT/'tree-shape.json').read_text(encoding='utf-8'))
LEAF_TINT=(.55,.72,.45,1)
def crown_profile(t):
    source=SHAPE['sourceCrownStartFraction'];target=SHAPE['targetCrownStartFraction']
    return t/source*target if t<source else target+(t-source)/(1-source)*(1-target)

def material(name,kind,leaf=False):
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    bsdf=nodes.get('Principled BSDF')
    bsdf.inputs['Roughness'].default_value=.85
    for channel,socket in [('diff','Base Color'),('rough','Roughness'),('nor_gl','Normal')]:
        node=nodes.new('ShaderNodeTexImage')
        extension='jpg' if channel=='diff' and not leaf else 'png'
        path=OUT/f'textures/jacaranda_tree_{kind}_{channel}_1k.{extension}'
        node.image=bpy.data.images.load(str(path),check_existing=True)
        node.image.colorspace_settings.name='sRGB' if channel=='diff' else 'Non-Color'
        if channel=='nor_gl':
            normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.45 if leaf else .7
            links.new(node.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs[socket])
        elif leaf and channel=='diff':
            tint=nodes.new('ShaderNodeMix');tint.data_type='RGBA';tint.blend_type='MULTIPLY'
            tint.inputs[0].default_value=1
            a=next(s for s in tint.inputs if s.type=='RGBA' and s.name=='A')
            b=next(s for s in tint.inputs if s.type=='RGBA' and s.name=='B');b.default_value=LEAF_TINT
            result=next(s for s in tint.outputs if s.type=='RGBA')
            links.new(node.outputs['Color'],a);links.new(result,bsdf.inputs[socket])
        else:links.new(node.outputs['Color'],bsdf.inputs[socket])
        if leaf and channel=='diff':links.new(node.outputs['Alpha'],bsdf.inputs['Alpha'])
    if leaf:mat.surface_render_method='DITHERED';mat.use_backface_culling=False
    return mat

mats={
    'jacaranda_tree_branches':material('Atlas tree · branch bark','branches'),
    'jacaranda_tree_trunk':material('Atlas tree · trunk bark','trunk'),
    'jacaranda_tree_leaves':material('Atlas tree · leaves','leaves',True),
}
def convex_hull(points):
    points=sorted(set(tuple(float(v) for v in p) for p in points))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[];upper=[]
    for p in points:
        while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=1e-8:lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=1e-8:upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]

def lightweight_spray(letter):
    original=bpy.data.objects[f'jacaranda_tree_leaves_{letter}_LOD1'].data
    remaining={p.index for p in original.polygons if original.materials[p.material_index].name=='jacaranda_tree_leaves'}
    by_vertex={}
    for index in remaining:
        for vertex in original.polygons[index].vertices:by_vertex.setdefault(vertex,set()).add(index)
    vertices=[];uvs=[];faces=[]
    while remaining:
        start=remaining.pop();component=[start];stack=[start]
        while stack:
            for vertex in original.polygons[stack.pop()].vertices:
                for index in by_vertex[vertex]:
                    if index in remaining:remaining.remove(index);stack.append(index);component.append(index)
        # Small detached stem fragments fall within the retained alpha card;
        # keeping them would duplicate that silhouette after planar fitting.
        if len(component)<=3:continue
        loops=[original.loops[i] for index in component for i in original.polygons[index].loop_indices]
        a=np.array([[*original.uv_layers.active.data[l.index].uv,1] for l in loops])
        b=np.array([original.vertices[l.vertex_index].co[:] for l in loops])
        fit=np.linalg.lstsq(a,b,rcond=None)[0]
        hull=convex_hull(a[:,:2]);assert len(hull)>=3
        normal=Vector(fit[0]).cross(Vector(fit[1]))
        authored=sum((original.polygons[i].normal for i in component),Vector())
        if normal.dot(authored)<0:hull.reverse()
        offset=len(vertices)
        for uv in hull:vertices.append((np.array([*uv,1])@fit).tolist());uvs.append(uv)
        for i in range(1,len(hull)-1):faces.append((offset,offset+i,offset+i+1))
    mesh=bpy.data.meshes.new(f'Atlas alpha spray {letter}');mesh.from_pydata(vertices,[],faces);mesh.update()
    uv=mesh.uv_layers.new(name='UVMap')
    for loop in mesh.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
    mesh.materials.append(bpy.data.materials['jacaranda_tree_leaves'])
    obj=bpy.data.objects.new(f'Atlas leaf prototype {letter}',mesh);prototypes.objects.link(obj)
    return {'source':letter,'sourcePolygons':len(original.polygons),'outputTriangles':len(faces)}

source=bpy.data.objects['jacaranda_tree_geometry_nodes']
prototypes=bpy.data.collections.new('Atlas optimized authored leaf sprays a b c d e')
bpy.context.scene.collection.children.link(prototypes)
prototype_report=[lightweight_spray(letter) for letter in 'abcde']
work=source.copy();work.data=source.data.copy();work.location=(0,0,0)
bpy.context.scene.collection.objects.link(work)
mod,tips=work.modifiers
for current in [mod,tips]:
    current.node_group=current.node_group.copy()
    for node in current.node_group.nodes:
        if node.bl_idname=='GeometryNodeCollectionInfo':node.inputs['Collection'].default_value=prototypes
        elif node.bl_idname=='GeometryNodeObjectInfo':
            # The second stage inherits the complete first-stage trunk.
            # Appending it again would create coplanar duplicate bark.
            node.inputs['Object'].default_value=bpy.data.objects['jacaranda_tree_trunk_LOD1'] if current==mod else None
# Preserve the source's leaves_main attribute mask. In Blender 5.2, modifier
# values moved to properties.inputs.<identifier>.value; defaults are not values.
assert mod.properties.inputs.Input_2.type=='ATTRIBUTE'
assert mod.properties.inputs.Input_2.attribute_name=='leaves_main'
assert tips.properties.inputs.Input_2.attribute_name=='leaves_tips'

output_objects=[]
report={'schema':'bursa-zoo-generic-tree-lods/v1','blender':bpy.app.version_string,
    'source':{'asset':'jacaranda_tree','url':'https://polyhaven.com/a/jacaranda_tree',
        'authors':['Rico Cilliers','Rob Tuytel'],'license':'CC0','licenseUrl':'https://polyhaven.com/license',
        'sha256':EXPECTED_SOURCE},
    'limitations':['Generic visual vegetation; species, height and placement are not a current botanical survey.',
        'Leaf cards are alpha-tested surfaces. Bark is a decimated source mesh, not certified manifold CAD.',
        'The leaf masks and branch structure are from the licensed source; all M5 positions are kept by the viewer.'],
    'leafPrototypeOptimization':prototype_report,'artisticShape':SHAPE,'leafTintLinear':LEAF_TINT,'trunkCopies':1,'lods':[]}
base_z=min(v.co.z for v in bpy.data.objects['jacaranda_tree_trunk_LOD1'].data.vertices)
base_height=max(v.co.z for v in work.data.vertices)-base_z
normalization=Matrix.Diagonal((10/base_height,)*3+(1,))@Matrix.Translation((0,0,-base_z))

for level,factor,leaf_scale,branch_ratio,trunk_ratio in [(0,14.0,1.3,.14,.09),(1,1.5,3.9,.07,.025)]:
    inp=mod.properties.inputs
    inp.Input_4.value=factor;inp.Input_3.value=0
    inp.Input_5.value=1.26*leaf_scale;inp.Input_6.value=2.68*leaf_scale
    tips.show_viewport=tips.show_render=level==0
    tips.properties.inputs.Input_4.value=35.0
    tips.properties.inputs.Input_5.value=1.087*1.75;tips.properties.inputs.Input_6.value=1.355*1.75
    work.update_tag();bpy.context.view_layer.update()
    evaluated=work.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get())
    lod={'level':level,'densityMultiplier':factor,'leafScaleMultiplier':leaf_scale,
        'tipDensityMultiplier':35.0 if level==0 else 0,'tipLeafScaleMultiplier':1.75 if level==0 else 0,'meshes':[]}
    for index,source_mat in enumerate(mesh.materials):
        part=mesh.copy();bm=bmesh.new();bm.from_mesh(part)
        bmesh.ops.delete(bm,geom=[face for face in bm.faces if face.material_index!=index],context='FACES')
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
        if source_mat.name=='jacaranda_tree_branches':
            radius=bm.verts.layers.float.get('radius');assert radius is not None
            # Keep the authored branch topology, pruning sub-pixel twigs by
            # the source radius attribute before simplifying the wood alone.
            limit=.035 if level==0 else .08
            bmesh.ops.delete(bm,geom=[f for f in bm.faces if max(v[radius] for v in f.verts)<limit],context='FACES')
            bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
        if source_mat.name!='jacaranda_tree_leaves':
            before=len(bm.verts)
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
            print('WOOD WELD',level,source_mat.name,before,len(bm.verts),flush=True)
        bm.to_mesh(part);bm.free()
        part.materials.clear();part.materials.append(mats[source_mat.name])
        for polygon in part.polygons:polygon.material_index=0
        obj=bpy.data.objects.new(f'tree_lod{level}_{source_mat.name.rsplit("_",1)[-1]}',part)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        if source_mat.name!='jacaranda_tree_leaves':
            dec=obj.modifiers.new('Wood only · preserve leaf alpha cards','DECIMATE')
            dec.ratio=trunk_ratio if source_mat.name.endswith('trunk') else branch_ratio
            bpy.ops.object.modifier_apply(modifier=dec.name)
        obj.select_set(False)
        obj.data.transform(normalization)
        for vertex in obj.data.vertices:vertex.co.z=10*crown_profile(vertex.co.z/10)
        obj.data.update()
        for polygon in obj.data.polygons:polygon.use_smooth=True
        obj.data.calc_loop_triangles()
        lod['meshes'].append({'name':obj.name,'triangles':len(obj.data.loop_triangles),'vertices':len(obj.data.vertices)})
        output_objects.append(obj)
    lod['triangles']=sum(p['triangles'] for p in lod['meshes'])
    assert lod['triangles']<(150000 if level==0 else 8000),lod
    report['lods'].append(lod)
    bpy.data.meshes.remove(mesh)

# Create a compact derivative .blend containing only the baked editable LODs,
# with source textures packed. No source text blocks or animation are retained.
for obj in list(bpy.data.objects):
    if obj not in output_objects:bpy.data.objects.remove(obj,do_unlink=True)
for text_block in list(bpy.data.texts):bpy.data.texts.remove(text_block)
for obj in output_objects:
    obj.animation_data_clear();obj.select_set(True)
    obj['source']='Poly Haven jacaranda_tree · CC0; generic visual vegetation'
    obj['lod']=int(obj.name[8]);obj.hide_render=obj['lod']==1
bpy.context.view_layer.objects.active=output_objects[0]
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'generic-broadleaf-tree.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'generic-broadleaf-tree.glb'),export_format='GLB',
    use_selection=True,export_animations=False,export_cameras=False,export_lights=False,
    export_extras=True,export_yup=True,export_materials='EXPORT',export_image_format='AUTO',
    export_tangents=True,export_vertex_color='NONE',export_apply=False)

# Explicit MASK avoids sorting artifacts. Keep identical leaf materials for
# both LODs and remove an unneeded alpha-blend extension if exporter created it.
path=OUT/'generic-broadleaf-tree.glb';blob=path.read_bytes()
jlen,jtype=struct.unpack_from('<II',blob,12);assert jtype==0x4e4f534a
gltf=json.loads(blob[20:20+jlen]);tail=bytearray(blob[20+jlen:])
repairs=0
for mesh in gltf['meshes']:
    for primitive in mesh['primitives']:
        attributes=primitive['attributes'];ta=gltf['accessors'][attributes['TANGENT']];na=gltf['accessors'][attributes['NORMAL']]
        tv=gltf['bufferViews'][ta['bufferView']];nv=gltf['bufferViews'][na['bufferView']]
        assert ta['componentType']==na['componentType']==5126
        for i in range(ta['count']):
            offset=8+tv.get('byteOffset',0)+ta.get('byteOffset',0)+i*tv.get('byteStride',16)
            tangent=Vector(struct.unpack_from('<4f',tail,offset)[:3])
            if tangent.length<1e-6:
                noffset=8+nv.get('byteOffset',0)+na.get('byteOffset',0)+i*nv.get('byteStride',12)
                normal=Vector(struct.unpack_from('<3f',tail,noffset)).normalized()
                axis=min([Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1))],key=lambda a:abs(a.dot(normal)))
                fallback=normal.cross(axis).normalized()
                struct.pack_into('<4f',tail,offset,*fallback,1.0);repairs+=1
report['degenerateUvPoleTangentFallbacks']=repairs
for mat in gltf.get('materials',[]):
    if mat['name']=='Atlas tree · leaves':
        mat.update(alphaMode='MASK',alphaCutoff=.1,doubleSided=True)
        assert np.allclose(mat['pbrMetallicRoughness'].get('baseColorFactor'),LEAF_TINT,atol=1e-6),mat
gltf['asset']['copyright']='CC0 source: Poly Haven / Rico Cilliers, Rob Tuytel. Local derivative: Bursa Zoo Atlas.'
gltf.setdefault('extras',{})['source']=report['source']
encoded=json.dumps(gltf,ensure_ascii=False,separators=(',',':')).encode();encoded+=b' '*(-len(encoded)%4)
path.write_bytes(struct.pack('<III',0x46546c67,2,12+8+len(encoded)+len(tail))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+bytes(tail))
for filename in ['generic-broadleaf-tree.blend','generic-broadleaf-tree.glb']:
    p=OUT/filename;report.setdefault('files',[]).append({'name':filename,'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
report['boundsZUp']=[[min(v.co[i] for obj in output_objects for v in obj.data.vertices) for i in range(3)],
    [max(v.co[i] for obj in output_objects for v in obj.data.vertices) for i in range(3)]]
(OUT/'build-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=True))
