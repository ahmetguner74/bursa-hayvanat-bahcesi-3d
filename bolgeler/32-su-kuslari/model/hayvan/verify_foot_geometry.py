"""Inspect the actual exported membranes after welding render-normal splits.

Source feather/body surfaces are recorded separately, never advertised as a
watertight fabrication model. This gate concerns the newly added foot webs.
"""
from pathlib import Path
import hashlib, json
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
path = HERE / 'greater-flamingo.glb'
scene = trimesh.load(path, force='scene', process=False)
web = next(m for name, m in scene.geometry.items() if 'feet' in name)
web.merge_vertices(merge_tex=True, merge_norm=True)
parts = []
for positive_x in (False, True):
    side = (web.vertices[:, 0] > 0) == positive_x
    faces = web.faces[np.all(side[web.faces], axis=1)]
    part = trimesh.Trimesh(web.vertices, faces, process=True)
    part.merge_vertices(merge_tex=True, merge_norm=True)
    zero_area = int((part.area_faces < 1e-14).sum())
    assert len(part.faces) == 20
    assert part.is_watertight and part.is_winding_consistent
    assert part.volume > 0 and zero_area == 0
    parts.append({'positiveX': positive_x, 'triangles': len(part.faces),
                  'closedAfterWeldingNormalSplits': bool(part.is_watertight),
                  'consistentOutwardWinding': bool(part.is_winding_consistent),
                  'volumeM3': float(part.volume), 'zeroAreaFaces': zero_area})
report = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
          'footMembranes': parts,
          'scope': 'Two locally added closed interdigital membranes only; original feather/body topology is not a watertight fabrication mesh.'}
(HERE / 'foot-geometry-verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
print(json.dumps(report))
