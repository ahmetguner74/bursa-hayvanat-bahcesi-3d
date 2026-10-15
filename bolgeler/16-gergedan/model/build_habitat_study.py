"""Editable first photographic habitat component, separate from atlas placement."""
from pathlib import Path
import hashlib,json,math,sys
import numpy as np
import trimesh
from PIL import Image
from shapely.geometry import Point,box,Polygon
from shapely.affinity import scale,translate

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'bolgeler'))
from model_tools import polygon_mesh,pbr,postprocess_gltf

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    texture_dir=HERE/'textures';texture_dir.mkdir(exist_ok=True)
    texture_specs=[('soil','penguin-pale-gravel-v1.png'),('rock','penguin-artificial-rock-v1.png'),('bark','woodland-tree-bark-v1.png')]
    texture_records=[]
    for name,source in texture_specs:
        original=ROOT/'viewer/assets'/source;target=texture_dir/(name+'.jpg')
        with Image.open(original) as image:
            image=image.convert('RGB');image.thumbnail((512,512),Image.Resampling.LANCZOS);image.save(target,quality=88,optimize=True,subsampling=0)
        texture_records.append({'file':target.name,'source':'viewer/assets/'+source,'sourceSha256':digest(original),'sha256':digest(target),'method':'512px RGB JPEG derivative of existing generated material; no zoo reference photo used as texture'})
    materials={
      'soil':pbr('compacted_sandy_soil',[.64,.54,.40,1],texture_dir/'soil.jpg'),
      'mud':pbr('damp_earth',[.22,.17,.105,1],texture_dir/'soil.jpg',roughness=.32),
      'rock':pbr('pale_boulders',[.70,.68,.59,1],texture_dir/'rock.jpg'),
      'bark':pbr('weathered_timber',[.36,.27,.17,1],texture_dir/'bark.jpg'),
      'wall':pbr('faded_red_retaining_wall',[.40,.17,.13,1],roughness=.97),
      'cap':pbr('concrete_wall_cap',[.56,.53,.46,1],roughness=.95),
    }
    full=box(-7,-5,7,5)
    outer=translate(scale(Point(0,0).buffer(1,quad_segs=32),2.8,1.7),-2.8,2.1)
    inner=translate(scale(Point(0,0).buffer(1,quad_segs=32),2.2,1.15),-2.8,2.1)
    wall=box(-6.4,4.2,-.2,4.52)
    dry=full.difference(outer).difference(wall)
    pieces={'dry_ground':(polygon_mesh(dry,0),'soil'),'wallow_floor':(polygon_mesh(inner,-.18),'mud')}
    outside=list(outer.exterior.coords)[:-1];inside=list(inner.exterior.coords)[:-1]
    vertices=[[x,y,z] for ring,z in [(outside,0),(inside,-.18)] for x,y in ring];faces=[];n=len(outside)
    for i in range(n):
        j=(i+1)%n;faces.extend([[i,j,n+j],[i,n+j,n+i]])
    ramp=trimesh.Trimesh(vertices,faces,process=True);ramp.fix_normals()
    if ramp.face_normals[:,2].mean()<0:ramp.invert()
    pieces['wallow_shallow_bank']=(ramp,'mud')
    pieces['retaining_wall']=(polygon_mesh(wall,.75,-.15),'wall')
    pieces['wall_cap']=(polygon_mesh(wall,.82,.75),'cap')
    posts=[];rails=[]
    for x in np.linspace(-6.5,6.5,8):
        post=trimesh.creation.box([.18,.18,1.45]);post.apply_translation([x,4.76,.725]);posts.append(post)
    for z in [.70,1.20]:
        rail=trimesh.creation.box([13.2,.14,.15]);rail.apply_translation([0,4.76,z]);rails.append(rail)
    pieces['timber_posts']=(trimesh.util.concatenate(posts),'bark')
    pieces['timber_rails']=(trimesh.util.concatenate(rails),'bark')
    rock_specs=[(4.7,2.8,1.12,.8,.66),(5.4,1.8,.9,.70,.55),(4.0,1.65,1.18,.74,.50),(5.9,3.4,.85,.71,.49),(3.5,3.3,.78,.62,.44)]
    rocks=[]
    for k,(x,y,sx,sy,h) in enumerate(rock_specs):
        rock=trimesh.creation.icosphere(subdivisions=2)
        v=rock.vertices;rock.vertices=v*(1+.11*np.sin(v[:,0]*4+k)*np.cos(v[:,1]*3))[:,None]*[sx,sy,h]
        rock.apply_translation([x,y,h*.58]);rocks.append(rock)
    pieces['boulders']=(trimesh.boolean.union(rocks,engine='manifold'),'rock')
    trunk=trimesh.creation.cylinder(radius=.20,height=4.4,sections=12);trunk.apply_translation([4.7,2.75,2.2]);pieces['tree_trunk_study']=(trunk,'bark')
    scene=trimesh.Scene();triangle_count=0
    for name,(mesh,kind) in pieces.items():
        uv=mesh.vertices[:,:2]*.65
        if kind=='bark':uv=np.column_stack((mesh.vertices[:,0]+mesh.vertices[:,1],mesh.vertices[:,2]*.6))
        mesh.visual=trimesh.visual.TextureVisuals(uv=uv,material=materials[kind])
        mesh.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]))
        scene.add_geometry(mesh,node_name=name,geom_name=name);triangle_count+=len(mesh.faces)
    evidence={'region':16,'scope':'Photo-based component study, not whole exhibit or measured reconstruction',
      'interpretation':'14x10m presentation patch; wall, rail, boulder, trunk and mud positions/dimensions are illustrative. Not added to M5 atlas.',
      'sources':[{'url':'https://www.bursahayvanatbahcesi.com/wp-content/uploads/2020/09/gergedan2.jpg','local':'../kaynaklar/fotograflar/resmi-site-2826.jpg','sha256':digest(HERE.parent/'kaynaklar/fotograflar/resmi-site-2826.jpg'),'date':'Upload 2020-09-29; capture date unverified','observed':'Sandy ground, pale boulders around tree, dark horizontal timber barrier, red/cream retaining edge'},
        {'url':'https://www.bursahayvanatbahcesi.com/wp-content/uploads/2022/09/kolaj-gergedan.jpg','observed':'Rhinos in shallow muddy area; does not establish its present boundary/location'}],
      'groundPartition':{'totalM2':full.area,'dryM2':dry.area,'mudM2':inner.area,'bankM2':outer.difference(inner).area,'wallM2':wall.area,
         'overlapM2':dry.intersection(outer).area,'uncoveredM2':full.difference(dry.union(outer).union(wall)).area},
      'unit':'metre','coordinates':'Local prototype XYZ Z-up, exported glTF Y-up; no claimed M5 placement',
      'textures':texture_records,'triangles':triangle_count,'meshes':len(pieces),
      'status':'First local habitat component; current entire boundary, stable and mud position remain unverified'}
    result=scene.export(file_type='glb',tree_postprocessor=lambda tree:postprocess_gltf(tree,evidence));path=HERE/'rhino-habitat-study.glb';path.write_bytes(result)
    evidence.update(file=path.name,bytes=len(result),sha256=digest(path))
    (HERE/'model-report.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert evidence['groundPartition']['overlapM2']==0 and evidence['groundPartition']['uncoveredM2']<1e-7
    print(json.dumps({key:evidence[key] for key in ['file','bytes','triangles','meshes','groundPartition']}))

if __name__=='__main__':main()
