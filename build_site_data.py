"""Assemble a clipped zoo plan from original-DGN intermediate exports and OSM boundary."""

from __future__ import annotations

from collections import Counter
import json
import re
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyproj import Transformer
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source-ascii"
SHEETS = ("H22D01C2A", "H22D01C2B", "H22D01C2C", "H22D01C2D")
OSM_WAY = 26445905
OSM_URL = f"https://api.openstreetmap.org/api/0.6/way/{OSM_WAY}/full"
COORD = re.compile(r"^(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)$")
LAYERS = {
    "Yol_Sose": "road_edge", "Yol_Toprak_Duz": "road_edge", "Yol_Toprak_Kesik": "road_edge",
    "Yol_Kaldirim_kenari_bordurtasi": "curb", "Yol_Durak_Kapali": "transport",
    "Hid_Havuz": "water", "Hid_Dere_Sulu": "water",
    "B_Mesken": "building", "B_Ticari": "building", "B_Resmi": "building",
    "B_Ahir": "building", "B_Sundurma": "canopy", "B_Teras": "building",
    "B_Betonzemin": "paving", "B_Merdiven": "steps",
    "Sinir_Cit_bir_taraf": "fence", "Sinir_Tel_bir_taraf": "fence",
    "Sinir_Tel_iki_taraf": "fence", "Sinir_Parmaklik_bir_taraf": "fence",
    "Sinir_Duvar_tek_tarafa_ait": "wall", "Sinir_Ist_Duvari": "wall",
    "S_Tek_Agac": "tree", "S_Y_Doken_Agac_Grup": "tree",
}


def transform_boundary() -> tuple[dict, Polygon]:
    with urllib.request.urlopen(OSM_URL, timeout=30) as response:
        root = ET.fromstring(response.read())
    nodes = {item.attrib["id"]: (float(item.attrib["lon"]), float(item.attrib["lat"]))
             for item in root.findall("node")}
    way = next(item for item in root.findall("way") if item.attrib["id"] == str(OSM_WAY))
    ll = [nodes[item.attrib["ref"]] for item in way.findall("nd")]
    transformer = Transformer.from_crs(4326, 5254, always_xy=True)
    xy = []
    for lon, lat in ll:
        e, n = transformer.transform(lon, lat)
        xy.append((37.10573 + 1.00000397 * e + 0.00000074 * n,
                   167.84018 + 1.00000397 * n - 0.00000074 * e))
    polygon = Polygon(xy)
    if not polygon.is_valid:
        raise ValueError("OSM boundary is invalid")
    metadata = {"osmWay": OSM_WAY, "version": int(way.attrib["version"]),
                "timestamp": way.attrib["timestamp"], "url": OSM_URL,
                "wgs84LonLat": ll}
    return metadata, polygon


def features_from_sheet(path: Path):
    attrs: dict[str, str] = {}
    points: list[tuple[float, float, float]] = []
    ordinal = 0

    def finish():
        if points:
            yield ordinal, attrs, points

    with path.open(encoding="utf-8", errors="replace") as stream:
        for raw in stream:
            line = raw.strip()
            if line.startswith("GM_TYPE="):
                yield from finish()
                ordinal += 1
                attrs = {"GM_TYPE": line[8:]}
                points = []
            elif match := COORD.match(line):
                points.append(tuple(float(match.group(i)) for i in (1, 2, 3)))
            elif "=" in line:
                key, value = line.split("=", 1)
                attrs[key] = value
    yield from finish()


def linear_parts(shape):
    if shape.is_empty:
        return []
    if shape.geom_type == "Polygon":
        return [list(shape.exterior.coords)]
    if shape.geom_type in ("LineString", "LinearRing"):
        return [list(shape.coords)]
    if hasattr(shape, "geoms"):
        return [item for part in shape.geoms for item in linear_parts(part)]
    return []


