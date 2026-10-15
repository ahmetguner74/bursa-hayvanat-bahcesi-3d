"""Technical 8-bit runtime derivatives; keep all CC0 original files intact."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parent/'textures'
SOURCE=OUT.parents[4]/'bolgeler/_qa/tree-assets/jacaranda-source'
OUT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((SOURCE/'source-files.json').read_text(encoding='utf-8-sig'))
records=[]
for record in manifest['files']:
    src=SOURCE/record['file']
    if src.suffix!='.png':continue
    assert hashlib.sha256(src.read_bytes()).hexdigest()==record['sha256']
    image=Image.open(src)
    if image.mode.startswith('I'):
        values=np.asarray(image,dtype=np.float64)
        assert values.max()<=65535
        image=Image.fromarray(np.round(values/257).astype('uint8'))
    filename=src.name
    if '_nor_gl_' in filename:
        values=np.asarray(image.convert('RGB').resize((512,512),Image.Resampling.LANCZOS),dtype=np.float32)/127.5-1
        values/=np.maximum(np.linalg.norm(values,axis=-1,keepdims=True),1e-6)
        image=Image.fromarray(np.round((values+1)*127.5).clip(0,255).astype('uint8'))
    elif '_rough_' in filename:image=image.resize((256,256),Image.Resampling.BOX)
    if '_diff_' in filename and 'leaves' not in filename:
        dst=OUT/(src.stem+'.jpg');image.convert('RGB').save(dst,quality=90,subsampling=0,optimize=True)
    else:
        dst=OUT/filename;image.save(dst,optimize=True,compress_level=9)
    records.append({'file':dst.name,'source':record['file'],'sourceSha256':record['sha256'],
        'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'size':dst.stat().st_size,
        'conversion':'Runtime 8-bit; diffuse wood JPEG quality90; normal maps512px and renormalized; roughness256px; leaf color/alpha1024px. No repainting.'})
(OUT/'manifest.json').write_text(json.dumps({'source':manifest['source'],'license':'CC0','files':records},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(records),'totalBytes':sum(r['size'] for r in records)}))
