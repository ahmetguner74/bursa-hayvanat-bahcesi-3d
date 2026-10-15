"""Add architectural references for the #31/#32 dome interpretation."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent
AREAS = PROJECT / "bolgeler"
PHOTO_ROOT = PROJECT / "reference-photos-private"
PHOTO_MANIFEST = {item["file"]: item for item in json.loads(
    (PHOTO_ROOT / "manifest.json").read_text(encoding="utf-8"))}


def add_to(area: Path) -> None:
    source_path = area / "kaynaklar/kaynakca.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    items = []
    for name in sorted(PHOTO_MANIFEST):
        if not (name.startswith("uskon-") or name.startswith("trend-insaat-")
                or name.startswith("gezi-bilen-")):
            continue
        original = PHOTO_ROOT / name
        target = area / "kaynaklar/fotograflar" / name
        if not target.exists():
            try:
                os.link(original, target)
            except OSError:
                shutil.copy2(original, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != PHOTO_MANIFEST[name]["sha256"]:
            raise ValueError(f"Source bytes differ: {target}")
        items.append({"file": str(target.relative_to(area)),
            "url": PHOTO_MANIFEST[name]["url"],
            "sha256": PHOTO_MANIFEST[name]["sha256"],
            "role": "Yapı biçimi/plan/fotoğrafı; tarihî kaynak, mevcut iç peyzajı tek başına doğrulamaz",
            "captureDate": "bilinmiyor", "publication": "yalnız yerel araştırma"})
    source["architecturalReferences"] = items
    source["architecturalDocument"] = {
        "title": "USKON Bursa Zoo Waterbird Cage — imalatçı teknik açıklaması",
        "url": "https://uskon.com/en/bursa-zoo-waterbird-cage-single-wall-elliptical-dome/",
        "facts": {"lengthM": 70, "widthM": 40, "heightM": 20,
                  "pipeCount": 2029, "nodeCount": 700, "nylonNetApertureCm": 5},
        "scopeNote": "Resmî krokide kubbe #31 işaretinin üzerinde; #32 güneyinde. Etiket-yapı eşleşmesi kesinleşmedi."
    }
    source_path.write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8")


for folder in ("31-pelikan-goleti", "32-su-kuslari"):
    add_to(AREAS / folder)
