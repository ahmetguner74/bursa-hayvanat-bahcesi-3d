"""Verify the exported candidate pond, source records and sole surface ownership."""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
from PIL import Image
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def polygons(items):return unary_union([Polygon(p['outer'],p['holes']) for p in items])

inputs=read(HERE/'model-inputs.json');report=read(HERE/'model-report.json')
site=read(ROOT/'site-data.json');native={f['id']:f for f in site['features']}
assert inputs['siteDataSha256']==sha(ROOT/'site-data.json')
assert native[inputs['poolSourceId']]['closed']
assert native[inputs['poolSourceId']]['paths'][0]==inputs['poolOutlineM5XY']
context=read(HERE.parent/'kaynaklar/harita-verisi/model-kaynak-m5.json')
assert context['sourceSha256']==inputs['siteDataSha256'] and context['originEd50']==site['originEd50']
assert context['features']==[native[inputs['poolSourceId']]]
for item in inputs['references']:assert sha((HERE/item['file']).resolve())==item['sha256']
for item in read(HERE/'textures/manifest.json'):
    file=HERE/'textures'/item['file']
    assert sha(file)==item['sha256'] and sha((file.parent/item['source']).resolve())==item['sourceSha256']
    with Image.open(file) as image:assert list(image.size)==item['size'] and image.mode==item['mode']

asset=HERE/'boz-ayi-havuz-kiyisi.glb';validation=read(HERE/'gltf-validation.json')
assert validation['localEvidence']['assetSha256']==sha(asset)
assert validation['issues']['numErrors']==validation['issues']['numWarnings']==0
scene=trimesh.load(asset,force='scene',process=False);meshes={}
for name in scene.graph.nodes_geometry:
    transform,key=scene.graph[name];mesh=scene.geometry[key].copy()
    assert np.isfinite(mesh.vertices).all() and (mesh.area_faces>1e-12).all(),name
    assert mesh.unique_faces().all(),name
    if name not in ['pool_water','bank_plants']:
        welded=mesh.copy();welded.merge_vertices(merge_tex=True,merge_norm=True)
        assert welded.is_watertight and welded.is_winding_consistent and welded.volume>0,name
    mesh.apply_transform(transform)
    mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    mesh.apply_translation(inputs['originM5LocalXY']+[0.]);meshes[name]=mesh
assert report['triangles']==sum(len(m.faces) for m in meshes.values())
assert asset.stat().st_size==report['glbBytes']

def top(names,z):
    triangles=[]
    for name in names:
        m=meshes[name];selected=(m.face_normals[:,2]>.999)&(np.abs(m.triangles_center[:,2]-z)<2e-6)
        triangles.extend(Polygon(t[:,:2]) for t in m.triangles[selected])
    return unary_union(triangles)

surfaces=read(ROOT/'surface-layers.json');levels=surfaces['renderLevels'];dims=inputs['interpretedDimensions']
pool=Polygon(inputs['poolOutlineM5XY']);bank=polygons(inputs['interpretedBankMaskM5XY']);ground=polygons(inputs['previewGroundMaskM5XY'])
deltas={
    'nativePoolWater':top(['pool_water'],levels['waterZ']).symmetric_difference(pool).area,
    'nativePoolBed':top(['pool_bed'],dims['bedTopZ']).symmetric_difference(pool).area,
    'interpretedBank':top([n for n in meshes if n.startswith('concrete_bank_')],levels['terrainZ']+dims['bankTopOffset']).symmetric_difference(bank).area,
    'previewGround':top([n for n in meshes if n.startswith('preview_ground_')],levels['terrainZ']).symmetric_difference(ground).area,
}
assert all(v<.001 for v in deltas.values()),deltas
overlaps={k:bank.intersection(polygons(surfaces['layers'][k])).area for k in ['water','path','terrain']}
assert all(v<1e-6 for v in overlaps.values()),overlaps
assert bank.difference(polygons(surfaces['layers']['building'])).area<1e-6
water=polygons([p for p in surfaces['layers']['water'] if p.get('waterPresentationColor')==inputs['waterPresentationColor']])
assert water.symmetric_difference(pool).area<1e-6
assert surfaces['source']['bearInputsSha256']==sha(HERE/'model-inputs.json')
catalog=read(ROOT/'scene-model-catalog.json');item=next(m for m in catalog['models'] if m['key']=='bearPool')
assert item['sha256']==sha(asset) and item['originXYZMetres']==inputs['originM5LocalXY']+[0]
assert set(item['hiddenNodes'])=={n for n in meshes if n.startswith('preview_ground_') or n in ['pool_bed','pool_water']}
layout=read(ROOT/'landscape-layout.json')
native_trees=[t['xy'] for t in site.get('treeClusters',[])]
for rock in inputs['interpretedRocks']:
    footprint=Point(rock['xyM5']).buffer(rock['size'][0]*1.35)
    assert ground.covers(footprint)
    assert all(not footprint.buffer(.35).covers(Point(t[:2])) for t in native_trees+layout['trees'])
proof={'triangles':report['triangles'],'glbBytes':report['glbBytes'],'closedSolidParts':len(meshes)-2,
    'nativePoolAreaM2':pool.area,'exportProjectionDeltaM2':deltas,'bankOtherSurfaceOverlapM2':overlaps,
    'sourceCoordinatesUnchanged':True,'bankRemovedFromMainTerrain':True,
    'photographicDimensionsSurveyed':False,'preciseRegion28_29BoundaryVerified':False}
(HERE/'asset-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof))
