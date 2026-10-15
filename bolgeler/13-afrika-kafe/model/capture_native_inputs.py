"""Capture reviewed native candidates once; do not overwrite later edits."""
from pathlib import Path
import hashlib,json
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
if (HERE/'model-inputs.json').exists():raise SystemExit('Inputs already exist; review/edit them explicitly.')
site_path=ROOT/'site-data.json';site=json.loads(site_path.read_text(encoding='utf-8'))
ids=['H22D01C2B:'+str(n) for n in [152,153,154,155,156,243]]
features=[next(f for f in site['features'] if f['id']==sid) for sid in ids]
centre=unary_union([Polygon(f['paths'][0]) for f in features]).centroid
sources=json.loads((HERE.parent/'kaynaklar/kaynakca.json').read_text(encoding='utf-8'))
records=[next(r for r in sources['architecturalReferences'] if '6722_'+str(n)+'_' in r['file']) for n in [6,10]]
records.append(sources['architecturalDocuments'][0])
references=[{'file':'../'+r['file'],'sha256':r['sha256'],'url':r['url']} for r in records]
inputs={'schema':'bursa-zoo-african-cafe-inputs/v1','siteDataSha256':hashlib.sha256(site_path.read_bytes()).hexdigest(),
    'originM5LocalXY':[centre.x,centre.y],
    'roofs':[{'sourceId':f['id'],'type':'building' if f['role']=='building' else 'canopy','sourceH':f['sourceH'],'outlineM5XY':f['paths'][0]} for f in features],
    'references':references,
    'interpretedDimensionsMetres':{'floorZ':-.105,'floorBottomZ':-.46,'mainEaveZ':3.15,'canopyEaveZ':2.9,
        'roofEdgeDepth':.13,'roofSlope':.6,'maximumRoofRise':1.65,'wallInset':.35,'wallThickness':.18,'postInset':.3,'postWidth':.16,'beamDepth':.18},
    'interpretation':[
        'Six native M5 outlines152–156 and243 are candidates near the September cafe label. Their association follows the illustrated plan and is not a surveyed/current site verification.',
        'The 2011 official opening photographs show dark timber, open-sided square hipped gazebos and warm brown roofs. They do not determine the exact position or present condition of every pavilion.',
        'All heights, roof slopes/ridges, timber sections, post placement, wall inset and two wall openings are editable visual estimates. No interior furniture or operational layout is asserted.',
        'A 0.000716m2 overlap of native roof152/153 is clipped only in the derived render geometry; all original source coordinates remain in inputs and the native context file.',
        'One continuous floor replaces terrain/path in the shared surface partition; the generic box for source243 is removed from the scene shell. Original QGIS road polygons are unchanged.',
        'Existing generated wood/roof/paving presentation materials are reused; no source photograph is republished or used as a licensed texture.',
    ]}
(HERE/'model-inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
native={'schema':'bursa-zoo-native-model-context/v1','number':13,'sourceFile':'../../../../site-data.json',
    'sourceSha256':inputs['siteDataSha256'],'originEd50':site['originEd50'],'coordinateFrame':site['coordinateFrame'],
    'unit':'metre','features':features,'association':'cafe candidate outlines, approximate; source features unchanged'}
(HERE.parent/'kaynaklar/harita-verisi/model-kaynak-m5.json').write_text(json.dumps(native,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sourceIds':ids,'origin':inputs['originM5LocalXY']}))
