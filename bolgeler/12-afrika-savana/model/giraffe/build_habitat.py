"""Reference-informed open Savanna section, sharing the existing M5 frame."""
from pathlib import Path
import sys,json,hashlib,math
import numpy as np,trimesh
from PIL import Image
from shapely.geometry import Point,Polygon,LineString
from shapely.ops import unary_union
from shapely import affinity
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'bolgeler'))
from model_tools import polygon_mesh,pbr,tube,postprocess_gltf
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def parts(g):return [g] if g.geom_type=='Polygon' else list(g.geoms)
def main():
 old=json.loads((R/'site-data.json').read_text());layers=json.loads((R/'surface-layers.json').read_text())
 circuit=Polygon(next(f['pointsXYMetres']for f in json.loads((R/'current-plan-data.json').read_text())['features']if f['id']=='savanna_visitor_circuit'))
 keep=unary_union([Polygon(p['outer'],p.get('holes',[]))for k in ['water','path','building'] for p in layers['layers'][k]])
 previous=json.loads((H/'habitat-inputs.json').read_text()) if(H/'habitat-inputs.json').exists()else None
 compound=Polygon(previous['compoundOutlineM5XY']) if previous else affinity.scale(Point(60,48).buffer(1,quad_segs=48),27,19).intersection(circuit.buffer(-12)).difference(keep.buffer(.6))
 assert compound.geom_type=='Polygon'
 origin=np.array([60,48]);ground=-.24
 # The source photographs show green two-rail barriers and low stone boundaries.
 # This is one interpreted open viewing segment, not a surveyed enclosure wall.
 fence_line=LineString([[60+27*math.cos(t),48+19*math.sin(t)]for t in np.linspace(math.pi*1.12,math.pi*1.88,65)])
 gate=LineString([[58.1,27],[58.1,34]]).buffer(1.7,cap_style=2)
 visible=fence_line.difference(gate);wallmask=visible.buffer(.24,cap_style=2).intersection(compound)
 soil=compound.difference(wallmask)
 textures=H/'habitat-textures';textures.mkdir(exist_ok=True)
 source=R/'bolgeler/16-gergedan/model/material-source/gravelly_sand_diff_1k.jpg';target=textures/'soil.jpg'
 with Image.open(source) as im:im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS).save(target,quality=88,optimize=True)
 wood=R/'viewer/assets/savanna-platform-wood-v1.png';wtarget=textures/'wood.jpg'
 with Image.open(wood)as im:im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS).save(wtarget,quality=87,optimize=True)
 rock=R/'viewer/assets/penguin-artificial-rock-v1.png';rtarget=textures/'rock.jpg'
 with Image.open(rock)as im:im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS).save(rtarget,quality=87,optimize=True)
 mats={'soil':pbr('SandAndEarth',[.86,.82,.70,1],target),'wood':pbr('TimberPosts',[.44,.34,.24,1],wtarget),'rock':pbr('LowStoneBoundary',[.58,.61,.53,1],rtarget),'steel':pbr('BursaGreenBarrier',[.12,.25,.20,1],roughness=.68),'leaf':pbr('BrowseLeaves',[.27,.36,.11,1])};mats['leaf'].doubleSided=True;pieces={}
 def add(n,m,k):pieces[n]=(m,k)
 def beam(a,b,w,h,z):
  a,b=np.array(a),np.array(b);v=b-a;m=trimesh.creation.box([np.linalg.norm(v),w,h]);m.apply_transform(trimesh.transformations.rotation_matrix(math.atan2(v[1],v[0]),[0,0,1]));m.apply_translation([*((a+b)/2),z+h/2]);return m
 add('savanna_owned_sand',polygon_mesh(soil,ground),'soil')
 add('low_stone_viewing_boundary',polygon_mesh(wallmask,ground+.48,ground),'rock')
 rails=[];posts=[]
 lines=[visible]if visible.geom_type=='LineString' else list(visible.geoms)
 for line in lines:
  for a,b in zip(line.coords,list(line.coords)[1:]):
   for z in [.82,1.32]:rails.append(beam(a,b,.09,.10,ground+z))
  for d in np.arange(0,line.length,2.5):
   p=line.interpolate(d);m=trimesh.creation.box([.12,.12,1.55]);m.apply_translation([p.x,p.y,ground+.775]);posts.append(m)
 add('green_horizontal_visitor_rails',trimesh.util.concatenate(rails+posts),'steel')
 # Two high browse posts and branching foliage, consistent with municipal feeding photos.
 feeder_xy=[[56,57],[72,56]];branches=[];leaves=[]
 for i,(x,y) in enumerate(feeder_xy):
  branches.append(tube([[x,y,ground],[x+.10,y+.07,3.50]],.14,sections=12))
  for k in range(6):
   a=k*math.tau/6+i*.3;start=np.array([x,y,3.1]);end=start+[math.cos(a)*.85,math.sin(a)*.85,.5+.15*math.cos(k)]
   branches.append(tube([start,end],.025,sections=6))
   for q in range(3):
    c=start+(end-start)*(.45+.20*q);v=np.array([.15*math.cos(a+.6),.15*math.sin(a+.6),.12]);other=np.array([-.08*math.sin(a),.08*math.cos(a),.04]);vertices=[c-v,c+other,c+v,c-other];leaves.append(trimesh.Trimesh(vertices,[[0,1,2],[0,2,3]],process=False))
 add('elevated_branch_browse_feeders',trimesh.util.concatenate(branches),'wood');add('leaf_browse_branches',trimesh.util.concatenate(leaves),'leaf')
 # No large invented stable: its existence is documented, facade/position are unresolved.
 trees=[[43,58],[78,59]];rocks=[]
 for xy in trees:
  for k in range(6):
   m=trimesh.creation.icosphere(subdivisions=1);m.apply_scale([.7,.58,.45]);m.apply_translation([xy[0]+1.4*math.cos(k*math.tau/6),xy[1]+1.25*math.sin(k*math.tau/6),ground+.23]);rocks.append(m)
 add('tree_root_boulders',trimesh.util.concatenate(rocks),'rock')
 scene=trimesh.Scene();rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);tris=0
 for name,(mesh,kind)in pieces.items():
  mesh.apply_translation([-origin[0],-origin[1],0]);uv=mesh.vertices[:,:2]*.4
  if kind=='wood':uv=np.column_stack((mesh.vertices[:,0]+mesh.vertices[:,1],mesh.vertices[:,2]*.7))
  mesh.visual=trimesh.visual.TextureVisuals(uv=uv,material=mats[kind]);mesh.apply_transform(rot);scene.add_geometry(mesh,node_name=name,geom_name=name);tris+=len(mesh.faces)
 tree=trimesh.load(R/'bolgeler/_ortak/peyzaj/model/generic-broadleaf-tree.glb',force='scene',process=False);nodes=[n for n in tree.graph.nodes_geometry if 'lod1'in n];bounds=[]
 for n in nodes:
  matrix,key=tree.graph[n];m=tree.geometry[key].copy();m.apply_transform(matrix);bounds.extend(m.vertices.tolist())
 b=np.array(bounds);scale=9/(b[:,1].max()-b[:,1].min())
 for i,xy in enumerate(trees):
  for n in nodes:
   matrix,key=tree.graph[n];m=tree.geometry[key].copy();m.visual.material=m.visual.material.copy();m.visual.material.normalTexture=None;m.apply_transform(matrix);m.apply_scale(scale);m.apply_translation([xy[0]-origin[0],ground-b[:,1].min()*scale,-(xy[1]-origin[1])]);scene.add_geometry(m,node_name=f'giraffe_tree_{i}_{n}',geom_name=f'giraffe_tree_{i}_{n}');tris+=len(m.faces)
 obstacles=unary_union([Point(p).buffer(2.6)for p in trees]+[Point(p).buffer(1.7)for p in feeder_xy]+[wallmask])
 safe=compound.difference(obstacles).buffer(-2.7)
 routes=[]
 for i,(cx,cy,rx,ry)in enumerate([[49,41,5.5,4],[70,41,5.0,4.6]]):
  ps=[[cx+rx*math.cos(t),cy+ry*math.sin(t)]for t in np.linspace(0,math.tau,64,endpoint=False)]
  assert all(safe.covers(Point(p))for p in ps),(i,'route outside safe zone')
  routes.append({'points':ps,'initialPhase':.48 if i==0 else .2,'direction':1 if i==0 else -1,'scale':1 if i==0 else .91})
 asset=json.loads((H/'giraffe-asset.json').read_text())
 meta={'schema':'bursa-zoo-giraffe-colony/v1','region':12,'originM5LocalXY':origin.tolist(),'centre':[60,46,2.4],'boundsRadius':32,'groundZ':ground,'assetSha256':asset['delivery']['sha256'],'routes':routes,'walkSpeedAtClipRateOne':.48,'minimumSeparationMetres':5.5,'bodyRadiusMetres':2.7,'safeDomain':[{'outer':list(p.exterior.coords),'holes':[list(h.coords)for h in p.interiors]}for p in parts(safe)],'habitatKey':'giraffeHabitat','scope':'Two illustrative adult Baringo-style giraffes; not a zoo census or individual likeness.'}
 if(H/'blend-ground.json').exists():
  blend=json.loads((H/'blend-ground.json').read_text());assert blend['assetSha256']==meta['assetSha256'];meta['blendGround']=blend
 (H/'giraffe-colony.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 inputs={'schema':'bursa-zoo-savanna-open-section-inputs/v1','originM5LocalXY':origin.tolist(),'groundZ':ground,'compoundOutlineM5XY':list(compound.exterior.coords),'floorOwnershipMasks':[{'outer':list(compound.exterior.coords),'holes':[list(h.coords)for h in compound.interiors]}],'treeCentresM5XY':trees,'feedersXY':feeder_xy,'sourceRegistrationSha256':sha(R/'current-plan-registration.json'),'siteDataSha256':sha(R/'site-data.json'),'sourcePhotoFiles':['23247_YHG_8895_201702021252.jpg','26077_IMG_8891_201806301148.jpg','26077_IMG_8908_201806301148.jpg'],'sources':['https://www.bursa.bel.tr/haber/bursa-zoonun-yeni-konuklari-gergedanlar-26077','https://www.bursahayvanatbahcesi.com/hayvan/baringo-zurafasi/','https://www.bursahayvanatbahcesi.com/zurafalara-uludagdan-ozel-diyet/'],'surveyed':False,'interpretation':'One open viewing/feeding section inside the illustrated Savanna circuit. Fence,feeder,tree positions and all dimensions are visual interpretation. Existing platform is preserved at its original candidate M5 location. Heated tall stable exists per official report but is not reconstructed without facade/location proof.','areasM2':{'ownedFloor':compound.area,'soil':soil.area,'stoneBoundary':wallmask.area},'floorCheck':{'overlapM2':soil.intersection(wallmask).area,'gapM2':compound.symmetric_difference(unary_union([soil,wallmask])).area}}
 # Once integrated, the surface builder deliberately classifies this owned
 # floor as a building mask. Do not subtract our own floor on the next build.
 inputs['initialSurfaceSha256']=previous.get('initialSurfaceSha256',sha(R/'surface-layers.json')) if previous else sha(R/'surface-layers.json')
 for k in ['water','path']:assert compound.intersection(unary_union([Polygon(p['outer'],p.get('holes',[]))for p in layers['layers'][k]])).area<1e-8
 (H/'habitat-inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 report={**inputs,'schema':'bursa-zoo-giraffe-habitat-model/v1','triangles':tris,'meshCount':len(scene.geometry),'atlasHiddenNodes':[],'parts':list(pieces),'soilCredit':'Gravelly Sand by Dario Barresi,Poly Haven CC0;512px technical JPEG derivative','treeCredit':'Jacaranda by Rico Cilliers/Rob Tuytel,Poly Haven CC0;LOD1 only,normal map omitted where tangents unavailable;illustrative species','feederLeaves':'Simple authored closed branch tubes and small double-sided geometric leaves,not a new image texture'}
 output=H/'zurafa-acik-yasam-alani.glb';output.write_bytes(scene.export(file_type='glb',tree_postprocessor=lambda tree:postprocess_gltf(tree,report)));report.update(file=output.name,bytes=output.stat().st_size,sha256=sha(output));(H/'habitat-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k]for k in ['file','bytes','triangles','meshCount','areasM2','floorCheck']}))
if __name__=='__main__':main()
