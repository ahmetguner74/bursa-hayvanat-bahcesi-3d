"""Copy the rhino study to the existing local viewer; no public output."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
MODEL=ROOT/'bolgeler/16-gergedan/model'
def main():
    target=ROOT/'dist/model-review/rhino';target.mkdir(parents=True,exist_ok=True)
    # Superseded generated runtime copies are now shared in dist/models.
    assert target.resolve().is_relative_to((ROOT/'dist').resolve())
    for name in ['white-rhinoceros.glb','rhino-habitat-study.glb','rhino-asset.json','rhino-habitat.json','ATTRIBUTION.txt']:
        (target/name).unlink(missing_ok=True)
    for name in ['index.html','rhino-study.js']:shutil.copy2(HERE/name,target/name)
    (ROOT/'dist/models').mkdir(exist_ok=True)
    for source,name in [(MODEL/'gergedan-yasam-alani.glb','gergedan-yasam-alani.glb'),(MODEL/'colony-layout.json','rhino-colony.json'),(MODEL/'hayvan/white-rhinoceros.glb','white-rhinoceros.glb'),(MODEL/'hayvan/source-manifest.json','rhino-asset.json'),(MODEL/'habitat-report.json','rhino-habitat.json')]:shutil.copy2(source,ROOT/'dist/models'/name)
    for name in ['rhinos.js','rhino-motion.js']:shutil.copy2(ROOT/'viewer'/name,ROOT/'dist'/name)
    print('Local rhino study: http://127.0.0.1:8768/model-review/rhino/')
if __name__=='__main__':main()
