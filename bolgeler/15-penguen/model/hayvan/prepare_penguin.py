"""Create the metric runtime asset and safe domains from unchanged sources."""
from pathlib import Path
import hashlib,json,struct,zipfile
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def polygons(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    return [p for child in g.geoms for p in polygons(child)]
def rings(g):return [{'outer':[list(v) for v in p.exterior.coords],'holes':[[list(v) for v in h.coords] for h in p.interiors]} for p in polygons(g)]

def main():
    original=HERE/'source/major-african-penguin-original.glb'
    if sha(original)!='ecee6a9f7293e058061898e6726b7f83ba42c6e4b4c50e7becaf0ddc447437b7':raise ValueError('Penguin source changed')
    source=original.read_bytes();length=struct.unpack_from('<I',source,12)[0];tree=json.loads(source[20:20+length]);binary=bytearray(source[20+length:])
    rig=json.loads((HERE/'rig-inspection.json').read_text());idle=next(c for c in rig['clips'] if c['name']=='Idle')
    low,high=idle['samples'][0]['bounds'];body_low=idle['samples'][0]['bodyGround'];height=.62;scale=height/(high[1]-body_low)
    wrapper={'name':'AfricanPenguin_MetricOrigin','translation':[0,-body_low*scale,.20*scale],'scale':[scale]*3,'children':tree['scenes'][tree.get('scene',0)]['nodes']}
    tree['scenes'][tree.get('scene',0)]['nodes']=[len(tree['nodes'])];tree['nodes'].append(wrapper)
    skinned=[index for index,node in enumerate(tree['nodes']) if 'skin' in node]
    for node in tree['nodes']:
        if 'children' in node:node['children']=[index for index in node['children'] if index not in skinned]
    tree['scenes'][tree.get('scene',0)]['nodes'].extend(skinned)
    cleared=0
    for mesh in tree['meshes']:
        for primitive in mesh['primitives']:
            joints=tree['accessors'][primitive['attributes']['JOINTS_0']];weights=tree['accessors'][primitive['attributes']['WEIGHTS_0']]
            joint_view=tree['bufferViews'][joints['bufferView']];weight_view=tree['bufferViews'][weights['bufferView']]
            joint_size={5121:1,5123:2}[joints['componentType']]
            if weights['componentType']!=5126:raise ValueError('Unexpected skin weight type')
            for i in range(joints['count']):
                jo=8+joint_view.get('byteOffset',0)+joints.get('byteOffset',0)+i*joint_view.get('byteStride',joint_size*4)
                wo=8+weight_view.get('byteOffset',0)+weights.get('byteOffset',0)+i*weight_view.get('byteStride',16)
                for k in range(4):
                    if struct.unpack_from('<f',binary,wo+k*4)[0]==0 and any(binary[jo+k*joint_size:jo+(k+1)*joint_size]):
                        binary[jo+k*joint_size:jo+(k+1)*joint_size]=b'\0'*joint_size;cleared+=1
    # Sketchfab writes a redundant tightly-packed byteStride on animation data;
    # glTF forbids that property there. Remove it only after verifying packing
    # and that no vertex attribute references those buffer views. Bytes stay exact.
    vertex_views={tree['accessors'][a]['bufferView'] for m in tree['meshes'] for p in m['primitives'] for a in p['attributes'].values()}
    animation_accessors={s[key] for a in tree['animations'] for s in a['samplers'] for key in ['input','output']}
    sizes={'SCALAR':4,'VEC3':12,'VEC4':16}
    for index in animation_accessors:
        a=tree['accessors'][index];view=tree['bufferViews'][a['bufferView']]
        if 'byteStride' in view:
            if a['componentType']!=5126 or view['byteStride']!=sizes[a['type']] or a['bufferView'] in vertex_views:raise ValueError('Animation data is not tightly packed')
            del view['byteStride']
    for mesh in tree['meshes']:
        for primitive in mesh['primitives']:
            primitive['attributes'].pop('TEXCOORD_1',None);primitive['attributes'].pop('TEXCOORD_2',None)
    tree['asset']['extras']['modifications']='Metric 0.62m standing height, ground origin, nonmetallic feather material and 0.55 normal-map intensity. Removed redundant tightly-packed animation byteStride and unused duplicate UV references; cleared zero-weight joint indices; skinned nodes moved to scene root per glTF. Shape, active skin weights, keyframes and PNG bytes preserved.'
    for material in tree['materials']:
        material['pbrMetallicRoughness']['metallicFactor']=0
        material['normalTexture']['scale']=.55
    encoded=json.dumps(tree,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
    output=struct.pack('<4sII',b'glTF',2,20+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+binary
    (HERE/'african-penguin.glb').write_bytes(output)
    pool_inputs=ROOT/'bolgeler/15-penguen/model/model-inputs.json';surface_file=ROOT/'surface-layers.json'
    inputs=json.loads(pool_inputs.read_text());surface=json.loads(surface_file.read_text());pool=Polygon(inputs['waterOutline']['outer'])
    land=unary_union([Polygon(p['outer'],p['holes']) for p in surface['layers']['terrain']]).intersection(Polygon(inputs['gravelContextMask']['outer']))
    arc=[]
    for i in range(121):
        p=pool.exterior.interpolate(pool.exterior.length*i/120)
        if p.y>136.5:arc.append((p.x,p.y+2))
    cliff=LineString(arc).buffer(.72,join_style=2).intersection(land)
    dry=land.buffer(-.34).difference(pool.buffer(2.05)).difference(cliff.buffer(.52)).difference(box(-6.95,132.55,-1.05,139.45))
    # Keep this small first colony on the southern beach, away from bank stones.
    beach=unary_union([p for p in polygons(dry) if p.contains(Point(-7,123))])
    water=pool.buffer(-.8)
    for x,y,sx,sy in [(-18.2,136.5,2.2,1.1),(-21.8,132.7,1.7,.9)]:
        from shapely.affinity import scale as stretch
        water=water.difference(stretch(Point(x,y).buffer(1),sx+.6,sy+.6,origin=(x,y)))
    water=water.difference(box(-7,132.4,-.9,139.6))
    starts=[[-8.4,123.0],[-6.7,123.0],[-4.9,123.0]]
    swimmers=[[-13.0,133.2],[-17.3,134.1]]
    for point in starts:
        if not beach.contains(Point(point)):raise ValueError('Beach start outside safe land: '+str(point))
    for point in swimmers:
        if not water.contains(Point(point)):raise ValueError('Swimmer start outside safe pool: '+str(point))
    clips={c['name']:{'duration':c['duration'],'groundOffsetMetres':[(body_low-s['bodyGround'])*scale for s in c['samples']]} for c in rig['clips']}
    meta={'schema':'bursa-zoo-penguin-colony/v1','sourceUrl':tree['asset']['extras']['source'],'author':'Major','license':'CC BY 4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/',
        'asset':'models/african-penguin.glb','assetSha256':sha(HERE/'african-penguin.glb'),'sourceSha256':sha(original),'unit':'metre','standingHeightMetres':height,'heightIsSurveyed':False,
        'forwardAxis':'glTF +Z; atlas wrapper maps to -Y before heading','trianglesPerBird':sum(m['triangles'] for m in rig['meshes']),'jointsPerBird':64,'meshDrawsPerBird':2,
        'groundZ':surface['renderLevels']['terrainZ'],'waterZ':surface['renderLevels']['waterZ'],'groundingReference':'Body mesh lowest point; transparent feather fringe is excluded so it cannot leave feet hovering.','groundDomain':rings(beach),'waterDomain':rings(water),'landStarts':starts,'waterStarts':swimmers,
        'clips':clips,'walkSpeedMetresPerSecond':.21,'swimSpeedMetresPerSecond':.50,'swimAnchorOffsetMetres':-.29,
        'interpretation':'Five illustrative adults, not the zoo census. Dry and swimming individuals remain separate; no invented crossing of the vertical coping. Safe domains exclude rocks, cliff, deck and shoreline. Heights/speeds/positions are editable illustrative settings.',
        'inputs':{'poolInputsSha256':sha(pool_inputs),'surfaceSha256':sha(surface_file)}}
    (HERE/'colony-layout.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    source_dir=HERE/'source'
    with zipfile.ZipFile(source_dir/'major-african-penguin-original.zip') as archive:
        for item in archive.infolist():
            target=(source_dir/item.filename).resolve()
            if not target.is_relative_to(source_dir.resolve()):raise ValueError('Unsafe archive path')
            if not item.is_dir():target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(item))
    manifest={'author':'Major','sourceUrl':meta['sourceUrl'],'license':'CC BY 4.0','licenseUrl':meta['licenseUrl'],'retrievedAt':'2026-10-15','downloadMethod':'Sketchfab logged-in official Download buttons; original FBX ZIP and converted GLB',
        'originals':[{'file':str(p.relative_to(HERE)).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size} for p in source_dir.rglob('*') if p.is_file()],
        'delivery':{'file':'african-penguin.glb','sha256':meta['assetSha256'],'bytes':len(output),'modifications':tree['asset']['extras']['modifications']}}
    (HERE/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (HERE/'ATTRIBUTION.txt').write_text('African penguin (Spheniscus demersus) Low poly by Major\n'+meta['sourceUrl']+'\nLicensed under Creative Commons Attribution 4.0: '+meta['licenseUrl']+'\n'+tree['asset']['extras']['modifications']+'\n',encoding='utf-8')
    print(json.dumps({'bytes':len(output),'heightMetres':height,'scale':scale,'groundAreaM2':beach.area,'swimAreaM2':water.area,'birds':5}))

if __name__=='__main__':main()
