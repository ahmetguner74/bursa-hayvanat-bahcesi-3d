"""Editable reconstruction of the Turkish-village building group.

The footprint partition is captured from M5. Hip roofs use a straight skeleton,
so concave wings share real roof facets instead of overlapping roof boxes.
Facade openings are removed from the wall before recessed frames are inserted.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image
from py_straight_skeleton import compute_skeleton
from shapely import constrained_delaunay_triangles
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
BASE_Z = -.24
ORIGIN = np.array([-68.0, 8.0, 0.0])


class Mesh:
    def __init__(self):
        self.vertices, self.faces, self.uv = [], [], []

    def triangle(self, points, uv=None):
        points = np.asarray(points, dtype=float)
        if np.linalg.norm(np.cross(points[1] - points[0], points[2] - points[0])) < 1e-9:
            return
        offset = len(self.vertices)
        self.vertices.extend(points.tolist())
        self.faces.append([offset, offset + 1, offset + 2])
        self.uv.extend(uv if uv is not None else [[0, 0]] * 3)

    def quad(self, a, b, c, d):
        self.triangle([a, b, c])
        self.triangle([a, c, d])

    def solid(self, mesh):
        for face in mesh.faces:
            self.triangle(mesh.vertices[face])

    def export(self, material):
        mesh = trimesh.Trimesh(vertices=self.vertices, faces=self.faces, process=False)
        mesh.visual = trimesh.visual.TextureVisuals(uv=np.asarray(self.uv), material=material)
        return mesh


def material(name, color, texture=None, roughness=1):
    return trimesh.visual.material.PBRMaterial(name=name, baseColorFactor=np.asarray(color, dtype=float),
        baseColorTexture=Image.open(texture) if texture else None,
        metallicFactor=0, roughnessFactor=roughness)


def triangles(polygon):
    if polygon.is_empty:
        return []
    return [orient(part, 1) for part in constrained_delaunay_triangles(polygon).geoms
            if part.area > 1e-10]


def make_roof(item, output):
    original = orient(Polygon(item["outer"], item["holes"]), 1)
    # Sub-millimetre seam vertices in the captured render mask otherwise create
    # zero-time skeleton events. Roof faces are clipped back to the exact mask.
    poly = original.simplify(.0005, preserve_topology=True)
    skeleton = compute_skeleton(exterior=list(poly.exterior.coords)[:-1],
        holes=[list(ring.coords)[:-1] for ring in poly.interiors])
    maximum = max(node.time for node in skeleton.nodes)
    rise = min(2.0, maximum * .47)
    eaves = item["z"] - rise
    roof_faces = []
    for indices in skeleton.get_faces():
        points = [skeleton.nodes[index].position for index in indices]
        face = orient(Polygon([(p.x, p.y) for p in points]), 1).intersection(original)
        first, second = points[0], points[1]
        dx, dy = second.x - first.x, second.y - first.y
        length = math.hypot(dx, dy)
        if length < 1e-8:
            raise ValueError("Roof skeleton produced a zero base edge")
        slope = rise / maximum
        for tri in triangles(face):
            xyz, uv = [], []
            for x, y in list(tri.exterior.coords)[:3]:
                along = ((x - first.x) * dx + (y - first.y) * dy) / length
                inward = abs((x - first.x) * dy - (y - first.y) * dx) / length
                xyz.append([x, y, eaves + inward * slope])
                uv.append([along / 2, inward * math.sqrt(1 + slope * slope) / 2])
            output.triangle(xyz, uv)
        roof_faces.append(face)
    projected = unary_union(roof_faces)
    remaining = original.difference(projected)
    for tri in triangles(remaining):
        output.triangle([[x, y, eaves] for x, y in list(tri.exterior.coords)[:3]])
    projected = unary_union([projected, remaining])
    delta = original.symmetric_difference(projected).area
    if delta > .000001:
        raise ValueError(f"Roof footprint changed: {item['sourceId']} {delta}")
    return {"id": item["sourceId"], "polygon": original, "eaves": eaves,
            "ridge": item["z"], "facets": len(roof_faces), "area": original.area}


def wall_mesh(a, b, bottom, top, openings, stone, upper):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    wall = box(0, bottom, length, top)
    if openings:
        wall = wall.difference(unary_union([box(*opening) for opening in openings]))
    for low, high, target in [(bottom, min(top, 2.8), stone), (max(bottom, 2.8), top, upper)]:
        if high <= low:
            continue
        panel = wall.intersection(box(0, low, length, high))
        for tri in triangles(panel):
            vertices, uv = [], []
            for s, z in list(tri.exterior.coords)[:3]:
                vertices.append([a[0] + dx * s / length, a[1] + dy * s / length, z])
                uv.append([s / 3, z / 3])
            target.triangle(vertices, uv)


def facade_detail(a, b, openings, eaves, window_mesh, door_mesh, wood):
    tangent = (np.array(b) - np.array(a)) / np.linalg.norm(np.array(b) - np.array(a))
    normal = np.array([tangent[1], -tangent[0]])
    angle = math.atan2(tangent[1], tangent[0])

    def point(s, z, offset=0):
        xy = np.array(a) + tangent * s + normal * offset
        return [xy[0], xy[1], z]

    def beam(s, z, length, depth, height):
        item = trimesh.creation.box(extents=(length, depth, height))
        item.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1]))
        item.apply_translation(point(s, z, .055))
        wood.solid(item)

    length = np.linalg.norm(np.array(b) - np.array(a))
    if length > 1:
        beam(length / 2, eaves - .055, length, .13, .13)
        if eaves > 4.0:
            beam(length / 2, 2.85, length, .13, .15)
            for s in np.arange(.15, length, 3.0):
                beam(s, (2.85 + eaves) / 2, .1, .13, eaves - 2.85)
    for s0, z0, s1, z1 in openings:
        door = z0 < .5
        target = door_mesh if door else window_mesh
        target.quad(point(s0, z0, -.08), point(s1, z0, -.08),
                    point(s1, z1, -.08), point(s0, z1, -.08))
        # Four reveals connect the actual opening perimeter to its inset panel.
        wood.quad(point(s0, z0), point(s0, z0, -.08), point(s0, z1, -.08), point(s0, z1))
        wood.quad(point(s1, z0), point(s1, z1), point(s1, z1, -.08), point(s1, z0, -.08))
        wood.quad(point(s0, z1), point(s0, z1, -.08), point(s1, z1, -.08), point(s1, z1))
        wood.quad(point(s0, z0), point(s1, z0), point(s1, z0, -.08), point(s0, z0, -.08))
        for s in (s0, s1):
            beam(s, (z0 + z1) / 2, .075, .12, z1 - z0 + .1)
        for z in (z0, z1):
            beam((s0 + s1) / 2, z, s1 - s0 + .1, .12, .075)
        if not door:
            beam((s0 + s1) / 2, (z0 + z1) / 2, .045, .1, z1 - z0)
            beam((s0 + s1) / 2, z0 + (z1 - z0) * .55, s1 - s0, .1, .045)


def main():
    inputs = json.loads((HERE / "model-footprints.json").read_text(encoding="utf-8"))
    if hashlib.sha256((PROJECT / "site-data.json").read_bytes()).hexdigest() != inputs["siteDataSha256"]:
        raise ValueError("M5 source changed; recapture the village footprint partition")
    roof, stone, upper, wood, window, door, base = [Mesh() for _ in range(7)]
    regions = [make_roof(item, roof) for item in inputs["roofs"]]
    footprint = unary_union([r["polygon"] for r in regions])
    if abs(sum(r["area"] for r in regions) - footprint.area) > .000001:
        raise ValueError("Village roof regions overlap in XY")
    linework = unary_union([r["polygon"].boundary for r in regions])
    exterior_walls, internal_steps, opening_count = 0, 0, 0
    for line in linework.geoms:
        for a, b in zip(line.coords, list(line.coords)[1:]):
            length = math.dist(a, b)
            if length < .001:
                continue
            midpoint = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            touching = [r for r in regions if r["polygon"].boundary.distance(midpoint) < 1e-6]
            outside = footprint.boundary.distance(midpoint) < 1e-6
            if not touching:
                raise ValueError("Village wall has no owning roof")
            high = max(touching, key=lambda r: r["eaves"])
            top = high["eaves"]
            bottom = BASE_Z if outside else min(r["eaves"] for r in touching)
            if top - bottom < 1e-6:
                continue
            dx, dy = b[0] - a[0], b[1] - a[1]
            left = Point(midpoint.x - dy / length * 1e-5, midpoint.y + dx / length * 1e-5)
            if not high["polygon"].contains(left):
                a, b = b, a
            openings = []
            if outside and length > 4.5:
                count = max(1, math.floor(length / 3.2))
                for index in range(count):
                    s = length * (index + .5) / count
                    if top > 4.8:
                        openings.append((s - .42, 3.45, s + .42, min(top - .4, 4.9)))
                if exterior_walls % 5 == 0:
                    s = length * .5
                    openings.append((s - .5, 0.0, s + .5, min(2.15, top - .25)))
            wall_mesh(a, b, bottom, top, openings, stone, upper)
            if outside:
                exterior_walls += 1
                opening_count += len(openings)
                facade_detail(a, b, openings, top, window, door, wood)
            else:
                internal_steps += 1
    for tri in triangles(footprint):
        xyz = [[x, y, BASE_Z] for x, y in list(tri.exterior.coords)[:3]]
        base.triangle(xyz[::-1])
    assets = PROJECT / "viewer/assets"
    materials = [
        material("terracotta_hip_roof", [1, 1, 1, 1], assets / "turk-koyu-roof-tiles-v1.png"),
        material("fieldstone_lower_wall", [.9, .88, .81, 1], assets / "turk-koyu-stone-wall-v1.png"),
        material("warm_upper_wall", [.53, .43, .32, 1]),
        material("dark_timber_frames", [.23, .14, .085, 1]),
        material("recessed_window", [.035, .07, .055, 1], roughness=.35),
        material("recessed_door", [.18, .105, .06, 1]),
        material("closed_bottom", [.32, .3, .25, 1]),
    ]
    scene = trimesh.Scene()
    for name, builder, mat in zip(["hip_roofs", "stone_walls", "upper_walls", "timber_frames",
                                  "inset_windows", "inset_doors", "bottom"],
                                 [roof, stone, upper, wood, window, door, base], materials):
        if not builder.faces:
            continue
        mesh = builder.export(mat)
        if not np.isfinite(mesh.vertices).all() or np.any(mesh.area_faces < 1e-12):
            raise ValueError(f"Invalid {name} mesh")
        mesh.apply_translation(-ORIGIN)
        scene.add_geometry(mesh, node_name=name)
    scene.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0]))
    (HERE / "turk-koyu.glb").write_bytes(scene.export(file_type="glb", include_normals=True))
    report = {"schema": "bursa-zoo-turkish-village-model/v1", "sourceIds": inputs["sourceIds"],
        "originM5LocalXY": ORIGIN[:2].tolist(), "unit": "metre", "upAxis": "glTF Y-up",
        "footprintAreaM2": footprint.area, "roofProjectedOverlapM2": 0,
        "buildingCount": len(regions), "hipFacetCount": sum(r["facets"] for r in regions),
        "exteriorWallSegments": exterior_walls, "internalHeightSteps": internal_steps,
        "facadeOpenings": opening_count,
        "triangles": sum(len(mesh.faces) for mesh in scene.geometry.values()),
        "interpretation": "M5 footprint partition retained; hip roofs, eaves, material and facade details interpreted from historical aerial photo; windows are not a measured facade survey",
        "architecturalSource": "https://www.trendinsaat.com.tr/tr/projeler/kent-parklari",
        "roofHeights": [{"sourceId": r["id"], "ridgeZ": r["ridge"], "eavesZ": r["eaves"]} for r in regions]}
    (HERE / "model-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ["buildingCount", "hipFacetCount", "facadeOpenings", "triangles"]}))


if __name__ == "__main__":
    main()
