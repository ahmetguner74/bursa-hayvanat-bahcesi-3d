"""Technical image delivery preparation; keep generated originals unmodified."""
from pathlib import Path
import hashlib,json
from PIL import Image

ROOT=Path(__file__).resolve().parent;ASSETS=ROOT/'viewer/assets'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
source=ASSETS/'woodland-wildflower-clump-v1.png'
records=json.loads((ASSETS/'asset-manifest.json').read_text(encoding='utf-8'))['assets']
assert sha(source)==next(r['sha256'] for r in records if r['file']==source.name)
with Image.open(source) as image:
    assert image.mode=='RGBA'
    image.thumbnail((512,512),Image.Resampling.LANCZOS)
    target=ASSETS/'woodland-wildflower-clump-web-v1.png';image.save(target,optimize=True)
    size=list(image.size)
record={'file':target.name,'sha256':sha(target),'source':source.name,'sourceSha256':sha(source),
    'size':size,'mode':'RGBA','baseV':1078/1254,
    'derivation':'Lanczos max512px PNG; preserve RGBA. No painting, hue or alpha-mask editing.'}
(ASSETS/'woodland-wildflower-derivative.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'vegetationDeliveryBytes':target.stat().st_size,'size':size}))

foliage_records=[]
for name in ['foliage-cluster-v1.png','foliage-cluster-dark-v1.png','woodland-fern-clump-v1.png',
             'woodland-broadleaf-clump-v1.png','woodland-grass-tussock-v1.png','woodland-shrub-spray-v1.png']:
    source=ASSETS/name
    assert sha(source)==next(r['sha256'] for r in records if r['file']==name)
    with Image.open(source) as image:
        assert image.mode=='RGBA'
        image.thumbnail((512,512),Image.Resampling.LANCZOS)
        target=ASSETS/name.replace('-v1.png','-web-v1.png');image.save(target,optimize=True)
    foliage_records.append({'file':target.name,'sha256':sha(target),'source':source.name,'sourceSha256':sha(source),
        'size':list(image.size),'mode':'RGBA','bytes':target.stat().st_size,
        'derivation':'Lanczos max512px PNG; preserve RGBA, no painting or alpha-mask editing.'})
(ASSETS/'woodland-foliage-derivatives.json').write_text(json.dumps(foliage_records,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'foliageDeliveryTextures':len(foliage_records),'bytes':sum(r['bytes'] for r in foliage_records)}))
