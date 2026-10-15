"""Fetch reviewed Three.js r186 addons for the local-only scene."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin

import requests

ROOT=Path(__file__).resolve().parent
VENDOR=ROOT/'vendor'
BASE='https://cdn.jsdelivr.net/npm/three@0.186.0/examples/jsm/'
START=['postprocessing/GTAOPass.js','postprocessing/OutputPass.js','objects/Water.js','utils/BufferGeometryUtils.js']


def main():
    todo=list(START);seen=set();records=[]
    while todo:
        name=todo.pop(0)
        if name in seen:continue
        seen.add(name)
        url=BASE+name
        response=requests.get(url,timeout=25);response.raise_for_status()
        path=VENDOR/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(response.content)
        records.append({'file':name,'url':url,'sha256':hashlib.sha256(response.content).hexdigest()})
        for relative in re.findall(r"(?m)^import[\s\S]*?from\s+['\"]([^'\"]+)['\"]\s*;",response.text):
            if relative.startswith('.'):
                child=urljoin(url,relative)
                if not child.startswith(BASE):raise ValueError('Unexpected addon dependency '+child)
                todo.append(child[len(BASE):])
            elif relative!='three':raise ValueError('Unexpected addon import '+relative)
    normal_url='https://raw.githubusercontent.com/mrdoob/three.js/r186/examples/textures/waternormals.jpg'
    response=requests.get(normal_url,timeout=25);response.raise_for_status()
    path=ROOT/'viewer/assets/three-water-normals-r186.jpg';path.write_bytes(response.content)
    records.append({'file':'../viewer/assets/'+path.name,'url':normal_url,
        'sha256':hashlib.sha256(response.content).hexdigest(),'purpose':'Technical normal map from the official example; local use only, not a site photograph'})
    (VENDOR/'scene-effects-sources.json').write_text(json.dumps({'version':'three0.186.0',
        'license':'Three.js MIT, see vendor/LICENSE; example texture retained only for local review',
        'files':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Fetched reviewed addons:',len(seen),'normal map:',len(response.content),'bytes')


if __name__=='__main__':main()
