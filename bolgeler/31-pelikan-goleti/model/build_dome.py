"""Parametric, editable glTF study of the waterbird dome shell.

The USKON source documents the 70 × 40 × 20 m envelope, but not every node
coordinate. This triangulation is an explicit visual reconstruction, never an
as-built structural model. The two portal clearances are clipped in 3D.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import trimesh


HERE = Path(__file__).resolve().parent
LENGTH, WIDTH, HEIGHT = 70.0, 40.0, 20.0
NEAR_N, NEAR_M = 36, 18
STEEL = np.array([227, 232, 226, 255], dtype=np.uint8)
PORTAL = np.array([83, 96, 92, 255], dtype=np.uint8)
PORTAL_EDGE = np.array([152, 161, 153, 255], dtype=np.uint8)
STEEL_LINEAR = [.40197778, .48514994, .4286905, 1.0]  # sRGB #aab9af, matching the atlas.


def point_grid(n: int, m: int) -> np.ndarray:
    result = np.empty((n + 1, m + 1, 3), dtype=np.float64)
    for i in range(n + 1):
        x = -LENGTH / 2 + .02 + (LENGTH - .04) * i / n
        scale = math.sqrt(max(0, 1 - (x / (LENGTH / 2)) ** 2))
        for j in range(m + 1):
            angle = math.pi * j / m
            result[i, j] = [x, WIDTH / 2 * scale * math.cos(angle),
                            HEIGHT * scale * math.sin(angle)]
    return result


def outside_box(a: np.ndarray, b: np.ndarray, bounds: tuple) -> list[tuple]:
    """Return segment pieces outside an axis-aligned box, preserving openings."""
    lo, hi = np.asarray(bounds[0]), np.asarray(bounds[1])
    direction = b - a
    enter, leave = 0.0, 1.0
    for axis in range(3):
        if abs(direction[axis]) < 1e-10:
            if a[axis] < lo[axis] or a[axis] > hi[axis]:
                return [(a, b)]
            continue
        t0 = (lo[axis] - a[axis]) / direction[axis]
        t1 = (hi[axis] - a[axis]) / direction[axis]
        if t0 > t1:
            t0, t1 = t1, t0
        enter, leave = max(enter, t0), min(leave, t1)
        if enter >= leave:
            return [(a, b)]
    parts = []
    if enter > 0:
        parts.append((a, a + direction * enter))
    if leave < 1:
        parts.append((a + direction * leave, b))
    return parts


def portals(radius: float) -> list[tuple]:
    margin = radius + .03
    return [
        ((-35.5 - margin, -1.75 - margin, -.2 - margin),
         (-29.5 + margin, 1.75 + margin, 2.8 + margin)),
        ((29.5 - margin, -1.75 - margin, -.2 - margin),
         (35.5 + margin, 1.75 + margin, 2.8 + margin)),
    ]


def bar_segments(grid: np.ndarray, radius: float, sparse: bool) -> list[tuple]:
    n, m = grid.shape[0] - 1, grid.shape[1] - 1
    step = 3 if sparse else 1
    pieces = []

    def append(a, b):
        segments = [(a, b)]
        for bounds in portals(radius):
            segments = [piece for p, q in segments for piece in outside_box(p, q, bounds)]
        pieces.extend((p, q) for p, q in segments if np.linalg.norm(q - p) > .08)

    for i in range(0, n + 1, step):
        for j in range(0, m + 1, step):
            if i + step <= n:
                append(grid[i, j], grid[i + step, j])
            if j + step <= m and (not sparse or 0 < i < n):
                append(grid[i, j], grid[i, j + step])
            if i + step <= n and j + step <= m:
                if not sparse or (i // step + j // step) % 2 == 0:
                    append(grid[i, j], grid[i + step, j + step])
    return pieces


def cylinders(segments: list[tuple], radius: float, color: np.ndarray) -> trimesh.Trimesh:
    meshes = [trimesh.creation.cylinder(radius=radius, segment=np.array([a, b]), sections=8)
              for a, b in segments]
    mesh = trimesh.util.concatenate(meshes)
    mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        name="light_galvanized_steel", baseColorFactor=STEEL_LINEAR,
        metallicFactor=.12, roughnessFactor=.69))
    return mesh


def portal_frame() -> trimesh.Trimesh:
    parts = []
    for sign in (-1, 1):
        x = sign * 32.4
        # Side walls and two roof leaves form a roofed passage, with a clear
        # 3.5 m wide × 2.8 m high centre for visitors.
        for side in (-1, 1):
            wall = trimesh.creation.box(extents=(5.6, .18, 3.25))
            wall.apply_translation((x, side * 2.57, 1.625))
            wall.visual.vertex_colors = PORTAL
            parts.append(wall)
            roof = trimesh.creation.box(extents=(5.9, 3.04, .18))
            roof.apply_transform(trimesh.transformations.rotation_matrix(-side * .54, (1, 0, 0)))
            roof.apply_translation((x, side * 1.25, 3.94))
            roof.visual.vertex_colors = PORTAL_EDGE
            parts.append(roof)
        for side in (-1, 1):
            post = trimesh.creation.box(extents=(.16, .38, 3.25))
            post.apply_translation((x + sign * 2.91, side * 2.4, 1.625))
            post.visual.vertex_colors = PORTAL
            parts.append(post)
        lintel = trimesh.creation.box(extents=(.16, 3.9, .28))
        lintel.apply_translation((x + sign * 2.91, 0, 3.07))
        lintel.visual.vertex_colors = PORTAL
        parts.append(lintel)
    mesh = trimesh.util.concatenate(parts)
    mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        name="painted_entry_portal", baseColorFactor=[.31, .38, .35, 1],
        metallicFactor=.08, roughnessFactor=.8))
    return mesh


def make_scene(sparse: bool) -> tuple[trimesh.Scene, dict]:
    n, m = NEAR_N, NEAR_M
    grid = point_grid(n, m)
    radius = .09 if sparse else .052  # Sparse radius is presentation-only.
    bars = bar_segments(grid, radius, sparse)
    scene = trimesh.Scene()
    scene.add_geometry(cylinders(bars, radius, STEEL), node_name="steel_rods")
    proxy_segments = []
    if sparse:
        proxy_segments = bar_segments(grid, radius, False)
        proxy = trimesh.load_path(np.asarray(proxy_segments))
        scene.add_geometry(proxy, node_name="fine_structure_line_proxy", geom_name="fine_structure_line_proxy")
    if not sparse:
        visible = [p for p in grid.reshape(-1, 3)
                   if not any(np.all(p >= lo) and np.all(p <= hi) for lo, hi in portals(.078))]
        ball = trimesh.creation.icosphere(subdivisions=1, radius=.078)
        balls = []
        for p in visible:
            mesh = ball.copy()
            mesh.apply_translation(p)
            balls.append(mesh)
        nodes = trimesh.util.concatenate(balls)
        nodes.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            name="light_galvanized_nodes", baseColorFactor=STEEL_LINEAR,
            metallicFactor=.12, roughnessFactor=.69))
        scene.add_geometry(nodes, node_name="steel_nodes")
    scene.add_geometry(portal_frame(), node_name="roofed_entry_exit")
    ring = []
    for i in range(96):
        a, b = 2 * math.pi * i / 96, 2 * math.pi * (i + 1) / 96
        ring.append((np.array([35 * math.cos(a), 20 * math.sin(a), .08]),
                     np.array([35 * math.cos(b), 20 * math.sin(b), .08])))
    scene.add_geometry(cylinders(ring, .09, STEEL), node_name="perimeter_footing")
    # Source coordinates are Z-up; glTF is Y-up. Apply the mapping once at the
    # root so any DCC tool imports a level dome without guessing axis metadata.
    scene.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, (1, 0, 0)))
    report = {"variant": "far" if sparse else "near", "lengthM": LENGTH,
        "widthM": WIDTH, "heightM": HEIGHT, "steelBars": len(bars),
        "renderRadiusM": radius, "measuredRadius": False,
        "radiusInterpretation": "Display radius for distance" if sparse else "Representative radius within the published diameter range; individual pipes were not measured",
        "portalClearOpeningM": [3.5, 2.8],
        "originM5LocalXY": [-30, -64], "rotationOnM5Degrees": 9,
        "triangles": sum(len(m.faces) for m in scene.geometry.values() if isinstance(m, trimesh.Trimesh)),
        "fineStructureProxySegments": len(proxy_segments),
        "fineStructureProxyWidth": "one render pixel, presentation only" if sparse else None,
        "steelSrgbColor": "#aab9af",
        "coordinateConvention": "glTF Y-up; X=longitudinal, Z=transverse",
        "source": "https://uskon.com/en/bursa-zoo-waterbird-cage-single-wall-elliptical-dome/",
        "limitation": "Triangulation, portal details and location approximate; not as-built"}
    return scene, report


def line_material(tree):
    """Assign the line proxy an explicit blend material in the glTF tree.

    Trimesh emits Path3D as standard glTF LINES but assigns a default material.
    This callback changes only that material; the mesh keeps primitive mode 1.
    """
    for mesh in tree.get("meshes", []):
        if mesh.get("name") == "fine_structure_line_proxy":
            index = len(tree["materials"])
            tree["materials"].append({"name": "fine_structure_display_lines",
                "pbrMetallicRoughness": {"baseColorFactor": [*STEEL_LINEAR[:3], .28],
                    "metallicFactor": 0, "roughnessFactor": 1}, "alphaMode": "BLEND"})
            for primitive in mesh["primitives"]:
                primitive["material"] = index


def main() -> None:
    reports = []
    for sparse in (False, True):
        scene, report = make_scene(sparse)
        name = "su-kuslari-kubbesi-uzak.glb" if sparse else "su-kuslari-kubbesi-yakin.glb"
        (HERE / name).write_bytes(scene.export(file_type="glb", include_normals=True, tree_postprocessor=line_material))
        reports.append(report | {"file": name})
        print(name, (HERE / name).stat().st_size, "bytes", report["steelBars"], "bars")
    (HERE / "model-report.json").write_text(json.dumps({"schema": "bursa-zoo-dome-model/v1",
        "variants": reports}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
