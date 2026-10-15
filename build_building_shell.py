"""Build a single exterior 2.5D shell for the provisional M5 building masses.

Each XY location receives the highest surveyed candidate roof. The output has
disjoint roof caps and one wall only where the height field changes, so the
viewer does not draw overlapping closed extrusions or internal side faces.
Run after ``build_surface_layers.py``.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess

from shapely import set_precision
from shapely.geometry import GeometryCollection, LineString, MultiLineString, MultiPolygon, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from build_surface_layers import (
    BUILDING_GRID_METRES,
    BUILDING_SEAM_CLOSE_METRES,
    clean,
    normalized_m5_building_mask,
    polygonal,
)


HERE = Path(__file__).resolve().parent
BASE_Z = -0.24
PATH_TOP_Z = -0.105  # viewer/model.js: path extrusion from -0.24 with 0.135 depth.
ROOF_OFFSET = 0.02
SKIPPED_IDS = {"H22D01C2B:301", "H22D01C2B:243"} | {
    f"H22D01C2B:{number}" for number in list(range(229, 237)) + [244]
}  # Separate cage, cafe and Turkish-village models own these footprints.
AREA_TOLERANCE = 0.000001
WALL_SNAP_METRES = BUILDING_GRID_METRES
NEAR_WALL_TOLERANCE = 1e-4  # 0.1 mm is below the 1 mm M5 source quantum.
MAX_PRECISION_ADJUSTMENT_AREA = 0.01
NARROW_SEAM_CLOSE_METRES = BUILDING_SEAM_CLOSE_METRES


def clean_ring(coordinates):
    """Remove GEOS overlay duplicates without moving surveyed cap edges."""
    points = [[float(x), float(y)] for x, y in coordinates[:-1]]
    unique = []
    for point in points:
        if unique and math.dist(point, unique[-1]) < 1e-10:
            continue
        unique.append(point)
    while len(unique) > 3 and math.dist(unique[0], unique[-1]) < 1e-10:
        unique.pop()
    if len(unique) < 3:
        raise ValueError("Building ring collapsed below three unique vertices")
    return unique + [unique[0]]


def polygon_parts(geometry):
    if geometry.is_empty:
        return []
    if isinstance(geometry, Polygon):
        return [geometry] if geometry.area > 1e-10 else []
    if isinstance(geometry, (GeometryCollection, MultiPolygon)):
        return [part for child in geometry.geoms for part in polygon_parts(child)]
    return []


def line_parts(geometry):
    if geometry.is_empty:
        return []
    if isinstance(geometry, LineString):
        return [geometry]
    if isinstance(geometry, (GeometryCollection, MultiLineString)):
        return [part for child in geometry.geoms for part in line_parts(child)]
    return []


def rings(geometry):
    result = []
    for part in sorted(polygon_parts(geometry), key=lambda p: (-p.area, p.bounds)):
        part = orient(part, sign=1)
        result.append({
            "outer": clean_ring(part.exterior.coords),
            "holes": [
                clean_ring(hole.coords)
                for hole in part.interiors
            ],
        })
    return result


def from_rings(parts):
    return polygonal(unary_union([
        Polygon(part["outer"], part["holes"]) for part in parts
    ]))


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def outward_wall_endpoints(a, b, high_geometry):
    """Orient a wall so its right-hand triangle normal faces outside high roof."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = (dx * dx + dy * dy) ** 0.5
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    left_x, left_y = -dy / length, dx / length
    for epsilon in (1e-6, 1e-7, 1e-5, 1e-4, 5e-4, 1e-3, 1e-2):
        left_inside = high_geometry.contains(Point(mx + left_x * epsilon, my + left_y * epsilon))
        right_inside = high_geometry.contains(Point(mx - left_x * epsilon, my - left_y * epsilon))
        if left_inside != right_inside:
            return (a, b) if left_inside else (b, a)
    raise ValueError(f"Cannot determine outward normal for building wall {a} → {b}")


