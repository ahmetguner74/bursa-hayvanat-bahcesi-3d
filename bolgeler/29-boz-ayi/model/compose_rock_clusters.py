"""Editable illustrative clusters; do not alter the archived native pool/masks."""
from pathlib import Path
import json,math,random
from shapely.geometry import Point,Polygon
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
path=HERE/'model-inputs.json';inputs=json.loads(path.read_text(encoding='utf-8'))
ground=unary_union([Polygon(p['outer'],p['holes']) for p in inputs['previewGroundMaskM5XY']])
site=json.loads((ROOT/'site-data.json').read_text(encoding='utf-8'))
trees=[Point(t['xy']) for t in site.get('treeClusters',[])]
# Chosen north-bank anchors are visual estimates in M5 XY, not surveyed rocks.
anchors=[[-141.5,-63.6],[-128.7,-59.9],[-110.6,-62.6]]
rng=random.Random(4029);rocks=[]
for cluster,(cx,cy) in enumerate(anchors):
    target=[6,5,6][cluster];accepted=0
    for attempt in range(300):
        if accepted==target:break
        sx=rng.uniform(.48,1.70);sy=sx*rng.uniform(.63,.92);height=rng.uniform(.70,1.72)
        x,y=cx+rng.uniform(-3.1,3.1),cy+rng.uniform(-1.4,1.9)
        footprint=Point(x,y).buffer(sx*1.35)
        if not ground.covers(footprint) or any(footprint.buffer(.35).covers(t) for t in trees):continue
        if any(math.dist([x,y],r['xyM5'])<.52*(sx+r['size'][0]) for r in rocks):continue
        rocks.append({'xyM5':[x,y],'size':[sx,sy,height],'angle':rng.uniform(-math.pi,math.pi),
                      'seed':cluster*300+attempt,'illustrativeCluster':cluster+1});accepted+=1
    assert accepted==target,(cluster,accepted)
plants=[]
for attempt in range(500):
    if len(plants)==9:break
    rock=rocks[attempt%len(rocks)];angle=rng.uniform(-math.pi,math.pi)
    distance=rock['size'][0]*1.5+.45;x,y=rock['xyM5']
    x+=distance*math.cos(angle);y+=distance*math.sin(angle)
    if not ground.covers(Point(x,y).buffer(.5)):continue
    if any(math.dist([x,y],r['xyM5'])<r['size'][0]*1.2+.25 for r in rocks):continue
    plants.append({'xyM5':[x,y],'height':rng.uniform(.50,.80),'width':.65,'seed':attempt})
assert len(plants)==9
inputs['interpretedRocks']=rocks;inputs['interpretedPlants']=plants
inputs['propLayoutNote']='Three asymmetrical illustrative north-bank clusters; the photograph establishes material character, not these positions. Native XY and mask records unchanged.'
path.write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rocks':len(rocks),'plants':len(plants),'clusters':len(anchors)}))
