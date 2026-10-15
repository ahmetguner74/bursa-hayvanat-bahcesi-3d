"""Trace visitor paths and the front access/parking pavement from the 2026 zoo map.

The March image is the sharper rendering of the same line art. Its measured
similarity transform maps every contour into the *September* source image; the
existing control-point registration then maps those pixels into M5-local metres.
The products are visual interpretations of an illustrated wayfinding map, not
surveyed or legal road geometry.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shapely.affinity import affine_transform
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "v2"
PRIVATE = HERE / "private"
MARCH_IMAGE = ROOT / "reference-maps-private" / "2026-03-kroki.jpg"
SEPTEMBER_IMAGE = ROOT / "reference-maps-private" / "2026-09-kroki.jpg"
TRACE = ROOT / "current-plan-trace-pixels.json"
REGISTRATION = ROOT / "current-plan-registration.json"

KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))


# March artwork coordinates. Each ribbon follows pale paving visible in the
# official artwork (or, where noted, a short continuation under an icon/tree).
# These are path centre-lines, not surveyed road axes. Keeping the waypoints
# explicit makes every inferred section inspectable and editable later.
REVIEWED_PEDESTRIAN_LINKS = (
    {"name": "west service perimeter", "points": ((322, 365), (327, 350)),
     "widthPx": 11, "confidence": "high"},
    {"name": "west visitor spur", "points": ((362, 545), (368, 534)),
     "widthPx": 10, "confidence": "high"},
    {"name": "Gulen Kus 23 icon occlusion", "points": ((386, 536),
     (387, 548), (387, 560), (387, 576), (385, 590)),
     "widthPx": 11, "confidence": "medium; dotted path under map icon"},
    {"name": "northwest upper loop west", "points": ((380, 150), (402, 148), (428, 151)),
     "widthPx": 11, "confidence": "medium"},
    {"name": "northwest upper loop east", "points": ((448, 151), (474, 157), (499, 168), (517, 181)),
     "widthPx": 12, "confidence": "medium"},
    {"name": "northwest service courtyard", "points": ((398, 227), (421, 229),
     (445, 235), (469, 242), (498, 240), (506, 234)),
     "widthPx": 13, "confidence": "medium"},
    {"name": "service to penguin north walk", "points": ((583, 211), (608, 214),
     (630, 220), (655, 226), (681, 232), (710, 234), (739, 235),
     (763, 238), (790, 245)),
     "widthPx": 12, "confidence": "low; centre under tree canopy inferred"},
    {"name": "African village 14 icon occlusion", "points": ((954, 339),
     (971, 343), (989, 349), (1004, 353)),
     "widthPx": 11, "confidence": "medium; path continuation under map icon"},
    {"name": "African cafe sign occlusion", "points": ((1002, 347), (1017, 353)),
     "widthPx": 10, "confidence": "high"},
    {"name": "African cafe eastern junction", "points": ((1055, 424),
     (1067, 421), (1080, 417)),
     "widthPx": 14, "confidence": "high"},
)


def refine_pedestrian_mask(image_bgr: np.ndarray, seed: np.ndarray,
                           vehicle: np.ndarray) -> tuple[np.ndarray, dict]:
    """Grow *locally* into paving texture, without flooding planted islands.

    A 7-pixel probable-foreground band lets GrabCut classify shaded path edges.
    Only accepted pixels within 3 pixels of the source seed survive, and newly
    accepted red roofs, green planting and blue water are rejected. This avoids
    a global dilation, which incorrectly joins paths across narrow planters.
    """
    distance = cv2.distanceTransform((1 - seed).astype("uint8"), cv2.DIST_L2, 3)
    grab = np.full(seed.shape, cv2.GC_BGD, dtype="uint8")
    grab[distance <= 24] = cv2.GC_PR_BGD
    grab[distance <= 7] = cv2.GC_PR_FGD
    grab[seed > 0] = cv2.GC_FGD
    grab[vehicle > 0] = cv2.GC_BGD
    cv2.setRNGSeed(0)
    cv2.grabCut(image_bgr, grab, None, np.zeros((1, 65), np.float64),
                np.zeros((1, 65), np.float64), 5, cv2.GC_INIT_WITH_MASK)
    accepted = np.isin(grab, (cv2.GC_FGD, cv2.GC_PR_FGD)) & (distance <= 3)
    r = image_bgr[:, :, 2].astype("int16")
    g = image_bgr[:, :, 1].astype("int16")
    b = image_bgr[:, :, 0].astype("int16")
    non_paving = (((r - g > 28) & (r - b > 28)) |
                  ((g - r > 18) & (g - b > 15)) |
                  ((b - r > 35) & (b - g > 18)))
    refined = ((seed > 0) | (accepted & ~non_paving)).astype("uint8")
    classified_px = int(refined.sum())
    classified_mask = refined.copy()

    # Use finite ribbons only where a path can be followed on the map. The
    # long penguin link is intentionally marked low-confidence: canopy hides
    # its exact centre, although pale road is visible on both sides.
    bridge_layer = np.zeros_like(refined)
    for item in REVIEWED_PEDESTRIAN_LINKS:
        pts = np.asarray(item["points"], dtype="int32")
        cv2.polylines(bridge_layer, [pts], False, 1, item["widthPx"], cv2.LINE_8)
        for pt in pts:
            cv2.circle(bridge_layer, tuple(pt), item["widthPx"] // 2, 1, -1)
    refined |= bridge_layer
    refined[vehicle > 0] = 0
    return refined, {"seedPedestrianMaskPx": int(seed.sum()),
                     "classifiedPedestrianMaskPx": classified_px,
                     "reviewedBridgeAddedPx": int(np.sum((refined > 0) & (classified_mask == 0))),
                     "finalPedestrianMaskPx": int(refined.sum())}


def largest_components(mask: np.ndarray, retained_ranks: tuple[int, ...]) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype("uint8"), 8)
    ranked = np.argsort(stats[1:, cv2.CC_STAT_AREA])[::-1] + 1
    selected = np.zeros_like(mask, dtype="uint8")
    for rank in retained_ranks:
        if rank < len(ranked):
            selected[labels == ranked[rank]] = 1
    return selected


def source_masks() -> tuple[np.ndarray, np.ndarray, dict]:
    image_bgr = cv2.imread(str(MARCH_IMAGE), cv2.IMREAD_COLOR)
    rgb = image_bgr[:, :, ::-1].astype(np.int16)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]

    # Warm, pale paving material. The shared largest component follows the
    # visitor network, while separately listed NW components lie under trees
    # or around the service/animal-care buildings. Components at rhino sand,
    # penguin rockwork and eastern pale enclosure earth are deliberately out.
    warm = ((r > 175) & (g > 170) & (b > 150) &
            (r - g >= 0) & (r - g < 18) &
            (g - b >= 8) & (g - b < 32) & (r - b < 45)).astype("uint8")
    warm[:70] = 0
    warm[1040:] = 0
    warm[:, :145] = 0
    warm[:, 1570:] = 0
    ped = largest_components(warm, (0, 1, 2, 5, 7, 13, 14, 16, 17, 21, 23))
    selected_warm_pixels = int(ped.sum())
    ped = cv2.morphologyEx(ped, cv2.MORPH_CLOSE, KERNEL)

    # Neutral grey front pavement (including the west service/access edge).
    # The largest connected component excludes grey roof plates and cage mesh.
    # The brighter lower bound sheds most of the soft grey illustration shadow.
    grey = ((r > 155) & (g > 155) & (b > 155) &
            (r < 235) & (g < 235) & (b < 235) &
            (np.abs(r - g) < 9) & (np.abs(g - b) < 10)).astype("uint8")
    grey[:65] = 0
    grey[1030:] = 0
    grey[:, :145] = 0
    grey[:, 1580:] = 0
    vehicle = largest_components(grey, (0,))
    selected_grey_pixels = int(vehicle.sum())
    vehicle = cv2.morphologyEx(vehicle, cv2.MORPH_CLOSE, KERNEL)
    ped, refinement_stats = refine_pedestrian_mask(image_bgr, ped, vehicle)
    return ped, vehicle, {"warmCandidatesPx": int(warm.sum()),
                          "selectedWarmPx": selected_warm_pixels,
                          "greyCandidatesPx": int(grey.sum()),
                          "selectedGreyPx": selected_grey_pixels,
                          "finalVehicleMaskPx": int(vehicle.sum()),
                          **refinement_stats}


def mask_to_geometry(mask: np.ndarray) -> Polygon | MultiPolygon:
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        raise ValueError("Empty road mask")
    hierarchy = hierarchy[0]
    polygons = []
    for outer_index, h in enumerate(hierarchy):
        if h[3] >= 0:
            continue
        if cv2.contourArea(contours[outer_index]) < 70:
            continue
        outer = cv2.approxPolyDP(contours[outer_index], 1.0, True)[:, 0, :].tolist()
        holes = []
        child = h[2]
        while child >= 0:
            if cv2.contourArea(contours[child]) >= 70:
                ring = cv2.approxPolyDP(contours[child], 1.0, True)[:, 0, :].tolist()
                if len(ring) >= 3:
                    holes.append(ring)
            child = hierarchy[child][0]
        if len(outer) >= 3:
            poly = Polygon(outer, holes).buffer(0)
            if not poly.is_empty:
                polygons.append(poly)
    merged = unary_union(polygons).buffer(0)
    return merged.simplify(0.55, preserve_topology=True)


def shape_counts(geom):
    parts = [geom] if isinstance(geom, Polygon) else list(geom.geoms)
    return {"components": len(parts), "holes": sum(len(p.interiors) for p in parts),
            "vertices": sum(len(p.exterior.coords) + sum(len(h.coords) for h in p.interiors)
                            for p in parts)}


def coordinates(geom, decimals: int):
    def poly_coords(poly):
        rings = [poly.exterior, *poly.interiors]
        return [[[round(x, decimals), round(y, decimals)] for x, y in ring.coords]
                for ring in rings]
    if isinstance(geom, Polygon):
        return {"type": "Polygon", "coordinates": poly_coords(geom)}
    return {"type": "MultiPolygon", "coordinates": [poly_coords(p) for p in geom.geoms]}


def polygon_parts(geom):
    return [geom] if isinstance(geom, Polygon) else list(geom.geoms)


def draw_geometry(draw: ImageDraw.ImageDraw, geom, transform, color: tuple[int, int, int]):
    for poly in polygon_parts(geom):
        outer = [transform(x, y) for x, y in poly.exterior.coords]
        draw.polygon(outer, fill=color)
        for hole in poly.interiors:
            draw.polygon([transform(x, y) for x, y in hole.coords], fill=(251, 250, 246))


def make_qa(sep_ped, sep_vehicle, metre_ped, metre_vehicle):
    # Public QA image contains only the derived road geometry, no source raster.
    x_min, x_max, y_min, y_max, ppm = -320, 420, -270, 270, 2
    width, height = (x_max - x_min) * ppm, (y_max - y_min) * ppm
    base = Image.new("RGB", (width, height), (251, 250, 246))
    d = ImageDraw.Draw(base)
    for x in range(-300, 401, 100):
        col = (226, 229, 220)
        xx = (x - x_min) * ppm
        d.line([(xx, 0), (xx, height)], fill=col, width=1)
        d.text((xx + 5, height - 24), f"{x} m E", fill=(102, 112, 105))
    for y in range(-200, 201, 100):
        yy = (y_max - y) * ppm
        d.line([(0, yy), (width, yy)], fill=(226, 229, 220), width=1)
        d.text((8, yy + 3), f"{y} m N", fill=(102, 112, 105))
    target = lambda x, y: ((x - x_min) * ppm, (y_max - y) * ppm)
    draw_geometry(d, metre_vehicle, target, (204, 151, 107))
    draw_geometry(d, metre_ped, target, (83, 130, 113))
    d.rectangle((20, 15, 840, 94), fill=(251, 250, 246))
    d.text((28, 22), "Bursa Zoo V2 - source map road trace / M5 local metres", fill=(33, 50, 45))
    d.rectangle((28, 57, 55, 78), fill=(83, 130, 113))
    d.text((64, 57), "Pedestrian paths", fill=(33, 50, 45))
    d.rectangle((265, 57, 292, 78), fill=(204, 151, 107))
    d.text((301, 57), "Front road and parking", fill=(33, 50, 45))
    base.save(HERE / "roads-qa.png")

    # Private reference comparison, retained outside the published build.
    source = Image.open(SEPTEMBER_IMAGE).convert("RGB")
    layer = Image.new("RGB", source.size, (255, 255, 255))
    draw = ImageDraw.Draw(layer)
    draw_geometry(draw, sep_vehicle, lambda x, y: (x, y), (242, 129, 45))
    draw_geometry(draw, sep_ped, lambda x, y: (x, y), (235, 18, 214))
    Image.blend(source, layer, .37).save(PRIVATE / "roads-source-qa.png")

    rectified_path = PRIVATE / "rectified-september.png"
    if rectified_path.exists():
        rectified = Image.open(rectified_path).convert("RGB")
        if rectified.size == (width, height):
            color_layer = Image.new("RGB", rectified.size, (255, 255, 255))
            rd = ImageDraw.Draw(color_layer)
            draw_geometry(rd, metre_vehicle, target, (242, 129, 45))
            draw_geometry(rd, metre_ped, target, (235, 18, 214))
            Image.blend(rectified, color_layer, .37).save(PRIVATE / "roads-rectified-qa.png")


def main():
    PRIVATE.mkdir(parents=True, exist_ok=True)
    trace = json.loads(TRACE.read_text(encoding="utf-8"))
    reg = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    march_to_sep = trace["marchToSeptemberPixelTransform"]["affineMatrix"]
    to_sep = [march_to_sep[0][0], march_to_sep[0][1],
              march_to_sep[1][0], march_to_sep[1][1],
              march_to_sep[0][2], march_to_sep[1][2]]
    m = reg["fit"]["imagePixelsToLocalMetres"]
    to_metre = [m["x"][0], m["x"][1], m["y"][0], m["y"][1], m["x"][2], m["y"][2]]

    ped_mask, vehicle_mask, extraction_stats = source_masks()
    march_ped = mask_to_geometry(ped_mask)
    march_vehicle = mask_to_geometry(vehicle_mask)
    # Vehicle pavement takes precedence where classification/closing meet.
    march_ped = march_ped.difference(march_vehicle).buffer(0)
    # Drop only tiny antialiasing remnants; all reviewed road links survive.
    march_ped = unary_union([p for p in polygon_parts(march_ped) if p.area >= 80]).buffer(0)
    sep_ped = affine_transform(march_ped, to_sep)
    sep_vehicle = affine_transform(march_vehicle, to_sep)
    metre_ped = affine_transform(sep_ped, to_metre)
    metre_vehicle = affine_transform(sep_vehicle, to_metre)
    overlap = metre_ped.intersection(metre_vehicle).area
    assert overlap < 1e-5, overlap

    by_kind = (("pedestrian_surface", sep_ped, metre_ped, "medium"),
               ("vehicle_surface", sep_vehicle, metre_vehicle, "medium"))
    features_sep, features_metre = [], []
    for kind, source_geom, metric_geom, confidence in by_kind:
        common = {"id": "v2-" + kind.replace("_surface", ""), "kind": kind,
                  "traceConfidence": confidence,
                  "realWorldConfidence": "low",
                  "source": "Official September 2026 visitor map, path artwork cross-checked against sharper March 2026 rendering",
                  "limitations": "Illustrated path edges and front pavement; not surveyed widths or alignments."}
        features_sep.append({**common, "geometry": coordinates(source_geom, 4)})
        features_metre.append({**common, "geometry": coordinates(metric_geom, 6)})

    metrics = {
        "areaSquareMetres": {"pedestrian": round(metre_ped.area, 2),
                              "vehicle": round(metre_vehicle.area, 2)},
        "pedestrian": shape_counts(metre_ped),
        "vehicle": shape_counts(metre_vehicle),
        "pedestrianVehicleOverlapSquareMetres": round(overlap, 8),
        "selectedWarmPavingCandidatePixelsPercent": round(100 * extraction_stats["selectedWarmPx"] /
                                                       extraction_stats["warmCandidatesPx"], 1),
        "candidateCoverageNote": "Color-candidate coverage is a processing diagnostic, not a measured recall of real paths; omitted candidates include exhibits and buildings.",
        "sourceMaskPixels": {"seed": extraction_stats["seedPedestrianMaskPx"],
                             "classified": extraction_stats["classifiedPedestrianMaskPx"],
                             "final": extraction_stats["finalPedestrianMaskPx"],
                             "reviewedBridgeAdded": extraction_stats["reviewedBridgeAddedPx"]},
        "reviewedPedestrianLinks": [dict(item) for item in REVIEWED_PEDESTRIAN_LINKS],
        "unresolved": [
            "The service-to-penguin north walk passes under trees; its centre line is an approximate interpretation of visible pale paving on either side.",
            "Entrance thresholds underneath labels/building roofs cannot be traced precisely.",
            "The illustrated front road soft edge and planted medians are approximate; no surveyed curb line is available.",
        ],
    }
    common = {"schema": "bursa-zoo-v2-roads/v1", "createdOn": "2026-10-14",
              "purpose": "Reviewed road-surface trace for the V2 road-only scene",
              "sources": {"officialSeptember": reg["officialSource"]["imageUrl"],
                          "detailMarch": trace["sources"]["geometry"]["url"]},
              "method": "Color classification, component review, local GrabCut edge refinement bounded to 3 source pixels, reviewed path links, and contour vectorization on March artwork; similarity transform into September pixels, then 12-control affine map to M5 metres. Vehicle surface wins at contacts.",
              "metrics": metrics}
    source_data = {**common,
                   "coordinateFrame": {"unit": "September source image pixel", "size": [1600, 864],
                                       "origin": "top left", "x": "right", "y": "down"},
                   "features": features_sep}
    metric_data = {**common,
                   "coordinateFrame": {"unit": "metre", "source": "M5 ED50/TM30 local XY",
                                       "originED50": reg["metricSource"]["originEd50"],
                                       "x": "east", "y": "north",
                                       "registrationRmsMetres": reg["fit"]["rmsMetreResidual"],
                                       "practicalUncertaintyMetres": reg["fit"]["practicalUncertaintyMetres"]},
                   "features": features_metre}
    (HERE / "roads-source-pixels.json").write_text(json.dumps(source_data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    (HERE / "roads-metric.json").write_text(json.dumps(metric_data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    make_qa(sep_ped, sep_vehicle, metre_ped, metre_vehicle)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
