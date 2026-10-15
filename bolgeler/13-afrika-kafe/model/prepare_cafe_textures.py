"""Encode opaque presentation textures for the small cafe glTF derivative."""
from pathlib import Path
import hashlib,json
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
target=HERE/'textures';target.mkdir(exist_ok=True)
records=[]
for name in ['afrika-koyu-roof-shingles-v1','savanna-platform-wood-v1','woodland-stone-path-v1']:
    source=ROOT/'viewer/assets'/f'{name}.png';image=Image.open(source).convert('RGB');image.thumbnail((512,512),Image.Resampling.LANCZOS)
    path=target/f'{name}.jpg';image.save(path,quality=90,subsampling=0,optimize=True)
    records.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,
        'source':'../../../../viewer/assets/'+source.name,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'size':list(image.size),'process':'Opaque RGB JPEG90, maximum512px; technical glTF encoding. Original generated image unchanged.'})
(target/'manifest.json').write_text(json.dumps({'schema':'bursa-zoo-cafe-textures/v1','files':records},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'textures':len(records),'bytes':sum(r['bytes'] for r in records)}))
