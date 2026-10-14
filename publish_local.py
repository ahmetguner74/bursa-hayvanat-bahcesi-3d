"""Build the standalone Bursa Zoo viewer for local use and GitHub Pages."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
VIEWER = HERE / "viewer"
VENDOR = HERE / "vendor"
DIST = HERE / "dist"
DOCS = HERE / "docs"


def main() -> None:
    if not (VENDOR / "three.module.js").is_file():
        raise FileNotFoundError("The standalone Three.js vendor files are missing")
    # Validate and rebuild the mutually exclusive scene surfaces from source data.
    subprocess.run([sys.executable, str(HERE / "build_surface_layers.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "build_building_shell.py")], cwd=HERE, check=True)
    for target in (DIST, DOCS):
        target.mkdir(exist_ok=True)
        for name in ("index.html", "style.css", "app.js", "model.js"):
            shutil.copy2(VIEWER / name, target / name)
        shutil.copytree(VENDOR, target / "vendor", dirs_exist_ok=True)
        shutil.copy2(HERE / "site-data.json", target / "site-data.json")
        shutil.copy2(HERE / "current-plan-data.json", target / "current-plan-data.json")
        shutil.copy2(HERE / "surface-layers.json", target / "surface-layers.json")
        shutil.copy2(HERE / "building-shell.json", target / "building-shell.json")
        for old_public_file in ("model-sources.json", "MODEL_STANDARD.md"):
            (target / old_public_file).unlink(missing_ok=True)
        (target / ".nojekyll").touch()
        print(target)


if __name__ == "__main__":
    main()