def main() -> None:
    osm, boundary = transform_boundary()
    centre = boundary.centroid
    origin = (round(centre.x), round(centre.y))
    selected = []
    counts = Counter()
    for sheet in SHEETS:
        path = SOURCE / f"{sheet}.txt"
        if not path.exists():
            raise FileNotFoundError(path)
        for ordinal, attrs, points in features_from_sheet(path):
            layer = attrs.get("DESCRIPTION", "")
            role = LAYERS.get(layer)
            if not role or not points:
                continue
            if not (min(x for x, _, _ in points) <= boundary.bounds[2]
                    and max(x for x, _, _ in points) >= boundary.bounds[0]
                    and min(y for _, y, _ in points) <= boundary.bounds[3]
                    and max(y for _, y, _ in points) >= boundary.bounds[1]):
                continue
            unique = [(x, y) for x, y, _ in points]
            is_closed = attrs.get("CLOSED") == "YES" and len(unique) >= 4
            shape = Polygon(unique) if is_closed else LineString(unique) if len(unique) >= 2 else None
            if shape is None or not shape.is_valid or not shape.intersects(boundary):
                continue
            # Point-like tree cells can be represented by their measured anchor centre.
            if role == "tree":
                clipped = shape.centroid if boundary.contains(shape.centroid) else None
                if clipped is None:
                    continue
                paths = [[[round(clipped.x - origin[0], 3), round(clipped.y - origin[1], 3)]]]
            else:
                clipped = shape.intersection(boundary)
                paths = [
                    [[round(x - origin[0], 3), round(y - origin[1], 3)] for x, y in part]
                    for part in linear_parts(clipped) if len(part) >= 2
                ]
            if not paths:
                continue
            counts[layer] += 1
            selected.append({"id": f"{sheet}:{ordinal}", "sheet": sheet,
                             "layer": layer, "role": role, "closed": is_closed,
                             "sourceH": round(sum(z for _, _, z in points) / len(points), 4),
                             "paths": paths})
    outline = [[round(x - origin[0], 3), round(y - origin[1], 3)]
               for x, y in boundary.exterior.coords]
    road_lines = [LineString([(x + origin[0], y + origin[1]) for x, y in path])
                  for item in selected if item["role"] == "road_edge"
                  for path in item["paths"] if len(path) >= 2]
    # Visual trial only: the DGN provides path edges, not a classified path fill.
    # A small symmetric buffer makes the circulation network legible in 3D.
    road_surface = unary_union([line.buffer(3.0, cap_style=2, join_style=2)
                                for line in road_lines]).intersection(boundary)
    walk_surfaces = []
    surfaces = list(road_surface.geoms) if hasattr(road_surface, "geoms") else [road_surface]
    for surface in surfaces:
        if surface.geom_type != "Polygon" or surface.area < 2:
            continue
        walk_surfaces.append({
            "outer": [[round(x - origin[0], 3), round(y - origin[1], 3)]
                      for x, y in surface.exterior.coords],
            "holes": [[[round(x - origin[0], 3), round(y - origin[1], 3)]
                       for x, y in ring.coords] for ring in surface.interiors],
        })
    # Four nearby M5 marks normally describe one tree symbol. Keep the source
    # features intact, but use one visual tree per cluster in the viewer.
    tree_features = [item for item in selected if item["role"] == "tree"]
    tree_points = [item["paths"][0][0] for item in tree_features]
    parent = list(range(len(tree_points)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    cells = {}
    for i, (x, y) in enumerate(tree_points):
        cell = (int(x // 2.5), int(y // 2.5))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in cells.get((cell[0] + dx, cell[1] + dy), []):
                    px, py = tree_points[j]
                    if (x - px) ** 2 + (y - py) ** 2 <= 2.5 ** 2:
                        parent[find(i)] = find(j)
        cells.setdefault(cell, []).append(i)
    groups = {}
    for i in range(len(tree_points)):
        groups.setdefault(find(i), []).append(i)
    tree_clusters = [{"xy": [round(sum(tree_points[i][axis] for i in members) / len(members), 3)
                               for axis in (0, 1)],
                      "sourceIds": [tree_features[i]["id"] for i in members]}
                     for members in groups.values()]

    # Two measured M5 water-edge segments meet to form the cage pond outline.
    pond_ids = ("H22D01C2A:3564", "H22D01C2B:4281")
    pond_parts = [next(item for item in selected if item["id"] == source_id)["paths"][0]
                  for source_id in pond_ids]
    pond_outline = pond_parts[0] + pond_parts[1][1:]
    if not Polygon(pond_outline).is_valid:
        raise ValueError("Cage pond outline from M5 water edges is invalid")
    result = {
        "schema": "bursa-zoo-site-study/v1",
        "status": "DGN-derived clipped plan; ground surface and structure contacts not accepted",
        "coordinateFrame": "M5 source ED50/TM30 XY metres; orthometric source H",
        "originEd50": origin,
        "osmBoundary": osm,
        "outline": outline,
        "walkSurfaces": walk_surfaces,
        "walkSurfaceMethod": "3 m visual buffer around M5 Yol_Sose/Yol_Toprak edge lines; not surveyed pavement width",
        "treeClusters": tree_clusters,
        "treeClusterMethod": "M5 four-mark tree symbols merged within 2.5 m for visualization; source features preserved",
        "cagePond": {"outer": pond_outline, "sourceFeatureIds": pond_ids},
        "features": selected,
        "sourceLayerCounts": dict(sorted(counts.items())),
        "sourceSheets": SHEETS,
        "sourceIdentityLimit": "IDs use SIMPLE_ASCII export order, not native DGN element IDs",
    }
    out = HERE / "site-data.json"
    out.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(12, 8), dpi=160)
    colors = {"road_edge": "#665b4a", "curb": "#a79072", "water": "#42a8d5",
              "building": "#8c5962", "canopy": "#cc9576", "paving": "#bbafa1",
              "steps": "#965b40", "fence": "#9aa08d", "wall": "#666a60", "tree": "#52825b"}
    for item in selected:
        if item["role"] == "tree":
            continue
        for path in item["paths"]:
            ax.plot([p[0] for p in path], [p[1] for p in path],
                    color=colors[item["role"]], lw=0.75, alpha=0.8)
    ax.plot([p[0] for p in outline], [p[1] for p in outline], color="#e14b44", lw=1.8)
    ax.set_aspect("equal")
    ax.grid(alpha=0.15)
    ax.set_title("Bursa Hayvanat Bahçesi — M5 çizgileri / OSM sınırı (ön inceleme)")
    fig.tight_layout()
    fig.savefig(HERE / "site-source-qa.png")
    print(json.dumps({"features": len(selected), "layers": counts,
                      "originEd50": origin, "osmWayVersion": osm["version"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
