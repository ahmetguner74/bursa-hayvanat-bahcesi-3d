"""Resample the current official visitor illustration onto the M5 metre grid.

This is a private visual reference for tracing. The visitor illustration is
stylised, so the result is not an orthophoto or a survey-grade plan.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
REGISTRATION = ROOT / "current-plan-registration.json"
SOURCE = ROOT / "reference-maps-private" / "2026-09-kroki.jpg"
OUTPUT = HERE / "private" / "rectified-september.png"
MANIFEST = HERE / "rectification.json"

# A half-metre grid retains the detail available in the 1600 x 864 source.
X_MIN, X_MAX = -320.0, 420.0
Y_MIN, Y_MAX = -270.0, 270.0
PIXELS_PER_METRE = 2.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration["schema"] != "bursa-zoo-current-plan-registration-v1":
        raise ValueError("Unexpected visitor-map registration")
    expected_width, expected_height = registration["officialSource"]["imageSizePixels"]
    source = cv2.imread(str(SOURCE), cv2.IMREAD_COLOR)
    if source is None or source.shape[:2] != (expected_height, expected_width):
        raise ValueError("The current September plan is missing or has changed size")

    width = round((X_MAX - X_MIN) * PIXELS_PER_METRE)
    height = round((Y_MAX - Y_MIN) * PIXELS_PER_METRE)
    columns = np.arange(width, dtype=np.float32)
    rows = np.arange(height, dtype=np.float32)
    east = X_MIN + (columns + 0.5) / PIXELS_PER_METRE
    north = Y_MAX - (rows + 0.5) / PIXELS_PER_METRE
    fit = registration["fit"]["localMetresToImagePixels"]
    u = fit["u"][0] * east[None, :] + fit["u"][1] * north[:, None] + fit["u"][2]
    v = fit["v"][0] * east[None, :] + fit["v"][1] * north[:, None] + fit["v"][2]
    # Broadcast each affine coordinate to the full output grid for cv2.remap.
    u = np.broadcast_to(u, (height, width)).astype(np.float32)
    v = np.broadcast_to(v, (height, width)).astype(np.float32)
    rgba = cv2.remap(
        cv2.cvtColor(source, cv2.COLOR_BGR2BGRA), u, v,
        interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(OUTPUT), rgba):
        raise OSError(f"Could not write {OUTPUT}")

    manifest = {
        "schema": "bursa-zoo-v2-rectified-visitor-map/v1",
        "source": {
            "imageUrl": registration["officialSource"]["imageUrl"],
            "privateLocalImage": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(SOURCE),
            "sizePixels": [expected_width, expected_height],
            "registrationPath": REGISTRATION.name,
            "registrationSha256": sha256(REGISTRATION),
        },
        "privateOutput": {
            "path": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(OUTPUT),
            "sizePixels": [width, height],
        },
        "grid": {
            "unit": "metre",
            "xMin": X_MIN, "xMax": X_MAX,
            "yMin": Y_MIN, "yMax": Y_MAX,
            "pixelsPerMetre": PIXELS_PER_METRE,
            "pixelCenterToLocalXY": [
                "x = xMin + (column + 0.5) / pixelsPerMetre",
                "y = yMax - (row + 0.5) / pixelsPerMetre",
            ],
            "localXYToPixelCorner": [
                "column = (x - xMin) * pixelsPerMetre",
                "row = (yMax - y) * pixelsPerMetre",
            ],
        },
        "registration": {
            "method": registration["fit"]["method"],
            "controlPointCount": len(registration["controlPoints"]),
            "rmsMetres": registration["fit"]["rmsMetreResidual"],
            "maxControlResidualMetres": max(p["fitResidualMetres"] for p in registration["controlPoints"]),
            "practicalUncertainty": registration["fit"]["practicalUncertaintyMetres"],
            "imagePixelsToLocalMetres": registration["fit"]["imagePixelsToLocalMetres"],
            "localMetresToImagePixels": fit,
        },
        "usage": "Private rectified reference; copied only into ignored dist/v2 for the user-controlled local overlay, never into docs/.",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Rectified current plan: {width} x {height} px -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
