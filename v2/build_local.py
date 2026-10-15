"""Build the isolated V2 road/official-map preview under dist/v2 only."""

from __future__ import annotations

import json
import hashlib
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE.parent / "dist" / "v2"
FILES = ("index.html", "style.css", "app.js", "rectification.json")
ROADS_SOURCE = HERE / "manual-roads-metric.json"
OVERLAY_SOURCE = HERE / "private" / "rectified-september.png"
OVERLAY_NAME = "official-kroki-rectified.png"


def main() -> None:
    for name in FILES:
        if not (HERE / name).is_file():
            raise FileNotFoundError(f"V2 source is missing: {HERE / name}")
    rectification = json.loads((HERE / "rectification.json").read_text(encoding="utf-8"))
    roads = json.loads(ROADS_SOURCE.read_text(encoding="utf-8"))
    if roads.get("schema") != "bursa-zoo-v2-manual-roads/v2":
        raise ValueError("Manual QGIS road package is missing or incompatible")
    if not isinstance(rectification.get("grid"), dict):
        raise ValueError("V2 rectification grid is missing")
    if not isinstance(roads.get("features"), list):
        raise ValueError("V2 roads feature list is missing")
    TARGET.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        shutil.copy2(HERE / name, TARGET / name)
    shutil.copy2(ROADS_SOURCE, TARGET / "roads-metric.json")
    output = TARGET / OVERLAY_NAME
    grid = rectification["grid"]
    width = round((grid["xMax"] - grid["xMin"]) * grid["pixelsPerMetre"])
    height = round((grid["yMax"] - grid["yMin"]) * grid["pixelsPerMetre"])
    overlay = {
        "available": False,
        "sourceUrl": rectification.get("source", {}).get("imageUrl"),
        "width": width,
        "height": height,
    }
    if OVERLAY_SOURCE.is_file():
        digest = hashlib.sha256(OVERLAY_SOURCE.read_bytes()).hexdigest()
        expected = rectification.get("privateOutput", {}).get("sha256")
        if digest != expected:
            raise ValueError("Rectified official map hash changed; run v2/rectify_plan.py again")
        if rectification.get("privateOutput", {}).get("sizePixels") != [width, height]:
            raise ValueError("Rectified official map size does not match the V2 grid")
        shutil.copy2(OVERLAY_SOURCE, output)
        overlay.update(available=True, path=f"{OVERLAY_NAME}?v={digest[:12]}", sha256=digest)
    else:
        output.unlink(missing_ok=True)
        print("Official map overlay is unavailable locally; the V2 page will show its source link.")
    (TARGET / "official-map.json").write_text(json.dumps(overlay, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"V2 local preview: {TARGET}")
    print(f"Road surfaces: {len(roads['features'])}")
    print(f"Official map overlay: {'ready' if overlay['available'] else 'missing'}")


if __name__ == "__main__":
    main()