def near_wall_overlap(first, second):
    """Return an overlapping XY section despite GEOS micrometre edge drift."""
    if min(first["top"], second["top"]) - max(first["bottom"], second["bottom"]) <= 0.01:
        return None
    tolerance = NEAR_WALL_TOLERANCE
    first_x = sorted((first["a"][0], first["b"][0]))
    first_y = sorted((first["a"][1], first["b"][1]))
    second_x = sorted((second["a"][0], second["b"][0]))
    second_y = sorted((second["a"][1], second["b"][1]))
    if first_x[1] + tolerance < second_x[0] or second_x[1] + tolerance < first_x[0] or first_y[1] + tolerance < second_y[0] or second_y[1] + tolerance < first_y[0]:
        return None
    first_line = LineString([first["a"], first["b"]])
    second_line = LineString([second["a"], second["b"]])
    # A tolerant line buffer extends beyond its endpoints. Adjacent edges at
    # a shallow angle can otherwise be mistaken for several metres of double
    # wall, even though their projected interiors never overlap.
    ux = (first["b"][0] - first["a"][0]) / first_line.length
    uy = (first["b"][1] - first["a"][1]) / first_line.length
    projected = [
        (point[0] - first["a"][0]) * ux + (point[1] - first["a"][1]) * uy
        for point in (second["a"], second["b"])
    ]
    projected_start = max(0.0, min(projected))
    projected_end = min(first_line.length, max(projected))
    if projected_end - projected_start <= 0.01:
        return None
    if first_line.distance(second_line) > tolerance:
        return None
    overlaps = [
        part for part in line_parts(first_line.intersection(second_line.buffer(tolerance)))
        if part.length > 0.01
    ]
    return max(overlaps, key=lambda part: part.length) if overlaps else None


def split_wall(wall, start, end, middle_bottom=None):
    """Split one wall along XY; None removes its overlapping middle section."""
    line = LineString([wall["a"], wall["b"]])
    length = line.length
    start, end = max(0.0, min(start, end)), min(length, max(start, end))
    sections = [(0.0, start, wall["bottom"])]
    if middle_bottom is not None:
        sections.append((start, end, middle_bottom))
    sections.append((end, length, wall["bottom"]))
    output = []
    for t0, t1, bottom in sections:
        if t1 - t0 < 1e-3 or wall["top"] - bottom < 1e-6:
            continue
        a, b = line.interpolate(t0), line.interpolate(t1)
        output.append({
            "a": [float(a.x), float(a.y)],
            "b": [float(b.x), float(b.y)],
            "bottom": float(bottom),
            "top": wall["top"],
        })
    return output


def resolve_near_wall_overlaps(walls):
    """Dissolve coincident vertical patches into one exposed height step."""
    walls = list(walls)
    for _ in range(1000):
        pair = None
        for i, first in enumerate(walls):
            for j in range(i + 1, len(walls)):
                overlap = near_wall_overlap(first, walls[j])
                if overlap is not None:
                    pair = i, j, overlap
                    break
            if pair is not None:
                break
        if pair is None:
            return walls
        i, j, overlap = pair
        first, second = walls[i], walls[j]
        if (second["top"], LineString([second["a"], second["b"]]).length) > (first["top"], LineString([first["a"], first["b"]]).length):
            # Recompute the overlap on the dominant wall's line.
            i, j = j, i
            first, second = second, first
            overlap = near_wall_overlap(first, second)
            if overlap is None:
                raise ValueError("Near-wall overlap disappeared after swapping")
        first_line = LineString([first["a"], first["b"]])
        second_line = LineString([second["a"], second["b"]])
        start = first_line.project(Point(overlap.coords[0]))
        end = first_line.project(Point(overlap.coords[-1]))
        lower_top = second["top"]
        first_parts = split_wall(first, start, end, max(first["bottom"], lower_top))
        second_start = second_line.project(Point(overlap.coords[0]))
        second_end = second_line.project(Point(overlap.coords[-1]))
        second_parts = split_wall(second, second_start, second_end)
        walls = [wall for k, wall in enumerate(walls) if k not in (i, j)] + first_parts + second_parts
    raise ValueError("Near-wall cleanup did not converge")


