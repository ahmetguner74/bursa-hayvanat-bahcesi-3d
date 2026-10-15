"""Capture original M5 records once; author editable photographic estimates."""
import hashlib,json,shutil
from pathlib import Path
from shapely.geometry import Polygon,Point,LineString

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if (HERE/'model-inputs.json').exists():raise SystemExit('Inputs already exist; edit them deliberately, do not overwrite.')
site=json.loads((ROOT/'site-data.json').read_text(encoding='utf-8'))
features={f['id']:f for f in site['features']}
ids=['H22D01C2B:'+str(n) for n in [57,58,149,150,641,642]]
island=Polygon(features[ids[0]]['paths'][0]);origin=list(island.centroid.coords)[0]
photos=HERE.parent/'kaynaklar/fotograflar';documents=HERE.parent/'kaynaklar/belgeler'
photos.mkdir(exist_ok=True);documents.mkdir(exist_ok=True)
hero=photos/'resmi-site-2021-habes-ada-baglam.jpg'
page=documents/'resmi-site-2021-habes-pasta.html.txt'
shutil.copy2(ROOT/'bolgeler/_qa/habes-2021-hero.jpg',hero)
shutil.copy2(ROOT/'bolgeler/_qa/habes-2021-candidate-page.html.txt',page)
manifest_path=HERE.parent/'kaynaklar/kaynakca.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
record={'file':hero.relative_to(HERE.parent).as_posix(),
 'url':'https://www.bursahayvanatbahcesi.com/wp-content/uploads/2021/11/30780_MTYxOGNlMW_9.jpg',
 'sourcePage':'https://www.bursahayvanatbahcesi.com/cocuklar-hayvanlara-pasta-hzirladi/',
 'sourcePublished':'2021-11-12','captureDate':'Teyitsiz; 2021 etkinlik sayfasının görseli, güncel saha ölçümü değil',
 'sha256':sha(hero),'sizePixels':[1805,1205],
 'role':'Ön plandaki ziyaretçi pergolası dışında arka planda açık toprak, kaya kümeleri, yüksek ahşap direkler, halat hatları ve alçak platform/merdiven görülür. Komşu kırma çatılı yapıların aidiyeti atanmaz.',
 'reviewed':'2026-10-15','publication':'Yalnız yerel araştırma; fotoğraf GLB dokusuna veya dist paketine eklenmez'}
from PIL import Image
with Image.open(hero) as image:record['sizePixels']=list(image.size)
manifest.setdefault('architecturalReferences',[])
manifest['architecturalReferences']=[r for r in manifest['architecturalReferences'] if r['file']!=record['file']]+[record]
doc={'file':page.relative_to(HERE.parent).as_posix(),'url':record['sourcePage'],'sha256':sha(page),
 'sourcePublished':'2021-11-12','role':'Resmî etkinlik sayfası arşivi; Habeş maymunları bağlamı ve fotoğraf kaynağı. HTML çalıştırılmaz.'}
manifest.setdefault('architecturalDocuments',[])
manifest['architecturalDocuments']=[r for r in manifest['architecturalDocuments'] if r['file']!=doc['file']]+[doc]
save(manifest_path,manifest)
posts=[(182,-9,4.8),(188,2,5.6),(200,7,5.1),(207,-6,4.9),(199,-18,5.2),(187,-20,4.4)]
rocks=[(183,-8,2.3,1.8,1.9),(185,-5,1.4,1.1,.9),(189,3,1.8,1.2,1.25),
       (201,4,1.2,1.8,1),(204,-11,1.5,1.25,1.5),(194,-19,1.15,1.4,.9),
       (186,-14,1,1,.8),(201,-24,1.6,1.3,1.1)]
