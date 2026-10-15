"""Deterministic visual planting on the exclusive terrain surface.

This is a scenic layer inspired by the approved woodland mockup. It is not a
survey of individual 2026 trees or species. Points are derived from the single
terrain polygon, never placed on path, water or building top surfaces.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep


ROOT = Path(__file__).resolve().parent
SURFACE = ROOT / "surface-layers.json"
SITE = ROOT / "site-data.json"
CAGE_X, CAGE_Y, CAGE_ANGLE = -30.0, -64.0, math.radians(9)


def inside_cage_margin(x: float, y: float, length: float = 42, width: float = 27) -> bool:
    dx, dy = x - CAGE_X, y - CAGE_Y
    u = dx * math.cos(CAGE_ANGLE) + dy * math.sin(CAGE_ANGLE)
    v = -dx * math.sin(CAGE_ANGLE) + dy * math.cos(CAGE_ANGLE)
    return (u / length) ** 2 + (v / width) ** 2 < 1


def cell_points(bounds, spacing: float, seed: int):
    randomizer = random.Random(seed)
    x0, y0, x1, y1 = bounds
    ix0, ix1 = math.floor(x0 / spacing), math.ceil(x1 / spacing)
    iy0, iy1 = math.floor(y0 / spacing), math.ceil(y1 / spacing)
    for ix in range(ix0, ix1):
        for iy in range(iy0, iy1):
            x = (ix + .18 + randomizer.random() * .64) * spacing
            y = (iy + .18 + randomizer.random() * .64) * spacing
            yield x, y, randomizer


def main() -> None:
    partition = json.loads(SURFACE.read_text(encoding="utf-8"))
    site = json.loads(SITE.read_text(encoding="utf-8"))
    current_plan=json.loads((ROOT/'current-plan-data.json').read_text(encoding='utf-8'))
    savanna=next(f for f in current_plan['features'] if f['id']=='savanna_visitor_circuit')
    open_savanna=Polygon(savanna['pointsXYMetres']).buffer(-5)
    lemur_island=Polygon(next(f for f in site['features'] if f['id']=='H22D01C2B:60')['paths'][0])
    lemur_moat=Polygon(next(f for f in site['features'] if f['id']=='H22D01C2B:61')['paths'][0])
    habes_island=Polygon(next(f for f in site['features'] if f['id']=='H22D01C2B:57')['paths'][0])
    habes_moat=Polygon(next(f for f in site['features'] if f['id']=='H22D01C2B:58')['paths'][0])
    bear_pool=Polygon(next(f for f in site['features'] if f['id']=='H22D01C2B:278')['paths'][0])
    bear_inputs=json.loads((ROOT/'bolgeler/29-boz-ayi/model/model-inputs.json').read_text(encoding='utf-8'))
    bear_rocks=unary_union([Point(r['xyM5']).buffer(r['size'][0]*1.35+.35) for r in bear_inputs['interpretedRocks']])
    rhino=Polygon(json.loads((ROOT/'bolgeler/16-gergedan/model/habitat-inputs.json').read_text(encoding='utf-8'))['compoundOutlineM5XY'])
    open_habitats=unary_union([open_savanna,lemur_island.buffer(.8),habes_island.buffer(.8),bear_rocks,rhino.buffer(.5)])
    terrain = unary_union([Polygon(item["outer"], item["holes"])
                           for item in partition["layers"]["terrain"]
                           if item.get("surfaceStyle") != "penguin-gravel"])
    tree_ground = prep(terrain.buffer(-2.0).difference(open_habitats))
    plant_ground = prep(terrain.buffer(-.45).difference(open_habitats))
    original_trees = [tuple(item["xy"]) for item in site.get("treeClusters", [])]
    tree_occupied = {}

    def nearby_tree(x, y):
        ix, iy = math.floor(x / 6), math.floor(y / 6)
        for px in range(ix - 1, ix + 2):
            for py in range(iy - 1, iy + 2):
                for tx, ty in tree_occupied.get((px, py), []):
                    if (x - tx) ** 2 + (y - ty) ** 2 < 5.5 ** 2:
                        return True
        return False

    for x, y in original_trees:
        tree_occupied.setdefault((math.floor(x / 6), math.floor(y / 6)), []).append((x, y))
    trees = []
    for x, y, rng in cell_points(terrain.bounds, 7.2, 31015):
        if not tree_ground.contains(Point(x, y)) or inside_cage_margin(x, y):
            continue
        distance = math.hypot(x - CAGE_X, y - CAGE_Y)
        chance = .95 if distance < 130 else .36
        if rng.random() > chance or nearby_tree(x, y):
            continue
        height = round(6 + rng.random() * 6.2, 2)
        radius = round(2.2 + rng.random() * 1.9, 2)
        trees.append([round(x, 2), round(y, 2), height, radius,
                      rng.randrange(5)])
        tree_occupied.setdefault((math.floor(x / 6), math.floor(y / 6)), []).append((x, y))
    plants = []
    for x, y, rng in cell_points(terrain.bounds, 2.25, 80315):
        if not plant_ground.contains(Point(x, y)) or inside_cage_margin(x, y, 37, 22):
            continue
        distance = math.hypot(x - CAGE_X, y - CAGE_Y)
        # Dense low woodland around the approved cage view; the outer-site
        # density stays approximately unchanged. Open habitats remain excluded.
        chance = .96 if distance < 130 else .16
        if rng.random() > chance:
            continue
        plants.append([round(x, 2), round(y, 2), round(.9 + rng.random() * 1.0, 2),
                       rng.randrange(6)])
    # Preserve the previous planting coordinates, then fill selected woodland
    # groves near the cage. This is interpreted garden density, not new survey.
    occupied_plants={}
    def plant_cell(x,y):return math.floor(x/1.1),math.floor(y/1.1)
    def record_plant(p):occupied_plants.setdefault(plant_cell(*p[:2]),[]).append(p[:2])
    for p in plants:record_plant(p)
    infill_ground=prep(terrain.buffer(-.70).difference(open_habitats))
    infill_count=0
    for x,y,rng in cell_points((CAGE_X-110,CAGE_Y-110,CAGE_X+110,CAGE_Y+110),1.25,101512):
        if math.hypot(x-CAGE_X,y-CAGE_Y)>110 or inside_cage_margin(x,y,37,22):continue
        if not infill_ground.contains(Point(x,y)):continue
        ix,iy=plant_cell(x,y)
        neighbours=[q for px in range(ix-1,ix+2) for py in range(iy-1,iy+2) for q in occupied_plants.get((px,py),[])]
        if any(math.hypot(x-qx,y-qy)<.95 for qx,qy in neighbours):continue
        grove=.5+.25*math.sin(x*.13+y*.07)+.25*math.cos(y*.17-x*.05)
        if rng.random()>.38+.60*grove:continue
        p=[round(x,2),round(y,2),round(.65+rng.random()*.70,2),rng.randrange(6)]
        plants.append(p);record_plant(p);infill_count+=1
    for p in plants:
        if math.hypot(p[0]-CAGE_X,p[1]-CAGE_Y)<115 and (int(p[0]*100)*37+int(p[1]*100)*19)%11==0:p[3]=6
    shore_stones, shore_plants = [], []
    shore_rng = random.Random(11315)
    for item in partition["layers"]["water"]:
        pond = Polygon(item["outer"], item["holes"])
        centre = pond.representative_point()
        if inside_cage_margin(centre.x, centre.y, 35, 20):
            continue  # The cage's interpreted lagoon has its own bank model.
        if centre.distance(Point(-14,134)) < 2:
            continue  # The separately modelled penguin pool owns its bank.
        if pond.intersection(lemur_moat).area > .1:
            continue  # Lemur asset owns the concrete bank; keep its island open.
        if pond.intersection(habes_moat).area > .1:
            continue  # Habes asset owns its bank and open climbing island.
        if pond.intersection(bear_pool).area > .1:
            continue  # The bear pond component owns its rocky bank and plants.
        for ring in [pond.exterior, *pond.interiors]:
            count = max(1, math.floor(ring.length / 1.45))
            for index in range(count):
                distance = ring.length * index / count
                point = ring.interpolate(distance)
                before = ring.interpolate((distance - .15) % ring.length)
                after = ring.interpolate((distance + .15) % ring.length)
                dx, dy = after.x - before.x, after.y - before.y
                norm = math.hypot(dx, dy)
                if norm < .001:
                    continue
                for sign in (-1, 1):
                    nx, ny = -dy / norm * sign, dx / norm * sign
                    x, y = point.x + nx * .48, point.y + ny * .48
                    if not terrain.contains(Point(x, y)):
                        continue
                    size = .44 + shore_rng.random() * .4
                    shore_stones.append([round(x, 2), round(y, 2), round(size, 2),
                                         round(.24 + shore_rng.random() * .28, 2),
                                         round(math.atan2(dy, dx), 3)])
                    px, py = point.x + nx * 1.4, point.y + ny * 1.4
                    if index % 3 == 0 and plant_ground.contains(Point(px, py)):
                        shore_plants.append([round(px, 2), round(py, 2),
                                             round(.5 + shore_rng.random() * .65, 2),
                                             shore_rng.randrange(6)])
                    break
    result = {"schema": "bursa-zoo-woodland-visual-layout/v1",
        "sourceSurfaceSha256": hashlib.sha256(SURFACE.read_bytes()).hexdigest(),
        "sourcePlanSha256":hashlib.sha256((ROOT/'current-plan-data.json').read_bytes()).hexdigest(),
        "status": "Görsel yorum; 2026 ağaç ve bitki envanteri değil",
        "coordinateFrame": "M5 local XY metres", "trees": trees, "plants": plants,
        "plantingInterpretation":{"nearCageInfillCount":infill_count,"infillRadiusMetres":110,"newStemSpacingMetres":.95,
            "wildflowerCount":sum(p[3]==6 for p in plants),"fieldSurvey":False},
        "shoreStones": shore_stones, "shorePlants": shore_plants,
        "checks": {"treeCount": len(trees), "plantCount": len(plants),
                   "shoreStoneCount": len(shore_stones), "shorePlantCount": len(shore_plants),
                   "treesOnTerrain": all(terrain.contains(Point(x, y)) for x, y, *_ in trees),
                   "plantsOnTerrain": all(terrain.contains(Point(x, y)) for x, y, *_ in plants),
                   "shoreOnTerrain": all(terrain.contains(Point(x, y))
                                         for x, y, *_ in shore_stones + shore_plants),
                   "newTreesOutsideOpenSavanna":all(not open_savanna.covers(Point(x,y)) for x,y,*_ in trees),
                   "newPlantsOutsideOpenSavanna":all(not open_savanna.covers(Point(x,y)) for x,y,*_ in plants),
                   "newTreesOutsideHabesIsland":all(not habes_island.covers(Point(x,y)) for x,y,*_ in trees),
                   "newPlantsOutsideHabesIsland":all(not habes_island.covers(Point(x,y)) for x,y,*_ in plants),
                   "newTreeTrunksOutsideBearRocks":all(not bear_rocks.covers(Point(x,y)) for x,y,*_ in trees),
                   "newTreesOutsideLemurIsland":all(not lemur_island.covers(Point(x,y)) for x,y,*_ in trees),
                   "newPlantsOutsideLemurIsland":all(not lemur_island.covers(Point(x,y)) for x,y,*_ in plants)}}
    if not all(result["checks"][key] for key in ("treesOnTerrain", "plantsOnTerrain", "shoreOnTerrain")):
        raise ValueError("Visual planting escaped the exclusive terrain")
    (ROOT / "landscape-layout.json").write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(result["checks"])


if __name__ == "__main__":
    main()
