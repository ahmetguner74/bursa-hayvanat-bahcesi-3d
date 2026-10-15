"""Capture the native candidate bear pond and reviewed source photographs once."""
import hashlib,json,math,shutil,sys
from pathlib import Path
from PIL import Image
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT))
from build_surface_layers import serialized_polygons
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if (HERE/'model-inputs.json').exists():raise SystemExit('Existing inputs are protected; edit deliberately.')
site=json.loads((ROOT/'site-data.json').read_text(encoding='utf-8'))
feature=next(f for f in site['features'] if f['id']=='H22D01C2B:278')
assert feature['closed'] and feature['role']=='water'
pool=Polygon(feature['paths'][0]);origin=list(pool.centroid.coords)[0]
surface=json.loads((ROOT/'surface-layers.json').read_text(encoding='utf-8'))
available=unary_union([Polygon(p['outer'],p['holes']) for p in surface['layers']['terrain']])
bank=pool.buffer(.40).difference(pool).intersection(available)
context=pool.buffer(6).difference(pool).intersection(available).difference(bank)
photos=HERE.parent/'kaynaklar/fotograflar';documents=HERE.parent/'kaynaklar/belgeler'
manifest_path=HERE.parent/'kaynaklar/kaynakca.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
refs=[]
for media_id,role in [(2108,'Havuz kıyısında beton/taş kenar, büyük gri kaya kümeleri ve yeşil zemin geçişi. Bütün havuz çevresi görünmüyor.'),
                      (1905,'Karlı ayı alanında kaya karakteri; havuz veya bütün barınak sınırı için ölçü kanıtı değil.')]:
    candidate=ROOT/'bolgeler/_qa/new-enclosure-references'
    meta=json.loads((candidate/(str(media_id)+'.json')).read_text(encoding='utf-8'))
    target=photos/('resmi-site-'+str(media_id)+'-baglam'+('.png' if media_id==2108 else '.jpg'));shutil.copy2(candidate/(str(media_id)+'.jpg'),target)
    with Image.open(target) as image:size=list(image.size)
    rec={'file':target.relative_to(HERE.parent).as_posix(),'url':meta['source_url'],'sourcePage':
         'https://www.bursahayvanatbahcesi.com/'+('karin-gec-gelmesi-ayilari-uykusuz-birakti/' if media_id==2108 else 'kar-uzerinde-ayilara-balik-ziyafeti/'),
         'uploaded':meta['date'],'captureDate':'Teyitsiz; eski resmî haber fotoğrafı güncel saha ölçümü değil',
         'sha256':sha(target),'sizePixels':size,'role':role,'reviewed':'2026-10-15',
         'publication':'Yalnız yerel araştırma; fotoğraf GLB dokusuna veya dist içine eklenmez'}
    manifest.setdefault('architecturalReferences',[])
    manifest['architecturalReferences']=[r for r in manifest['architecturalReferences'] if r['file']!=rec['file']]+[rec]
    refs.append({'file':'../'+rec['file'],'sha256':rec['sha256'],'role':role})
page=documents/'resmi-site-2018-ayi-havuz-baglam.html.txt'
shutil.copy2(ROOT/'bolgeler/_qa/new-enclosure-references/bear-2018.html.txt',page)
doc={'file':page.relative_to(HERE.parent).as_posix(),'url':manifest['architecturalReferences'][-2]['sourcePage'],
     'sha256':sha(page),'sourcePublished':'2018-01-11','role':'Resmî ayı haberi ve havuz/kaya fotoğrafının sayfa arşivi; HTML çalıştırılmaz.'}
manifest.setdefault('architecturalDocuments',[])
manifest['architecturalDocuments']=[r for r in manifest['architecturalDocuments'] if r['file']!=doc['file']]+[doc]
save(manifest_path,manifest);refs.append({'file':'../'+doc['file'],'sha256':doc['sha256'],'role':doc['role']})
rocks=[];ring=pool.exterior;sign=1 if ring.is_ccw else -1
for index in range(max(1,int(ring.length/3.6))):
    distance=ring.length*(index+.35)/max(1,int(ring.length/3.6))
    point=ring.interpolate(distance);a=ring.interpolate((distance-.1)%ring.length);b=ring.interpolate((distance+.1)%ring.length)
    if point.y<pool.centroid.y+1:continue
    dx,dy=b.x-a.x,b.y-a.y;length=math.hypot(dx,dy);nx,ny=dy/length*sign,-dx/length*sign
    for row in [0,1]:
        sx=.46+(index%4)*.055 if row==0 else 1.0+(index%4)*.16
        sy=sx*.78;height=.42+(index%3)*.13 if row==0 else 1.12+(index%3)*.32
        offset=1.1 if row==0 else 2.8
        x,y=point.x+nx*offset,point.y+ny*offset
        if not context.covers(Point(x,y).buffer(sx*1.35)):continue
        rocks.append({'xyM5':[x,y],'size':[sx,sy,height],'angle':math.atan2(dy,dx)+(index%3)*.23,'seed':index*13+row})
plants=[]
for index,rock in enumerate(rocks):
    if index%2:continue
    x,y=rock['xyM5'];x+=.85;y+=.65
    if context.covers(Point(x,y).buffer(.5)):plants.append({'xyM5':[x,y],'height':.55+(index%3)*.1,'width':.65,'seed':index})
inputs={'schema':'bursa-zoo-bear-pool-inputs/v1','unit':'metre','siteDataSha256':sha(ROOT/'site-data.json'),
 'sourceSurfaceBeforeBearSha256':sha(ROOT/'surface-layers.json'),'poolSourceId':feature['id'],
 'poolOutlineM5XY':feature['paths'][0],'sourceH':feature['sourceH'],'originM5LocalXY':list(origin),
 'interpretedBankMaskM5XY':serialized_polygons(bank),'previewGroundMaskM5XY':serialized_polygons(context),
 'interpretedDimensions':{'bankWidth':.40,'bankTopOffset':.10,'bankBottomZ':-1.55,'bedTopZ':-1.26,'bedBottomZ':-1.65},
 'interpretedRocks':rocks,'interpretedPlants':plants,'references':refs,
 'waterPresentationColor':'#52734e',
 'interpretation':['Native pool278 XY is retained. Its association with region29 is approximate; the precise28/29 enclosure boundary is unresolved.',
   'The photograph shows one bank. Concrete width/height, pool depth, rock quantity/positions and vegetation are editable visual estimates, not surveyed construction data.',
   'The 40 cm illustrative bank is clipped to previously available dry terrain; QGIS road and existing building footprints are not moved.',
   'The native source H is metadata only. Photographic upload/publication dates do not confirm present-day condition.',
   'Only the pond and photographed-style rocky bank component is modelled. Enclosure perimeter, service building, animal and unseen banks are not invented.']}
save(HERE/'model-inputs.json',inputs)
save(HERE.parent/'kaynaklar/harita-verisi/model-kaynak-m5.json',{'sourceSha256':inputs['siteDataSha256'],'originEd50':site['originEd50'],
 'coordinateFrame':site['coordinateFrame'],'features':[feature]})
print(json.dumps({'nativePoolAreaM2':pool.area,'bankAreaM2':bank.area,'rocks':len(rocks),'plants':len(plants)}))
