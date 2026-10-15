"""Editable first interpretation of the cafe's native M5 roofs and gazebos.

Footprints are native data; roof form, timber work, openings and levels are
historical-photo estimates, not a current survey or construction design.
"""
from pathlib import Path
import hashlib,json,math,sys
import numpy as np
import trimesh
from shapely import constrained_delaunay_triangles,voronoi_polygons
from shapely.geometry import Polygon,Point,MultiPoint
from shapely.geometry.polygon import orient
from shapely.ops import unary_union,nearest_points

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'bolgeler'))
from model_tools import pbr,polygon_mesh,postprocess_gltf


def roof_solid(polygon,eave,bottom,slope,max_rise,seeds=None):
    """Offset rings give a continuous hipped upper surface and one flat soffit.

    Shared strip vertices are welded. There are no stacked flat roof caps.
    A fine inward mitred offset allows the irregular native cafe outline to
    develop several ridges without stretching it into a guessed rectangle.
    """
    cells=[polygon] if not seeds else [cell.intersection(polygon) for cell in voronoi_polygons(MultiPoint(seeds),extend_to=polygon.envelope.buffer(5)).geoms]
    vertices=[];faces=[]
    for cell in cells:
        if cell.is_empty:continue
        current=cell;distance=0.
        while not current.is_empty:
            distance+=.2
            inner=cell.buffer(-distance,join_style=2)
            strip=current.difference(inner)
            for triangle in constrained_delaunay_triangles(strip).geoms:
                points=list(orient(triangle,1).exterior.coords)[:3]
                start=len(vertices)
                vertices.extend([[x,y,eave+min(max_rise,cell.boundary.distance(Point(x,y))*slope)] for x,y in points])
                faces.append([start,start+1,start+2])
            if inner.is_empty:break
            current=inner
    upper=trimesh.Trimesh(vertices,faces,process=True)
    boundary=upper.edges_unique[np.bincount(upper.edges_unique_inverse)==1]
    assert all(polygon.boundary.distance(Point(*upper.vertices[i,:2]))<1e-6 for edge in boundary for i in edge),'Internal roof seam'
    count=len(upper.vertices);vertices=np.vstack([upper.vertices,upper.vertices.copy()]);vertices[count:,2]=bottom
    faces=list(upper.faces)+[list(reversed(face+count)) for face in upper.faces]
    directed={tuple(sorted(edge)):edge for face in upper.faces for edge in zip(face,np.roll(face,-1))}
    for edge in boundary:
        a,b=directed[tuple(edge)]
        faces.extend([[b,a,a+count],[b,a+count,b+count]])
    mesh=trimesh.Trimesh(vertices,faces,process=True)
    if mesh.volume<0:mesh.invert()
    return mesh


def textured(mesh,material,scale=1.,wood=False):
    """Face-local UV seams with metric scale; avoid stretched box projection."""
    vertices=[];uv=[]
    for triangle,normal in zip(mesh.triangles,mesh.face_normals):
        axis=int(np.argmax(np.abs(normal)))
        coordinates=triangle[:,[0,1] if axis==2 else [1,2] if axis==0 else [0,2]]
        if wood and axis!=2:coordinates=coordinates[:,::-1]
        vertices.extend(triangle);uv.extend(coordinates/scale)
    result=trimesh.Trimesh(vertices,np.arange(len(vertices)).reshape(-1,3),process=False)
    result.visual=trimesh.visual.TextureVisuals(uv=np.array(uv),material=material)
    return result


