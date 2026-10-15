"""Curved stable, doors, gates, perimeter and a single owned outdoor floor."""
from pathlib import Path
import hashlib,json,math,sys
import numpy as np
import trimesh
from PIL import Image
from shapely import affinity
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'bolgeler'))
from model_tools import polygon_mesh,pbr,postprocess_gltf,tube
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    inputs=json.loads((HERE/'habitat-inputs.json').read_text(encoding='utf-8'));o=np.array(inputs['originM5LocalXY']);dims=inputs['dimensions'];ground=dims['soilZ']
    compound=Polygon(inputs['compoundOutlineM5XY']);building=Polygon(inputs['buildingOutlineM5XY']);yard=compound.difference(building)
    tex=HERE/'textures';tex.mkdir(exist_ok=True);texture_records=[]
    for kind,source in [('soil','penguin-pale-gravel-v1.png'),('rock','penguin-artificial-rock-v1.png'),('wood','savanna-platform-wood-v1.png'),('green','woodland-meadow-v1.png')]:
        p=HERE/'material-source/gravelly_sand_diff_1k.jpg' if kind=='soil' else ROOT/'viewer/assets'/source;target=tex/(kind+'.jpg')
        with Image.open(p) as im:im=im.convert('RGB');im.thumbnail((512,512),Image.Resampling.LANCZOS);im.save(target,quality=88,optimize=True,subsampling=0)
        texture_records.append({'file':target.name,'source':p.name,'sourceSha256':sha(p),'sha256':sha(target)})
    mats={'soil':pbr('dusty_sand',[.94,.90,.82,1],tex/'soil.jpg'),
      'mud':pbr('damp_mud',[.22,.16,.10,1],tex/'soil.jpg',roughness=.90),
      'floor':pbr('stable_floor',[.49,.46,.36,1],tex/'soil.jpg'),
      'wall':pbr('warm_pale_concrete',[.68,.67,.57,1]),'red':pbr('ochre_wall_base',[.48,.31,.20,1]),
      'steel':pbr('galvanized_doors',[.28,.35,.33,1],roughness=.58),'dark':pbr('steel_partitions',[.15,.18,.16,1],roughness=.62),
      'wood':pbr('timber_barrier',[.37,.27,.16,1],tex/'wood.jpg'),
      'roof':pbr('green_roof',[.42,.46,.27,1],tex/'green.jpg'),
      'rock':pbr('pale_boulders',[.77,.75,.65,1],tex/'rock.jpg'),
      'glass':pbr('visitor_glazing',[.19,.29,.26,1],roughness=.18),'grass':pbr('tree_bed',[.45,.44,.27,1],tex/'green.jpg')}
    pieces={}
    def add(name,mesh,kind):pieces[name]=(mesh,kind)
    def beam(extent,centre,angle=0):
        m=trimesh.creation.box(extent);m.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,0,1]));m.apply_translation(centre);return m
    def segment(a,b,width,height,z):
        a,b=np.array(a),np.array(b);v=b-a;return beam([np.linalg.norm(v),width,height],[*((a+b)/2),z+height/2],math.atan2(v[1],v[0]))
    # The compound owns its floor in the atlas; no second grass/path cap below it.
    outer_wall=compound.exterior.buffer(.18,cap_style=2,join_style=2).intersection(compound)
    gate_centre=Point(inputs['gateXY']);gate_point=compound.exterior.interpolate(compound.exterior.project(gate_centre))
    distance=compound.exterior.project(gate_point);before=compound.exterior.interpolate(distance-1);after=compound.exterior.interpolate(distance+1)
    gate_dir=np.array(after.coords[0])-np.array(before.coords[0]);gate_dir/=np.linalg.norm(gate_dir);ga=np.array(gate_point.coords[0])-gate_dir*dims['gateWidth']/2;gb=np.array(gate_point.coords[0])+gate_dir*dims['gateWidth']/2
    gate_mask=LineString([ga,gb]).buffer(.5,cap_style=2)
    outer_wall=outer_wall.difference(gate_mask).difference(building)
    tree_masks=[Point(xy).buffer(2.0,quad_segs=16) for xy in inputs['treeCentresM5XY']]
    trees_area=unary_union(tree_masks).intersection(yard)
    centre=inputs['mudCentreM5XY']
    mud_outer=Polygon([(centre[0]+3.3*math.cos(a)*(1+.07*math.sin(3*a)+.04*math.cos(5*a)),centre[1]+2.15*math.sin(a)*(1+.07*math.sin(3*a)+.04*math.cos(5*a))) for a in np.linspace(0,math.tau,128,endpoint=False)]).intersection(yard.buffer(-1.0))
    mud_inner=mud_outer.buffer(-.7)
    soil=compound.difference(unary_union([building,outer_wall,mud_outer,trees_area]))
    floor_parts=[soil,building,outer_wall,mud_outer,trees_area]
    floor_overlap=sum(a.intersection(b).area for i,a in enumerate(floor_parts) for b in floor_parts[i+1:])
    floor_gap=compound.symmetric_difference(unary_union(floor_parts)).area
    assert floor_overlap<1e-6 and floor_gap<1e-6,(floor_overlap,floor_gap)
    add('yard_soil',polygon_mesh(soil,ground),'soil');add('stable_floor',polygon_mesh(building,ground),'floor')
    add('mud_floor',polygon_mesh(mud_inner,ground-dims['mudDepth']),'mud')
    # One sloped annulus joins dry soil to the recessed mud. Different ring
    # vertex counts are triangulated from the actual polygon, then heights vary.
    bank=polygon_mesh(mud_outer.difference(mud_inner),ground)
    for v in bank.vertices:
        d=Point(v[:2]).distance(mud_outer.boundary);v[2]=ground-dims['mudDepth']*min(1,d/.7)
    add('mud_bank',bank,'mud');add('tree_bed',polygon_mesh(trees_area,ground),'grass')
    wall=building.difference(building.buffer(-dims['wallThickness']))
    openings=[];doors=[];frames=[]
    transform=json.loads((ROOT/'current-plan-registration.json').read_text(encoding='utf-8'))['fit']['imagePixelsToLocalMetres']
    for item in inputs['doors']:
        tangent=np.array([sum(transform[k][i]*item['tangentUv'][i] for i in range(2)) for k in ['x','y']]);tangent/=np.linalg.norm(tangent);angle=math.atan2(tangent[1],tangent[0]);xy=np.array(item['xy'])
        opening=affinity.rotate(box(-item['width']/2,-1,item['width']/2,1),angle,use_radians=True);opening=affinity.translate(opening,*xy);openings.append(opening)
        for sign in [-1,1]:frames.append(beam([.11,.32,item['height']+.2],[*(xy+tangent*sign*(item['width']/2+.06)),ground+(item['height']+.2)/2],angle))
        frames.append(beam([item['width']+.25,.32,.14],[*xy,ground+item['height']+.12],angle))
        for sign in [-1,1]:doors.append(beam([item['width']/2-.035,.12,item['height']-.12],[*(xy+tangent*sign*item['width']/4),ground+item['height']/2],angle))
    holes=unary_union(openings)
    add('stable_outer_walls',polygon_mesh(wall.difference(holes),ground+dims['wallHeight'],ground),'wall')
    add('door_lintels',polygon_mesh(wall.intersection(holes),ground+dims['wallHeight'],ground+2.95),'wall')
    basewall=wall.difference(holes);add('stable_ochre_base',polygon_mesh(basewall,ground+.65,ground),'red')
    # Ochre is a separate lower wall section, not a coplanar overlay.
    pieces['stable_outer_walls']=(polygon_mesh(wall.difference(holes),ground+dims['wallHeight'],ground+.65),'wall')
    add('steel_door_leaves',trimesh.util.concatenate(doors),'steel');add('steel_door_frames',trimesh.util.concatenate(frames),'dark')
    add('green_roof',polygon_mesh(building,ground+dims['roofTop'],ground+dims['wallHeight']),'roof')
    parapet=building.difference(building.buffer(-.22));add('roof_parapet',polygon_mesh(parapet,ground+dims['parapetTop'],ground+dims['roofTop']),'wall')
    internal=[];sills=[]
    for part in inputs['interiorPartitions']:
        a,b=np.array(part['a']),np.array(part['b']);length=np.linalg.norm(b-a);sills.append(segment(a,b,.22,.3,ground))
        for z in [.38,1.8]:internal.append(segment(a,b,.08,.08,ground+z))
        for t in np.linspace(0,1,max(2,round(length/.4))):
            p=a+(b-a)*t;internal.append(beam([.065,.065,1.45],[*p,ground+1.045]))
    add('interior_partition_sills',trimesh.util.concatenate(sills),'wall');add('interior_steel_partitions',trimesh.util.concatenate(internal),'dark')
    add('perimeter_concrete',polygon_mesh(outer_wall,ground+dims['boundaryWallHeight'],ground),'wall')
    timber=[]
    for a,b in zip(compound.exterior.coords,list(compound.exterior.coords)[1:]):
        line=LineString([a,b]);visible=line.difference(building.buffer(.45)).difference(gate_mask)
        if visible.is_empty:continue
        parts=[visible] if visible.geom_type=='LineString' else [g for g in visible.geoms if g.geom_type=='LineString']
        for part in parts:
            a,b=part.coords[0],part.coords[-1]
            timber.append(segment(a,b,.13,.14,ground+1.42))
            for d in np.arange(0,part.length,3.0):
                p=part.interpolate(d);timber.append(beam([.16,.16,1.70],[p.x,p.y,ground+.85]))
    add('boundary_timber',trimesh.util.concatenate(timber),'wood')
    gate=[]
    for z in [.15,1.0,1.75]:gate.append(segment(ga,gb,.12,.1,ground+z))
    for t in np.linspace(0,1,12):
        p=ga+(gb-ga)*t;gate.append(beam([.085,.085,1.7],[*p,ground+.9]))
    add('separate_service_gate',trimesh.util.concatenate(gate),'steel')
    rocks=[]
    for tree_i,xy in enumerate(inputs['treeCentresM5XY']):
        for k in range(7):
            a=k*math.tau/7;x,y=np.array(xy)+[math.cos(a)*1.55,math.sin(a)*1.30]
            m=trimesh.creation.icosphere(subdivisions=2);m.vertices*=1+.09*np.sin(m.vertices[:,0:1]*5+k);m.apply_scale([.85,.62,.55]);m.apply_translation([x,y,ground+.30]);rocks.append(m)
    add('tree_boulders',trimesh.boolean.union(rocks,engine='manifold'),'rock')
    scene=trimesh.Scene();zup_to_gltf=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);triangles=0
    for name,(mesh,kind) in pieces.items():
        mesh.apply_translation([-o[0],-o[1],0]);uv=mesh.vertices[:,:2]*(.40 if kind in ['soil','mud','floor'] else .30)
        if kind=='wood':uv=np.column_stack((mesh.vertices[:,0]+mesh.vertices[:,1],mesh.vertices[:,2]*.6))
        if kind=='rock':uv=mesh.vertices[:,[0,2]]*.5
        mesh.visual=trimesh.visual.TextureVisuals(uv=uv,material=mats[kind]);mesh.apply_transform(zup_to_gltf);scene.add_geometry(mesh,node_name=name,geom_name=name);triangles+=len(mesh.faces)
    # CC0 source LOD1 only: real branches, no camera-facing sprite animation.
    source_tree=trimesh.load(ROOT/'bolgeler/_ortak/peyzaj/model/generic-broadleaf-tree.glb',force='scene',process=False)
    tree_nodes=[n for n in source_tree.graph.nodes_geometry if 'lod1' in n];tree_bounds=[]
    for n in tree_nodes:
        matrix,key=source_tree.graph[n];m=source_tree.geometry[key].copy();m.apply_transform(matrix);tree_bounds.extend(m.vertices.tolist())
    tb=np.array(tree_bounds);tree_scale=8.5/(tb[:,1].max()-tb[:,1].min())
    for ti,xy in enumerate(inputs['treeCentresM5XY']):
        for n in tree_nodes:
            matrix,key=source_tree.graph[n];m=source_tree.geometry[key].copy();m.visual.material=m.visual.material.copy();m.visual.material.normalTexture=None;m.apply_transform(matrix);m.apply_scale(tree_scale)
            m.apply_translation([xy[0]-o[0],ground-tb[:,1].min()*tree_scale,-(xy[1]-o[1])]);scene.add_geometry(m,node_name=f'rhino_tree_{ti}_{n}',geom_name=f'rhino_tree_{ti}_{n}');triangles+=len(m.faces)
    safe=yard.difference(unary_union([outer_wall,mud_outer,trees_area.buffer(1.3)])).buffer(-2.35)
    routes=[]
    for i,candidate in enumerate(inputs['routeCandidates']):
        centre=np.array(candidate['centre']);rx,ry=candidate['radii'];found=None
        for factor in [1,.9,.8,.7,.6]:
            points=[(centre+[rx*factor*math.cos(k*math.tau/64),ry*factor*math.sin(k*math.tau/64)]).tolist() for k in range(64)]
            if all(safe.covers(Point(p)) for p in points):found=points;break
        if found is None:raise ValueError('No safe rhino route: '+str(i))
        routes.append({'points':found,'initialPhase':.5 if i==0 else .31,'direction':1 if i==0 else -1,'scale':1 if i==0 else .96,'dust':.30 if i==0 else .36})
    manifest=json.loads((HERE/'hayvan/source-manifest.json').read_text(encoding='utf-8'))
    colony={'schema':'bursa-zoo-rhino-colony/v1','originM5LocalXY':o.tolist(),'groundZ':ground,'asset':'models/white-rhinoceros.glb','assetSha256':manifest['delivery']['sha256'],'assetMeta':'models/rhino-asset.json','routes':routes,'walkSpeedAtClipRateOne':.388,'minimumSeparationMetres':5.2,'bodyRadiusMetres':2.35,'habitatKey':'rhinoHabitat','scope':'Two illustrative adults,not exact zoo census or individual portrait. Registered illustration and reference-informed habitat.'}
    colony['safeDomain']=[{'outer':[list(p) for p in poly.exterior.coords],'holes':[[list(p) for p in h.coords] for h in poly.interiors]} for poly in ([safe] if safe.geom_type=='Polygon' else safe.geoms)]
    blend=json.loads((HERE/'hayvan/blend-ground.json').read_text(encoding='utf-8'))
    assert blend['assetSha256']==colony['assetSha256'],'Grounding table does not match the animal asset'
    colony['blendGround']=blend
    (HERE/'colony-layout.json').write_text(json.dumps(colony,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report={'schema':'bursa-zoo-rhino-habitat-model/v2','originM5LocalXY':o.tolist(),'triangles':triangles,'meshCount':len(scene.geometry),'areasM2':inputs['areasM2'],'surveyed':False,'source':inputs['sources'],'uncertainty':inputs['uncertainty'],'atlasHiddenNodes':[],
      'floorOwnership':'Entire registered compound owns one floor,stable and mud surfaces. Atlas terrain/path caps excluded by compound mask. Roof,wall and door junctions meet without coplanar overlay.',
      'treeCredit':'Jacaranda tree by Rico Cilliers/Rob Tuytel,Poly Haven,CC0; only 6942 triangle LOD1 used,scaled to 8.5m; illustrative species; normal map omitted because the exported mesh has no tangents',
      'soilCredit':'Gravelly Sand by Dario Barresi,Poly Haven,CC0; 1K source reduced to 512px JPEG,2.5m tiling',
      'floorCheck':{'overlapM2':floor_overlap,'gapM2':floor_gap},
      'textureDerivatives':texture_records,'parts':list(pieces),'roofNodes':['green_roof','roof_parapet'],'routeCount':len(routes)}
    output=HERE/'gergedan-yasam-alani.glb';output.write_bytes(scene.export(file_type='glb',tree_postprocessor=lambda tree:postprocess_gltf(tree,report)))
    report.update(file=output.name,bytes=output.stat().st_size,sha256=sha(output));(HERE/'habitat-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['file','bytes','triangles','meshCount','areasM2','routeCount']}))
if __name__=='__main__':main()
