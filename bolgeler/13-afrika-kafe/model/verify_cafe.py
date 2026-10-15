"""Check actual exported geometry, native placement and scene surface ownership."""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
inputs=json.loads((HERE/'model-inputs.json').read_text(encoding='utf-8'))
report=json.loads((HERE/'model-report.json').read_text(encoding='utf-8'))
site_path=ROOT/'site-data.json';site=json.loads(site_path.read_text(encoding='utf-8'))
assert hashlib.sha256(site_path.read_bytes()).hexdigest()==inputs['siteDataSha256']
features={f['id']:f for f in site['features']}
native=json.loads((HERE.parent/'kaynaklar/harita-verisi/model-kaynak-m5.json').read_text(encoding='utf-8'))
assert native['features']==[features[r['sourceId']] for r in inputs['roofs']]
for record in inputs['references']:assert hashlib.sha256((HERE/record['file']).read_bytes()).hexdigest()==record['sha256']
scene=trimesh.load(HERE/'afrika-kafe.glb',force='scene',process=False)
assert sum(len(mesh.faces) for mesh in scene.geometry.values())==report['triangles']
world={}
for node in scene.graph.nodes_geometry:
    matrix,key=scene.graph[node];mesh=scene.geometry[key]
    assert np.isfinite(mesh.vertices).all() and np.isfinite(mesh.vertex_normals).all(),node
    assert (mesh.area_faces>1e-12).all() and mesh.unique_faces().all(),node
    welded=mesh.copy();welded.merge_vertices(merge_tex=True,merge_norm=True)
    assert welded.is_watertight and welded.is_winding_consistent and welded.volume>0,node
    mesh=mesh.copy();mesh.apply_transform(matrix);mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]));mesh.apply_translation(inputs['originM5LocalXY']+[0.])
    world[node]=mesh
def upper_projection(mesh):
    return unary_union([Polygon(mesh.vertices[f,:2]) for f,n in zip(mesh.faces,mesh.face_normals) if n[2]>1e-5])
native_roofs=unary_union([Polygon(r['outlineM5XY']) for r in inputs['roofs']])
roof_projection=unary_union([upper_projection(mesh) for name,mesh in world.items() if name.endswith('_roof')])
floor_projection=unary_union([upper_projection(mesh) for name,mesh in world.items() if name.startswith('cafe_floor_')])
roof_delta=roof_projection.symmetric_difference(native_roofs).area
floor_delta=floor_projection.symmetric_difference(native_roofs).area
assert roof_delta<1e-3 and floor_delta<1e-3,(roof_delta,floor_delta)
surfaces=json.loads((ROOT/'surface-layers.json').read_text(encoding='utf-8'))
assert surfaces['source']['africanCafeInputsSha256']==hashlib.sha256((HERE/'model-inputs.json').read_bytes()).hexdigest()
layer=lambda kind:unary_union([Polygon(p['outer'],p['holes']) for p in surfaces['layers'][kind]])
overlaps={kind:native_roofs.intersection(layer(kind)).area for kind in ['terrain','path','water']}
assert max(overlaps.values())<1e-6,overlaps
assert native_roofs.difference(layer('building')).area<1e-6
shell=json.loads((ROOT/'building-shell.json').read_text(encoding='utf-8'))
assert not any(r['sourceId']=='H22D01C2B:243' for r in shell['roofs'])
validation=json.loads((HERE/'gltf-validation.json').read_text(encoding='utf-8'))
assert validation['localEvidence']['assetSha256']==hashlib.sha256((HERE/'afrika-kafe.glb').read_bytes()).hexdigest()
assert validation['issues']['numErrors']==validation['issues']['numWarnings']==0
for record in json.loads((HERE/'textures/manifest.json').read_text(encoding='utf-8'))['files']:
    assert hashlib.sha256((HERE/'textures'/record['file']).read_bytes()).hexdigest()==record['sha256']
    assert hashlib.sha256((HERE/'textures'/record['source']).resolve().read_bytes()).hexdigest()==record['sourceSha256']
result={'roofCount':6,'closedMeshParts':len(world),'triangles':report['triangles'],'glbBytes':report['glbBytes'],
    'exportedRoofDeltaM2':roof_delta,'exportedFloorDeltaM2':floor_delta,'otherGroundOverlapM2':overlaps,
    'generic243BoxRemoved':True,'sourceCoordinatesUnchanged':True,'fieldDimensionsVerified':False}
(HERE/'asset-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
