"""Trace the illustrated compound into the existing approximate M5 crosswalk."""
from pathlib import Path
import hashlib,json,math
from shapely.geometry import Polygon,Point

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    registration=json.loads((ROOT/'current-plan-registration.json').read_text(encoding='utf-8'))
    transform=registration['fit']['imagePixelsToLocalMetres']
    def xy(p):return [sum(transform[k][i]*p[i] for i in range(2))+transform[k][2] for k in ['x','y']]
    compound_uv=[[365,288],[369,275],[381,264],[400,258],[404,260],[404,266],[417,268],[430,274],[440,282],[448,280],[451,291],[451,306],[445,324],[434,337],[419,346],[401,350],[391,344],[382,333],[373,320],[367,308]]
    building_uv=[[365,288],[369,275],[381,264],[400,258],[403,260],[403,265],[416,267],[430,273],[440,282],[425,293],[422,288],[415,285],[408,283],[401,284],[394,288],[390,294],[387,302],[387,309],[390,317],[382,325],[373,316],[368,305],[366,295]]
    compound=Polygon([xy(p) for p in compound_uv]);building=Polygon([xy(p) for p in building_uv]).intersection(compound)
    origin=xy([407,303]);yard=compound.difference(building)
    data={'schema':'bursa-zoo-rhino-habitat-inputs/v2','region':16,'unit':'metre','originM5LocalXY':origin,
      'sourceMapUrl':registration['officialSource']['imageUrl'],'sourceMapSha256':sha(ROOT/'reference-maps-private/2026-09-kroki.jpg'),
      'registrationSha256':sha(ROOT/'current-plan-registration.json'),'siteDataSha256':sha(ROOT/'site-data.json'),
      'traceCompoundSourceUV':compound_uv,'traceBuildingSourceUV':building_uv,
      'compoundOutlineM5XY':[list(p) for p in compound.exterior.coords],
      'buildingOutlineM5XY':[list(p) for p in building.exterior.coords],
      'doors':[{'uv':p,'xy':xy(p),'tangentUv':t,'width':3.1,'height':2.8} for p,t in [([392,291],[4,-6]),([407,283],[7,1]),([420,287],[5,3])]],
      'interiorPartitions':[{'a':xy(a),'b':xy(b)} for a,b in [([391,292],[376,278]),([401,284],[400,263]),([416,286],[429,276]),([387,306],[369,306])]],
      'treeCentresM5XY':[xy([437,307])],'mudCentreM5XY':xy([427,329]),
      'gateUv':[440,332], 'gateXY':xy([440,332]),
      'routeCandidates':[{'centre':xy([425,315]),'radii':[5.4,5.0]},{'centre':xy([407,305]),'radii':[3.5,3.5]}],
      'dimensions':{'wallHeight':4.4,'roofTop':4.60,'parapetTop':4.85,'wallThickness':.35,'boundaryWallHeight':1.25,'gateWidth':3.5,'gateHeight':1.8,'soilZ':-.24,'mudDepth':.18},
      'sources':[{'url':'https://www.bursa.bel.tr/haber/bursa-zoonun-yeni-konuklari-gergedanlar-26077','date':'2018-06-30','finding':'Organic curved form and green roof; shared rhino,zebra,common and visitor spaces.1057/3621m2 are the shared historical complex,not used as a forced scale.'},
       {'url':'https://www.bursa.bel.tr/sehir-kameralari/gergedanlar-23324','reference':'../kaynaklar/daylight-camera-reference.json','finding':'Retrieved daylight frame: soil yard,concrete perimeter,tree/rocks and pale facade with steel doors. Capture time not independently verified.'},
       {'url':'https://www.bursahayvanatbahcesi.com/wp-content/uploads/2020/09/gergedan2.jpg','finding':'Pale dusty grey animals,light boulders,tree and horizontal timber barrier'},
       {'url':'https://www.bursahayvanatbahcesi.com/wp-content/uploads/2022/09/kolaj-gergedan.jpg','finding':'Muddy shallow area; exact current position unverified'},
       {'url':'https://www.bursahayvanatbahcesi.com/dunya-gergedan-gunu/','date':'2026-09-22','finding':'Amadou and Tayo mentioned. Two illustrative adults chosen; not a complete census or individual likeness.'}],
      'surveyed':False,'uncertainty':'Illustrated footprint with existing10-25m registration uncertainty. Door positions,heights,interior partitions,mud,tree and fence details are editable visual interpretation,not as-built plans.',
      'areasM2':{'compound':compound.area,'building':building.area,'openYard':yard.area}}
    (HERE/'habitat-inputs.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'origin':origin,'areas':data['areasM2']}))
if __name__=='__main__':main()
