"""Check actual exported geometry, texture provenance and atlas pixel identity."""
from pathlib import Path
import hashlib,json,struct,io
import numpy as np
from PIL import Image
import trimesh

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
report=json.loads((HERE/'build-report.json').read_text(encoding='utf-8'))
for item in report['files']:
    path=HERE/item['name'];assert path.stat().st_size==item['size']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
scene=trimesh.load(HERE/'generic-broadleaf-tree.glb',force='scene',process=False)
assert len(scene.geometry)==6
expected={m['name']:m['triangles'] for lod in report['lods'] for m in lod['meshes']}
for name in scene.graph.nodes_geometry:
    mesh=scene.geometry[scene.graph[name][1]]
    assert len(mesh.faces)==expected[name],name
    assert np.isfinite(mesh.vertices).all()
    assert mesh.area_faces.min()>1e-12,(name,float(mesh.area_faces.min()))
blob=(HERE/'generic-broadleaf-tree.glb').read_bytes();n=struct.unpack_from('<I',blob,12)[0]
gltf=json.loads(blob[20:20+n]);binary=blob[20+n+8:]
leaf=[mat for mat in gltf['materials'] if mat['name']=='Atlas tree · leaves'];assert len(leaf)==1
assert leaf[0]['alphaMode']=='MASK' and not leaf[0].get('extensions',{}).get('KHR_materials_unlit')
assert leaf[0]['alphaCutoff']==.1
assert np.allclose(leaf[0]['pbrMetallicRoughness']['baseColorFactor'],report['leafTintLinear'],atol=1e-6)
texture=gltf['textures'][leaf[0]['pbrMetallicRoughness']['baseColorTexture']['index']]
image=gltf['images'][texture['source']];view=gltf['bufferViews'][image['bufferView']]
pixels=Image.open(io.BytesIO(binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]))
assert pixels.mode=='RGBA' and pixels.getextrema()[3]==(0,255)
assert np.array_equal(np.asarray(pixels),np.asarray(Image.open(HERE/'textures/jacaranda_tree_leaves_diff_1k.png')))
for item in json.loads((HERE/'textures/manifest.json').read_text())['files']:
    assert hashlib.sha256((HERE/'textures'/item['file']).read_bytes()).hexdigest()==item['sha256']
metadata=json.loads((ROOT/'viewer/assets/forest-impostor-metadata.json').read_text())
assert len(metadata['frames'])==16 and metadata['license']=='CC0'
if metadata['renderEngine'].startswith('three-webgl/'):
    assert metadata['renderEngine']=='three-webgl/r186'
else:
    assert metadata['renderSourceBlendSha256']==next(r['sha256'] for r in report['files'] if r['name'].endswith('.blend'))
assert metadata['renderSourceGltfSha256']==next(r['sha256'] for r in report['files'] if r['name'].endswith('.glb'))
assert metadata['sourceTriangles']==report['lods'][0]['triangles'] and metadata['sourceModelLOD']==0
atlas_path=ROOT/'viewer/assets'/metadata['atlas']['file']
assert hashlib.sha256(atlas_path.read_bytes()).hexdigest()==metadata['atlas']['sha256']
atlas=Image.open(atlas_path);assert atlas.size==(2048,2048) and atlas.mode=='RGBA'
if metadata.get('atlasRgbaSha256'):
    assert hashlib.sha256(np.asarray(atlas).tobytes()).hexdigest()==metadata['atlasRgbaSha256']
for frame in metadata['frames']:
    index=frame['index'];path=HERE/'impostors'/frame['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==frame['sha256']
    x=(index%4)*512;y=(index//4)*512
    assert np.array_equal(np.asarray(atlas.crop((x,y,x+512,y+512))),np.asarray(Image.open(path)))
    if frame.get('rgbaSha256'):
        assert hashlib.sha256(np.asarray(Image.open(path)).tobytes()).hexdigest()==frame['rgbaSha256']
assert hashlib.sha256((ROOT/'site-data.json').read_bytes()).hexdigest()=='022a88053df75b9d755e082079ed31f6b922e79bb8bca03016890c52cc828358'
assert hashlib.sha256((ROOT/'v2/manual-roads-metric.json').read_bytes()).hexdigest()=='d5038924b6356022b273fff88bc12ba6f3091c8df2294ca6fd64decf1a5fad56'
result={'geometryMeshes':6,'nearTriangles':report['lods'][0]['triangles'],'farMeshTriangles':report['lods'][1]['triangles'],
    'farImpostorTrianglesPerTree':2,'renderFrames':16,'atlasBytes':atlas_path.stat().st_size,
    'renderEngine':metadata['renderEngine'],'alphaCutoff':leaf[0]['alphaCutoff'],
    'atlasFramesPixelIdentical':True,'nearAndFarShareGeometrySource':True,'leafColorFactorExported':True,'m5AndQgisSourceUnchanged':True}
(HERE/'asset-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
