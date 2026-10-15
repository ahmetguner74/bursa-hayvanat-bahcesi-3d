"""Register current legend anchors and preserve area-specific M5 context.

Anchors are manually read label positions in the September illustration,
not surveyed exhibit centres or boundaries. Native source coordinates remain
unchanged in context files. Historical March numbers are not substituted.
"""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
ANCHORS={
 1:[[660,579]],2:[[664,531]],3:[[586,533]],4:[[549,577]],5:[[654,493]],
 6:[[774,518]],7:[[828,519]],8:[[888,527]],9:[[756,439]],10:[[824,443]],
 11:[[869,439]],12:[[588,376]],13:[[650,323]],14:[[640,285]],15:[[440,264]],
 16:[[431,311]],17:[[313,309]],18:[[324,339]],19:[[255,356]],20:[[338,383]],
 21:[[330,426]],22:[[206,415]],23:[[238,438]],24:[[196,482]],25:[[258,504]],
 26:[[206,596]],27:[[239,625]],28:[[303,569]],29:[[314,530]],
 30:[[393,416],[501,432]],31:[[466,498]],32:[[433,566]],33:[[371,599]],
 34:[[462,603]],35:[[503,568]],36:[[264,202]],37:[[308,194]],38:[[382,210]],
 39:[[433,368]],40:[],41:[[492,635]],
 42:[[243,155],[243,280],[446,384],[622,534],[279,628],[932,497]],
 43:[[205,197],[609,559],[950,516]],
}
CROPS={12:[450,262,845,476],15:[413,210,547,289],16:[345,255,462,360],
       30:[345,385,548,479],31:[382,463,522,556],32:[381,531,475,591],
       40:[80,110,1000,740],41:[80,585,1000,740]}


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    index=json.loads((ROOT/'index.json').read_text(encoding='utf-8'))
    registration=json.loads((PROJECT/'current-plan-registration.json').read_text(encoding='utf-8'))
    transform=registration['fit']['imagePixelsToLocalMetres']
    source_path=PROJECT/'site-data.json'
    site=json.loads(source_path.read_text(encoding='utf-8'))
    source_hash=hashlib.sha256(source_path.read_bytes()).hexdigest()
    map_hash=hashlib.sha256((PROJECT/'reference-maps-private/2026-09-kroki.jpg').read_bytes()).hexdigest()
    def xy(u,v):
        return [transform[k][0]*u+transform[k][1]*v+transform[k][2] for k in ['x','y']]
    areas=[]
    for area in index['areas']:
        number=area['number'];folder=ROOT/area['folder'];points=ANCHORS[number]
        crop=CROPS.get(number)
        if crop is None:
            crop=[max(80,min(p[0] for p in points)-48),max(110,min(p[1] for p in points)-48),
                  min(1000,max(p[0] for p in points)+48),min(740,max(p[1] for p in points)+48)]
        x0,y0,x1,y1=crop
        corners=[xy(x0,y0),xy(x1,y0),xy(x1,y1),xy(x0,y1)]
        context=Polygon(corners)
        bounds=list(context.bounds)
        anchors=[{'sourcePixelUV':p,'localXYMetres':xy(*p)} for p in points]
        item={'number':number,'name':area['name'],'folder':area['folder'],'type':area['type'],
              'anchors':anchors,'cropWindowPixels':crop,'contextBoundsXYMetres':bounds,
              'status':'illustrated-label-anchor' if points else 'unresolved',
              'modelStatus':area['modelStatus'],'isModelStarted':area['modelStatus']!='bekliyor',
              'note':'Kroki etiketi; ölçülmüş bölge merkezi veya sınırı değil. Yaklaşık10–25m eşleme belirsizliği.'}
        if number==40:
            item['note']='Eylül lejantında40 Çocuk Oyun Alanı var; haritada40 etiketi seçilemiyor. Mart haritasındaki40 otoparkta ve aynı yer olarak kabul edilmedi.'
        location_path=folder/'kaynaklar/krokiler/bolge-konumu.json'
        save(location_path,{'schema':'bursa-zoo-area-map-context/v1',**item,
             'sourceMap':'2026-09-resmi-kroki.jpg','sourceMapSha256':map_hash,
             'registration':'../../../../current-plan-registration.json',
             'purpose':'Görsel araştırma bağlamı, sınır/aplikasyon değil'})
        # A browser crop displays the unchanged original pixels; no generated
        # or repainted map is used as source evidence.
        width,height=x1-x0,y1-y0
        title=html.escape(f'{number:02d} {area["name"]}')
        note=html.escape(item['note'])
        page=f'''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · kroki bağlamı</title><style>body{{margin:20px;background:#eef2e8;color:#254335;font:15px/1.5 system-ui}}h1{{font-size:21px}}p{{max-width:760px}}.crop{{position:relative;overflow:hidden;width:{width}px;height:{height}px;max-width:100%;background:#fff}}img{{position:absolute;width:1600px;height:864px;max-width:none;left:-{x0}px;top:-{y0}px}}a{{color:#205746}}</style><h1>{title}</h1><p>{note}</p><div class="crop"><img src="2026-09-resmi-kroki.jpg" alt="Eylül2026 resmî krokisinin bu bölgeyi içeren özgün piksel kesiti"></div><p>Bu çerçeve bölge sınırı değildir; komşu alanları da içerir. <a href="2026-09-resmi-kroki.jpg">Tam resmî kroki</a> · <a href="bolge-konumu.json">Konum ve kaynak kaydı</a></p></html>'''
        (location_path.parent/'bolge-gorunumu.html').write_text(page,encoding='utf-8')
        selected=[]
        if points:
            for feature in site['features']:
                include=False
                for path in feature['paths']:
                    if len(path)<2:continue
                    geom=LineString(path)
                    if feature['closed'] and feature['role'] in ['building','water','paving'] and len(path)>=4:
                        candidate=Polygon(path)
                        if candidate.is_valid:geom=candidate
                    if geom.intersects(context):include=True;break
                if include:selected.append(feature)
        trees=[tree for tree in site.get('treeClusters',[]) if points and context.covers(Point(tree['xy']))]
        metric_folder=folder/'kaynaklar/harita-verisi';metric_folder.mkdir(exist_ok=True)
        metric_path=metric_folder/'m5-baglam.json'
        save(metric_path,{'schema':'bursa-zoo-area-m5-context/v1','number':number,
             'coordinateFrame':site['coordinateFrame'],'originEd50':site['originEd50'],'unit':'metre',
             'sourceFile':'../../../../site-data.json','sourceSha256':source_hash,
             'selectionContextPolygonXY':corners if points else [],
             'selection':'Ölçeksiz kroki bağlamıyla kesişen eski M5 öğeleri; tam özgün koordinatlar korunur, çerçeve dışına uzanabilir. Bu öğeler kesin bölge aidiyeti kanıtı değildir.',
             'status':'selected-context' if points else 'no-location-no-geometric-selection',
             'features':selected,'treeClusters':trees})
        source_manifest=folder/'kaynaklar/kaynakca.json'
        sources=json.loads(source_manifest.read_text(encoding='utf-8'))
        sources['areaContext']={'locationFile':location_path.relative_to(folder).as_posix(),
             'locationSha256':hashlib.sha256(location_path.read_bytes()).hexdigest(),
             'metricFile':metric_path.relative_to(folder).as_posix(),
             'metricSha256':hashlib.sha256(metric_path.read_bytes()).hexdigest(),
             'nativeFeatureCount':len(selected),'nativeTreeCount':len(trees),'status':item['status']}
        save(source_manifest,sources)
        areas.append(item)
    save(PROJECT/'region-locations.json',{'schema':'bursa-zoo-region-locations/v1',
        'sourceMapUrl':registration['officialSource']['imageUrl'],'sourceMapSha256':map_hash,
        'registrationSha256':hashlib.sha256((PROJECT/'current-plan-registration.json').read_bytes()).hexdigest(),
        'unit':'M5 local metres','surveyed':False,'areas':areas})
    print(json.dumps({'areaContexts':len(areas),'locatedAreas':sum(bool(a['anchors']) for a in areas),
                      'unresolved':[a['number'] for a in areas if not a['anchors']]}))


if __name__=='__main__':
    main()