def main():
    inputs=json.loads((HERE/'model-inputs.json').read_text(encoding='utf-8'))
    site_path=ROOT/'site-data.json'
    assert hashlib.sha256(site_path.read_bytes()).hexdigest()==inputs['siteDataSha256']
    site=json.loads(site_path.read_text(encoding='utf-8'));features={f['id']:f for f in site['features']}
    for record in inputs['references']:
        assert hashlib.sha256((HERE/record['file']).read_bytes()).hexdigest()==record['sha256']
    origin=np.array(inputs['originM5LocalXY']);p=inputs['interpretedDimensionsMetres']
    native=[Polygon(item['outlineM5XY']) for item in inputs['roofs']]
    for item in inputs['roofs']:assert features[item['sourceId']]['paths'][0]==item['outlineM5XY']
    # M5 152/153 have a 0.000716 m2 sub-millimetre overlap. The source remains
    # untouched; the latter roof is clipped to its one exclusive render owner.
    owned=[];occupied=Polygon()
    for polygon in native:
        clipped=polygon.difference(occupied);assert clipped.geom_type=='Polygon'
        owned.append(orient(clipped,1));occupied=unary_union([occupied,polygon])
    local=[Polygon(np.array(poly.exterior.coords)-origin) for poly in owned]
    floor_mask=unary_union(local)
    assets=HERE/'textures'
    materials={
        'roof':pbr('cafe_warm_weathered_roof',[.87,.75,.55,1],assets/'afrika-koyu-roof-shingles-v1.jpg'),
        'timber':pbr('cafe_dark_timber',[.36,.29,.2,1],assets/'savanna-platform-wood-v1.jpg'),
        'floor':pbr('cafe_stone_paving',[.8,.76,.65,1],assets/'woodland-stone-path-v1.jpg'),
    }
    scene=trimesh.Scene();checks={};projection_delta=0.;post_count=0
    def add(name,mesh,material,scale=1.,wood=False):
        nonlocal checks
        assert np.isfinite(mesh.vertices).all() and (mesh.area_faces>1e-11).all(),name
        welded=mesh.copy();welded.merge_vertices(merge_tex=True,merge_norm=True)
        assert welded.is_watertight and welded.is_winding_consistent and welded.volume>0,name
        checks[name]={'watertight':True,'consistentWinding':True,'volumeM3':float(welded.volume)}
        scene.add_geometry(textured(mesh,materials[material],scale,wood),node_name=name,geom_name=name)
    floor_parts=[floor_mask] if floor_mask.geom_type=='Polygon' else list(floor_mask.geoms)
    # Two native pads meet only at a corner. Keep each connected floor solid
    # separate so welding that zero-area contact cannot create a four-face edge.
    for index,part in enumerate(floor_parts):
        add(f'cafe_floor_{index:02d}',polygon_mesh(part,p['floorZ'],p['floorBottomZ']),'floor',2.)
    for item,polygon in zip(inputs['roofs'],local):
        main_building=item['type']=='building';eave=p['mainEaveZ'] if main_building else p['canopyEaveZ'];soffit=eave-p['roofEdgeDepth']
        name=item['sourceId'].replace(':','_')
        seeds=item.get('interpretedRoofSeedsM5XY')
        roof=roof_solid(polygon,eave,soffit,p['roofSlope'],p['maximumRoofRise'],(np.array(seeds)-origin).tolist() if seeds else None)
        projected=unary_union([Polygon(roof.vertices[f,:2]) for f,n in zip(roof.faces,roof.face_normals) if n[2]>1e-6])
        delta=projected.symmetric_difference(polygon).area;assert delta<1e-7,(name,delta)
        projection_delta+=delta;add(name+'_roof',roof,'roof',1.4)
        if main_building:
            wall_outline=polygon.buffer(-p['wallInset'],join_style=2)
            wall_ring=wall_outline.difference(wall_outline.buffer(-p['wallThickness'],join_style=2))
            wall=polygon_mesh(wall_ring,soffit,p['floorZ']);frames=[];cuts=[]
            edges=[(np.array(a),np.array(b)) for a,b in zip(wall_outline.exterior.coords,list(wall_outline.exterior.coords)[1:]) if math.dist(a,b)>3.]
            edges=sorted(edges,key=lambda edge:(edge[0][1]+edge[1][1])/2)[:2]
            for index,(a,b) in enumerate(edges):
                length=np.linalg.norm(b-a);axis=(b-a)/length;centre=(a+b)/2;angle=math.atan2(axis[1],axis[0])
                width=min(2.0,length-.8);height=2.18 if index==0 else 1.32;base=p['floorZ'] if index==0 else .82
                cut=trimesh.creation.box([width,.9,height]);cut.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,0,1]));cut.apply_translation([*centre,base+height/2]);cuts.append(cut)
                for along,z,w,h in [(-width/2-.04,base+height/2,.08,height),(width/2+.04,base+height/2,.08,height),(0,base+height+.04,width+.16,.08)]+([] if index==0 else [(0,base-.04,width+.16,.08)]):
                    frame=trimesh.creation.box([w,.12,h]);frame.apply_transform(trimesh.transformations.rotation_matrix(angle,[0,0,1]));frame.apply_translation([*(centre+axis*along),z]);frames.append(frame)
            wall=trimesh.boolean.difference([wall,*cuts],engine='manifold')
            wall=trimesh.boolean.union([wall,*frames],engine='manifold')
            # The boolean's Float32 corner contacts can leave collapsed frame
            # triangles. Weld at1 micrometre and remove only collapsed faces;
            # the closed-solid assertion below still has to pass.
            wall.merge_vertices(digits_vertex=6)
            wall.update_faces(wall.nondegenerate_faces(height=1e-7));wall.remove_unreferenced_vertices()
            add(name+'_walls_with_openings',wall,'timber',1.6,True)
        else:
            beam_outer=polygon.buffer(-p['postInset']+.08,join_style=2)
            beam_inner=polygon.buffer(-p['postInset']-.08,join_style=2)
            beam_bottom=soffit-p['beamDepth']
            beam=polygon_mesh(beam_outer.difference(beam_inner),soffit,beam_bottom)
            points=[];inner=polygon.buffer(-p['postInset'],join_style=2)
            ring=list(polygon.exterior.coords)[:-1]
            for i,xy in enumerate(ring):
                a=np.array(ring[i-1]);b=np.array(xy);c=np.array(ring[(i+1)%len(ring)])
                incoming=b-a;outgoing=c-b
                if incoming[0]*outgoing[1]-incoming[1]*outgoing[0]<=0:continue
                target=nearest_points(Point(xy),inner.boundary)[1]
                if all(target.distance(other)>.55 for other in points):points.append(target)
            supports=[]
            for point in points:
                post=trimesh.creation.box([p['postWidth'],p['postWidth'],beam_bottom-p['floorZ']]);post.apply_translation([point.x,point.y,(beam_bottom+p['floorZ'])/2]);supports.append(post)
            post_count+=len(supports)
            add(name+'_posts',trimesh.util.concatenate(supports),'timber',1.6,True)
            add(name+'_eave_beams',beam,'timber',1.6,True)
    scene.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]))
    extras={'unit':'metre','originM5LocalXY':inputs['originM5LocalXY'],'sourceIds':[item['sourceId'] for item in inputs['roofs']],
        'dimensionsSurveyed':False,'sourceAssociation':'Cafe anchor and historical opening photos; approximate'}
    glb=scene.export(file_type='glb',include_normals=True,tree_postprocessor=lambda tree:postprocess_gltf(tree,extras))
    (HERE/'afrika-kafe.glb').write_bytes(glb)
    report={'schema':'bursa-zoo-african-cafe/v1',**extras,'roofCount':len(native),'postCount':post_count,
        'nativeRoofAreaM2':sum(poly.area for poly in native),'exclusiveFloorAreaM2':floor_mask.area,
        'nativeRoofOverlapRemovedM2':sum(poly.area for poly in native)-floor_mask.area,
        'roofProjectionSymmetricDifferenceM2':projection_delta,'triangles':sum(len(m.faces) for m in scene.geometry.values()),
        'glbBytes':len(glb),'solidChecks':checks,'interpretation':inputs['interpretation'],
        'meshOwnership':'One unioned floor replaces underlying terrain/path. Six exclusive roof solids, open timber gazebos, real wall openings. Structural contacts are intentional; native M5/QGIS data remain untouched.'}
    (HERE/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:report[key] for key in ['roofCount','postCount','exclusiveFloorAreaM2','triangles','glbBytes']}))


if __name__=='__main__':main()
