"""Seven native circular eaves; hut walls and tiered roofs are photo estimates."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[2]
sys.path.insert(0,str(PROJECT/'bolgeler'))
from model_tools import pbr, polygon_mesh, postprocess_gltf


def tiered_roof(outline, centre, radius, dimensions):
    """One closed stepped shell. The lowest eave retains every M5 vertex.

    Invented upper courses use90 segments; the two native1080-point eave rings
    retain the source footprint. Zipper triangles connect unequal ring sizes.
    """
    points=np.array(Polygon(outline).exterior.coords[:-1],dtype=float)
    angles=np.mod(np.arctan2(points[:,1]-centre[1],points[:,0]-centre[0]),2*math.pi)
    points=points[np.argsort(angles)];start=float(np.min(angles))
    bottom,eave=dimensions['roofBottomZ'],dimensions['eaveZ']
    rings=[np.column_stack((points,np.full(len(points),bottom))),
           np.column_stack((points,np.full(len(points),eave)))]
    course_specs=[]
    for k in range(1,6):
        r=1-k*.165;z=eave+k*.32
        course_specs.extend([(r,z),(r+.022,z),(r+.022,z+.07)])
    course_specs.extend([(.075,eave+1.86),(.022,eave+2.43)])
    a=start+np.arange(90)*2*math.pi/90
    for r,z in course_specs:
        rings.append(np.column_stack((centre[0]+radius*r*np.cos(a),centre[1]+radius*r*np.sin(a),np.full(90,z))))
    vertices=[];offsets=[];faces=[]
    for ring in rings:
        offsets.append(len(vertices));vertices.extend(ring)
    for index,(lower,upper) in enumerate(zip(rings,rings[1:])):
        n,m=len(lower),len(upper);i=j=0;lo,hi=offsets[index:index+2]
        while i<n or j<m:
            if j==m or (i<n and (i+1)/n <= (j+1)/m):
                faces.append([lo+i%n,lo+(i+1)%n,hi+j%m]);i+=1
            else:
                faces.append([lo+i%n,hi+(j+1)%m,hi+j%m]);j+=1
    bottom_index=len(vertices);vertices.append([*centre,bottom])
    for k in range(len(rings[0])):
        faces.append([bottom_index,(k+1)%len(rings[0]),k])
    top_index=len(vertices);vertices.append([*centre,eave+2.65])
    off=offsets[-1]
    for k in range(90):faces.append([off+k,off+(k+1)%90,top_index])
    mesh=trimesh.Trimesh(vertices,faces,process=True)
    # UV seams are split per triangle; U follows the circumference and V the
    # roof slope. Courses in the generated image stay horizontal around each hut.
    xyz,uv=[],[]
    for triangle in mesh.triangles:
        relative=triangle[:,:2]-centre
        u=np.mod(np.arctan2(relative[:,1],relative[:,0])-start,2*math.pi)/(2*math.pi)
        if np.ptp(u)>.5:u[u<.5]+=1
        xyz.extend(triangle)
        uv.extend(np.column_stack((u*2*math.pi*radius,(triangle[:,2]-eave)*1.45)))
    output=trimesh.Trimesh(xyz,np.arange(len(xyz)).reshape(-1,3),process=False)
    return output,np.array(uv)


def main():
    inputs=json.loads((HERE/'model-inputs.json').read_text(encoding='utf-8'))
    path=PROJECT/'site-data.json'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=inputs['siteDataSha256']:
        raise ValueError('M5 source changed; review the seven canopy circles')
    photo=(HERE/inputs['sourcePhoto']).resolve()
    if hashlib.sha256(photo.read_bytes()).hexdigest()!=inputs['sourcePhotoSha256']:
        raise ValueError('Historical source image changed')
    document=(HERE/inputs['sourceDocument']).resolve()
    if hashlib.sha256(document.read_bytes()).hexdigest()!=inputs['sourceDocumentSha256']:
        raise ValueError('Municipal source report changed')
    site=json.loads(path.read_text(encoding='utf-8'));features={f['id']:f for f in site['features']}
    origin=np.array(inputs['originM5LocalXY']+[0.]);p=inputs['interpretedDimensionsMetres']
    mats={
        'roof':pbr('weathered_brown_grey_shingles',[.85,.8,.72,1.],PROJECT/'viewer/assets/afrika-koyu-roof-shingles-v1.png'),
        'walls':pbr('warm_white_plaster',[.79,.8,.73,1.]),
        'floor':pbr('concrete_threshold',[.31,.32,.27,1.]),
        'frame':pbr('dark_green_door_frame',[.055,.075,.045,1.],roughness=.8),
    }
    scene=trimesh.Scene();checks={};roof_areas=[];projection_deltas=[]
    for hut in inputs['huts']:
        sid=hut['sourceId']
        if features[sid]['paths'][0]!=hut['eaveOutlineM5XY']:
            raise ValueError('Native eave changed: '+sid)
        centre=np.array(hut['centreM5XY'])-origin[:2]
        outline=np.array(hut['eaveOutlineM5XY'])-origin[:2]
        wall=Polygon(np.array(hut['wallOutlineM5XY'])-origin[:2])
        ring=wall.difference(wall.buffer(-p['wallThickness'],join_style=2))
        wall_mesh=polygon_mesh(ring,p['roofBottomZ'],p['floorZ'])
        angle=math.radians(hut['interpretedDoorFacingDegrees'])
        normal=np.array([math.cos(angle),math.sin(angle)])
        apothem=hut['wallCircumradiusMetres']*math.cos(math.pi/8)
        door_xy=centre+normal*apothem
        door=trimesh.creation.box(extents=[p['wallThickness']+.5,p['doorWidth'],p['doorHeight']])
        door.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,0,1]))
        door.apply_translation([*door_xy,p['floorZ']+p['doorHeight']/2])
        wall_mesh=trimesh.boolean.difference([wall_mesh,door],engine='manifold')
        floor=polygon_mesh(wall,p['floorZ'],-.46)
        frames=[]
        tangent=np.array([-normal[1],normal[0]])
        for sign in [-1,1]:
            post=trimesh.creation.box(extents=[.07,.07,p['doorHeight']+.055])
            post.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,0,1]))
            post.apply_translation([*(door_xy+normal*.035+tangent*sign*(p['doorWidth']/2+.035)),p['floorZ']+(p['doorHeight']+.055)/2]);frames.append(post)
        lintel=trimesh.creation.box(extents=[.07,p['doorWidth']+.12,.07])
        lintel.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,0,1]))
        lintel.apply_translation([*(door_xy+normal*.035),p['floorZ']+p['doorHeight']+.035]);frames.append(lintel)
        frame=trimesh.boolean.union(frames,engine='manifold')
        roof,uv=tiered_roof(outline,centre,hut['roofRadiusMetres'],p)
        parts={'roof':roof,'walls':wall_mesh,'floor':floor,'frame':frame}
        for key,mesh in parts.items():
            welded=mesh.copy();welded.merge_vertices(merge_tex=True,merge_norm=True)
            if not np.isfinite(mesh.vertices).all() or (mesh.area_faces<=1e-12).any():
                raise ValueError('Non-finite/degenerate '+sid+'/'+key)
            if not welded.is_watertight or not welded.is_winding_consistent or welded.volume<=0:
                raise ValueError('Open/inverted '+sid+'/'+key)
            node=sid.replace(':','_')+'_'+key
            checks[node]={'watertight':True,'consistentWinding':True,'volumeM3':float(welded.volume)}
            mesh.visual=trimesh.visual.TextureVisuals(uv=uv if key=='roof' else None,material=mats[key])
            scene.add_geometry(mesh,node_name=node,geom_name=node)
        # All native eave points survive in the GLB, including their original
        # non-circular rounding. Check the actual roof's projected upper faces.
        projected=unary_union([Polygon(roof.vertices[f,:2]) for f,n in zip(roof.faces,roof.face_normals) if n[2]>1e-5])
        delta=projected.symmetric_difference(Polygon(outline)).area
        if delta>1e-8:raise ValueError('Roof projection changed: '+sid)
        projection_deltas.append(delta);roof_areas.append(Polygon(outline).area)
    scene.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]))
    extras={'unit':'metre','originM5LocalXY':inputs['originM5LocalXY'],
        'sourceIds':[h['sourceId'] for h in inputs['huts']],
        'sourceAssociation':'native circle row / historical photograph, approximate',
        'sourcePhoto':inputs['sourcePhoto'],'dimensionsSurveyed':False}
    (HERE/'afrika-koyu.glb').write_bytes(scene.export(file_type='glb',include_normals=True,
        tree_postprocessor=lambda tree:postprocess_gltf(tree,extras)))
    report={'schema':'bursa-zoo-african-village/v1',**extras,
        'hutCount':len(inputs['huts']),'nativeEaveAreaM2':sum(roof_areas),
        'roofProjectionSymmetricDifferenceM2':sum(projection_deltas),
        'triangles':sum(len(m.faces) for m in scene.geometry.values()),'solidChecks':checks,
        'interpretedFloorAreaM2':sum(Polygon(h['wallOutlineM5XY']).area for h in inputs['huts']),
        'meshOwnership':'One closed stepped shell per roof. Wall doors are true cut openings; walls start at the sole floor top, with no shared volume. Interpreted wall footprints replace terrain/path through the shared partition.',
        'interpretation':inputs['interpretation']}
    (HERE/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['hutCount','nativeEaveAreaM2','triangles']}))


if __name__=='__main__':main()
