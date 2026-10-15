"""Native candidate pond and an editable photographic interpretation of its bank."""
from __future__ import annotations
import hashlib,json,math,os,sys
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image
from shapely import affinity,set_precision,from_wkb
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'bolgeler'))
from model_tools import polygon_mesh,pbr,postprocess_gltf
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def parts(geometry):return [geometry] if geometry.geom_type=='Polygon' else list(geometry.geoms)
def colour(hex_value):
    rgb=np.array([int(hex_value[i:i+2],16)/255 for i in [1,3,5]])
    return np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4).tolist()
def surface_uv(mesh,scale):
    # Face charts preserve independent UVs at rock/concrete projection seams.
    triangles=mesh.triangles;uv=[]
    for triangle,normal in zip(triangles,mesh.face_normals):
        axes=[[1,2],[0,2],[0,1]][np.abs(normal).argmax()]
        uv.extend(triangle[:,axes]*scale)
    result=trimesh.Trimesh(triangles.reshape(-1,3),np.arange(len(triangles)*3).reshape(-1,3),process=False)
    result.vertex_normals=mesh.vertex_normals[mesh.faces].reshape(-1,3)
    return result,np.array(uv)

def main():
    inputs=read(HERE/'model-inputs.json');assert sha(ROOT/'site-data.json')==inputs['siteDataSha256']
    site=read(ROOT/'site-data.json');native=next(f for f in site['features'] if f['id']==inputs['poolSourceId'])
    assert native['closed'] and native['role']=='water' and native['paths'][0]==inputs['poolOutlineM5XY']
    for rec in inputs['references']:assert sha((HERE/rec['file']).resolve())==rec['sha256']
    origin=np.array(inputs['originM5LocalXY']+[0.]);local=lambda p:affinity.translate(p,-origin[0],-origin[1])
    pool_world=Polygon(inputs['poolOutlineM5XY']);pool=local(pool_world)
    bank_world=unary_union([Polygon(p['outer'],p['holes']) for p in inputs['interpretedBankMaskM5XY']])
    ground_world=unary_union([Polygon(p['outer'],p['holes']) for p in inputs['previewGroundMaskM5XY']])
    bank,ground=map(local,[bank_world,ground_world]);params=inputs['interpretedDimensions']
    # Only the derived preview ground is normalised. The native pond is untouched.
    # Overlay intersections contain near-duplicate corners that triangulate to zero.
    ground_original=ground
    ground=from_wkb(set_precision(ground,1e-6).wkb)
    ground_delta=ground.symmetric_difference(ground_original).area
    # A zero-area spike can be longer than the precision grid. Bound its area,
    # and report its displacement instead of claiming a native footprint move.
    ground_hausdorff=ground.hausdorff_distance(ground_original)
    assert ground_delta<.001
    levels=read(ROOT/'surface-layers.json')['renderLevels'];gz,wz=levels['terrainZ'],levels['waterZ']
    pieces={'pool_bed':polygon_mesh(pool,params['bedTopZ'],params['bedBottomZ']),
            'pool_water':polygon_mesh(pool,wz)}
    hidden=['pool_bed','pool_water']
    for index,polygon in enumerate(parts(bank)):
        pieces[f'concrete_bank_{index:02d}']=polygon_mesh(polygon,gz+params['bankTopOffset'],params['bankBottomZ'])
    for index,polygon in enumerate(parts(ground)):
        name=f'preview_ground_{index:02d}';pieces[name]=polygon_mesh(polygon,gz,gz-.5);hidden.append(name)
    rocks=[]
    ground_clip=trimesh.creation.box([200,200,40]);ground_clip.apply_translation([0,0,gz+20])
    for rec in inputs['interpretedRocks']:
        sx,sy,h=rec['size'];x,y=np.array(rec['xyM5'])-origin[:2]
        assert ground_world.covers(Point(rec['xyM5']).buffer(sx*1.35)),rec
        rock=trimesh.creation.icosphere(subdivisions=2);v=rock.vertices
        factor=1+.15*np.sin(v[:,0]*3.5+rec['seed'])*np.cos(v[:,1]*3-v[:,2]*2.3)
        rock.vertices=v*factor[:,None]*[sx,sy,h*.72]
        cut=trimesh.creation.box([sx*1.65,sy*1.72,h*1.10]);cut.apply_translation([sx*.1,-sy*.04,h*.08])
        rock=trimesh.boolean.intersection([rock,cut],engine='manifold')
        rock.apply_transform(trimesh.transformations.rotation_matrix(rec['angle'],[0,0,1]));rock.apply_translation([x,y,gz+h*.44])
        rocks.append(rock)
    pieces['rock_bank']=trimesh.boolean.intersection([trimesh.boolean.union(rocks,engine='manifold'),ground_clip],engine='manifold')
    assets=ROOT/'viewer/assets';textures=HERE/'textures';textures.mkdir(exist_ok=True)
    records={r['file']:r for r in read(assets/'asset-manifest.json')['assets']};texture_records=[]
    for label,source_name,alpha in [('meadow','woodland-meadow-v1.png',False),('rocks','penguin-artificial-rock-v1.png',False),('plants','woodland-grass-tussock-v1.png',True)]:
        source=assets/source_name;assert sha(source)==records[source_name]['sha256']
        with Image.open(source) as image:
            image=image.convert('RGBA' if alpha else 'RGB');image.thumbnail((512,512),Image.Resampling.LANCZOS)
            target=textures/(label+('.png' if alpha else '.jpg'))
            if alpha:image.save(target,optimize=True)
            else:image.save(target,quality=90,subsampling=0,optimize=True)
            texture_records.append({'file':target.name,'sha256':sha(target),'size':list(image.size),'mode':image.mode,
              'bytes':target.stat().st_size,'source':os.path.relpath(source,textures).replace('\\','/'),'sourceSha256':sha(source),
              'method':'Max512px Lanczos, preserve alpha in PNG or RGB JPEG90 4:4:4; no painting or source-photo texture.'})
    (textures/'manifest.json').write_text(json.dumps(texture_records,indent=2)+'\n',encoding='utf-8')
    plant_vertices=[];plant_faces=[];plant_uv=[]
    for rec in inputs['interpretedPlants']:
        x,y=np.array(rec['xyM5'])-origin[:2];height,width=rec['height'],rec['width']
        assert ground_world.covers(Point(rec['xyM5']).buffer(.5))
        for angle in [rec['seed']*.73+k*math.pi/3 for k in range(3)]:
            along=np.array([math.cos(angle),math.sin(angle)])*width*.5
            low,high=gz-height*.051,gz+height*.949
            start=len(plant_vertices)
            plant_vertices.extend([[x-along[0],y-along[1],low],[x+along[0],y+along[1],low],
                                   [x+along[0],y+along[1],high],[x-along[0],y-along[1],high]])
            plant_faces.extend([[start,start+1,start+2],[start,start+2,start+3]])
            plant_uv.extend([[0,0],[1,0],[1,1],[0,1]])
    pieces['bank_plants']=trimesh.Trimesh(plant_vertices,plant_faces,process=False)
    mats={'ground':pbr('preview_meadow',[.90,.94,.78,1],textures/'meadow.jpg'),
          'concrete':pbr('weathered_concrete',[.45,.46,.39,1]),
          'rocks':pbr('rough_bank_rock',[.81,.80,.73,1],textures/'rocks.jpg'),
          'plants':pbr('bank_grass',[.92,.98,.82,1],textures/'plants.png'),
          'water':pbr('illustrative_olive_water',colour(inputs['waterPresentationColor'])+[.86],roughness=.28)}
    mats['plants'].alphaMode='MASK';mats['plants'].alphaCutoff=.45;mats['plants'].doubleSided=True
    mats['water'].alphaMode='BLEND'
    scene=trimesh.Scene();checks={}
    for name,mesh in pieces.items():
        assert np.isfinite(mesh.vertices).all() and (mesh.area_faces>1e-12).all(),name
        if name not in ['pool_water','bank_plants']:
            welded=mesh.copy();welded.merge_vertices(merge_tex=True,merge_norm=True)
            assert welded.is_watertight and welded.is_winding_consistent and welded.volume>0,name
            checks[name]={'watertight':True,'consistentWinding':True,'volumeM3':float(welded.volume)}
        material='ground' if name.startswith('preview_ground') else 'rocks' if name=='rock_bank' else 'plants' if name=='bank_plants' else 'water' if name=='pool_water' else 'concrete'
        if name=='bank_plants':uv=np.array(plant_uv)
        else:mesh,uv=surface_uv(mesh,.2 if material=='ground' else .65)
        mesh.visual=trimesh.visual.TextureVisuals(uv=uv if mats[material].baseColorTexture else None,material=mats[material])
        scene.add_geometry(mesh,node_name=name,geom_name=name)
    scene.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]))
    extras={'unit':'metre','originM5LocalXY':inputs['originM5LocalXY'],'sourceIds':[inputs['poolSourceId']],
      'sourceAssociation':'Candidate region29 pond; precise28/29 physical scope unverified','propDimensionsSurveyed':False}
    target=HERE/'boz-ayi-havuz-kiyisi.glb'
    target.write_bytes(scene.export(file_type='glb',include_normals=True,tree_postprocessor=lambda tree:postprocess_gltf(tree,extras)))
    report={'schema':'bursa-zoo-bear-pool/v1',**extras,'nativePoolAreaM2':pool_world.area,'interpretedBankAreaM2':bank_world.area,
      'previewGroundAreaM2':ground_world.area,'previewGroundNormalisationGridM':1e-6,'previewGroundNormalisationDeltaM2':ground_delta,
      'previewGroundCollapsedSliverExtentM':ground_hausdorff,
      'interpretedRockCount':len(rocks),'interpretedPlantCount':len(inputs['interpretedPlants']),
      'triangles':sum(len(m.faces) for m in scene.geometry.values()),'glbBytes':target.stat().st_size,'solidChecks':checks,
      'atlasHiddenNodes':hidden,'interpretation':inputs['interpretation']}
    (HERE/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['nativePoolAreaM2','interpretedBankAreaM2','triangles','glbBytes','interpretedRockCount']}))

if __name__=='__main__':main()
