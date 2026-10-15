"""Build mutually exclusive XY surface regions for the zoo viewer.

Run with ``python build_surface_layers.py``.  Coordinates remain in the M5
local metre frame; this is a topology pass, not a resurvey of the source data.
The ``building`` output is a mask for the existing building solids, not an
instruction to draw an extra coplanar floor beneath them.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from shapely import make_valid, set_precision
from shapely.affinity import rotate, translate
from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Polygon, box, shape
from shapely.geometry.polygon import orient
from shapely.ops import unary_union


HERE = Path(__file__).resolve().parent
SOURCE_QUANTUM_METRES = 0.001
BUILDING_GRID_METRES = 0.0001
BUILDING_SEAM_CLOSE_METRES = 0.0002
MIN_HOLE_AREA_M2 = 1.0  # Matches the current viewer's provisional path rule.
MIN_POLYGON_AREA_M2 = 0.000001
ISLAND_IDS = {
    "H22D01C2B:58": "H22D01C2B:57",
    "H22D01C2B:61": "H22D01C2B:60",
}
SKIPPED_BUILDING_IDS = {"H22D01C2B:301", "H22D01C2B:243"}  # Dome interior; cafe floor owns243 below.


def polygon_parts(geometry):
    if geometry.is_empty:
        return []
    if isinstance(geometry, Polygon):
        return [geometry] if geometry.area > MIN_POLYGON_AREA_M2 else []
    if isinstance(geometry, (GeometryCollection, MultiPolygon)):
        return [part for child in geometry.geoms for part in polygon_parts(child)]
    return []


def polygonal(geometry):
    parts = polygon_parts(geometry)
    return unary_union(parts) if parts else GeometryCollection()


def clean(geometry):
    """Repair source self-touches without moving surveyed/registered vertices."""
    return polygonal(make_valid(geometry))


def difference(a, b):
    return polygonal(a.difference(b))


def normalized_m5_building_mask(source):
    """Close sub-millimetre M5 hairline gaps on one shared render grid."""
    snapped = polygonal(set_precision(source, BUILDING_GRID_METRES))
    closed = polygonal(set_precision(
        set_precision(snapped, 0)
        .buffer(BUILDING_SEAM_CLOSE_METRES, join_style=2)
        .buffer(-BUILDING_SEAM_CLOSE_METRES, join_style=2),
        BUILDING_GRID_METRES,
    ))
    # Subsequent overlays must not inherit the snap model: GEOS can otherwise
    # silently add or erase skinny polygons while computing intersections.
    return set_precision(closed, 0)


def source_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cage_to_site(local, anchor):
    """Place interpreted cage-local geometry in the registered M5 XY frame."""
    angle = anchor["provisionalShellAngleDegreesCounterclockwiseFromEast"]
    centre_x, centre_y = anchor["provisionalShellCentreXYMetres"]
    return translate(rotate(local, angle, origin=(0, 0)), centre_x, centre_y)


def centripetal_catmull_rom(control, samples):
    """Sample the former viewer centreline, matching Three.js's centripetal spline."""
    def axis(index, weight):
        p1, p2 = control[index:index + 2]
        p0 = control[index - 1] if index else [2 * p1[k] - p2[k] for k in range(2)]
        p3 = control[index + 2] if index + 2 < len(control) else [2 * p2[k] - p1[k] for k in range(2)]
        dt0 = sum((p1[k] - p0[k]) ** 2 for k in range(2)) ** .25
        dt1 = sum((p2[k] - p1[k]) ** 2 for k in range(2)) ** .25
        dt2 = sum((p3[k] - p2[k]) ** 2 for k in range(2)) ** .25
        if dt1 < .0001:
            dt1 = 1
        if dt0 < .0001:
            dt0 = dt1
        if dt2 < .0001:
            dt2 = dt1
        result = []
        for k in range(2):
            x0, x1, x2, x3 = p0[k], p1[k], p2[k], p3[k]
            t1 = ((x1 - x0) / dt0 - (x2 - x0) / (dt0 + dt1) + (x2 - x1) / dt1) * dt1
            t2 = ((x2 - x1) / dt1 - (x3 - x1) / (dt1 + dt2) + (x3 - x2) / dt2) * dt1
            c2 = -3 * x1 + 3 * x2 - 2 * t1 - t2
            c3 = 2 * x1 - 2 * x2 + t1 + t2
            result.append(x1 + t1 * weight + c2 * weight ** 2 + c3 * weight ** 3)
        return result

    result = []
    for sample in range(samples + 1):
        point = (len(control) - 1) * sample / samples
        index = min(int(point), len(control) - 2)
        result.append(axis(index, point - index))
    return result


