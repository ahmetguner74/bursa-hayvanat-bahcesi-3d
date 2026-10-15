"""Editable penguin-pool interpretation from M5 and municipal 2017 photos.

In the atlas, pool_water and gravel_ground are hidden: the planar partition
owns those exact surfaces. The same asset is self-contained in model review.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image
from shapely import constrained_delaunay_triangles
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
ORIGIN = np.array([-14.0, 134.0, 0.0])
BASE = -.24


def parts(geometry):
    if geometry.is_empty:
        return []
    if isinstance(geometry, Polygon):
        return [geometry] if geometry.area > 1e-9 else []
    return [piece for child in geometry.geoms for piece in parts(child)]


class Mesh:
    def __init__(self):
        self.vertices, self.faces, self.uv = [], [], []

    def triangle(self, xyz, uv=None):
        xyz = np.asarray(xyz, dtype=float)
        if np.linalg.norm(np.cross(xyz[1]-xyz[0], xyz[2]-xyz[0])) < 1e-10:
            return
        offset = len(self.vertices)
        self.vertices.extend(xyz.tolist())
        self.faces.append([offset, offset+1, offset+2])
        self.uv.extend(uv if uv is not None else [[0, 0]]*3)

    def quad(self, a, b, c, d, uv=None):
        self.triangle([a, b, c], [uv[0], uv[1], uv[2]] if uv else None)
        self.triangle([a, c, d], [uv[0], uv[2], uv[3]] if uv else None)

    def solid(self, mesh, scale=3):
        for face in mesh.faces:
            xyz = mesh.vertices[face]
            self.triangle(xyz, [[p[0]/scale, (p[1]+p[2])/scale] for p in xyz])

    def export(self, material):
        mesh = trimesh.Trimesh(vertices=self.vertices, faces=self.faces, process=False)
        mesh.visual = trimesh.visual.TextureVisuals(
            uv=np.asarray(self.uv) if material.baseColorTexture is not None else None,
            material=material)
        if not np.isfinite(mesh.vertices).all() or (mesh.area_faces < 1e-12).any():
            raise ValueError('Invalid pool mesh')
        mesh.apply_translation(-ORIGIN)
        return mesh


def cap(output, polygon, height, scale=3, reverse=False):
    for part in parts(polygon):
        for tri in constrained_delaunay_triangles(part).geoms:
            coords = list(orient(tri, 1).exterior.coords)[:3]
            if reverse:
                coords.reverse()
            xyz = [[x, y, height(x, y) if callable(height) else height] for x, y in coords]
            output.triangle(xyz, [[x/scale, y/scale] for x, y in coords])


def extrude(output, polygon, bottom, top, scale=3):
    cap(output, polygon, top, scale)
    cap(output, polygon, bottom, scale, reverse=True)
    for part in parts(polygon):
        part = orient(part, 1)
        for ring in [part.exterior, *part.interiors]:
            distance = 0
            for a, b in zip(ring.coords, list(ring.coords)[1:]):
                length = math.dist(a, b)
                az = top(*a) if callable(top) else top
                bz = top(*b) if callable(top) else top
                output.quad([*a, bottom], [*b, bottom], [*b, bz], [*a, az],
                    [[distance/scale,bottom/scale],[(distance+length)/scale,bottom/scale],
                     [(distance+length)/scale,bz/scale],[distance/scale,az/scale]])
                distance += length


def basin(output,pool):
    """A single stepped basin shell, including its visible underwater floor."""
    outer=pool.buffer(.28,quad_segs=6)
    lower=pool.buffer(.04,quad_segs=6)
    cap(output,outer.difference(pool),-.105)
    cap(output,pool,-1.45)
    cap(output,lower,-1.5,reverse=True)
    cap(output,outer.difference(lower),-.55,reverse=True)
    for polygon,bottom,top,inward in [(outer,-.55,-.105,False),(lower,-1.5,-.55,False),(pool,-1.45,-.105,True)]:
        for part in parts(polygon):
            ring=list(orient(part,1).exterior.coords)
            for a,b in zip(ring,ring[1:]):
                xyz=([*a,bottom],[*b,bottom],[*b,top],[*a,top])
                output.quad(*xyz[::-1] if inward else xyz)


def beam(output, centre, extent, angle=0):
    mesh = trimesh.creation.box(extents=extent)
    mesh.apply_transform(trimesh.transformations.rotation_matrix(angle, [0,0,1]))
    mesh.apply_translation(centre)
    output.solid(mesh)


def material(name, color, texture=None, roughness=1, alpha=False):
    return trimesh.visual.material.PBRMaterial(name=name,
        baseColorFactor=np.asarray(color,dtype=float),
        baseColorTexture=Image.open(texture) if texture else None,
        metallicFactor=0,roughnessFactor=roughness,
        alphaMode='BLEND' if alpha else 'OPAQUE',doubleSided=alpha)


def shared_textures(tree):
    """Share identical embedded images/textures across differently tinted parts."""
    unique,remap,lookup=[],{},{}
    for index,item in enumerate(tree.get('images',[])):
        key=json.dumps({k:v for k,v in item.items() if k!='name'},sort_keys=True)
        if key not in lookup:
            lookup[key]=len(unique);unique.append(item)
        remap[index]=lookup[key]
    tree['images']=unique
    unique,texture_remap,lookup=[],{},{}
    for index,item in enumerate(tree.get('textures',[])):
        item['source']=remap[item['source']]
        key=json.dumps({k:v for k,v in item.items() if k!='name'},sort_keys=True)
        if key not in lookup:
            lookup[key]=len(unique);unique.append(item)
        texture_remap[index]=lookup[key]
    tree['textures']=unique
    for mat in tree.get('materials',[]):
        for container in [mat,mat.get('pbrMetallicRoughness',{})]:
            for key,value in container.items():
                if key.endswith('Texture') and isinstance(value,dict) and 'index' in value:
                    value['index']=texture_remap[value['index']]


def main():
    inputs = json.loads((HERE/'model-inputs.json').read_text(encoding='utf-8'))
    if hashlib.sha256((PROJECT/'site-data.json').read_bytes()).hexdigest()!=inputs['siteDataSha256']:
        raise ValueError('M5 input changed; review the penguin outline')
    surfaces = json.loads((PROJECT/'surface-layers.json').read_text(encoding='utf-8'))
    pool = Polygon(inputs['waterOutline']['outer'],inputs['waterOutline']['holes'])
    terrain = unary_union([Polygon(item['outer'],item['holes']) for item in surfaces['layers']['terrain']])
    land = terrain.intersection(Polygon(inputs['gravelContextMask']['outer']))
    builders = {name:Mesh() for name in ['pool_water','gravel_ground','blue_coping','drain_band',
        'artificial_cliff','emergent_rocks','bank_stones','wooden_viewing_deck','green_viewing_panels']}
    cap(builders['pool_water'],pool,surfaces['renderLevels']['waterZ'])
    extrude(builders['gravel_ground'],land,-1.5,BASE,1.5)
    coping = pool.buffer(.28,quad_segs=6).difference(pool)
    drain = pool.buffer(.57,quad_segs=6).difference(pool.buffer(.28,quad_segs=6))
    basin(builders['blue_coping'],pool)
    extrude(builders['drain_band'],drain,-.55,-.10)

    # One connected, varying-height cliff volume follows the northern bank.
    arc = []
    for i in range(121):
        p = pool.exterior.interpolate(pool.exterior.length*i/120)
        if p.y>136.5:
            arc.append((p.x,p.y+2.0))
    if len(arc)<4:
        raise ValueError('Missing northern-bank reference arc')
    cliff = LineString(arc).buffer(.72,join_style=2).intersection(land)
    def cliff_top(x,y):
        return 2.8+.35*math.sin(x*1.5)+.18*math.sin(y*2.1)
    extrude(builders['artificial_cliff'],cliff,BASE,cliff_top)

    # Low rocks emerge from water; their volume touches the water naturally.
    rng = random.Random(151017)
    for x,y,sx,sy,height in [(-18.2,136.5,2.2,1.1,.42),(-21.8,132.7,1.7,.9,.33)]:
        rock=trimesh.creation.icosphere(subdivisions=2,radius=1)
        for vertex in rock.vertices:
            vertex *= 1+.06*math.sin(vertex[0]*9+vertex[1]*11)
        rock.apply_scale([sx,sy,height]);rock.apply_translation([x,y,-.10])
        builders['emergent_rocks'].solid(rock)
    for i in range(int(pool.exterior.length/.47)):
        p=pool.exterior.interpolate(i*.47)
        for offset in [1.0,1.6]:
            nearest=Point(p.x,p.y)
            towards=np.array([p.x-pool.centroid.x,p.y-pool.centroid.y])
            towards/=np.linalg.norm(towards)
            x,y=np.array(p.coords[0])+towards*offset
            if not land.contains(Point(x,y)) or cliff.buffer(.25).contains(Point(x,y)):
                continue
            size=.17+rng.random()*.18
            rock=trimesh.creation.icosphere(subdivisions=1,radius=1)
            rock.apply_scale([size,size*(.7+rng.random()*.4),size*.5])
            rock.apply_translation([x,y,BASE+size*.46])
            builders['bank_stones'].solid(rock,1.5)

    # Photo shows a wooden viewing platform across the narrow eastern end.
    # Individual boards, posts and rails are solids with open visitor space.
    cx,cy=-4.0,136.0
    width,depth,z=4.8,6.1,.72
    count=round(depth/.18)
    for i in range(count):
        y=cy-depth/2+(i+.5)*depth/count
        beam(builders['wooden_viewing_deck'],[cx,y,z],[width,depth/count-.015,.13])
    for x in [cx-width/2+.12,cx+width/2-.12]:
        for y in [cy-depth/2+.1,cy,cy+depth/2-.1]:
            beam(builders['wooden_viewing_deck'],[x,y,.67],[.18,.18,2.5])
        for height in [z+.25,z+1.1]:
            beam(builders['wooden_viewing_deck'],[x,cy,height],[.14,depth,.13])
        for y in np.arange(cy-depth/2+.24,cy+depth/2,.32):
            beam(builders['wooden_viewing_deck'],[x,y,z+.65],[.055,.055,.86])
    # Recessed green glazed panels below the board edge are separate from rails.
    beam(builders['green_viewing_panels'],[cx-width/2-.02,cy,-.05],[.045,depth-.4,1.25])

    assets=PROJECT/'viewer/assets'
    mats={
        'pool_water':material('pool_water_teal',[.08,.27,.24,.82],roughness=.3,alpha=True),
        'gravel_ground':material('pale_gravel',[1.,1.,1.,1.],assets/'penguin-pale-gravel-v1.png'),
        'blue_coping':material('blue_pool_coping',[.035,.13,.19,1.]),
        'drain_band':material('pool_drain_band',[.31,.33,.32,1.],roughness=.7),
        'artificial_cliff':material('artificial_rock',[.82,.84,.84,1.],assets/'penguin-artificial-rock-v1.png'),
        'emergent_rocks':material('emergent_rock',[.68,.71,.70,1.],assets/'penguin-artificial-rock-v1.png'),
        'bank_stones':material('pale_bank_stones',[1.,1.,1.,1.],assets/'penguin-pale-gravel-v1.png'),
        'wooden_viewing_deck':material('viewing_platform_wood',[.26,.115,.055,1.]),
        'green_viewing_panels':material('green_glazed_viewing_panels',[.055,.23,.20,.45],roughness=.23,alpha=True),
    }
    scene=trimesh.Scene()
    for name,builder in builders.items():
        if builder.faces:
            scene.add_geometry(builder.export(mats[name]),node_name=name,geom_name=name)
    scene.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]))
    (HERE/'penguen-havuzu.glb').write_bytes(scene.export(file_type='glb',include_normals=True,tree_postprocessor=shared_textures))
    solid_checks={}
    for name in ['blue_coping','artificial_cliff','gravel_ground','drain_band']:
        mesh=scene.geometry[name].copy();mesh.merge_vertices(merge_tex=True,merge_norm=True)
        solid_checks[name]={'watertight':bool(mesh.is_watertight),'consistentWinding':bool(mesh.is_winding_consistent),'volumeM3':float(mesh.volume)}
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume<=0:
            raise ValueError('Open or inverted solid: '+name)
    report={'schema':'bursa-zoo-penguin-model/v1','originM5LocalXY':ORIGIN[:2].tolist(),
        'unit':'metre','upAxis':'glTF Y-up','waterMaskAreaM2':pool.area,'gravelTerrainAreaM2':land.area,
        'renderWaterZMetres':surfaces['renderLevels']['waterZ'],'renderWaterHeightSurveyed':False,
        'cliffFootprintAreaM2':cliff.area,'triangles':sum(len(m.faces) for m in scene.geometry.values()),
        'atlasHiddenNodes':['pool_water','gravel_ground'],
        'solidChecks':solid_checks,
        'surfaceOwnership':'Atlas planar partition supplies water and gravel once; only physical coping, rock and deck solids are added.',
        'historicalAreasM2':inputs['historicalDocumentAreasM2'],'areaDiscrepancy':inputs['areaDiscrepancy'],
        'interpretation':inputs['interpretation'],'sourcePage':inputs['sourcePage']}
    (HERE/'model-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['waterMaskAreaM2','gravelTerrainAreaM2','triangles']}))


if __name__=='__main__':
    main()
