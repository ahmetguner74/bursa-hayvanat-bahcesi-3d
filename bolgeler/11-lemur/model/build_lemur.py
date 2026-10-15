"""Native M5 island/moat, with camera-interpreted rock and climbing elements.

The acquired camera frame is not dated survey evidence. Prop positions, heights
and quantities are editable estimates; no neighbouring building is reassigned.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import Point, Polygon

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
sys.path.insert(0, str(PROJECT/'bolgeler'))
from model_tools import bark_uv, pbr, polygon_mesh, postprocess_gltf, tube


def main():
    inputs = json.loads((HERE/'model-inputs.json').read_text(encoding='utf-8'))
    site_path = PROJECT/'site-data.json'
    photo = (HERE/inputs['sourcePhoto']).resolve()
    if hashlib.sha256(site_path.read_bytes()).hexdigest() != inputs['siteDataSha256']:
        raise ValueError('M5 source changed; review island and moat outlines')
    if hashlib.sha256(photo.read_bytes()).hexdigest() != inputs['sourcePhotoSha256']:
        raise ValueError('Camera reference changed; review interpreted elements')
    site = json.loads(site_path.read_text(encoding='utf-8'))
    features = {f['id']:f for f in site['features']}
    for key in ['island', 'moat']:
        if features[inputs[key+'SourceId']]['paths'][0] != inputs[key+'OutlineM5XY']:
            raise ValueError('Native '+key+' coordinates changed')
    island_world = Polygon(inputs['islandOutlineM5XY'])
    moat_world = Polygon(inputs['moatOutlineM5XY'])
    origin = np.array(inputs['originM5LocalXY']+[0.])
    island = affinity.translate(island_world, -origin[0], -origin[1])
    moat = affinity.translate(moat_world, -origin[0], -origin[1]).difference(island)
    levels = json.loads((PROJECT/'surface-layers.json').read_text(encoding='utf-8'))['renderLevels']
    ground_z, water_z = levels['terrainZ'], levels['waterZ']
    params = inputs['interpretedDimensionsMetres']
    assets = PROJECT/'viewer/assets'
    mats = {
        'island_ground':pbr('meadow', [.83,.89,.72,1.], assets/'woodland-meadow-v1.png'),
        'moat_bed':pbr('moat_concrete', [.32,.36,.27,1.]),
        'moat_water':pbr('water', [.035,.40,.34,.78], roughness=.23),
        'concrete_coping':pbr('weathered_concrete', [.59,.58,.45,1.]),
        'rocks':pbr('moss_tinted_rock', [.63,.64,.48,1.], assets/'penguin-artificial-rock-v1.png'),
        'climbing_timber':pbr('weathered_bark', [.69,.62,.46,1.], assets/'woodland-tree-bark-v1.png'),
        'climbing_ropes':pbr('natural_rope', [.32,.29,.19,1.]),
    }
    mats['moat_water'].alphaMode = 'BLEND'
    pieces = {
        'island_ground':polygon_mesh(island, ground_z, -.8),
        'moat_bed':polygon_mesh(moat, -.95, -1.25),
        'moat_water':polygon_mesh(moat, water_z),
        'concrete_coping':polygon_mesh(island.buffer(params['bankWidth']).difference(island.buffer(-.05)),
                                      ground_z+.045, -.85),
    }
    rock_meshes = []
    rng = np.random.default_rng(11015)
    for item in inputs['interpretedRocks']:
        centre = np.array(item['xyM5'])-origin[:2]
        sx, sy, height = item['size']
        if not island_world.covers(Point(item['xyM5']).buffer(max(sx, sy))):
            raise ValueError('Interpreted rock footprint escaped island')
        rock = trimesh.creation.icosphere(subdivisions=2)
        # Low-frequency irregularity remains a closed solid; avoid jagged noise.
        v = rock.vertices
        variation = 1+.12*np.sin(v[:,0]*4+item['seed'])*np.cos(v[:,1]*3-v[:,2]*2)
        rock.vertices = v*variation[:,None]*[sx,sy,height*.63]
        rock.apply_transform(trimesh.transformations.rotation_matrix(rng.uniform(0,math.pi),[0,0,1]))
        rock.apply_translation([*centre,ground_z+height*.37])
        rock_meshes.append(rock)
    pieces['rocks'] = trimesh.boolean.union(rock_meshes, engine='manifold')
    paths, timber = [], []
    for item in inputs['interpretedTimber']:
        points = np.array(item['pointsM5XYZ'],dtype=float)-origin
        if not all(island.covers(Point(p[:2]).buffer(item['radius'])) for p in points):
            raise ValueError('Climbing element escaped island')
        paths.append(points)
        timber.append(tube(points, item['radius'], 12))
    pieces['climbing_timber'] = trimesh.boolean.union(timber, engine='manifold')
    pieces['climbing_timber'] = trimesh.boolean.difference([pieces['climbing_timber'],pieces['rocks']],engine='manifold')
    ropes = []
    for item in inputs['interpretedRopes']:
        a, b = np.array(item['fromM5XYZ'])-origin, np.array(item['toM5XYZ'])-origin
        points = []
        for t in np.linspace(0,1,31):
            p = a+(b-a)*t;p[2] -= 4*item['sag']*t*(1-t);points.append(p)
        ropes.append(tube(points, params['ropeRadius'], 8))
    pieces['climbing_ropes'] = trimesh.boolean.union(ropes,engine='manifold')
    pieces['climbing_ropes'] = trimesh.boolean.difference(
        [pieces['climbing_ropes'],pieces['climbing_timber'],pieces['rocks']],engine='manifold')
    scene, checks = trimesh.Scene(), {}
    for key, mesh in pieces.items():
        if not np.isfinite(mesh.vertices).all() or (mesh.area_faces <= 1e-12).any():
            raise ValueError('Non-finite/degenerate '+key)
        if key != 'moat_water':
            welded = mesh.copy();welded.merge_vertices()
            if not welded.is_watertight or not welded.is_winding_consistent or welded.volume <= 0:
                raise ValueError('Open/inverted '+key)
            checks[key] = {'watertight':True,'consistentWinding':True,'volumeM3':float(welded.volume)}
        if key == 'climbing_timber':
            mesh, uv = bark_uv(mesh, paths)
        else:
            uv = np.column_stack((mesh.vertices[:,0],mesh.vertices[:,1]+mesh.vertices[:,2]))
            uv *= .2 if key == 'island_ground' else 1/3
        mesh.visual = trimesh.visual.TextureVisuals(uv=uv if mats[key].baseColorTexture else None,material=mats[key])
        scene.add_geometry(mesh,node_name=key,geom_name=key)
    scene.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]))
    extras = {'unit':'metre','originM5LocalXY':inputs['originM5LocalXY'],
        'sourceIds':[inputs['islandSourceId'],inputs['moatSourceId']],
        'sourceAssociation':'illustration/camera-context association, approximate',
        'sourcePhoto':inputs['sourcePhoto'],'propDimensionsSurveyed':False}
    (HERE/'lemur-adasi.glb').write_bytes(scene.export(file_type='glb',include_normals=True,
        tree_postprocessor=lambda tree:postprocess_gltf(tree,extras)))
    report = {'schema':'bursa-zoo-lemur-island/v1',**extras,
        'islandAreaM2':island_world.area,'moatOuterAreaM2':moat_world.area,'moatWaterAreaM2':moat.area,
        'renderGroundZMetres':ground_z,'renderWaterZMetres':water_z,'renderLevelsAreSurveyed':False,
        'triangles':sum(len(m.faces) for m in scene.geometry.values()),'solidChecks':checks,
        'interpretedRockCount':len(rock_meshes),'interpretedTimberCount':len(timber),'interpretedRopeCount':len(ropes),
        'meshOwnership':'Native island/moat planes are self-contained preview context, hidden in atlas where the surface partition owns them. Same-material props united, timber/rock and rope/timber hidden joints clipped.',
        'atlasHiddenNodes':['island_ground','moat_bed','moat_water'],
        'interpretation':inputs['interpretation']}
    (HERE/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['islandAreaM2','moatWaterAreaM2','triangles','interpretedTimberCount']}))


if __name__ == '__main__':
    main()
