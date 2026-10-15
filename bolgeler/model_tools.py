"""Small geometry/export helpers for editable, metre-based region assets."""
from __future__ import annotations

import json
import math

import numpy as np
import trimesh
from PIL import Image
from shapely import constrained_delaunay_triangles
from shapely.geometry.polygon import orient


def pbr(name, color, texture=None, roughness=.94):
    return trimesh.visual.material.PBRMaterial(
        name=name, baseColorFactor=np.array(color, dtype=float),
        baseColorTexture=Image.open(texture) if texture else None,
        metallicFactor=0., roughnessFactor=roughness)


def polygon_mesh(polygon, top, bottom=None):
    """A triangulated plane, or one closed prism including its holes."""
    vertices, faces = [], []
    def face(points):
        start = len(vertices)
        vertices.extend(points)
        faces.append([start, start+1, start+2])
    parts = [polygon] if polygon.geom_type == 'Polygon' else polygon.geoms
    for part in parts:
        part = orient(part, 1)
        for triangle in constrained_delaunay_triangles(part).geoms:
            ring = list(orient(triangle, 1).exterior.coords)[:3]
            face([[x, y, top] for x, y in ring])
            if bottom is not None:
                face([[x, y, bottom] for x, y in reversed(ring)])
        if bottom is not None:
            for ring in [part.exterior, *part.interiors]:
                for a, b in zip(ring.coords, list(ring.coords)[1:]):
                    face([[*a, bottom], [*b, bottom], [*b, top]])
                    face([[*a, bottom], [*b, top], [*a, top]])
    return trimesh.Trimesh(vertices, faces, process=True)


def tube(points, radius, sections=12):
    """A continuous capped tube, with transported frames along a polyline."""
    points = np.array(points, dtype=float)
    tangents = np.zeros_like(points)
    tangents[0] = points[1]-points[0]
    tangents[-1] = points[-1]-points[-2]
    tangents[1:-1] = points[2:]-points[:-2]
    tangents /= np.linalg.norm(tangents, axis=1)[:, None]
    radii = np.broadcast_to(np.asarray(radius), (len(points),))
    vertices, faces = [], []
    normal = np.cross(tangents[0], [0., 1., 0.])
    if np.linalg.norm(normal) < .01:
        normal = np.cross(tangents[0], [1., 0., 0.])
    for point, tangent, r in zip(points, tangents, radii):
        normal -= tangent*np.dot(normal, tangent)
        normal /= np.linalg.norm(normal)
        binormal = np.cross(tangent, normal)
        for k in range(sections):
            a = k*2*math.pi/sections
            vertices.append(point+r*(normal*math.cos(a)+binormal*math.sin(a)))
    for j in range(len(points)-1):
        for k in range(sections):
            a, b = j*sections+k, j*sections+(k+1)%sections
            c, d = a+sections, b+sections
            faces.extend([[a, b, d], [a, d, c]])
    for end, ring in [(0, 0), (-1, (len(points)-1)*sections)]:
        centre = len(vertices);vertices.append(points[end])
        for k in range(sections):
            a, b = ring+k, ring+(k+1)%sections
            faces.append([centre, b, a] if end == 0 else [centre, a, b])
    mesh = trimesh.Trimesh(vertices, faces, process=True)
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def bark_uv(mesh, paths):
    """Face-local cylindrical UVs; timber grain follows each closest branch."""
    segments = []
    for points in paths:
        distance = 0.
        for a, b in zip(points, points[1:]):
            a, b = np.array(a), np.array(b)
            length = np.linalg.norm(b-a);axis = (b-a)/length
            normal = np.cross(axis, [0., 1., 0.])
            if np.linalg.norm(normal) < .01:
                normal = np.cross(axis, [1., 0., 0.])
            normal /= np.linalg.norm(normal)
            segments.append((a, axis, length, normal, np.cross(axis, normal), distance))
            distance += length
    xyz, uv = [], []
    for triangle in mesh.triangles:
        centre = triangle.mean(axis=0)
        segment = min(segments, key=lambda s: np.linalg.norm(
            centre-s[0]-s[1]*np.clip(np.dot(centre-s[0], s[1]), 0, s[2])))
        a, axis, _, normal, binormal, distance = segment
        relative = triangle-a
        u = np.arctan2(relative@binormal, relative@normal)/(2*math.pi)+.5
        if np.ptp(u) > .5:
            u[u < .5] += 1
        xyz.extend(triangle)
        uv.extend(np.column_stack((u, (relative@axis+distance)/2.)))
    result = trimesh.Trimesh(xyz, np.arange(len(xyz)).reshape(-1, 3), process=False)
    return result, np.array(uv)


def postprocess_gltf(tree, extras):
    """Deduplicate shared image/texture objects and set GPU buffer targets."""
    images, lookup, remap = [], {}, {}
    for i, item in enumerate(tree.get('images', [])):
        key = json.dumps({k:v for k,v in item.items() if k != 'name'}, sort_keys=True)
        if key not in lookup:
            lookup[key] = len(images);images.append(item)
        remap[i] = lookup[key]
    tree['images'] = images
    textures, lookup, texture_remap = [], {}, {}
    for i, item in enumerate(tree.get('textures', [])):
        item['source'] = remap[item['source']]
        key = json.dumps(item, sort_keys=True)
        if key not in lookup:
            lookup[key] = len(textures);textures.append(item)
        texture_remap[i] = lookup[key]
    tree['textures'] = textures
    for item in tree.get('materials', []):
        for container in (item,item.get('pbrMetallicRoughness',{})):
            for key,value in container.items():
                if key.endswith('Texture') and isinstance(value,dict) and 'index' in value:
                    value['index']=texture_remap[value['index']]
    for mesh in tree['meshes']:
        for primitive in mesh['primitives']:
            for index in primitive['attributes'].values():
                tree['bufferViews'][tree['accessors'][index]['bufferView']]['target'] = 34962
            if 'indices' in primitive:
                tree['bufferViews'][tree['accessors'][primitive['indices']]['bufferView']]['target'] = 34963
    tree['scenes'][0]['extras'] = extras
