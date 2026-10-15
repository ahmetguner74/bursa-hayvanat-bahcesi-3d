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

RUNTIME_FILES = (
    "index.html", "style.css", "app.js", "model.js", "scene-effects.js", "forest.js",
    "forest-impostors.js", "region-models.js", "ground-material.js", "lighting.js",
    "plant-cards.js", "atlas-orbit.js", "penguins.js", "penguin-motion.js",
    "rhinos.js", "rhino-motion.js", "giraffes.js", "giraffe-motion.js", "aviary-birds.js",
    "animal-interaction.js", "tap-colony.js", "explorer-camera.js", "explorer-labels.js", "animal-info.js", "animal-profiles.js", "animal-views.js", "penguin-views.js", "touch-cue.js",
)


def copy_runtime(target: Path) -> None:
    for name in RUNTIME_FILES:
        shutil.copy2(VIEWER / name, target / name)
    shutil.copytree(VIEWER / "assets", target / "assets", dirs_exist_ok=True)
    for old_module in ("penguin-interaction-ui.js", "penguin-info.js"):
        (target / old_module).unlink(missing_ok=True)
    credits = []
    for name in ("penguin", "rhino", "giraffe", "aviary"):
        source = target / "models" / (name + "-ATTRIBUTION.txt")
        if source.is_file():
            credits.append(source.read_text(encoding="utf-8"))
    if credits:
        (target / "models/ATTRIBUTION.txt").write_text("\n\n".join(credits), encoding="utf-8")


def main(local_only: bool = True, runtime_only: bool = False) -> None:
    if not local_only:
        raise ValueError("This builder is local-only; public docs output is disabled")
    if not (VENDOR / "three.module.js").is_file():
        raise FileNotFoundError("The standalone Three.js vendor files are missing")
    if runtime_only:
        if not (DIST / "scene-model-catalog.json").is_file() or not (DIST / "models/penguin-colony.json").is_file():
            raise FileNotFoundError("Build the local model package before updating its runtime")
        copy_runtime(DIST)
        print(DIST)
        return
    # Validate and rebuild the mutually exclusive scene surfaces from source data.
    subprocess.run([sys.executable, str(HERE / "bolgeler/16-gergedan/model/hayvan/prepare_rhino.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/16-gergedan/model/build_habitat.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/12-afrika-savana/model/giraffe/build_habitat.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "build_surface_layers.py")], cwd=HERE, check=True)
    subprocess.run([sys.executable, str(HERE / "bolgeler/32-su-kuslari/model/build_bird_layout.py")], cwd=HERE, check=True)
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
    node=shutil.which('node')
    if not node:raise FileNotFoundError('Node.js is required to bake penguin transition grounding')
    subprocess.run([node,str(HERE / 'bolgeler/15-penguen/model/hayvan/bake_transitions.mjs')],cwd=HERE,check=True)
    for target in (DIST,):
        target.mkdir(exist_ok=True)
        shutil.copytree(VENDOR, target / "vendor", dirs_exist_ok=True)
        (target / "reference-maps").mkdir(exist_ok=True)
        shutil.copy2(HERE / "reference-maps-private/2026-09-kroki.jpg", target / "reference-maps/2026-09-resmi-kroki.jpg")
        (target / "models").mkdir(exist_ok=True)
        rhino = HERE / "bolgeler/16-gergedan/model"
        for source,name in [(rhino/'gergedan-yasam-alani.glb','gergedan-yasam-alani.glb'),(rhino/'colony-layout.json','rhino-colony.json'),(rhino/'hayvan/white-rhinoceros.glb','white-rhinoceros.glb'),(rhino/'hayvan/source-manifest.json','rhino-asset.json'),(rhino/'hayvan/ATTRIBUTION.txt','rhino-ATTRIBUTION.txt'),(rhino/'habitat-report.json','rhino-habitat.json')]:
            shutil.copy2(source,target/'models'/name)
        giraffe = HERE / 'bolgeler/12-afrika-savana/model/giraffe'
        for source,name in [(giraffe/'zurafa-acik-yasam-alani.glb','zurafa-acik-yasam-alani.glb'),(giraffe/'giraffe-colony.json','giraffe-colony.json'),(giraffe/'baringo-giraffe.glb','baringo-giraffe.glb'),(giraffe/'giraffe-asset.json','giraffe-asset.json'),(giraffe/'ATTRIBUTION.txt','giraffe-ATTRIBUTION.txt'),(giraffe/'habitat-report.json','giraffe-habitat.json')]:
            shutil.copy2(source,target/'models'/name)
        birds = HERE / 'bolgeler/32-su-kuslari/model'
        for source,name in [(birds/'hayvan/greater-flamingo.glb','greater-flamingo.glb'),(birds/'aviary-birds-layout.json','aviary-birds-layout.json'),(birds/'hayvan/ATTRIBUTION.txt','aviary-ATTRIBUTION.txt')]:
            shutil.copy2(source,target/'models'/name)
        penguin_animal = HERE / "bolgeler/15-penguen/model/hayvan"
        shutil.copy2(penguin_animal / "african-penguin.glb", target / "models/african-penguin.glb")
        shutil.copy2(penguin_animal / "colony-layout.json", target / "models/penguin-colony.json")
        shutil.copy2(penguin_animal / "penguin-transitions.json", target / "models/penguin-transitions.json")
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
            shutil.copytree(HERE / 'model-review/giraffe', review / 'giraffe', dirs_exist_ok=True)
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
        copy_runtime(target)
        (target / ".nojekyll").touch()
        print(target)
    rhino_study = HERE / "model-review/rhino/build_local.py"
    if rhino_study.is_file():
        subprocess.run([sys.executable, str(rhino_study)], cwd=HERE, check=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-only", action="store_true")
    parser.add_argument("--runtime-only", action="store_true", help="Update UI/runtime in an existing local dist package")
    args = parser.parse_args()
    main(runtime_only=args.runtime_only)
