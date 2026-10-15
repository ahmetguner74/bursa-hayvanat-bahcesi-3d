"""Pack original 3D render frames into one runtime atlas, without repainting."""
from pathlib import Path
from PIL import Image
import json,hashlib

HERE=Path(__file__).resolve().parent
OUT=HERE.parents[3]/'viewer/assets'
source=HERE/'impostors';metadata=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
assert len(metadata['frames'])==16
atlas=Image.new('RGBA',(2048,2048),(0,0,0,0))
for frame in metadata['frames']:
    path=source/frame['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==frame['sha256']
    image=Image.open(path);assert image.size==(512,512) and image.mode=='RGBA'
    assert image.getbbox() is not None
    index=frame['index'];atlas.paste(image,((index%4)*512,(index//4)*512))
path=OUT/'forest-impostor-atlas.png';atlas.save(path,optimize=True,compress_level=9)
metadata['atlas']={'file':path.name,'columns':4,'rows':4,'size':[2048,2048],
    'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
metadata['limitations']=['Generic CC0 vegetation, not proof of Bursa species.',
    'Far silhouette proxy with baked self-lighting; view changes have limited parallax and lighting is approximate.',
    'Near and far are exclusive. Original 3D source and editable derivative remain local.']
(OUT/'forest-impostor-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metadata['atlas']))
