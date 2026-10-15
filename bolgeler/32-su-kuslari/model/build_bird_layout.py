"""Place four illustrative resting birds on actual partitioned dry shore.

No native coordinates are edited. Shell/lagoon/landscaping remain visual
interpretations; this verifies placement against the current built atlas.
"""
from pathlib import Path
import json,math,hashlib
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
load=lambda p:json.loads(p.read_text(encoding='utf8'))
surfaces=load(ROOT/'surface-layers.json');local=load(ROOT/'cage-local-surfaces.json')
anchor=next(f['modelAnchor'] for f in load(ROOT/'current-plan-data.json')['features'] if 'modelAnchor' in f)
cx,cy=anchor['provisionalShellCentreXYMetres'];angle=math.radians(anchor['provisionalShellAngleDegreesCounterclockwiseFromEast']);c,s=math.cos(angle),math.sin(angle)
world=lambda p:[cx+p[0]*c-p[1]*s,cy+p[0]*s+p[1]*c]
layers={k:unary_union([Polygon(p['outer'],p['holes']) for p in v]) for k,v in surfaces['layers'].items()}
lagoon=Polygon(local['lagoonOutline']);signed=1 if lagoon.exterior.is_ccw else -1
plants=[]
pts=local['lagoonOutline']
for i,(a,b) in enumerate(zip(pts,pts[1:])):
    length=math.dist(a,b);count=max(1,math.floor(length/.72+.5))
    for j in range(count):
        if (i*11+j)%3:continue
        t=(j+.5)/count;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
        nx=(b[1]-a[1])/length*signed;ny=-(b[0]-a[0])/length*signed
        size=.38+((i*7+j*3)%9)*.045;offset=.85+((i*3+j)%5)*.19
        px,py=x+nx*offset,y+ny*offset
        if all(layers['terrain'].covers(Point(world((px+u,py+v)))) for u,v in [(0,0),(size*1.05,0),(-size*1.05,0),(0,size*1.05),(0,-size*1.05)]):plants.append((px,py,size*1.05))
for x,y in [[-22,9],[-18,11],[-5,12],[0,13],[18,-8],[21,8],[-20,-10],[22,-4],[-4,-13],[9,-11]]:
    for k in range(4):plants.append((x+(k%2)*1.1,y+(k//2)*.95,(.65+(k%3)*.13)*1.1))
trees=[[-23,8],[-18,10],[-11,12],[17,-10],[21,7],[9,12]]
def audit(p):
    w=Point(world(p));return {'dryGround':layers['terrain'].covers(w.buffer(.65)), 'waterClearanceM':layers['water'].distance(w),'pathClearanceM':layers['path'].distance(w),'buildingClearanceM':layers['building'].distance(w),'plantClearanceM':min(math.hypot(p[0]-x,p[1]-y)-r for x,y,r in plants),'treeClearanceM':min(math.dist(p,t) for t in trees)}
chosen=[]
for initial in [[-11,-11.1],[-8.3,-10.6],[-5.3,-11.4],[-2.2,-11.1]]:
    candidates=[]
    for dx in [0,-.3,.3,-.6,.6,-.9,.9]:
        for dy in [0,-.3,.3,-.6,.6]:
            p=[initial[0]+dx,initial[1]+dy];check=audit(p)
            if check['dryGround'] and check['plantClearanceM']>.68 and check['treeClearanceM']>1.5 and check['pathClearanceM']>.7 and check['waterClearanceM']>.7 and all(math.dist(p,q)>2.1 for q in chosen):candidates.append((math.dist(p,initial),p,check))
    assert candidates,initial
    _,p,check=min(candidates,key=lambda row:row[0]);chosen.append(p)
asset=load(HERE/'hayvan/asset-manifest.json')
meta={'schema':'bursa-zoo-aviary-bird-colony/v1','species':'Greater flamingo / Phoenicopterus roseus','label':'Flamingolar · temsili kıyı kolonisi','asset':'greater-flamingo.glb','assetSha256':asset['deliverySha256'],'heightM':1.30,'geometryTrianglesPerAnimal':asset['triangles'],'jointsPerAnimal':5,'groundZ':surfaces['renderLevels']['terrainZ'],'coordinateFrame':'Cage-local XY, transformed only by the existing current-plan modelAnchor; M5 inputs untouched','anchor':{'x':cx,'y':cy,'angle':angle},'layoutStatus':'Yorum','evidenceLabel':'Tür Bursa Zoo’da doğrulanır; bu dört bireyin güncel kubbe içi konumu ve sayısı doğrulanmadı. Yerleşim görsel yorumdur.','sourceAnimation':False,'behaviors':['Rest','LookAround','Settle'],'unsupportedBehaviors':['walking','swimming','flying','feeding','true feather preening'],'animals':[],'credits':{'title':asset['sourceUrl'],'author':'Pigcraft','authorUrl':asset['authorUrl'],'license':'CC BY4.0','licenseUrl':asset['licenseUrl'],'changes':asset['modifications'],'provenance':asset['provenance']},'sources':[{'url':'https://www.bursahayvanatbahcesi.com/hayvan/flamingo-greater-flamingo/','role':'Species present in zoo; exact current enclosure not stated'},{'url':'https://www.bursahayvanatbahcesi.com/sulari-temiz-tut-ekosistemi-yasat/','imageUrl':'https://www.bursahayvanatbahcesi.com/wp-content/uploads/2026/04/su-kuslari.png','role':'Official educational image shows pale pink waterbird plumage; capture location and date unverified'},{'url':'https://uskon.com/en/bursa-zoo-waterbird-cage-single-wall-elliptical-dome/','role':'Historical interior confirms waterbirds in dome; photographs show stork/egret forms, does not establish current flamingo census'},{'url':'https://www.wwt.org.uk/wetland-centres/slimbridge/flamingo-diary/hot-pink-flamingos-flamingo-care-in-warm-weather','role':'Rest and feather care can occupy a large part of the day; quiet shore group plausible'},{'url':'https://animals.sandiegozoo.org/animals/flamingo','role':'Greater flamingo adult height120–145cm; social/rest behavior'}]}
for i,p in enumerate(chosen):
    meta['animals'].append({'id':f'illustrative-flamingo-{i+1}','localXY':p,'worldXY':world(p),'scale':[1,.97,1.025,.99][i],'heading':[2.75,1.25,-2.2,.9][i],'initialClip':['LookAround','Rest','Rest','Settle'][i],'phase':[0,1.8,3.2,.9][i],'behaviorSeed':42+i*113,'clearance':audit(p)})
(HERE/'aviary-birds-layout.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'animals':len(chosen),'localPositions':chosen,'minPlantClearanceM':min(a['clearance']['plantClearanceM'] for a in meta['animals']),'assetSha256':meta['assetSha256']}))