def cage_path_polygon(spec):
    if spec["kind"] == "centripetalCatmullRom":
        line = centripetal_catmull_rom(spec["controlPoints"], spec["samples"])
    elif spec["kind"] == "harmonicLoop":
        line = []
        for i in range(spec["samples"]):
            angle = 2 * math.pi * i / spec["samples"]
            line.append([
                spec["xCos"] * math.cos(angle) + spec["xSin3"] * math.sin(3 * angle),
                spec["ySin"] * math.sin(angle) + spec["yCos2"] * math.cos(2 * angle),
            ])
        line.append(line[0])
    else:
        raise ValueError(f"Unknown cage walking path type: {spec['kind']}")
    # A single true polygon replaces the old ribbon's separate coplanar mesh.
    # Flat ends preserve the old approach length; round joins soften its bends.
    return LineString(line).buffer(spec["width"] / 2, cap_style="flat", join_style="round")


def serialized_polygons(geometry):
    result = []
    for part in sorted(polygon_parts(geometry), key=lambda p: (-p.area, p.bounds)):
        part = orient(part, sign=1)

        def coordinates(ring):
            # Overlay intersections need their full double precision even
            # though the source vertices were already quantized to 1 mm.
            # Rounding here can create a real overlap along a shared edge.
            return [[float(x), float(y)] for x, y in ring.coords]

        result.append({
            "outer": coordinates(part.exterior),
            "holes": [coordinates(hole) for hole in part.interiors],
        })
    return result


def from_serialized(parts):
    return polygonal(unary_union([
        Polygon(part["outer"], part["holes"]) for part in parts
    ]))


