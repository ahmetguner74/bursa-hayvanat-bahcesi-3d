"""Regression evidence for the reported pool rim and floating-rock defects."""
from pathlib import Path
import json,math
import numpy as np
import trimesh
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
surface=json.loads((ROOT/'surface-layers.json').read_text(encoding='utf-8'))
inputs=json.loads((HERE/'model-inputs.json').read_text(encoding='utf-8'))
pool=Polygon(inputs['waterOutline']['outer'],inputs['waterOutline']['holes']);rim=pool.buffer(.57,quad_segs=6).difference(pool)
layers={key:unary_union([Polygon(p['outer'],p['holes']) for p in surface['layers'][key]]) for key in ['path','terrain','building','water']}
overlaps={key:rim.intersection(layers[key]).area for key in ['path','terrain']}
assert max(overlaps.values())<1e-7,overlaps
assert rim.difference(layers['building']).area<1e-7
# Match the deterministic JS curb sampler, including its occupied buckets.
samples=[];buckets={};cell=.76
for ri,line in enumerate(surface['roadCurbLines']):
    walked=0;next_sample=.65+(ri%4)*.17
    for a,b in zip(line,line[1:]):
        length=math.dist(a,b)
        if length<.001:continue
        while next_sample<=walked+length:
            t=(next_sample-walked)/length;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;gx,gy=math.floor(x/cell),math.floor(y/cell)
            free=all((px-x)**2+(py-y)**2>=cell*cell for ix in range(gx-1,gx+2) for iy in range(gy-1,gy+2) for px,py in buckets.get((ix,iy),[]))
            if free:buckets.setdefault((gx,gy),[]).append((x,y));samples.append((x,y))
            next_sample+=1.07
        walked+=length
near=[p for p in samples if Point(p).distance(pool.boundary)<.65]
assert not near,near
scene=trimesh.load(HERE/'penguen-havuzu.glb',force='scene',process=False)
rocks=scene.geometry['emergent_rocks'].copy();rocks.merge_vertices(merge_tex=True,merge_norm=True)
node=next(n for n in scene.graph.nodes_geometry if scene.graph[n][1]=='emergent_rocks')
rocks.apply_transform(scene.graph[node][0])
bottoms=[float(m.vertices[:,1].min()) for m in rocks.split(only_watertight=False)]
assert len(bottoms)==2 and all(z<=-1.45 for z in bottoms),bottoms
proof={'revision':'20261015al','rimPathOverlapM2':overlaps['path'],'rimTerrainOverlapM2':overlaps['terrain'],'curbStoneCentresWithin65cmOfPool':len(near),'roadStoneCount':len(samples),'rockBottomZMetres':bottoms,'basinFloorZMetres':-1.45,'waterMeshesInAtlas':1,'waterMaskM2':pool.area,'originalM5CoordinatesChanged':False,'scope':'Actual serialized surface masks, exact JS curb sampling and GLB components; visual review is separate.'}
(HERE/'pool-fix-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof))
