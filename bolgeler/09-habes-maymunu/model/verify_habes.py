"""Check the actual exported asset, native XY projection and surface ownership."""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
from PIL import Image
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
inputs=read(HERE/'model-inputs.json');report=read(HERE/'model-report.json')
assert sha(ROOT/'site-data.json')==inputs['siteDataSha256']
site=read(ROOT/'site-data.json');native={f['id']:f for f in site['features']}
context=read(HERE.parent/'kaynaklar/harita-verisi/model-kaynak-m5.json')
assert context['sourceSha256']==inputs['siteDataSha256'] and context['originEd50']==site['originEd50']
assert all(f==native[f['id']] for f in context['features'])
for key in ['island','moat']:
    assert native[inputs[key+'SourceId']]['closed']
    assert native[inputs[key+'SourceId']]['paths'][0]==inputs[key+'OutlineM5XY']
for rec in inputs['platforms']+inputs['internalWater']:
    assert native[rec['sourceId']]['paths'][0]==rec['outlineM5XY']
for source_id in inputs['unmodeledOpenWaterLineSourceIds']:assert not native[source_id]['closed']
assert not inputs['internalWater'],'The archived open lines must not become invented pools'
for rec in inputs['references']:assert sha((HERE/rec['file']).resolve())==rec['sha256']
for rec in read(HERE/'textures/manifest.json'):
    assert sha(HERE/'textures'/rec['file'])==rec['sha256']
    assert sha((HERE/'textures'/rec['source']).resolve())==rec['sourceSha256']
    with Image.open(HERE/'textures'/rec['file']) as image:assert image.mode=='RGB' and list(image.size)==rec['size']
asset=HERE/'habes-maymunu-adasi.glb';validation=read(HERE/'gltf-validation.json')
assert validation['localEvidence']['assetSha256']==sha(asset)
assert validation['issues']['numErrors']==validation['issues']['numWarnings']==0
scene=trimesh.load(asset,force='scene',process=False)
meshes={}
for name in scene.graph.nodes_geometry:
    transform,key=scene.graph[name];mesh=scene.geometry[key].copy()
    assert np.isfinite(mesh.vertices).all() and (mesh.area_faces>1e-12).all(),name
    assert mesh.unique_faces().all(),name
    if name!='moat_water':
        welded=mesh.copy();welded.merge_vertices(merge_tex=True,merge_norm=True)
        assert welded.is_watertight and welded.is_winding_consistent and welded.volume>0,name
    mesh.apply_transform(transform);mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    mesh.apply_translation(inputs['originM5LocalXY']+[0.]);meshes[name]=mesh
assert sum(len(m.faces) for m in meshes.values())==report['triangles']
def top_projection(name,z):
    mesh=meshes[name]
    selected=(mesh.face_normals[:,2]>.999)&(np.abs(mesh.triangles_center[:,2]-z)<2e-6)
    return unary_union([Polygon(t[:,:2]) for t in mesh.triangles[selected]])
surfaces=read(ROOT/'surface-layers.json');levels=surfaces['renderLevels']
island=Polygon(inputs['islandOutlineM5XY']);outer=Polygon(inputs['moatOutlineM5XY'])
coping=island.difference(island.buffer(-inputs['interpretedDimensions']['bankWidth'],join_style='round'))
soil=island.difference(coping);water=outer.difference(island)
deltas={
    'soil':top_projection('island_ground',levels['terrainZ']).symmetric_difference(soil).area,
    'coping':top_projection('concrete_coping',levels['terrainZ']+inputs['interpretedDimensions']['bankTopOffset']).symmetric_difference(coping).area,
    'water':top_projection('moat_water',levels['waterZ']).symmetric_difference(water).area,
}
for rec in inputs['platforms']:
    deltas[rec['sourceId']]=top_projection('platform_'+rec['sourceId'].split(':')[1],rec['interpretedDeckTopZ']).symmetric_difference(Polygon(rec['outlineM5XY'])).area
assert all(value<1e-3 for value in deltas.values()),deltas
overlaps={}
for key in ['water','path','terrain']:
    layer=unary_union([Polygon(p['outer'],p['holes']) for p in surfaces['layers'][key]])
    overlaps[key]=coping.intersection(layer).area
assert all(value<1e-6 for value in overlaps.values()),overlaps
styled=unary_union([Polygon(p['outer'],p['holes']) for p in surfaces['layers']['terrain'] if p.get('surfaceStyle')=='habes-earth'])
assert styled.symmetric_difference(soil).area<1e-6
assert surfaces['source']['habesInputsSha256']==sha(HERE/'model-inputs.json')
proof={'triangles':report['triangles'],'glbBytes':asset.stat().st_size,'closedMeshParts':len(meshes)-1,
       'nativeIslandAreaM2':island.area,'exportProjectionDeltaM2':deltas,'copingOtherSurfaceOverlapM2':overlaps,
       'sourceCoordinatesUnchanged':True,'openWaterLinesNotInventedAsPools':True,'fieldDimensionsVerified':False}
(HERE/'asset-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof))