def main():
    site_path = HERE / "site-data.json"
    plan_path = HERE / "current-plan-data.json"
    cage_path = HERE / "cage-local-surfaces.json"
    manual_roads_path = HERE / "v2/manual-roads-metric.json"
    site = json.loads(site_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    cage = json.loads(cage_path.read_text(encoding="utf-8"))
    manual_roads = json.loads(manual_roads_path.read_text(encoding="utf-8"))
    if manual_roads.get("schema") != "bursa-zoo-v2-manual-roads/v2":
        raise ValueError("Unknown QGIS manual road source schema")
    if cage.get("schema") != "bursa-zoo-interpreted-cage-local-surfaces/v1":
        raise ValueError("Unknown cage-local surface source schema")
    boundary = clean(Polygon(site["outline"]))

    water_features = {
        feature["id"]: feature for feature in site["features"]
        if feature["role"] == "water" and feature["closed"]
    }
    water_sources = []
    water_source_ids = []
    for feature_id, feature in water_features.items():
        if feature_id in ISLAND_IDS.values():
            continue
        island = water_features.get(ISLAND_IDS.get(feature_id))
        holes = island["paths"] if island else []
        for path in feature["paths"]:
            if len(path) < 4:
                continue
            water_sources.append(clean(Polygon(path, [h for h in holes if len(h) >= 4])))
            water_source_ids.append(feature_id)

    entrance = next(
        (f for f in plan["features"] if f["id"] == "entrance_pond_5"), None
    )
    if entrance and len(entrance.get("pointsXYMetres", [])) >= 4:
        water_sources.append(clean(Polygon(entrance["pointsXYMetres"])))
        water_source_ids.append("current-plan:entrance_pond_5")
    if len(site.get("alligatorPond", {}).get("outer", [])) >= 4:
        water_sources.append(clean(Polygon(site["alligatorPond"]["outer"])))
        water_source_ids.append("site-data:alligatorPond")

    anchor = next(
        f for f in plan["features"] if f["id"] == "waterbird_aviary_dome_candidate"
    )["modelAnchor"]
    cage_lagoon = cage_to_site(Polygon(cage["lagoonOutline"]), anchor)
    water_sources.append(clean(cage_lagoon))
    water_source_ids.append("cage-local-surfaces.json:lagoonOutline")
    water = clean(unary_union(water_sources).intersection(boundary))

    building_sources = []
    building_source_ids = []
    for feature in site["features"]:
        if feature["role"] != "building" or not feature["closed"]:
            continue
        if feature["id"] in SKIPPED_BUILDING_IDS:
            continue
        for path in feature["paths"]:
            if len(path) >= 4:
                building_sources.append(clean(Polygon(path)))
                building_source_ids.append(feature["id"])
    mill = cage["millFootprint"]
    mx, my = mill["centre"]
    mill_footprint = box(mx - mill["width"] / 2, my - mill["depth"] / 2,
                         mx + mill["width"] / 2, my + mill["depth"] / 2)
    mill_building = cage_to_site(mill_footprint, anchor)
    building_source_ids.append("cage-local-surfaces.json:millFootprint")
    source_m5_building = difference(clean(unary_union(building_sources).intersection(boundary)), water)
    m5_building = normalized_m5_building_mask(source_m5_building)
    building_mask_adjustment = source_m5_building.symmetric_difference(m5_building).area
    if building_mask_adjustment > 0.01:
        raise ValueError(f"M5 building mask moved too far: {building_mask_adjustment:.6f} m2")
    village_input_path=HERE/'bolgeler/14-afrika-koyu/model/model-inputs.json'
    village_floors=GeometryCollection()
    village={}
    if village_input_path.is_file():
        village=json.loads(village_input_path.read_text(encoding='utf-8'))
        if village['siteDataSha256']!=source_hash(site_path):
            raise ValueError('African Village source changed; review interpreted floors')
        village_floors=clean(unary_union([Polygon(h['wallOutlineM5XY']) for h in village['huts']]))
        building_source_ids.extend([h['sourceId']+':interpreted-wall-footprint' for h in village['huts']])
    cafe_input_path=HERE/'bolgeler/13-afrika-kafe/model/model-inputs.json'
    cafe=json.loads(cafe_input_path.read_text(encoding='utf-8'))
    if cafe['siteDataSha256']!=source_hash(site_path):
        raise ValueError('Cafe source changed; review native floor outlines')
    cafe_floors=clean(unary_union([Polygon(r['outlineM5XY']) for r in cafe['roofs']]))
    building_source_ids.extend([r['sourceId']+':cafe-floor' for r in cafe['roofs']])
    habes_input_path=HERE/'bolgeler/09-habes-maymunu/model/model-inputs.json'
    habes=json.loads(habes_input_path.read_text(encoding='utf-8'))
    if habes['siteDataSha256']!=source_hash(site_path):
        raise ValueError('Habes island source changed; review interpreted coping')
    habes_island=Polygon(habes['islandOutlineM5XY'])
    habes_coping=clean(habes_island.difference(habes_island.buffer(-habes['interpretedDimensions']['bankWidth'],join_style='round')))
    building_source_ids.append(habes['islandSourceId']+':interpreted-coping')
    bear_input_path=HERE/'bolgeler/29-boz-ayi/model/model-inputs.json'
    bear=json.loads(bear_input_path.read_text(encoding='utf-8'))
    if bear['siteDataSha256']!=source_hash(site_path):
        raise ValueError('Bear pool source changed; review interpreted bank')
    bear_pool=Polygon(bear['poolOutlineM5XY'])
    bear_bank=clean(unary_union([Polygon(p['outer'],p['holes']) for p in bear['interpretedBankMaskM5XY']]))
    building_source_ids.append(bear['poolSourceId']+':interpreted-bank')
    rhino_input_path=HERE/'bolgeler/16-gergedan/model/habitat-inputs.json'
    rhino_floor=GeometryCollection()
    if rhino_input_path.is_file():
        rhino_inputs=json.loads(rhino_input_path.read_text(encoding='utf-8'))
        if rhino_inputs['siteDataSha256']!=source_hash(site_path):
            raise ValueError('Rhino source frame changed')
        rhino_floor=Polygon(rhino_inputs['compoundOutlineM5XY'])
        building_source_ids.append('official-map:rhino16-model-owned-compound-floor')
    giraffe_input_path=HERE/'bolgeler/12-afrika-savana/model/giraffe/habitat-inputs.json'
    giraffe_floor=GeometryCollection()
    if giraffe_input_path.is_file():
        giraffe_inputs=json.loads(giraffe_input_path.read_text(encoding='utf-8'))
        if giraffe_inputs['siteDataSha256']!=source_hash(site_path):
            raise ValueError('Giraffe source frame changed')
        giraffe_floor=clean(unary_union([Polygon(p['outer'],p.get('holes',[])) for p in giraffe_inputs['floorOwnershipMasks']]))
        building_source_ids.append('official-map:savanna12-model-owned-open-section-floor')
    penguin_input_path=HERE/'bolgeler/15-penguen/model/model-inputs.json'
    penguin=json.loads(penguin_input_path.read_text(encoding='utf-8'))
    penguin_pool=Polygon(penguin['waterOutline']['outer'],penguin['waterOutline']['holes'])
    penguin_rim=clean(penguin_pool.buffer(.57,quad_segs=6).difference(penguin_pool))
    building_source_ids.append(penguin['sourceWaterFeatureId']+':model-owned-coping-and-drain')
    building = difference(clean(unary_union([m5_building, mill_building, village_floors, cafe_floors, habes_coping, bear_bank,rhino_floor,giraffe_floor,penguin_rim]).intersection(boundary)), water)

    # The manually drawn QGIS surfaces replace the old M5 buffer preview.
    # Both are already in the same local metre grid; surface priority removes
    # any parts under water or buildings without stacking coplanar meshes.
    road_features = {feature["id"]: feature for feature in manual_roads["features"]}
    if set(road_features) != {"pedestrian_surface", "vehicle_surface"}:
        raise ValueError("QGIS roads must contain pedestrian and vehicle surfaces")
    path_sources = [clean(shape(road_features[key]["geometry"]))
                    for key in ("pedestrian_surface", "vehicle_surface")]
    local_path_ids = []
    for spec in village.get('interpretedPathConnectors',[]):
        path_sources.append(clean(LineString(spec['pointsM5XY']).buffer(spec['widthMetres']/2)))
        local_path_ids.append(spec['id'])
    for spec in cage["walkingPaths"]:
        path_sources.append(clean(cage_to_site(cage_path_polygon(spec), anchor)))
        local_path_ids.append(spec["id"])
    path = difference(clean(unary_union(path_sources).intersection(boundary)),
                      unary_union([water, building]))
    terrain = difference(boundary, unary_union([water, building, path]))

    layers = {"water": water, "building": building, "path": path, "terrain": terrain}
    union = unary_union(list(layers.values()))
    checks = {
        "boundaryAreaM2": round(boundary.area, 6),
        "layerAreasM2": {name: round(geom.area, 6) for name, geom in layers.items()},
        "uncoveredAreaM2": round(boundary.difference(union).area, 9),
        "outsideBoundaryAreaM2": round(union.difference(boundary).area, 9),
        "pairwiseOverlapAreaM2": {},
        "m5BuildingMaskAdjustmentAreaM2": round(building_mask_adjustment, 6),
        "africanVillageInterpretedFloorAreaM2":round(village_floors.area,6),
        "africanCafeFloorAreaM2":round(cafe_floors.area,6),
    }
    names = list(layers)
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            overlap = layers[first].intersection(layers[second]).area
            checks["pairwiseOverlapAreaM2"][f"{first}/{second}"] = round(overlap, 9)
            if overlap > 0.000001:
                raise ValueError(f"Surface overlap: {first}/{second}: {overlap:.6f} m2")
    partition_delta = boundary.symmetric_difference(union).area
    if partition_delta > 0.000001:
        raise ValueError(f"Surface partition does not cover boundary: {partition_delta:.9f} m2")

    output_layers = {name: serialized_polygons(geom) for name, geom in layers.items()}
    for part in output_layers['water']:
        if Polygon(part['outer'],part['holes']).intersection(bear_pool).area>.1:
            part['waterPresentationColor']=bear['waterPresentationColor']
        if Polygon(part['outer'],part['holes']).intersection(penguin_pool).area>.1:
            part['waterReflectionStrength']=.55
    # Material regions split the terrain; no second gravel cap is stacked
    # above grass. The original water/building/path ownership stays intact.
    penguin_input_path = HERE / "bolgeler/15-penguen/model/model-inputs.json"
    if penguin_input_path.is_file():
        penguin = json.loads(penguin_input_path.read_text(encoding="utf-8"))
        mask = penguin["gravelContextMask"]
        gravel = clean(terrain.intersection(Polygon(mask["outer"],mask["holes"])))
        grass = difference(terrain,gravel)
        output_layers["terrain"] = serialized_polygons(grass) + [
            part | {"surfaceStyle":"penguin-gravel"} for part in serialized_polygons(gravel)]
        checks["penguinGravelAreaM2"] = round(gravel.area,6)
        checks["terrainStyleOverlapM2"] = round(grass.intersection(gravel).area,9)
        if grass.intersection(gravel).area > 0.000001:
            raise ValueError("Terrain material regions overlap")
    habes_earth=clean(terrain.intersection(habes_island))
    styled=[]
    for part in output_layers['terrain']:
        remaining=difference(Polygon(part['outer'],part['holes']),habes_earth)
        styled.extend(p|({'surfaceStyle':part['surfaceStyle']} if 'surfaceStyle' in part else {})
                      for p in serialized_polygons(remaining))
    output_layers['terrain']=styled+[p|{'surfaceStyle':'habes-earth'} for p in serialized_polygons(habes_earth)]
    checks['habesEarthAreaM2']=round(habes_earth.area,6)
    checks['habesCopingAreaM2']=round(habes_coping.area,6)
    checks['bearBankInterpretedAreaM2']=round(bear_bank.area,6)
    # A triangle generator consumes JSON, so validate the serialized rings too.
    for name, parts in output_layers.items():
        for part in parts:
            if not Polygon(part["outer"], part["holes"]).is_valid:
                raise ValueError(f"Invalid serialized {name} polygon")
        if layers[name].symmetric_difference(from_serialized(parts)).area > 0.000001:
            raise ValueError(f"Serialized {name} layer changed topology")
    serialized_geometries = {name: from_serialized(parts) for name, parts in output_layers.items()}
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            overlap = serialized_geometries[first].intersection(serialized_geometries[second]).area
            if overlap > 0.000001:
                region = serialized_geometries[first].intersection(serialized_geometries[second])
                raise ValueError(f"Serialized layers overlap: {first}/{second}: {overlap:.9f} m2, {region.wkt[:500]}")
    serialized_union = unary_union(list(serialized_geometries.values()))
    if boundary.symmetric_difference(serialized_union).area > 0.000001:
        raise ValueError("Serialized layers do not cover the boundary")

    # Decorative stones belong only to road-to-land edges, with space for their
    # physical radius. Pool rims, water and separately modelled walls own theirs.
    curb_geometry=path.boundary.intersection(terrain.boundary).difference(water.buffer(.40)).difference(building.buffer(.35))
    def curb_lines(g):
        if g.is_empty:return []
        if g.geom_type=='LineString':return [[list(p) for p in g.coords]] if g.length>.4 else []
        return [line for child in getattr(g,'geoms',[]) for line in curb_lines(child)]
    road_curb_lines=curb_lines(curb_geometry)
    checks['penguinRimPathOverlapM2']=round(penguin_rim.intersection(path).area,9)
    checks['penguinRimTerrainOverlapM2']=round(penguin_rim.intersection(terrain).area,9)
    checks['roadCurbLengthM']=round(sum(LineString(line).length for line in road_curb_lines),3)
    result = {
        "schema": "bursa-zoo-planar-surface-partition/v1",
        "coordinateFrame": site["coordinateFrame"],
        "originEd50": site["originEd50"],
        "unit": "metre",
        "sourceCoordinateQuantumMetres": SOURCE_QUANTUM_METRES,
        "priority": ["water", "building", "path", "terrain"],
        "renderLevels": {"terrainZ": -.24, "pathBottomZ": -.24, "pathTopZ": -.105, "waterZ": -.32},
        "renderLevelsAreSurveyed": False,
        "roadCurbLines":road_curb_lines,
        "source": {
            "siteDataSha256": source_hash(site_path),
            "currentPlanDataSha256": source_hash(plan_path),
            "cageLocalSurfacesSha256": source_hash(cage_path),
            "manualQgisRoadsSha256": source_hash(manual_roads_path),
            "penguinMaterialInputsSha256": source_hash(penguin_input_path) if penguin_input_path.is_file() else None,
            "africanVillageInputsSha256":source_hash(village_input_path) if village_input_path.is_file() else None,
            "africanCafeInputsSha256":source_hash(cafe_input_path),
            "habesInputsSha256":source_hash(habes_input_path),
            "bearInputsSha256":source_hash(bear_input_path),
            "waterSourceIds": water_source_ids,
            "buildingSourceIds": building_source_ids,
            "pathSource": "v2/manual-roads-metric.json:pedestrian_surface+vehicle_surface (Dot QGIS delivery), interpreted cage walks and African Village local connector",
            "cageLocalPathIds": local_path_ids,
        },
        "usage": {
            "building": "Footprint exclusion mask for existing solids; do not draw as another floor mesh.",
            "water": "Includes the interpreted cage lagoon; draw each water region once.",
            "path": "Provisional manually redrawn QGIS surfaces and interpreted cage walks; clipped away from water and buildings.",
            "terrain": "Remainder of the OSM-clipped boundary after higher-priority surfaces.",
        },
        "cageLocal": {
            "lagoonOutline": cage["lagoonOutline"],
            "westernBridgeRamp": cage["westernBridgeRamp"],
        },
        "unresolved": [{
            "id": "intentional_cage_3d_contacts",
            "reason": "The raised wooden bridge and railings cross the lagoon in 3D; individual bank stones, cage footing beams and portal posts meet the partitioned ground. These volumetric contacts do not introduce a second planar surface.",
        }],
        "checks": checks,
        "layers": output_layers,
    }
    output_path = HERE / "surface-layers.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n",
                           encoding="utf-8")
    print(f"Wrote {output_path.name}")
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    print("Polygon counts:", {key: len(value) for key, value in output_layers.items()})


if __name__ == "__main__":
    main()
