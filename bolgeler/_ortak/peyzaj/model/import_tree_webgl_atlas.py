"""Import the single PNG produced by the local model-review tree baker."""
import hashlib,json,shutil,sys,struct
from pathlib import Path
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
source=Path(sys.argv[1]).resolve();image=Image.open(source);image.load()
assert image.mode=='RGBA' and image.size==(2048,2048)
meta=json.loads(image.info['BursaZooTree'])
assert meta['renderEngine']=='three-webgl/r186' and len(meta['frames'])==16 and meta['sourceModelLOD']==0
build=json.loads((HERE/'build-report.json').read_text(encoding='utf-8'))
assert meta['renderSourceGltfSha256']==next(r['sha256'] for r in build['files'] if r['name'].endswith('.glb'))
assert meta['sourceTriangles']==build['lods'][0]['triangles']
blob=source.read_bytes();encoded=bytearray(blob[:8]);offset=8;metadata_chunks=0
while offset<len(blob):
    length=struct.unpack_from('>I',blob,offset)[0];chunk=blob[offset:offset+length+12]
    if chunk[4:8]==b'iTXt' and chunk[8:].startswith(b'BursaZooTree\0'):
        metadata_chunks+=1
    else:encoded.extend(chunk)
    offset+=length+12
assert metadata_chunks==1 and offset==len(blob)
assert hashlib.sha256(encoded).hexdigest()==meta['encodedPngSha256']
meta['canvasRgbaSha256BeforeEncoding']=meta.pop('atlasRgbaSha256')
meta['atlasRgbaSha256']=hashlib.sha256(np.asarray(image).tobytes()).hexdigest()
target=HERE/'impostors';target.mkdir(exist_ok=True)
for frame in meta['frames']:
    index=frame['index'];x=(index%4)*512;y=(index//4)*512;crop=image.crop((x,y,x+512,y+512))
    frame['canvasRgbaSha256BeforeEncoding']=frame['rgbaSha256']
    frame['rgbaSha256']=hashlib.sha256(np.asarray(crop).tobytes()).hexdigest()
    path=target/f'tree-{index:02d}.png';crop.save(path,optimize=True)
    frame.update(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),size=path.stat().st_size)
original=HERE/'browser-atlas-source.png'
if source!=original.resolve():shutil.copy2(source,original)
atlas=ROOT/'viewer/assets/forest-impostor-atlas.png';shutil.copy2(original,atlas)
meta['atlas']={'file':atlas.name,'columns':4,'rows':4,'size':[2048,2048],'sha256':hashlib.sha256(atlas.read_bytes()).hexdigest(),'bytes':atlas.stat().st_size}
meta['limitations']=['Generic visual vegetation, not a Bursa botanical survey.','View-dependent far proxy with limited parallax; fixed canonical lighting does not reproduce every rotated tree lighting state.','Near and far are exclusive.']
for path in [target/'manifest.json',ROOT/'viewer/assets/forest-impostor-metadata.json']:
    path.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frames':16,'atlasBytes':atlas.stat().st_size,'engine':meta['renderEngine'],'sourceSha256':meta['renderSourceGltfSha256']}))
