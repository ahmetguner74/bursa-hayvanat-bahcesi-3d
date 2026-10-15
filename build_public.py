"""Prepare the explicitly requested GitHub Pages release from the local build.

The local builders still write only dist/. This command copies an allowlist of
browser runtime files to docs/; research photos, DGN archives and source models
are never copied to the public website. No Git commit or push is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
PUBLIC = ROOT / "docs"
FILES = (
    ".nojekyll", "index.html", "style.css", "app.js", "model.js",
    "scene-effects.js", "forest.js", "forest-impostors.js", "region-models.js",
    "ground-material.js", "lighting.js", "plant-cards.js", "atlas-orbit.js",
    "penguins.js", "penguin-motion.js", "rhinos.js", "rhino-motion.js",
    "animal-interaction.js", "tap-colony.js", "explorer-camera.js", "explorer-labels.js", "animal-info.js", "animal-profiles.js", "animal-views.js", "penguin-views.js", "touch-cue.js",
    "giraffes.js", "giraffe-motion.js", "aviary-birds.js", "site-data.json", "current-plan-data.json",
    "surface-layers.json", "building-shell.json", "landscape-layout.json",
    "ground-material-layout.json", "region-locations.json", "scene-model-catalog.json",
)
DIRECTORIES = ("vendor", "assets", "models", "model-review", "v2", "reference-maps", "design-reference")
EXTENSIONS = {".js", ".html", ".css", ".json", ".glb", ".png", ".jpg", ".svg", ".txt"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", required=True, action="store_true",
                        help="Explicitly prepare docs/ for the requested public release")
    parser.parse_args()
    sources = [DIST / name for name in FILES]
    for folder in DIRECTORIES:
        directory = DIST / folder
        if not directory.is_dir():
            raise FileNotFoundError(directory)
        for file in directory.rglob("*"):
            if file.is_file() and (file.suffix in EXTENSIONS or file.name == "LICENSE"):
                if any(part.startswith(".") or part in {"private", "source", "node_modules", "__pycache__"}
                       for part in file.relative_to(DIST).parts):
                    raise ValueError(f"Unexpected private input: {file.relative_to(DIST)}")
                sources.append(file)
    for file in sources:
        if not file.is_file():
            raise FileNotFoundError(file)
        if file.stat().st_size >= 95 * 1024 * 1024:
            raise ValueError(f"Runtime file is too large for regular Git: {file.name}")
    PUBLIC.mkdir(exist_ok=True)
    for old_module in ("penguin-interaction-ui.js", "penguin-info.js"):
        (PUBLIC / old_module).unlink(missing_ok=True)
    records = []
    for file in sorted(sources):
        relative = file.relative_to(DIST)
        destination = PUBLIC / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, destination)
        records.append({"path": relative.as_posix(), "bytes": file.stat().st_size,
                        "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    revision = re.search(r"app\.js\?v=([\w-]+)", (DIST / "index.html").read_text(encoding="utf-8")).group(1)
    report = {
        "schema": "bursa-zoo-public-release/v1", "revision": revision,
        "source": "Verified local dist build; explicit --publish command",
        "officialMapSource": "https://www.bursahayvanatbahcesi.com/wp-content/uploads/2026/09/kroki.jpg",
        "officialMapCredit": "Bursa Hayvanat Bahçesi; overlay alignment is approximate, not surveyed",
        "files": records,
    }
    (PUBLIC / "publication.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"revision": revision, "files": len(records),
                      "runtimeMiB": round(sum(item["bytes"] for item in records) / 1048576, 2)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
