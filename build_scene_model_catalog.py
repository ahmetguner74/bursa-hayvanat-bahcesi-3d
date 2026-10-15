"""Small camera/loading catalog derived from the actual local GLB files."""
from pathlib import Path
import hashlib,itertools,json
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parent
specs=[
    ('bearPool',[29],'Boz Ayı havuzu ve kaya kıyısı','29-boz-ayi/model/boz-ayi-havuz-kiyisi.glb',json.loads((ROOT/'bolgeler/29-boz-ayi/model/model-inputs.json').read_text(encoding='utf-8'))['originM5LocalXY']+[0],json.loads((ROOT/'bolgeler/29-boz-ayi/model/model-report.json').read_text(encoding='utf-8'))['atlasHiddenNodes']),
    ('habesIsland',[9],'Habeş Maymunu Adası','09-habes-maymunu/model/habes-maymunu-adasi.glb',json.loads((ROOT/'bolgeler/09-habes-maymunu/model/model-inputs.json').read_text(encoding='utf-8'))['originM5LocalXY']+[0],['island_ground','moat_bed','moat_water']),
    ('turkishVillage',[30],'Türk Köyü','30-turk-koyu/model/turk-koyu.glb',[-68,8,0],[]),
    ('penguinPool',[15],'Penguen havuzu','15-penguen/model/penguen-havuzu.glb',[-14,134,0],['pool_water','gravel_ground']),
    ('savannaPlatform',[12],'Savanna ahşap yapı','12-afrika-savana/model/savanna-ahsap-platform.glb',[203.580448933036,44.67598741130142,0],[]),
    ('lemurIsland',[11],'Lemur Adası','11-lemur/model/lemur-adasi.glb',[271.59204047156146,-14.260351774594822,0],['island_ground','moat_bed','moat_water']),
    ('africanVillage',[14],'Afrika Köyü','14-afrika-koyu/model/afrika-koyu.glb',[100.71515985586787,96.67671636694187,0],[]),
    ('africanCafe',[13],'Afrika Kafe','13-afrika-kafe/model/afrika-kafe.glb',json.loads((ROOT/'bolgeler/13-afrika-kafe/model/model-inputs.json').read_text(encoding='utf-8'))['originM5LocalXY']+[0],[]),
]
records=[]
z_up=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],dtype=float)
for key,regions,name,relative,origin,hidden in specs:
    path=ROOT/'bolgeler'/relative;blob=path.read_bytes()
    scene=trimesh.load(path,force='scene',process=False)
    corners=[]
    for node in scene.graph.nodes_geometry:
        matrix,geometry=scene.graph[node];bounds=scene.geometry[geometry].bounds
        local=np.array([(*point,1) for point in itertools.product(*zip(bounds[0],bounds[1]))])
        points=(z_up@matrix@local.T).T[:,:3]+np.array(origin)
        corners.extend(points.tolist())
    points=np.array(corners)
    records.append({'key':key,'regions':regions,'name':name,'file':'models/'+path.name,
        'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob),'originXYZMetres':origin,'hiddenNodes':hidden,
        'boundsXYZMetres':[points.min(axis=0).tolist(),points.max(axis=0).tolist()],
        'fitPointsXYZMetres':np.round(points,6).tolist() if key in ['africanVillage','africanCafe','habesIsland','bearPool'] else [],
        'source':'Actual local GLB bounds; M5 placement unchanged. Bounds are for camera/loading, not survey.'})
output={'schema':'bursa-zoo-scene-models/v1','models':records}
(ROOT/'scene-model-catalog.json').write_text(json.dumps(output,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print(json.dumps({'models':len(records),'bytes':(ROOT/'scene-model-catalog.json').stat().st_size,
    'africanBounds':next(r['boundsXYZMetres'] for r in records if r['key']=='africanVillage')}))
