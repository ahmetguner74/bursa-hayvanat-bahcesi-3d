"""Editable M5 island and candidate climbing platforms; photographic estimates."""
from __future__ import annotations
import hashlib,json,math,os,sys
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image
from shapely import affinity
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'bolgeler'))
from model_tools import polygon_mesh,tube,bark_uv,pbr,postprocess_gltf

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def union(items):return trimesh.boolean.union(items,engine='manifold')
def difference(mesh,*others):return trimesh.boolean.difference([mesh,*others],engine='manifold')
def beam(a,b,width,depth):
    a,b=np.asarray(a),np.asarray(b);delta=b-a
    mesh=trimesh.creation.box([width,depth,np.linalg.norm(delta)])
    mesh.apply_transform(trimesh.geometry.align_vectors([0,0,1],delta))
    mesh.apply_translation((a+b)/2);return mesh

def main():
    inputs=json.loads((HERE/'model-inputs.json').read_text(encoding='utf-8'))
    assert sha(ROOT/'site-data.json')==inputs['siteDataSha256'],'M5 source changed'
    site=json.loads((ROOT/'site-data.json').read_text(encoding='utf-8'));native={f['id']:f for f in site['features']}
    for key in ['island','moat']:assert native[inputs[key+'SourceId']]['paths'][0]==inputs[key+'OutlineM5XY']
    for key in ['island','moat']:assert native[inputs[key+'SourceId']]['closed']
    for record in inputs['platforms']+inputs['internalWater']:assert native[record['sourceId']]['paths'][0]==record['outlineM5XY']
    for record in inputs['internalWater']:assert native[record['sourceId']]['closed'],'Open water-layer line is not a pool'
    for record in inputs['references']:assert sha((HERE/record['file']).resolve())==record['sha256']
    island_world=Polygon(inputs['islandOutlineM5XY']);outer_world=Polygon(inputs['moatOutlineM5XY'])
    internal_world=unary_union([Polygon(r['outlineM5XY']) for r in inputs['internalWater']])
    origin=np.array(inputs['originM5LocalXY']+[0.]);params=inputs['interpretedDimensions']
    local=lambda p:affinity.translate(p,-origin[0],-origin[1])
    island,outer,internal=map(local,[island_world,outer_world,internal_world])
    volume_internal=internal
    coping=island.difference(island.buffer(-params['bankWidth'],join_style='round'))
    ground=island.difference(unary_union([volume_internal,coping]))
    water=unary_union([outer.difference(island),volume_internal])
    dry_world=island_world.difference(internal_world)
    levels=json.loads((ROOT/'surface-layers.json').read_text(encoding='utf-8'))['renderLevels']
    gz,wz=levels['terrainZ'],levels['waterZ']
    pieces={'island_ground':polygon_mesh(ground,gz,-.9),'moat_bed':polygon_mesh(water,-1.,-1.3),
            'moat_water':polygon_mesh(water,wz),
            'concrete_coping':polygon_mesh(coping,gz+params['bankTopOffset'],-.8)}
    clip=trimesh.creation.box([180,180,40]);clip.apply_translation([0,0,gz+20])
    rocks=[]
    for record in inputs['interpretedRocks']:
        x,y=np.array(record['xyM5'])-origin[:2];sx,sy,h=record['size']
        assert dry_world.covers(Point(record['xyM5']).buffer(max(sx,sy)*1.2)),record
        rock=trimesh.creation.icosphere(subdivisions=2);v=rock.vertices
        factor=1+.12*np.sin(v[:,0]*4+record['seed'])*np.cos(v[:,1]*3-v[:,2]*2)
        rock.vertices=v*factor[:,None]*[sx,sy,h*.6];rock.apply_translation([x,y,gz+h*.4]);rocks.append(rock)
    pieces['rocks']=trimesh.boolean.intersection([union(rocks),clip],engine='manifold')
    paths,timber=[],[]
    for record in inputs['interpretedPosts']:
        x,y=np.array(record['xyM5'])-origin[:2]
        path=np.array([[x,y,gz],[x+.03,y-.02,gz+record['height']]])
        paths.append(path);timber.append(tube(path,params['climbingPostRadius'],16))
    for record in inputs['interpretedCrossLogs']:
        path=np.array(record['pointsM5XYZ'])-origin;paths.append(path);timber.append(tube(path,record['radius'],14))
    hollow=inputs['interpretedHollowLog'];ends=np.array(hollow['pointsM5XYZ'])-origin
    log=trimesh.creation.annulus(r_min=hollow['innerRadius'],r_max=hollow['outerRadius'],
        height=np.linalg.norm(ends[1]-ends[0]),sections=32)
    log.apply_transform(trimesh.geometry.align_vectors([0,0,1],ends[1]-ends[0]));log.apply_translation(ends.mean(axis=0))
    log=trimesh.boolean.intersection([log,clip],engine='manifold');timber.append(log);paths.append(ends)
    pieces['climbing_timber']=difference(union(timber),pieces['rocks'])
    platform_polygons=[]
    for record in inputs['platforms']:
        polygon=local(Polygon(record['outlineM5XY']));platform_polygons.append(polygon)
        top=record['interpretedDeckTopZ'];bottom=top-params['platformDeckThickness']
        deck=polygon_mesh(polygon,top,bottom);parts=[deck]
        for x,y in list(polygon.buffer(-.19,join_style='mitre').exterior.coords)[:-1]:
            post=trimesh.creation.box([params['platformPostWidth']]*2+[bottom-gz+.035])
            post.apply_translation([x,y,(bottom+gz)/2+.0175]);parts.append(post)
        pieces['platform_'+record['sourceId'].split(':')[1]]=union(parts)
    stair=inputs['interpretedStair'];a=np.array(stair['fromM5XY'])-origin[:2];b=np.array(stair['toM5XY'])-origin[:2]
    delta=b-a;length=np.linalg.norm(delta);direction=delta/length;normal=np.array([-direction[1],direction[0]])
    angle=math.atan2(direction[1],direction[0]);parts=[]
    for i in range(stair['steps']):
        t=(i+.5)/stair['steps'];top=gz+(stair['topZ']-gz)*(i+1)/stair['steps']
        board=trimesh.creation.box([length/stair['steps']+.025,stair['width'],.11])
        board.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,0,1]));board.apply_translation([*(a+delta*t),top-.055]);parts.append(board)
    for sign in [-1,1]:
        offset=normal*stair['width']*.35*sign
        parts.append(beam([*(a+offset),gz+.025],[*(b+offset),stair['topZ']-.08],.12,.16))
    platform_mask=polygon_mesh(unary_union(platform_polygons),10,-2)
    pieces['southern_stair']=difference(union(parts),platform_mask)
    ropes=[]
    for record in inputs['interpretedRopes']:
        a,b=np.array(record['fromM5XYZ'])-origin,np.array(record['toM5XYZ'])-origin
        points=[]
        for t in np.linspace(0,1,33):
            p=a+(b-a)*t;p[2]-=4*record['sag']*t*(1-t);points.append(p)
        assert island.covers(LineString(np.array(points)[:,:2]).buffer(params['ropeRadius']))
        ropes.append(tube(points,params['ropeRadius'],8))
    pieces['climbing_ropes']=difference(union(ropes),pieces['climbing_timber'],pieces['rocks'])
    # Only encoding/size derivatives of existing generated albedos are embedded.
    assets=ROOT/'viewer/assets';textures=HERE/'textures';textures.mkdir(exist_ok=True)
    asset_records={r['file']:r for r in json.loads((assets/'asset-manifest.json').read_text(encoding='utf-8'))['assets']}
    texture_records=[]
    mapping={'earth':'woodland-leaf-litter-v1.png','rocks':'penguin-artificial-rock-v1.png',
             'bark':'woodland-tree-bark-v1.png','boards':'savanna-platform-wood-v1.png'}
    for name,source in mapping.items():
        source=assets/source;assert sha(source)==asset_records[source.name]['sha256']
        with Image.open(source) as image:
            image=image.convert('RGB');image.thumbnail((512,512),Image.Resampling.LANCZOS)
            target=textures/(name+'.jpg');image.save(target,quality=90,subsampling=0,optimize=True)
            texture_records.append({'file':target.name,'sha256':sha(target),'bytes':target.stat().st_size,'size':list(image.size),
              'source':os.path.relpath(source,textures).replace('\\','/'),'sourceSha256':sha(source),
              'method':'RGB, max 512 px Lanczos, JPEG quality 90 4:4:4. No painting; generated albedo, not site photography.'})
    (textures/'manifest.json').write_text(json.dumps(texture_records,indent=2)+'\n',encoding='utf-8')
    mats={'earth':pbr('habes_dry_earth',[.96,.9,.72,1],textures/'earth.jpg'),
          'concrete':pbr('aged_concrete',[.49,.49,.42,1]),'water':pbr('preview_water',[.035,.4,.34,.78],roughness=.23),
          'rock':pbr('rough_rock',[.84,.86,.82,1],textures/'rocks.jpg'),
          'bark':pbr('weathered_poles',[.72,.68,.58,1],textures/'bark.jpg'),
          'boards':pbr('weathered_boards',[.72,.68,.58,1],textures/'boards.jpg'),
          'rope':pbr('natural_rope',[.56,.49,.32,1])}
    mats['water'].alphaMode='BLEND'
    scene=trimesh.Scene();checks={}
    for key,mesh in pieces.items():
        assert np.isfinite(mesh.vertices).all() and (mesh.area_faces>1e-12).all(),key
        if key!='moat_water':
            welded=mesh.copy();welded.merge_vertices(merge_tex=True,merge_norm=True)
            assert welded.is_watertight and welded.is_winding_consistent and welded.volume>0,key
            checks[key]={'watertight':True,'consistentWinding':True,'volumeM3':float(welded.volume)}
        material='earth' if key=='island_ground' else 'water' if key=='moat_water' else 'rock' if key=='rocks' else 'bark' if key=='climbing_timber' else 'rope' if key=='climbing_ropes' else 'boards' if key.startswith('platform_') or key=='southern_stair' else 'concrete'
        if material=='bark':mesh,uv=bark_uv(mesh,paths)
        else:uv=np.column_stack([mesh.vertices[:,0]/3,(mesh.vertices[:,1]+mesh.vertices[:,2])/3])
        mesh.visual=trimesh.visual.TextureVisuals(uv=uv if mats[material].baseColorTexture else None,material=mats[material])
        scene.add_geometry(mesh,node_name=key,geom_name=key)
    scene.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]))
    extras={'unit':'metre','originM5LocalXY':inputs['originM5LocalXY'],'sourceIds':[inputs['islandSourceId'],inputs['moatSourceId']]+[r['sourceId'] for r in inputs['platforms']+inputs['internalWater']],
            'sourceAssociation':'Historical M5 plus official 2021 photo/camera context; approximate','propDimensionsSurveyed':False}
    target=HERE/'habes-maymunu-adasi.glb'
    target.write_bytes(scene.export(file_type='glb',include_normals=True,tree_postprocessor=lambda tree:postprocess_gltf(tree,extras)))
    report={'schema':'bursa-zoo-habes-island/v1',**extras,'islandAreaM2':island_world.area,'outerMoatAreaM2':outer_world.area,
      'waterAreaM2':water.area,'internalWaterAreaM2':internal.area,'copingAreaM2':coping.area,'soilAreaM2':ground.area,
      'platformAreaM2':sum(p.area for p in platform_polygons),'triangles':sum(len(m.faces) for m in scene.geometry.values()),
      'glbBytes':target.stat().st_size,'solidChecks':checks,'interpretedPostCount':len(inputs['interpretedPosts']),
      'interpretedRopeCount':len(ropes),'interpretedRockCount':len(rocks),'candidatePlatformCount':len(platform_polygons),
      'atlasHiddenNodes':['island_ground','moat_bed','moat_water'],'interpretation':inputs['interpretation']}
    (HERE/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['islandAreaM2','waterAreaM2','platformAreaM2','triangles','glbBytes']}))

if __name__=='__main__':main()
