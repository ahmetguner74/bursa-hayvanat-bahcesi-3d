"""Verify numbered source folders and the locally generated glTF assets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import trimesh
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parent
index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
areas = index["areas"]
assert [x["number"] for x in areas] == list(range(1, 44))
photos = 0
site=json.loads((ROOT.parent/'site-data.json').read_text(encoding='utf-8'))
source_sha=hashlib.sha256((ROOT.parent/'site-data.json').read_bytes()).hexdigest()
native_features={json.dumps(x,sort_keys=True) for x in site['features']}
native_trees={json.dumps(x,sort_keys=True) for x in site['treeClusters']}
locations=json.loads((ROOT.parent/'region-locations.json').read_text(encoding='utf-8'))
assert [x['number'] for x in locations['areas']]==list(range(1,44))
contexts=0
for area in areas:
    folder = ROOT / area["folder"]
    assert folder.is_dir() and (folder / "model").is_dir()
    data = json.loads((folder / "kaynaklar/kaynakca.json").read_text(encoding="utf-8"))
    assert data["number"] == area["number"]
    assert len(data["mapSources"]) == 2
    assert area["officialPhotos"] == len(data["photos"]), area["number"]
    for item in data["mapSources"] + data["photos"] + data.get("architecturalReferences", []) + data.get("architecturalDocuments", []) + data.get("rejectedPhotos", []):
        path = folder / item["file"]
        assert path.is_file(), path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], path
    for item in data["sharedMetricSources"]:
        path = (folder / item.split(" — ")[0]).resolve()
        assert path.exists(), path
    context=data['areaContext']
    for kind in ['location','metric']:
        path=folder/context[kind+'File']
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==context[kind+'Sha256'],path
    metric=json.loads((folder/context['metricFile']).read_text(encoding='utf-8'))
    location=json.loads((folder/context['locationFile']).read_text(encoding='utf-8'))
    assert metric['sourceSha256']==source_sha and metric['originEd50']==site['originEd50']
    assert metric['coordinateFrame']==site['coordinateFrame']
    assert all(json.dumps(x,sort_keys=True) in native_features for x in metric['features'])
    assert all(json.dumps(x,sort_keys=True) in native_trees for x in metric['treeClusters'])
    assert len(metric['features'])==context['nativeFeatureCount'] and len(metric['treeClusters'])==context['nativeTreeCount']
    assert location['anchors']==locations['areas'][area['number']-1]['anchors']
    if area['number']==40:
        assert not location['anchors'] and not metric['features'] and not metric['treeClusters']
    contexts+=1
    photos += len(data["photos"])

model_folder = ROOT / "31-pelikan-goleti/model"
for variant in ("yakin", "uzak"):
    asset = model_folder / f"su-kuslari-kubbesi-{variant}.glb"
    scene = trimesh.load(asset, force="scene")
    extent = scene.bounds[1] - scene.bounds[0]
    assert 69 < extent[0] < 71 and 19 < extent[1] < 21 and 39 < extent[2] < 41
    assert all(len(mesh.faces) and mesh.is_winding_consistent for mesh in scene.geometry.values()
               if isinstance(mesh, trimesh.Trimesh))
    if variant == "uzak":
        assert any(isinstance(geometry, trimesh.path.Path3D) for geometry in scene.geometry.values())

village = ROOT / "30-turk-koyu/model"
report = json.loads((village / "model-report.json").read_text(encoding="utf-8"))
scene = trimesh.load(village / "turk-koyu.glb", force="scene")
assert report["roofProjectedOverlapM2"] == 0
assert len(report["sourceIds"]) == 9 and report["originM5LocalXY"] == [-68, 8]
assert sum(len(mesh.faces) for mesh in scene.geometry.values()) == report["triangles"]
assert all(np.isfinite(mesh.vertices).all() and (mesh.area_faces > 1e-12).all()
           for mesh in scene.geometry.values())
generic = json.loads((ROOT.parent / "building-shell.json").read_text(encoding="utf-8"))
assert set(report["sourceIds"]).isdisjoint({item["sourceId"] for item in generic["roofs"]})

penguin=ROOT/'15-penguen/model'
animal=penguin/'hayvan'
animal_manifest=json.loads((animal/'source-manifest.json').read_text(encoding='utf-8'))
for item in animal_manifest['originals']:
    path=animal/item['file'];assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],path
assert hashlib.sha256((animal/'african-penguin.glb').read_bytes()).hexdigest()==animal_manifest['delivery']['sha256']
animal_layout=json.loads((animal/'colony-layout.json').read_text(encoding='utf-8'))
assert animal_layout['schema']=='bursa-zoo-penguin-colony/v2' and len(animal_layout['waterRoutes'])==2
transition_ground=json.loads((animal/'penguin-transitions.json').read_text(encoding='utf-8'))
assert transition_ground['assetSha256']==animal_layout['assetSha256'] and len(transition_ground['tables'])==10
assert len(animal_layout['landStarts'])==3 and len(animal_layout['waterStarts'])==2
assert animal_layout['trianglesPerBird']==4124 and animal_layout['jointsPerBird']==64
assert animal_layout['inputs']['poolInputsSha256']==hashlib.sha256((penguin/'model-inputs.json').read_bytes()).hexdigest()
penguin_report=json.loads((penguin/'model-report.json').read_text(encoding='utf-8'))
scene=trimesh.load(penguin/'penguen-havuzu.glb',force='scene')
assert sum(len(mesh.faces) for mesh in scene.geometry.values())==penguin_report['triangles']
assert all(np.isfinite(mesh.vertices).all() and (mesh.area_faces>1e-12).all() for mesh in scene.geometry.values())
for name in penguin_report['solidChecks']:
    solid=scene.geometry[name].copy();solid.merge_vertices(merge_tex=True,merge_norm=True)
    assert solid.is_watertight and solid.is_winding_consistent and solid.volume>0, name
surfaces=json.loads((ROOT.parent/'surface-layers.json').read_text(encoding='utf-8'))
assert abs(surfaces['checks']['penguinGravelAreaM2']-penguin_report['gravelTerrainAreaM2'])<1e-6
assert surfaces['checks']['terrainStyleOverlapM2']==0
assert surfaces['renderLevels']['waterZ']<surfaces['renderLevels']['terrainZ']
assert penguin_report['renderWaterZMetres']==surfaces['renderLevels']['waterZ']
water=scene.geometry['pool_water'].copy();water.apply_transform(scene.graph['pool_water'][0])
assert np.allclose(water.vertices[:,1],surfaces['renderLevels']['waterZ'],atol=1e-6)
assert surfaces['renderLevelsAreSurveyed'] is False

platform=ROOT/'12-afrika-savana/model'
platform_report=json.loads((platform/'model-report.json').read_text(encoding='utf-8'))
scene=trimesh.load(platform/'savanna-ahsap-platform.glb',force='scene')
assert sum(len(mesh.faces) for mesh in scene.geometry.values())==platform_report['triangles']
assert platform_report['roofFootprintSymmetricDifferenceM2']<1e-8
assert platform_report['sourceAssociation']=='candidate, unconfirmed'
assert platform_report['sourceId'] not in {item['sourceId'] for item in generic['roofs']}
platform_inputs=json.loads((platform/'model-inputs.json').read_text(encoding='utf-8'))
roof=scene.geometry['roof'].copy()
roof.apply_transform(scene.graph['roof'][0])
roof.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
roof.apply_translation(platform_inputs['originM5LocalXY']+[0.])
projection=unary_union([Polygon(roof.vertices[f,:2]) for f,n in zip(roof.faces,roof.face_normals) if n[2]>.1])
export_delta=projection.symmetric_difference(Polygon(platform_inputs['roofOutlineM5XY'])).area
assert export_delta<1e-4,export_delta
for name,mesh in scene.geometry.items():
    assert np.isfinite(mesh.vertices).all() and (mesh.area_faces>1e-12).all(),name
    welded=mesh.copy();welded.merge_vertices(merge_tex=True,merge_norm=True)
    assert welded.is_watertight and welded.is_winding_consistent and welded.volume>0,name

lemur=ROOT/'11-lemur/model'
lemur_report=json.loads((lemur/'model-report.json').read_text(encoding='utf-8'))
lemur_inputs=json.loads((lemur/'model-inputs.json').read_text(encoding='utf-8'))
assert lemur_inputs['siteDataSha256']==source_sha
for kind in ['island','moat']:
    source=next(f for f in site['features'] if f['id']==lemur_inputs[kind+'SourceId'])
    assert source['paths'][0]==lemur_inputs[kind+'OutlineM5XY']
assert hashlib.sha256((lemur/lemur_inputs['sourcePhoto']).read_bytes()).hexdigest()==lemur_inputs['sourcePhotoSha256']
scene=trimesh.load(lemur/'lemur-adasi.glb',force='scene')
validation=json.loads((lemur/'gltf-validation.json').read_text(encoding='utf-8'))
assert validation['localEvidence']['assetSha256']==hashlib.sha256((lemur/'lemur-adasi.glb').read_bytes()).hexdigest()
assert validation['issues']['numErrors']==validation['issues']['numWarnings']==0
assert sum(len(m.faces) for m in scene.geometry.values())==lemur_report['triangles']
lemur_world={}
for name,mesh in scene.geometry.items():
    assert np.isfinite(mesh.vertices).all() and (mesh.area_faces>1e-12).all(),name
    assert mesh.unique_faces().all(),name
    welded=mesh.copy();welded.merge_vertices(merge_tex=True,merge_norm=True)
    if name!='moat_water':
        assert welded.is_watertight and welded.is_winding_consistent and welded.volume>0,name
    world=mesh.copy();world.apply_transform(scene.graph[name][0])
    world.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    world.apply_translation(lemur_inputs['originM5LocalXY']+[0.])
    lemur_world[name]=world
island=Polygon(lemur_inputs['islandOutlineM5XY'])
moat=Polygon(lemur_inputs['moatOutlineM5XY']).difference(island)
island_mesh=lemur_world['island_ground']
island_projection=unary_union([Polygon(island_mesh.vertices[f,:2]) for f,n in zip(island_mesh.faces,island_mesh.face_normals) if n[2]>.9])
lemur_export_delta=island_projection.symmetric_difference(island).area
assert lemur_export_delta<1e-4,lemur_export_delta
water=lemur_world['moat_water']
water_projection=unary_union([Polygon(water.vertices[f,:2]) for f in water.faces])
assert water_projection.symmetric_difference(moat).area<1e-4
assert water_projection.intersection(island).area<1e-4
assert np.allclose(water.vertices[:,2],surfaces['renderLevels']['waterZ'],atol=1e-6)
for name in ['rocks','climbing_timber','climbing_ropes']:
    assert island.buffer(1e-5).covers(Polygon(lemur_world[name].vertices[:,:2]).convex_hull),name
assert lemur_report['renderLevelsAreSurveyed'] is False
layout=json.loads((ROOT.parent/'landscape-layout.json').read_text(encoding='utf-8'))
from shapely.geometry import Point
assert all(not island.covers(Point(x,y)) for x,y,*_ in layout['trees']+layout['plants'])

african=ROOT/'14-afrika-koyu/model'
african_inputs=json.loads((african/'model-inputs.json').read_text(encoding='utf-8'))
african_report=json.loads((african/'model-report.json').read_text(encoding='utf-8'))
validation=json.loads((african/'gltf-validation.json').read_text(encoding='utf-8'))
assert validation['localEvidence']['assetSha256']==hashlib.sha256((african/'afrika-koyu.glb').read_bytes()).hexdigest()
assert validation['issues']['numErrors']==validation['issues']['numWarnings']==0
assert african_inputs['siteDataSha256']==source_sha and len(african_inputs['huts'])==7
native_model=json.loads((african.parent/'kaynaklar/harita-verisi/model-kaynak-m5.json').read_text(encoding='utf-8'))
assert native_model['sourceSha256']==source_sha and native_model['originEd50']==site['originEd50']
assert all(json.dumps(f,sort_keys=True) in native_features for f in native_model['features'])
assert {f['id'] for f in native_model['features']}=={h['sourceId'] for h in african_inputs['huts']}
for kind in ['Photo','Document']:
    assert hashlib.sha256((african/african_inputs['source'+kind]).read_bytes()).hexdigest()==african_inputs['source'+kind+'Sha256']
scene=trimesh.load(african/'afrika-koyu.glb',force='scene')
assert sum(len(m.faces) for m in scene.geometry.values())==african_report['triangles']
african_export_delta=0
for name,mesh in scene.geometry.items():
    assert np.isfinite(mesh.vertices).all() and (mesh.area_faces>1e-12).all(),name
    assert mesh.unique_faces().all(),name
    welded=mesh.copy();welded.merge_vertices(merge_tex=True,merge_norm=True)
    assert welded.is_watertight and welded.is_winding_consistent and welded.volume>0,name
for hut in african_inputs['huts']:
    f=next(f for f in site['features'] if f['id']==hut['sourceId'])
    assert f['paths'][0]==hut['eaveOutlineM5XY']
    name=hut['sourceId'].replace(':','_')+'_roof'
    mesh=scene.geometry[name].copy();mesh.apply_transform(scene.graph[name][0])
    mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]))
    mesh.apply_translation(african_inputs['originM5LocalXY']+[0.])
    projected=unary_union([Polygon(mesh.vertices[f,:2]) for f,n in zip(mesh.faces,mesh.face_normals) if n[2]>1e-5])
    delta=projected.symmetric_difference(Polygon(hut['eaveOutlineM5XY'])).area
    assert delta<1e-3,(name,delta)
    african_export_delta+=delta
floor_mask=unary_union([Polygon(h['wallOutlineM5XY']) for h in african_inputs['huts']])
assert abs(floor_mask.area-surfaces['checks']['africanVillageInterpretedFloorAreaM2'])<1e-6
path_geoms=[Polygon(p['outer'],p['holes']) for p in surfaces['layers']['path']]
for kind in ['path','terrain','water']:
    layer=unary_union([Polygon(p['outer'],p['holes']) for p in surfaces['layers'][kind]])
    assert floor_mask.intersection(layer).area<1e-5,kind
assert max(path_geoms,key=lambda p:p.area).buffer(1e-5).covers(Point(80,107)),'African courtyard disconnected'

import subprocess,sys
subprocess.run([sys.executable,str(ROOT/'13-afrika-kafe/model/verify_cafe.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'09-habes-maymunu/model/verify_habes.py')],check=True)
subprocess.run([sys.executable,str(ROOT/'29-boz-ayi/model/verify_bear_pool.py')],check=True)
assets=ROOT.parent/'viewer/assets'
asset_manifest=json.loads((assets/'asset-manifest.json').read_text(encoding='utf-8'))
for item in asset_manifest['assets']:
    assert hashlib.sha256((assets/item['file']).read_bytes()).hexdigest()==item['sha256'],item['file']
from PIL import Image
flower=json.loads((assets/'woodland-wildflower-derivative.json').read_text(encoding='utf-8'))
assert hashlib.sha256((assets/flower['source']).read_bytes()).hexdigest()==flower['sourceSha256']
assert hashlib.sha256((assets/flower['file']).read_bytes()).hexdigest()==flower['sha256']
with Image.open(assets/flower['file']) as image:
    assert image.mode=='RGBA' and list(image.size)==flower['size']
for foliage in json.loads((assets/'woodland-foliage-derivatives.json').read_text(encoding='utf-8')):
    assert hashlib.sha256((assets/foliage['source']).read_bytes()).hexdigest()==foliage['sourceSha256']
    assert hashlib.sha256((assets/foliage['file']).read_bytes()).hexdigest()==foliage['sha256']
    with Image.open(assets/foliage['file']) as image:
        assert image.mode=='RGBA' and list(image.size)==foliage['size']
ground=json.loads((ROOT.parent/'ground-material-layout.json').read_text(encoding='utf-8'))
assert ground['schema']=='bursa-zoo-ground-material-weights/v1'
for name,expected_sha in ground['sources'].items():
    assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==expected_sha,name
mask_path=ROOT.parent/'viewer'/ground['image']
assert hashlib.sha256(mask_path.read_bytes()).hexdigest()==ground['sha256']
with Image.open(mask_path) as image:
    assert image.mode=='RGB' and list(image.size)==ground['size']
    assert np.asarray(image).max(axis=(0,1)).tolist()==ground['checks']['channelMaxima']
for texture in [ground['litterTexture'],ground['rockTexture']]:
    assert hashlib.sha256((ROOT.parent/texture['source']).read_bytes()).hexdigest()==texture['sourceSha256']
    assert hashlib.sha256((ROOT.parent/'viewer'/texture['file']).read_bytes()).hexdigest()==texture['sha256']
    with Image.open(ROOT.parent/'viewer'/texture['file']) as image:
        assert image.mode=='RGB' and list(image.size)==texture['size']
vendor=ROOT.parent/'vendor'
effects_sources=json.loads((vendor/'scene-effects-sources.json').read_text(encoding='utf-8'))
for item in effects_sources['files']:
    assert hashlib.sha256((vendor/item['file']).read_bytes()).hexdigest()==item['sha256'],item['file']

rhino=ROOT/'16-gergedan/model'
rhino_report=json.loads((rhino/'habitat-report.json').read_text(encoding='utf-8'))
assert hashlib.sha256((rhino/rhino_report['file']).read_bytes()).hexdigest()==rhino_report['sha256']
assert rhino_report['floorCheck']['overlapM2']<1e-6 and rhino_report['floorCheck']['gapM2']<1e-6
rhino_asset=json.loads((rhino/'hayvan/source-manifest.json').read_text(encoding='utf-8'))
assert hashlib.sha256((rhino/'hayvan/white-rhinoceros.glb').read_bytes()).hexdigest()==rhino_asset['delivery']['sha256']
rhino_colony=json.loads((rhino/'colony-layout.json').read_text(encoding='utf-8'))
assert len(rhino_colony['routes'])==2 and rhino_colony['blendGround']['assetSha256']==rhino_asset['delivery']['sha256']
rhino_inputs=json.loads((rhino/'habitat-inputs.json').read_text(encoding='utf-8'))
rhino_floor=Polygon(rhino_inputs['compoundOutlineM5XY'])
for key in ['terrain','path','water']:
    assert rhino_floor.intersection(unary_union([Polygon(p['outer'],p['holes']) for p in surfaces['layers'][key]])).area<1e-6
giraffe=ROOT/'12-afrika-savana/model/giraffe'
giraffe_asset=json.loads((giraffe/'giraffe-asset.json').read_text(encoding='utf-8'))
giraffe_report=json.loads((giraffe/'habitat-report.json').read_text(encoding='utf-8'))
giraffe_colony=json.loads((giraffe/'giraffe-colony.json').read_text(encoding='utf-8'))
assert hashlib.sha256((giraffe/'baringo-giraffe.glb').read_bytes()).hexdigest()==giraffe_asset['delivery']['sha256']==giraffe_colony['assetSha256']==giraffe_colony['blendGround']['assetSha256']
assert hashlib.sha256((giraffe/giraffe_report['file']).read_bytes()).hexdigest()==giraffe_report['sha256']
assert len(giraffe_colony['routes'])==2
assert max(giraffe_report['floorCheck'].values())<1e-6
giraffe_floor=unary_union([Polygon(p['outer'],p.get('holes',[])) for p in giraffe_report['floorOwnershipMasks']])
for key in ['terrain','path','water']:
    assert giraffe_floor.intersection(unary_union([Polygon(p['outer'],p['holes']) for p in surfaces['layers'][key]])).area<1e-6
birds=ROOT/'32-su-kuslari/model'
bird_layout=json.loads((birds/'aviary-birds-layout.json').read_text(encoding='utf-8'))
bird_asset=json.loads((birds/'hayvan/asset-manifest.json').read_text(encoding='utf-8'))
assert hashlib.sha256((birds/'hayvan/greater-flamingo.glb').read_bytes()).hexdigest()==bird_asset['deliverySha256']==bird_layout['assetSha256']
assert len(bird_layout['animals'])==4 and all(a['clearance']['dryGround'] for a in bird_layout['animals'])
subprocess.run([sys.executable,str(ROOT/'15-penguen/model/verify_pool_fixes.py')],check=True)

print(json.dumps({"regions": len(areas), "officialPhotos": photos,
                  "verifiedAreaContexts":contexts,
                  "localMaps": len(areas) * 2, "habitatGltfVariants": len(list(ROOT.glob('[0-9][0-9]-*/model/*.glb'))),
                  "animalGltfVariants":4,"penguinColonyTriangles":animal_layout['trianglesPerBird']*5,
                  "giraffeColonyTriangles":giraffe_asset['delivery']['triangles']*2,"giraffeHabitatTriangles":giraffe_report['triangles'],
                  "flamingoColonyTriangles":bird_asset['triangles']*4,
                  "rhinoColonyTriangles":rhino_asset['delivery']['triangles']*2,"rhinoHabitatTriangles":rhino_report['triangles'],
                  "villageTriangles": report["triangles"],
                  "penguinTriangles":penguin_report['triangles'],
                  "savannaPlatformTriangles":platform_report['triangles'],
                  "lemurTriangles":lemur_report['triangles'],
                  "africanVillageTriangles":african_report['triangles'],
                  "exportedAfricanVillageRoofDeltaM2":african_export_delta,
                  "exportedLemurIslandDeltaM2":lemur_export_delta,
                  "exportedPlatformFootprintDeltaM2":export_delta,
                  "verifiedGeneratedAssets":len(asset_manifest['assets'])}, ensure_ascii=False))
