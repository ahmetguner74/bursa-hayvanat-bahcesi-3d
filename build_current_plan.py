"""Convert the official illustrated zoo plan trace into approximate M5-local XY.

The March 2026 illustration supplies the traced shapes. Its points are first
registered to the September 2026 edition, then to the older M5 metric frame.
This is a visual crosswalk, not a survey or a source of measured dimensions.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
TRACE_PATH = HERE / "current-plan-trace-pixels.json"
REGISTRATION_PATH = HERE / "current-plan-registration.json"
OUTPUT_PATH = HERE / "current-plan-data.json"

GEOMETRY_FIELDS = {
    "pointPx": "pointXYMetres",
    "labelAnchorPx": "labelAnchorXYMetres",
    "centerPx": "centerXYMetres",
    "pointsPx": "pointsXYMetres",
    "outlinePx": "outlineXYMetres",
    "approximateIslandPx": "approximateIslandXYMetres",
    "majorAxisEndpointsPx": "majorAxisEndpointsXYMetres",
    "minorAxisEndpointsPx": "minorAxisEndpointsXYMetres",
}
POINT_FIELDS = {"pointPx", "labelAnchorPx", "centerPx"}
METADATA_FIELDS = (
    "id", "name", "kind", "traceConfidence", "realWorldConfidence",
    "sourceIds", "notes",
)


def load_json(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8-sig"))
    return data, hashlib.sha256(raw).hexdigest()


def checked_matrix(value: object, label: str) -> tuple[tuple[float, ...], ...]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{label} must be a 2 x 3 affine matrix")
    rows = []
    for row in value:
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError(f"{label} must be a 2 x 3 affine matrix")
        if any(not isinstance(n, (int, float)) or not math.isfinite(n) for n in row):
            raise ValueError(f"{label} has a non-finite or non-numeric coefficient")
        rows.append(tuple(float(n) for n in row))
    return tuple(rows)


def apply_affine(point: object, matrix: tuple[tuple[float, ...], ...]) -> tuple[float, float]:
    if (not isinstance(point, (list, tuple)) or len(point) != 2 or
            any(not isinstance(n, (int, float)) or not math.isfinite(n) for n in point)):
        raise ValueError(f"Invalid two-dimensional point: {point!r}")
    x, y = point
    return (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2],
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2],
    )


def convert_point(
    point: object,
    march_to_september: tuple[tuple[float, ...], ...],
    september_to_local: tuple[tuple[float, ...], ...],
) -> list[float]:
    sep_point = apply_affine(point, march_to_september)
    local_point = apply_affine(sep_point, september_to_local)
    # A decimetre is finer than the registration's roughly 10 m RMS error.
    return [round(n, 1) for n in local_point]


def build() -> dict:
    trace, trace_hash = load_json(TRACE_PATH)
    registration, registration_hash = load_json(REGISTRATION_PATH)
    if trace.get("schema") != "bursa-zoo-current-plan-pixel-trace/v1":
        raise ValueError("Unexpected trace schema")
    if registration.get("schema") != "bursa-zoo-current-plan-registration-v1":
        raise ValueError("Unexpected registration schema")

    march_to_september = checked_matrix(
        trace["marchToSeptemberPixelTransform"]["affineMatrix"],
        "March-to-September transform",
    )
    fit = registration["fit"]
    sep_to_local_components = fit["imagePixelsToLocalMetres"]
    september_to_local = checked_matrix(
        [sep_to_local_components["x"], sep_to_local_components["y"]],
        "September-to-M5 transform",
    )

    # Catch an accidentally paired map edition or registration before export.
    # The earlier hand-read dome estimate differs by about 4 m from the later
    # high-resolution trace, still well below the registration's 10.7 m RMS.
    dome_check = convert_point([701, 679], march_to_september, september_to_local)
    expected_dome = registration["waterbirdDome"]["officialIllustrationApproxDomeCentreMetres"]
    if math.dist(dome_check, expected_dome) > 5.0:
        raise ValueError("The March and September registrations disagree at the aviary dome")

    features = []
    seen_ids = set()
    for source_feature in trace["features"]:
        feature_id = source_feature["id"]
        if feature_id in seen_ids:
            raise ValueError(f"Duplicate feature id: {feature_id}")
        seen_ids.add(feature_id)
        unknown_geometry = {key for key in source_feature if key.endswith("Px")} - GEOMETRY_FIELDS.keys()
        if unknown_geometry:
            raise ValueError(f"Unhandled pixel geometry on {feature_id}: {sorted(unknown_geometry)}")

        feature = {key: source_feature[key] for key in METADATA_FIELDS}
        for input_field, output_field in GEOMETRY_FIELDS.items():
            if input_field not in source_feature:
                continue
            source_geometry = source_feature[input_field]
            if input_field in POINT_FIELDS:
                feature[output_field] = convert_point(
                    source_geometry, march_to_september, september_to_local
                )
            else:
                feature[output_field] = [
                    convert_point(point, march_to_september, september_to_local)
                    for point in source_geometry
                ]
        if not any(field in feature for field in GEOMETRY_FIELDS.values()):
            raise ValueError(f"Feature has no numeric geometry: {feature_id}")
        if feature_id == "waterbird_aviary_dome_candidate":
            dome = registration["waterbirdDome"]
            fence = dome["matchingOldM5Feature"]
            ellipse = fence["ellipseFit"]
            feature["modelAnchor"] = {
                "source": registration["metricSource"]["path"],
                "m5FenceFeatureId": fence["id"],
                "oldM5FenceEllipseCentreXYMetres": ellipse["centreXYMetres"],
                "provisionalShellCentreXYMetres": dome["provisionalModelCentreXYMetres"],
                "provisionalShellAngleDegreesCounterclockwiseFromEast": dome[
                    "provisionalModelAngleDegreesCounterclockwiseFromEast"
                ],
                "independentMajorMinorDimensionsMetres": ellipse[
                    "assumedMajorMinorDimensionsMetres"
                ],
                "illustrationToFenceCentreDistanceMetres": round(
                    math.dist(feature["centerXYMetres"], ellipse["centreXYMetres"]), 1
                ),
                "guidance": (
                    "Anchor the provisional shell to the old M5 fence arc and "
                    "independent 70 x 40 m dimensions. The illustrated dome "
                    "centre is a separate approximate observation, not a "
                    "precision placement. Verify on current orthophoto or site."
                ),
                "limitations": ellipse["limitations"],
            }
        features.append(feature)

    source_meta = {}
    for source_id, source in trace["sources"].items():
        source_meta[source_id] = {
            key: source[key] for key in ("url", "publishedDate", "role")
        }

    return {
        "schema": "bursa-zoo-current-plan-local-geometry/v1",
        "createdOn": trace["createdOn"],
        "status": "Approximate interpretation of an illustrated visitor map; not surveyed geometry",
        "coordinateFrame": {
            "unit": "metre",
            "name": registration["metricSource"]["coordinateFrame"],
            "originEd50": registration["metricSource"]["originEd50"],
            "axisConvention": registration["metricSource"]["axisConvention"],
        },
        "builtFrom": {
            "pixelTrace": {"path": TRACE_PATH.name, "sha256": trace_hash},
            "registration": {"path": REGISTRATION_PATH.name, "sha256": registration_hash},
            "sequence": "March illustration to September illustration to M5 local XY",
        },
        "registrationResidualsMetres": {
            "rms": fit["rmsMetreResidual"],
            "maxAtControlPoint": max(
                point["fitResidualMetres"] for point in registration["controlPoints"]
            ),
            "practicalUncertainty": fit["practicalUncertaintyMetres"],
        },
        "sources": source_meta,
        "features": features,
    }


def main() -> None:
    result = build()
    OUTPUT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {OUTPUT_PATH.name} with {len(result['features'])} approximate features")


if __name__ == "__main__":
    main()