for x,y,h in posts:assert island.covers(Point(x,y).buffer(.3)),('post',x,y)
for x,y,sx,sy,h in rocks:assert island.covers(Point(x,y).buffer(max(sx,sy)*1.2)),('rock',x,y)
ropes=[]
for tier in [0,1]:
 for i in range(len(posts)):
  j=(i+1)%len(posts)
  a,b=posts[i],posts[j]
  ropes.append({'fromM5XYZ':[a[0],a[1],a[2]-(.32 if tier else 2)],
                'toM5XYZ':[b[0],b[1],b[2]-(.32 if tier else 2)],'sag':.55 if tier else .85})
inputs={'schema':'bursa-zoo-habes-island-inputs/v1','unit':'metre','siteDataSha256':sha(ROOT/'site-data.json'),
 'originM5LocalXY':list(origin),'islandSourceId':ids[0],'moatSourceId':ids[1],
 'islandOutlineM5XY':features[ids[0]]['paths'][0],'moatOutlineM5XY':features[ids[1]]['paths'][0],
 'internalWater':[{'sourceId':i,'outlineM5XY':features[i]['paths'][0]} for i in ids[-2:] if features[i]['closed']],
 'unmodeledOpenWaterLineSourceIds':[i for i in ids[-2:] if not features[i]['closed']],
 'platforms':[{'sourceId':i,'outlineM5XY':features[i]['paths'][0],'sourceH':features[i]['sourceH'],
               'interpretedDeckTopZ':z} for i,z in zip(ids[2:4],[1.25,.80])],
 'references':[{'file':'../'+record['file'],'sha256':record['sha256'],'role':record['role']},
               {'file':'../'+doc['file'],'sha256':doc['sha256'],'role':doc['role']},
               {'file':'../kaynaklar/fotograflar/resmi-site-3543.jpg','sha256':sha(photos/'resmi-site-3543.jpg'),'role':'Oyuk gövde/ahşap karakteri; hayvan yakın planı kesin yerleşim vermez.'}],
 'interpretedDimensions':{'bankWidth':.26,'bankTopOffset':.11,'platformDeckThickness':.16,'platformPostWidth':.15,
                          'climbingPostRadius':.20,'ropeRadius':.032},
 'interpretedPosts':[{'xyM5':[x,y],'height':h} for x,y,h in posts],
 'interpretedRocks':[{'xyM5':[x,y],'size':[sx,sy,h],'seed':i*7+9} for i,(x,y,sx,sy,h) in enumerate(rocks)],
 'interpretedRopes':ropes,
 'interpretedCrossLogs':[{'pointsM5XYZ':[[182,-9,1.1],[187,-20,1.2]],'radius':.16},
                         {'pointsM5XYZ':[[199,-18,1.1],[207,-6,1.4]],'radius':.16}],
 'interpretedHollowLog':{'pointsM5XYZ':[[190,-15,.38],[195,-12,.68]],'outerRadius':.64,'innerRadius':.42},
 'interpretedStair':{'fromM5XY':[196.1,-29.5],'toM5XY':[197.2,-26.85],'width':.95,'steps':5,'topZ':.80},
 'interpretation':['Island/moat and two small canopy XY outlines are copied unchanged from old M5 data.',
  'Canopy outlines are candidate raised wooden platform locations; their function/height is not verified. Source H is retained as metadata only.',
  'Open M5 water-layer line fragments 641/642 are archived but never closed into invented internal pools.',
  'Six poles, twelve ropes, eight rocks, cross logs, hollow log, stair and material are editable visual estimates based on the 2021 photo/camera context. Exact quantities and positions are not measured.',
  'The photograph shows the character of the enclosure, not its whole perimeter. Neighbouring red-roofed buildings and visitor pergola are not assigned to this asset.',
  'No animals or people are modelled from these photographs. Historical upload/event dates are not a current site survey.']}
save(HERE/'model-inputs.json',inputs)
save(HERE.parent/'kaynaklar/harita-verisi/model-kaynak-m5.json',{'sourceSha256':inputs['siteDataSha256'],
 'originEd50':site['originEd50'],'coordinateFrame':site['coordinateFrame'],'features':[features[i] for i in ids]})
print(json.dumps({'sourceIds':ids,'islandAreaM2':island.area,'origin':origin,'references':len(inputs['references'])}))
