"""Editable interpretation of the timber structure in municipal photo 8895.

The old M5 canopy is a candidate location, not a confirmed as-built match.
Roof footprint coordinates are retained; visible details are photo estimates.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image
from shapely import constrained_delaunay_triangles
from shapely.geometry import LineString, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import split
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[2]


def material(name,color,texture=None):
    return trimesh.visual.material.PBRMaterial(name=name,baseColorFactor=np.array(color,dtype=float),
        baseColorTexture=Image.open(texture) if texture and texture.is_file() else None,
        roughnessFactor=.88,metallicFactor=.0)


def main():
    inputs=json.loads((HERE/'model-inputs.json').read_text(encoding='utf-8'))
    site_path=PROJECT/'site-data.json'
    if hashlib.sha256(site_path.read_bytes()).hexdigest()!=inputs['siteDataSha256']:
        raise ValueError('M5 changed: review candidate canopy and footprint')
    site=json.loads(site_path.read_text(encoding='utf-8'))
    source=next(x for x in site['features'] if x['id']==inputs['sourceId'])
    if source['paths'][0]!=inputs['roofOutlineM5XY']:
        raise ValueError('Native canopy coordinates changed')
    origin=np.array(inputs['originM5LocalXY']+[0.])
    angle=math.radians(inputs['localXAxisDegrees'])
    u=np.array([math.cos(angle),math.sin(angle)])
    v=np.array([-u[1],u[0]])
    points=np.array(inputs['roofOutlineM5XY'])-origin[:2]
    roof=orient(Polygon(np.column_stack((points@u,points@v))),1)
    x0,y0,x1,y1=roof.bounds
    ridge_x=(x0+x1)/2
    params=inputs['interpretedDimensionsMetres']
    ground,deck,eave,ridge=params['groundZ'],params['deckZ'],params['eaveZ'],params['ridgeZ']
    half=(x1-x0)/2
    ridge_line=LineString([(ridge_x,y0-1),(ridge_x,y1+1)])
    halves=split(roof,ridge_line)
    texture=PROJECT/'viewer/assets/savanna-platform-wood-v1.png'
    mats={
        'timber':material('weathered_warm_timber',[.64,.46,.31,1.],texture),
        'deck':material('timber_deck',[.86,.72,.51,1.],texture),
        'roof':material('dark_weathered_roof',[.105,.14,.115,1.],texture),
        'metal':trimesh.visual.material.PBRMaterial(name='galvanized_feeder',baseColorFactor=np.array([.37,.42,.39,1.]),roughnessFactor=.65,metallicFactor=.35),
    }
    pieces={key:[] for key in mats}
    def add(mesh,key):
        pieces[key].append(mesh)
    def box(name,centre,extent,key='timber'):
        mesh=trimesh.creation.box(extents=extent)
        mesh.apply_translation(centre);mesh.metadata['part']=name;add(mesh,key)
    def beam(name,a,b,width=.15,depth=.15,key='timber'):
        a,b=np.array(a),np.array(b);delta=b-a
        mesh=trimesh.creation.box(extents=[width,depth,np.linalg.norm(delta)])
        mesh.apply_transform(trimesh.geometry.align_vectors([0,0,1],delta))
        mesh.apply_translation((a+b)/2);mesh.metadata['part']=name;add(mesh,key)
    def cylinder(a,b,r=.015):
        a,b=np.array(a),np.array(b);delta=b-a
        mesh=trimesh.creation.cylinder(radius=r,height=np.linalg.norm(delta),sections=6)
        mesh.apply_transform(trimesh.geometry.align_vectors([0,0,1],delta))
        mesh.apply_translation((a+b)/2);add(mesh,'metal')
    def roof_z(x,y):
        return ridge-(ridge-eave)*abs(x-ridge_x)/half
    # One closed roof volume. A shared ridge has no internal separating faces.
    xyz,faces=[],[]
    def tri(coords):
        start=len(xyz);xyz.extend(coords);faces.append([start,start+1,start+2])
    def quad(a,b,c,d):
        tri([a,b,c]);tri([a,c,d])
    for side in halves.geoms:
        for triangle in constrained_delaunay_triangles(side).geoms:
            ring=list(orient(triangle,1).exterior.coords)[:3]
            top=[[x,y,roof_z(x,y)] for x,y in ring]
            tri(top);tri([[x,y,z-.095] for x,y,z in top][::-1])
    ring=[]
    boundary=list(roof.exterior.coords)
    for a,b in zip(boundary,boundary[1:]):
        ring.append(a)
        if (a[0]-ridge_x)*(b[0]-ridge_x)<0:
            t=(ridge_x-a[0])/(b[0]-a[0])
            ring.append((ridge_x,a[1]+t*(b[1]-a[1])))
    ring.append(ring[0])
    for a,b in zip(ring,ring[1:]):
        quad([*a,roof_z(*a)-.095],[*b,roof_z(*b)-.095],[*b,roof_z(*b)],[*a,roof_z(*a)])
    roof_mesh=trimesh.Trimesh(xyz,faces,process=True);add(roof_mesh,'roof')
    top_projection=unary_union([Polygon(roof_mesh.vertices[face,:2]) for face,normal in zip(roof_mesh.faces,roof_mesh.face_normals) if normal[2]>.1])
    if top_projection.symmetric_difference(roof).area>1e-8:
        raise ValueError('Roof projection changed')
    # Four posts sit inside the source eave. Main frame and X-braces follow
    # visible construction; the unseen rear face is a symmetric interpretation.
    px0,px1=x0+.38,x1-.38;py0,py1=y0+.38,y1-.38
    for x in [px0,px1]:
        for y in [py0,py1]:
            box('post',[x,y,(ground+eave-.18)/2],[.21,.21,eave-.18-ground])
        beam('eave_beam',[x,py0-.1,eave-.22],[x,py1+.1,eave-.22],.21,.22)
        beam('side_cross_brace',[x,py0+.15,deck+.15],[x,py1-.15,eave-.4],.13,.13)
        beam('side_cross_brace',[x,py1-.15,deck+.15],[x,py0+.15,eave-.4],.13,.13)
        beam('subdeck_brace',[x,py0+.2,ground+.22],[x,py1-.2,deck-.15],.16,.16)
    for y in [py0,py1]:
        beam('gable_tie',[px0-.1,y,eave-.22],[px1+.1,y,eave-.22],.19,.19)
        beam('gable_rafter',[px0-.12,y,roof_z(px0-.12,y)-.16],[ridge_x,y,ridge-.16],.16,.16)
        beam('gable_rafter',[ridge_x,y,ridge-.16],[px1+.12,y,roof_z(px1+.12,y)-.16],.16,.16)
    beam('ridge_beam',[ridge_x,py0,ridge-.2],[ridge_x,py1,ridge-.2],.16,.17)
    # Individual decking planks have small real joints, without a second cap.
    count=max(4,round((py1-py0)/.24));pitch=(py1-py0)/count
    for i in range(count):
        y=py0+(i+.5)*pitch
        box('deck_plank',[ridge_x,y,deck-.06],[px1-px0,pitch-.012,.12],'deck')
    for x in [px0+.13,px1-.13]:
        beam('deck_joist',[x,py0,deck-.23],[x,py1,deck-.23],.15,.21)
    # Two short sloped timber approaches are visible in the photograph.
    # Their positions, inclination and decking joints are estimates.
    for side in [-1,1]:
        start=np.array([ridge_x,py0 if side<0 else py1,deck-.04])
        end=start+np.array([0,side*1.35,-.65])
        for offset in [-.58,.58]:
            beam('ramp_stringer',start+[offset,0,-.16],end+[offset,0,-.16],.15,.18)
        length=np.linalg.norm(end-start);count=7;direction=(end-start)/length
        for i in range(count):
            centre=start+(end-start)*(i+.5)/count
            mesh=trimesh.creation.box(extents=[1.3,length/count-.014,.10])
            # Rotate local Y along the sloping ramp, keeping its X transverse.
            rotation=math.atan2(direction[2],direction[1])
            mesh.apply_transform(trimesh.transformations.rotation_matrix(rotation,[1,0,0]))
            mesh.apply_translation(centre);add(mesh,'deck')
    # Two open wire feeding baskets. Cage walls are actual separated wires,
    # with an open top; no opaque cube or overlapping transparent plane.
    for y in [py0+.65,py1-.65]:
        x=px1+.24;bottom=deck+.48;top=bottom+.62;radius=.29
        cylinder([x,y,ground],[x,y,bottom],.055)
        for k in range(16):
            a=2*math.pi*k/16
            cylinder([x+radius*math.cos(a),y+radius*math.sin(a),bottom],[x+radius*math.cos(a),y+radius*math.sin(a),top],.009)
        for z in [bottom,bottom+.21,bottom+.42,top]:
            for k in range(16):
                a,b=2*math.pi*k/16,2*math.pi*(k+1)/16
                cylinder([x+radius*math.cos(a),y+radius*math.sin(a),z],[x+radius*math.cos(b),y+radius*math.sin(b),z],.009)
    # Merge intersecting construction pieces and remove hidden joint volumes.
    # Material ownership is roof, timber, decking; each exposed face is drawn once.
    merged={key:trimesh.boolean.union(items,engine='manifold') if len(items)>1 else items[0] for key,items in pieces.items()}
    merged['timber']=trimesh.boolean.difference([merged['timber'],merged['roof']],engine='manifold')
    merged['deck']=trimesh.boolean.difference([merged['deck'],merged['timber'],merged['roof']],engine='manifold')
    scene=trimesh.Scene();checks={}
    for key,mesh in merged.items():
        if not np.isfinite(mesh.vertices).all() or (mesh.area_faces<=1e-12).any():
            raise ValueError('Degenerate or non-finite '+key)
        welded=mesh.copy();welded.merge_vertices()
        if not welded.is_watertight or not welded.is_winding_consistent or welded.volume<=0:
            raise ValueError('Open/inverted '+key)
        checks[key]={'watertight':True,'consistentWinding':True,'volumeM3':float(welded.volume)}
        uv=np.column_stack((mesh.vertices[:,0],mesh.vertices[:,1]+mesh.vertices[:,2]))
        mesh.visual=trimesh.visual.TextureVisuals(uv=uv if mats[key].baseColorTexture is not None else None,material=mats[key])
        rotation=np.eye(4);rotation[:2,0]=u;rotation[:2,1]=v
        mesh.apply_transform(rotation)
        scene.add_geometry(mesh,node_name=key,geom_name=key)
    scene.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]))
    def postprocess(tree):
        # Same image bytes are reused by three wood colour variants. Reuse the
        # texture objects too, so a phone need not decode three identical maps.
        images,lookup,remap=[],{},{}
        for i,item in enumerate(tree.get('images',[])):
            key=json.dumps({k:v for k,v in item.items() if k!='name'},sort_keys=True)
            if key not in lookup:lookup[key]=len(images);images.append(item)
            remap[i]=lookup[key]
        tree['images']=images
        textures,lookup,texture_remap=[],{},{}
        for i,item in enumerate(tree.get('textures',[])):
            item['source']=remap[item['source']];key=json.dumps(item,sort_keys=True)
            if key not in lookup:lookup[key]=len(textures);textures.append(item)
            texture_remap[i]=lookup[key]
        tree['textures']=textures
        for item in tree.get('materials',[]):
            texture=item.get('pbrMetallicRoughness',{}).get('baseColorTexture')
            if texture:texture['index']=texture_remap[texture['index']]
        for mesh in tree['meshes']:
            for primitive in mesh['primitives']:
                for index in primitive['attributes'].values():
                    tree['bufferViews'][tree['accessors'][index]['bufferView']]['target']=34962
                if 'indices' in primitive:
                    tree['bufferViews'][tree['accessors'][primitive['indices']]['bufferView']]['target']=34963
        tree['scenes'][0]['extras']={'unit':'metre','originM5LocalXY':inputs['originM5LocalXY'],
            'sourceId':inputs['sourceId'],'sourceAssociation':'candidate, unconfirmed','sourcePhoto':inputs['sourcePhoto']}
    (HERE/'savanna-ahsap-platform.glb').write_bytes(scene.export(file_type='glb',include_normals=True,tree_postprocessor=postprocess))
    report={'schema':'bursa-zoo-savanna-platform/v1','sourceId':inputs['sourceId'],
        'originM5LocalXY':inputs['originM5LocalXY'],'unit':'metre','upAxis':'glTF Y-up',
        'roofFootprintAreaM2':roof.area,'nativeFootprintAreaM2':Polygon(source['paths'][0]).area,
        'roofFootprintSymmetricDifferenceM2':top_projection.symmetric_difference(roof).area,'roofRidgeZMetres':ridge,
        'triangles':sum(len(m.faces) for m in scene.geometry.values()),'solidChecks':checks,
        'sourceAssociation':'candidate, unconfirmed','interpretation':inputs['interpretation'],
        'details':'Photo-visible timber frame, X-bracing, elevated deck, two ramps and wire baskets; dimensions and unseen side are interpretations.',
        'meshOwnership':'Closed solids; intersecting same-material members united, roof/timber/decking joints clipped by material ownership. No terrain or generic canopy cap is added.',
        'sourceMemberCounts':{key:len(items) for key,items in pieces.items()}}
    (HERE/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['roofFootprintAreaM2','triangles','sourceAssociation']}))


if __name__=='__main__':main()
