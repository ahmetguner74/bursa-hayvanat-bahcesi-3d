"""Build the standalone Bursa Zoo viewer for local use only."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
VIEWER = HERE / "viewer"
VENDOR = HERE / "vendor"
DIST = HERE / "dist"


def main(local_only: bool = True) -> None:
    if not local_only:
        raise ValueError("This builder is local-only; public docs output is disabled")
    if not (VENDOR / "three.module.js").is_file():
        raise FileNotFoundError("The standalone Three.js vendor files are missing")
    # Validate and rebuild the mutually exclusive scene surfaces from source data.
    subprocess.run([sys.executable, str(HERE / "build_surface_layers.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/31-pelikan-goleti/model/build_dome.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/30-turk-koyu/model/build_village.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/15-penguen/model/build_penguin.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/12-afrika-savana/model/build_platform.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/11-lemur/model/build_lemur.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/14-afrika-koyu/model/build_african_village.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/13-afrika-kafe/model/prepare_cafe_textures.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/13-afrika-kafe/model/build_cafe.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/09-habes-maymunu/model/build_habes.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/29-boz-ayi/model/build_bear_pool.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "build_scene_model_catalog.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "build_building_shell.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "build_landscape_layout.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "build_ground_material.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "build_vegetation_materials.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/build_area_contexts.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/15-penguen/model/hayvan/prepare_penguin.py")], cwd=HERE, check=True)
    for target in (DIST,):
        target.mkdir(exist_ok=True)
        for name in ("index.html", "style.css", "app.js", "model.js", "scene-effects.js", "forest.js", "forest-impostors.js", "region-models.js", "ground-material.js", "lighting.js", "plant-cards.js", "atlas-orbit.js", "penguins.js", "penguin-motion.js"):
            shutil.copy2(VIEWER / name, target / name)
        shutil.copytree(VENDOR, target / "vendor", dirs_exist_ok=True)
        shutil.copytree(VIEWER / "assets", target / "assets", dirs_exist_ok=True)
        (target / "reference-maps").mkdir(exist_ok=True)
        shutil.copy2(HERE / "reference-maps-private/2026-09-kroki.jpg", target / "reference-maps/2026-09-resmi-kroki.jpg")
        (target / "models").mkdir(exist_ok=True)
        penguin_animal = HERE / "bolgeler/15-penguen/model/hayvan"
        shutil.copy2(penguin_animal / "african-penguin.glb", target / "models/african-penguin.glb")
        shutil.copy2(penguin_animal / "colony-layout.json", target / "models/penguin-colony.json")
        shutil.copy2(penguin_animal / "ATTRIBUTION.txt", target / "models/penguin-ATTRIBUTION.txt")
        shutil.copy2(HERE / "bolgeler/30-turk-koyu/model/turk-koyu.glb", target / "models/turk-koyu.glb")
        shutil.copy2(HERE / "bolgeler/15-penguen/model/penguen-havuzu.glb", target / "models/penguen-havuzu.glb")
        shutil.copy2(HERE / "bolgeler/12-afrika-savana/model/savanna-ahsap-platform.glb", target / "models/savanna-ahsap-platform.glb")
        shutil.copy2(HERE / "bolgeler/11-lemur/model/lemur-adasi.glb", target / "models/lemur-adasi.glb")
        shutil.copy2(HERE / "bolgeler/14-afrika-koyu/model/afrika-koyu.glb", target / "models/afrika-koyu.glb")
        shutil.copy2(HERE / "bolgeler/13-afrika-kafe/model/afrika-kafe.glb", target / "models/afrika-kafe.glb")
        shutil.copy2(HERE / "bolgeler/09-habes-maymunu/model/habes-maymunu-adasi.glb", target / "models/habes-maymunu-adasi.glb")
        shutil.copy2(HERE / "bolgeler/29-boz-ayi/model/boz-ayi-havuz-kiyisi.glb", target / "models/boz-ayi-havuz-kiyisi.glb")
        shutil.copy2(HERE / "bolgeler/_ortak/peyzaj/model/generic-broadleaf-tree.glb", target / "models/generic-broadleaf-tree.glb")
        shutil.copy2(HERE / "bolgeler/_ortak/peyzaj/model/build-report.json", target / "models/tree-model-metadata.json")
        shutil.copy2(HERE / "site-data.json", target / "site-data.json")
        shutil.copy2(HERE / "current-plan-data.json", target / "current-plan-data.json")
        shutil.copy2(HERE / "surface-layers.json", target / "surface-layers.json")
        shutil.copy2(HERE / "building-shell.json", target / "building-shell.json")
        shutil.copy2(HERE / "landscape-layout.json", target / "landscape-layout.json")
        shutil.copy2(HERE / "ground-material-layout.json", target / "ground-material-layout.json")
        shutil.copy2(HERE / "region-locations.json", target / "region-locations.json")
        shutil.copy2(HERE / "scene-model-catalog.json", target / "scene-model-catalog.json")
        for old_public_file in ("model-sources.json", "MODEL_STANDARD.md"):
            (target / old_public_file).unlink(missing_ok=True)
        if target == DIST:
            review = target / "model-review"
            review.mkdir(exist_ok=True)
            shutil.copy2(HERE / "model-review/index.html", review / "index.html")
            shutil.copy2(HERE / "model-review/tree-atlas-baker.js", review / "tree-atlas-baker.js")
            source_model = HERE / "bolgeler/31-pelikan-goleti/model"
            for name in ("su-kuslari-kubbesi-yakin.glb", "su-kuslari-kubbesi-uzak.glb"):
                shutil.copy2(source_model / name, review / name)
            shutil.copy2(HERE / "bolgeler/30-turk-koyu/model/turk-koyu.glb", review / "turk-koyu.glb")
            shutil.copy2(HERE / "bolgeler/15-penguen/model/penguen-havuzu.glb", review / "penguen-havuzu.glb")
            shutil.copy2(HERE / "bolgeler/12-afrika-savana/model/savanna-ahsap-platform.glb", review / "savanna-ahsap-platform.glb")
            shutil.copy2(HERE / "bolgeler/11-lemur/model/lemur-adasi.glb", review / "lemur-adasi.glb")
            shutil.copy2(HERE / "bolgeler/14-afrika-koyu/model/afrika-koyu.glb", review / "afrika-koyu.glb")
            shutil.copy2(HERE / "bolgeler/13-afrika-kafe/model/afrika-kafe.glb", review / "afrika-kafe.glb")
            shutil.copy2(HERE / "bolgeler/09-habes-maymunu/model/habes-maymunu-adasi.glb", review / "habes-maymunu-adasi.glb")
            shutil.copy2(HERE / "bolgeler/29-boz-ayi/model/boz-ayi-havuz-kiyisi.glb", review / "boz-ayi-havuz-kiyisi.glb")
            comparison = target / "design-reference"
            comparison.mkdir(exist_ok=True)
            for name in ("compare-local.html", "woodland-aviary-concept.png"):
                shutil.copy2(HERE / "design-reference" / name, comparison / name)
        (target / ".nojekyll").touch()
        print(target)


if __name__ == "__main__":
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--local-only"):
        raise SystemExit("Usage: python publish_local.py [--local-only]")
    main()
