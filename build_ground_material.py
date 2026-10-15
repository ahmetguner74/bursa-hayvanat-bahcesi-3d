"""Build numeric material weights from M5 trees and existing scene boundaries.

The PNG contains data channels, not painted terrain or extra visible geometry.
All placement and surface source files are read-only inputs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "viewer/assets"
SIZE = 1024


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    surface, site, landscape = map(read, ["surface-layers.json", "site-data.json", "landscape-layout.json"])
    source_texture = ASSETS / "woodland-leaf-litter-v1.png"
    asset_record = next(item for item in read("viewer/assets/asset-manifest.json")["assets"]
                        if item["file"] == source_texture.name)
    assert sha(source_texture) == asset_record["sha256"]
    delivery_texture = ASSETS / "woodland-leaf-litter-v1.jpg"
    with Image.open(source_texture) as image:
        image = image.convert("RGB")
        image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        image.save(delivery_texture, quality=90, subsampling=0, optimize=True)
        delivery_size = list(image.size)
    source_rock = ASSETS / "penguin-artificial-rock-v1.png"
    rock_record = next(item for item in read("viewer/assets/asset-manifest.json")["assets"]
                       if item["file"] == source_rock.name)
    assert sha(source_rock) == rock_record["sha256"]
    delivery_rock = ASSETS / "woodland-bank-rock-v1.jpg"
    with Image.open(source_rock) as image:
        image = image.convert("RGB")
        image.thumbnail((512, 512), Image.Resampling.LANCZOS)
        image.save(delivery_rock, quality=90, subsampling=0, optimize=True)
        rock_size = list(image.size)
    terrain = unary_union([Polygon(p["outer"], p.get("holes", []))
                           for p in surface["layers"]["terrain"] if p.get("surfaceStyle") not in ["penguin-gravel","habes-earth"]])
    x0, y0, x1, y1 = terrain.bounds
    bounds = [x0 - 2, y0 - 2, x1 + 2, y1 + 2]
    x0, y0, x1, y1 = bounds
    dx, dy = (x1 - x0) / SIZE, (y1 - y0) / SIZE
    xs = x0 + (np.arange(SIZE) + .5) * dx
    ys = y1 - (np.arange(SIZE) + .5) * dy
    litter = np.zeros((SIZE, SIZE), dtype=np.float32)
    specs = []
    for tree in site["treeClusters"]:
        x, y = tree["xy"]
        if not terrain.covers(Point(x, y)):
            continue
        seed = 0
        for char in tree["sourceIds"][0]:
            seed = ((seed * 31) + ord(char)) & 0xffffffff
        specs.append((x, y, 2.1 + (seed % 23) / 10, seed))
    specs += [(x, y, radius, seed) for x, y, height, radius, seed in landscape["trees"]]
    for x, y, radius, seed in specs:
        # A bounded illustrative leaf-fall area, not a botanical measurement.
        radius *= 1.35
        left, right = max(0, int((x - radius - x0) / dx)), min(SIZE, int((x + radius - x0) / dx) + 1)
        top, bottom = max(0, int((y1 - y - radius) / dy)), min(SIZE, int((y1 - y + radius) / dy) + 1)
        if left >= right or top >= bottom:
            continue
        xx, yy = np.meshgrid(xs[left:right] - x, ys[top:bottom] - y)
        distance = np.sqrt(xx * xx + yy * yy) / radius
        t = np.clip((1 - distance) / .65, 0, 1)
        patch = t * t * (3 - 2 * t) * (.58 + (seed % 7) * .025)
        litter[top:bottom, left:right] = np.maximum(litter[top:bottom, left:right], patch)

    def boundary_distance(layer):
        raster = Image.new("L", (SIZE, SIZE), 0)
        draw = ImageDraw.Draw(raster)
        for polygon in surface["layers"][layer]:
            for ring in [polygon["outer"], *polygon.get("holes", [])]:
                points = [((x - x0) / dx - .5, (y1 - y) / dy - .5) for x, y in ring]
                if points:
                    draw.line(points + points[:1], fill=255, width=1)
        return distance_transform_edt(np.asarray(raster) == 0, sampling=(dy, dx))

    damp = np.exp(-np.square(boundary_distance("water") / 2.8)) * .85
    verge = np.exp(-np.square(boundary_distance("path") / 1.45)) * .65
    pixels = np.round(np.stack([litter, damp, verge], axis=2).clip(0, 1) * 255).astype(np.uint8)
    output = ASSETS / "woodland-ground-weights-v1.png"
    Image.fromarray(pixels).save(output, optimize=True)
    meta = {
        "schema": "bursa-zoo-ground-material-weights/v1",
        "coordinateFrame": "M5 local XY metres",
        "boundsXYMetres": bounds,
        "image": "assets/" + output.name,
        "size": [SIZE, SIZE],
        "pixelSizeMetres": [dx, dy],
        "sha256": sha(output),
        "litterTexture": {"file": "assets/" + delivery_texture.name, "sha256": sha(delivery_texture),
                          "bytes": delivery_texture.stat().st_size, "size": delivery_size,
                          "source": "viewer/assets/" + source_texture.name, "sourceSha256": sha(source_texture),
                          "derivation": "RGB conversion, max 1024 px Lanczos, JPEG quality 90 4:4:4; no painting or geometry change"},
        "rockTexture": {"file": "assets/" + delivery_rock.name, "sha256": sha(delivery_rock),
                        "bytes": delivery_rock.stat().st_size, "size": rock_size,
                        "source": "viewer/assets/" + source_rock.name, "sourceSha256": sha(source_rock),
                        "derivation": "RGB conversion, max 512 px Lanczos, JPEG quality 90 4:4:4; existing generated artificial-rock albedo reused illustratively, not a natural rock scan"},
        "channels": {"r": "Illustrative leaf-fall weight around existing trees",
                     "g": "Illustrative dampness falloff from existing water boundaries",
                     "b": "Illustrative verge falloff from existing path boundaries"},
        "treePatches": len(specs),
        "sources": {name: sha(ROOT / name) for name in
                    ["site-data.json", "surface-layers.json", "landscape-layout.json", "v2/manual-roads-metric.json"]},
        "interpretation": "Material presentation only. No surface, road, water or tree coordinates are changed; not a current soil survey.",
        "checks": {"finite": bool(np.isfinite(pixels).all()), "channelMaxima": pixels.max(axis=(0, 1)).tolist(),
                   "channelMeans": pixels.mean(axis=(0, 1)).round(4).tolist()},
    }
    (ROOT / "ground-material-layout.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"maskBytes": output.stat().st_size, "treePatches": len(specs), "pixelSizeMetres": [dx, dy]}))


if __name__ == "__main__":
    main()