def main():
    site_path = HERE / "site-data.json"
    surface_path = HERE / "surface-layers.json"
    site = json.loads(site_path.read_text(encoding="utf-8"))
    surfaces = json.loads(surface_path.read_text(encoding="utf-8"))
    if surfaces.get("schema") != "bursa-zoo-planar-surface-partition/v1":
        raise ValueError("Build the surface partition before the building shell")
    building_mask = from_rings(surfaces["layers"]["building"])
    path_surface = from_rings(surfaces["layers"]["path"])

    candidates = []
    raw_footprints = []
    for feature in site["features"]:
        if feature["role"] != "building" or not feature["closed"]:
            continue
        if feature["id"] in SKIPPED_IDS:
            continue
        height = max(2.0, min(8.0, feature["sourceH"] - 93.5))
        for path_index, path in enumerate(feature["paths"]):
            if len(path) < 4:
                continue
            raw_footprint = clean(Polygon(path))
            raw_footprints.append(raw_footprint)
            footprint = polygonal(raw_footprint.intersection(building_mask))
            if footprint.is_empty:
                continue
            candidates.append({
                "id": feature["id"],
                "pathIndex": path_index,
                "height": height,
                "footprint": footprint,
            })
    # The shared building mask also contains the separately modeled cage mill.
    # This shell owns only the M5 candidates; the mill remains in makeCage().
    source_target_mask = polygonal(unary_union(raw_footprints).intersection(building_mask))
    # The M5 outlines contain sub-millimetre hairpin gaps. Their two nearly
    # parallel sides would both become vertical walls but collapse together in
    # Float32. Use the same normalization as the surface partition.
    target_mask = normalized_m5_building_mask(source_target_mask)
    # The surface partition gives water priority and clips to the site.
    # Honor that exact footprint after the local M5 normalization so the
    # shell base shares no positive XY area with paths, terrain or water.
    target_mask = polygonal(target_mask.intersection(set_precision(building_mask, 0)))
    surface_intersections = {
        name: target_mask.intersection(from_rings(surfaces["layers"][name])).area
        for name in ("water", "path", "terrain")
    }
    if any(area > AREA_TOLERANCE for area in surface_intersections.values()):
        raise ValueError(f"Building base overlaps other surface masks: {surface_intersections}")
    precision_adjustment = source_target_mask.symmetric_difference(target_mask).area
    if precision_adjustment > MAX_PRECISION_ADJUSTMENT_AREA:
        raise ValueError(f"Building grid moved M5 mask too far: {precision_adjustment:.6f} m2")
    for candidate in candidates:
        candidate_footprint = set_precision(candidate["footprint"], WALL_SNAP_METRES)
        # Claim the microscopic seam fill for an adjacent real roof. The
        # taller roof still wins in the regular height partition below.
        candidate_footprint = set_precision(candidate_footprint, 0).buffer(
            NARROW_SEAM_CLOSE_METRES, join_style=2
        )
        candidate_footprint = set_precision(
            set_precision(candidate_footprint, WALL_SNAP_METRES), 0
        )
        candidate["footprint"] = polygonal(candidate_footprint.intersection(target_mask))
    # When candidates intersect, the taller roof is the visible one. Stable
    # source order breaks ties without creating two caps at the same height.
    candidates.sort(key=lambda c: (-c["height"], c["id"], c["pathIndex"]))
    covered = GeometryCollection()
    roof_regions = []
    for candidate in candidates:
        visible = polygonal(candidate["footprint"].difference(covered))
        if not visible.is_empty:
            roof_regions.append({**candidate, "geometry": visible})
        covered = polygonal(unary_union([covered, candidate["footprint"]]))

    roof_union = polygonal(unary_union([r["geometry"] for r in roof_regions]))
    uncovered = target_mask.symmetric_difference(roof_union).area
    if uncovered > AREA_TOLERANCE:
        raise ValueError(f"Building shell does not cover building mask: {uncovered:.9f} m2")
    for i, first in enumerate(roof_regions):
        for second in roof_regions[i + 1:]:
            area = first["geometry"].intersection(second["geometry"]).area
            if area > AREA_TOLERANCE:
                raise ValueError(f"Roofs overlap: {first['id']}/{second['id']}: {area:.9f} m2")

    # Use exactly the cleaned rings that the viewer will triangulate when
    # deriving walls. Otherwise sub-nanometre slivers can create two wall
    # segments along what should be one roof edge.
    for region in roof_regions:
        serialized = rings(region["geometry"])
        for part in serialized:
            if not Polygon(part["outer"], part["holes"]).is_valid:
                raise ValueError(f"Cleaned roof ring is invalid: {region['id']}")
        region["geometry"] = from_rings(serialized)
    cleaned_union = polygonal(unary_union([r["geometry"] for r in roof_regions]))
    cleaned_difference = target_mask.symmetric_difference(cleaned_union).area
    if cleaned_difference > AREA_TOLERANCE:
        raise ValueError(f"Cleaned roof rings changed the building footprint: {cleaned_difference:.9f} m2")

    # The cleaned M5 mask is authoritative for base and exterior walls.
    # Roof overlay may retain a zero-area internal seam despite equal area;
    # that seam must not be mistaken for an exterior wall.
    wall_regions = roof_regions
    wall_covered = cleaned_union
    wall_footprint_shift = target_mask.symmetric_difference(wall_covered).area
    if wall_footprint_shift > AREA_TOLERANCE:
        raise ValueError(f"Snapped wall footprint moved too far: {wall_footprint_shift:.6f} m2")
    wall_path = polygonal(set_precision(set_precision(path_surface, WALL_SNAP_METRES), 0).difference(target_mask))

    # Unary union nodes coincident wall-region boundaries at height changes.
    # Each elementary line has one roof on an exterior edge or two adjacent
    # roofs at a step. Emit exactly one vertical quad for that line.
    # Noding with path boundaries also splits outside walls where the adjoining
    # paving changes to terrain. The paved extrusion owns the buried 0.135 m
    # side there; the building wall begins at its top instead of duplicating it.
    linework = unary_union([r["geometry"].boundary for r in wall_regions] + [wall_path.boundary])
    walls = []
    for line in line_parts(linework):
        points = list(line.coords)
        for a, b in zip(points, points[1:]):
            segment = LineString([a, b])
            if segment.length < 1e-3:
                continue
            midpoint = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            touching = [
                r for r in wall_regions
                if r["geometry"].boundary.distance(midpoint) < 1e-7
            ]
            if not touching:
                continue  # A path boundary away from every building.
            if len(touching) not in (1, 2):
                raise ValueError(f"Unclassified building wall {a} → {b}: {len(touching)} roofs")
            if len(touching) == 1 and target_mask.boundary.distance(midpoint) > NEAR_WALL_TOLERANCE:
                continue  # Zero-area seam within the same M5 building base.
            elevations = sorted([r["height"] + ROOF_OFFSET for r in touching])
            bottom = BASE_Z if len(elevations) == 1 else elevations[0]
            top = elevations[-1]
            if top - bottom < 1e-9:
                continue
            high_region = max(touching, key=lambda r: r["height"])
            a, b = outward_wall_endpoints(a, b, high_region["geometry"])
            if len(elevations) == 1:
                dx, dy = b[0] - a[0], b[1] - a[1]
                length = (dx * dx + dy * dy) ** 0.5
                mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
                if wall_path.contains(Point(mx + dy / length * 1e-6, my - dx / length * 1e-6)):
                    bottom = PATH_TOP_Z
            walls.append({
                "a": [float(a[0]), float(a[1])],
                "b": [float(b[0]), float(b[1])],
                "bottom": float(bottom),
                "top": float(top),
            })

    # Exterior faces have a different rule from internal height steps. Build
    # them directly from the one authoritative M5 base footprint, then clean
    # up only walls in its interior. In particular, an outside wall must never
    # lose its lower face when a nearby lower roof shares its XY edge.
    outside_boundary = target_mask.boundary
    inside_walls = []
    outside_buffer = outside_boundary.buffer(NEAR_WALL_TOLERANCE)
    for wall in walls:
        remaining = LineString([wall["a"], wall["b"]]).difference(outside_buffer)
        for part in line_parts(remaining):
            if part.length >= 1e-3:
                inside_walls.append({**wall, "a": list(part.coords[0]), "b": list(part.coords[-1])})
    inside_walls = resolve_near_wall_overlaps(inside_walls)

    def exterior_profile(a, b, fraction):
        x = a[0] + (b[0] - a[0]) * fraction
        y = a[1] + (b[1] - a[1]) * fraction
        point = Point(x, y)
        touching = [r for r in roof_regions if r["geometry"].distance(point) < NEAR_WALL_TOLERANCE]
        if not touching:
            raise ValueError(f"Exterior wall has no roof at {(x, y)}")
        top = max(r["height"] for r in touching) + ROOF_OFFSET
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = (dx * dx + dy * dy) ** 0.5
        out_point = Point(x + dy / length * 1e-6, y - dx / length * 1e-6)
        bottom = PATH_TOP_Z if path_surface.contains(out_point) else BASE_Z
        return bottom, top

    outside_walls = []
    def add_exterior(a, b, depth=0):
        length = LineString([a, b]).length
        if length < 1e-3:
            return
        a, b = outward_wall_endpoints(a, b, target_mask)
        profiles = [exterior_profile(a, b, fraction) for fraction in (0.1, 0.5, 0.9)]
        if len(set(profiles)) > 1 and length > 1e-3 and depth < 18:
            middle = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            add_exterior(a, middle, depth + 1)
            add_exterior(middle, b, depth + 1)
            return
        bottom, top = profiles[1]
        outside_walls.append({"a": list(a), "b": list(b), "bottom": bottom, "top": top})

    for line in line_parts(outside_boundary):
        for a, b in zip(line.coords, list(line.coords)[1:]):
            add_exterior(a, b)
    walls = inside_walls + outside_walls

    roofs = []
    for region in roof_regions:
        for part in rings(region["geometry"]):
            roofs.append({
                "sourceId": region["id"],
                "sourcePathIndex": region["pathIndex"],
                "z": float(region["height"] + ROOF_OFFSET),
                **part,
            })
    bases = rings(target_mask)
    serialized_union = from_rings(roofs)
    if target_mask.symmetric_difference(serialized_union).area > AREA_TOLERANCE:
        raise ValueError("Serialized roofs changed the building footprint")
    if target_mask.symmetric_difference(from_rings(bases)).area > AREA_TOLERANCE:
        raise ValueError("Serialized base changed the building footprint")

    # Exact line intersections miss nearly coincident GEOS overlay edges. A
    # tolerant XY and Z check is the publication gate for duplicate wall faces.
    wall_lines = [LineString([wall["a"], wall["b"]]) for wall in walls]
    near_duplicates = []
    for i, first in enumerate(walls):
        for j in range(i + 1, len(walls)):
            second = walls[j]
            shared_height = min(first["top"], second["top"]) - max(first["bottom"], second["bottom"])
            if shared_height <= 0.01:
                continue
            if near_wall_overlap(first, second) is not None:
                near_duplicates.append((i, j))
    if near_duplicates:
        examples = [
            (i, j, walls[i], walls[j]) for i, j in near_duplicates[:3]
        ]
        raise ValueError(f"Near-coincident building walls: {examples} ({len(near_duplicates)} pairs; {len(inside_walls)} interior, {len(outside_walls)} exterior)")
    outside_uncovered = outside_boundary.difference(unary_union(wall_lines).buffer(NEAR_WALL_TOLERANCE)).length
    if outside_uncovered > 0.01:
        raise ValueError(f"Exterior building wall gap: {outside_uncovered:.6f} m")

    result = {
        "schema": "bursa-zoo-building-shell/v1",
        "unit": "metre",
        "coordinateFrame": site["coordinateFrame"],
        "source": {
            "siteDataSha256": file_hash(site_path),
            "surfaceLayersSha256": file_hash(surface_path),
            "skippedBuildingIds": sorted(SKIPPED_IDS),
        },
        "baseZ": BASE_Z,
        "method": "Visible roof = each footprint minus all higher roofs; walls only at exterior and roof-height steps.",
        "checks": {
            "candidateCount": len(candidates),
            "roofCount": len(roofs),
            "baseCount": len(bases),
            "wallCount": len(walls),
            "m5BuildingMaskAreaM2": round(source_target_mask.area, 6),
            "renderBuildingMaskAreaM2": round(target_mask.area, 6),
            "precisionAdjustmentAreaM2": round(precision_adjustment, 6),
            "otherSurfaceOverlapAreaM2": {
                name: round(area, 9) for name, area in surface_intersections.items()
            },
            "separatelyModeledBuildingAreaM2": round(building_mask.difference(source_target_mask).area, 6),
            "roofAreaM2": round(sum(Polygon(r["outer"], r["holes"]).area for r in roofs), 6),
            "uncoveredAreaM2": round(uncovered, 9),
            "wallFaceAreaM2": round(sum(LineString([w["a"], w["b"]]).length * (w["top"] - w["bottom"]) for w in walls), 6),
            "pathEdgeWallLengthM": round(sum(LineString([w["a"], w["b"]]).length for w in walls if w["bottom"] == PATH_TOP_Z), 6),
            "nearDuplicateWallPairs": len(near_duplicates),
            "exteriorWallCount": len(outside_walls),
            "exteriorWallUncoveredM": round(outside_uncovered, 6),
            "wallFootprintShiftAreaM2": round(wall_footprint_shift, 6),
        },
        "roofs": roofs,
        "bases": bases,
        "walls": walls,
    }
    output_path = HERE / "building-shell.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {output_path.name}")
    print(json.dumps(result["checks"], indent=2))
    subprocess.run(["node", str(HERE / "verify_building_shell.mjs")], cwd=HERE, check=True)


if __name__ == "__main__":
    main()
