"""One-off frame collection from six publicly embedded municipal zoo feeds.

This is research collection, not monitoring. No signed stream URL is retained
in source manifests. Acquisition time is not claimed as the shooting date.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin

import cv2
import requests

ROOT=Path(__file__).resolve().parent
INDEX='https://www.bursa.bel.tr/sehir-kameralari'
CHOICES={9:'habes-maymunu-',11:'lemurlar-',12:'afrika-savana-',15:'penguenler-2-',16:'gergedanlar-',32:'su-kuslari-'}


class Tags(HTMLParser):
    def __init__(self):super().__init__();self.tags=[]
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))


def get(url):
    response=requests.get(url,timeout=25);response.raise_for_status();return response


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def collect(number,page_url):
    folder=next(ROOT.glob(f'{number:02d}-*'))
    page=get(page_url);tags=Tags();tags.feed(page.text)
    player=next(urljoin(page_url,a['src']) for t,a in tags.tags if t=='iframe' and 'player.bursa.bel.tr' in a.get('src',''))
    stamp=datetime.now(timezone.utc);filename=stamp.strftime('%Y%m%dT%H%M%SZ')
    document=folder/f'kaynaklar/belgeler/belediye-kamera-{filename}.html.txt';document.write_bytes(page.content)
    if number==9 and (ROOT/'_qa/habes-camera-frame.png').is_file():
        staged=ROOT/'_qa/habes-camera-frame.png'
        stamp=datetime.fromtimestamp(staged.stat().st_mtime,timezone.utc)
        image=cv2.imread(str(staged));method='Previously acquired municipal HLS segment, decoded first frame'
    else:
        player_html=get(player).text
        playlist=re.search(r'[\"\'](https:[^\"\']+m3u8[^\"\']*)[\"\']',player_html)[1]
        content=get(playlist).text
        media=urljoin(playlist,next(x for x in content.splitlines() if x and not x.startswith('#')))
        content=get(media).text
        segment=urljoin(media,[x for x in content.splitlines() if x and not x.startswith('#')][-1])
        data=get(segment).content
        if len(data)>8*1024*1024:raise ValueError('Unexpectedly large source fragment')
        staged=ROOT/f'_qa/camera-{number}-{filename}.ts';staged.write_bytes(data)
        video=cv2.VideoCapture(str(staged));okay,image=video.read();video.release()
        if not okay:raise ValueError('Public video fragment could not be decoded')
        method='Latest publicly listed HLS fragment, first decoded frame'
    image_path=folder/f'kaynaklar/fotograflar/belediye-kamera-{filename}.png'
    cv2.imwrite(str(image_path),image)
    manifest_path=folder/'kaynaklar/kaynakca.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    refs=[x for x in manifest.get('architecturalReferences',[]) if x.get('url')!=page_url]
    refs.append({'file':image_path.relative_to(folder).as_posix(),'url':page_url,'sourcePage':page_url,
        'sha256':sha(image_path),'fetchedAtUTC':stamp.isoformat(),'captureDate':'Çekim tarihi teyitsiz; edinim zamanı canlılık/güncel saha durumu kanıtı değildir',
        'method':method,'sizePixels':[image.shape[1],image.shape[0]],'role':'Belediye kamera akışından alan bağlamı; görsel inceleme bekliyor',
        'reviewed':False,'publication':'yalnız yerel araştırma; tekrar yayımlama izni varsayılmadı'})
    manifest['architecturalReferences']=refs
    docs=[x for x in manifest.get('architecturalDocuments',[]) if x.get('url')!=page_url]
    docs.append({'file':document.relative_to(folder).as_posix(),'url':page_url,'sha256':sha(document),
        'role':'Belediyenin herkese açık kamera sayfası arşivi; kaynak bağlantısı ve kamera adı, HTML çalıştırılmaz'})
    manifest['architecturalDocuments']=docs
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'number':number,'sourcePage':page_url,'frame':str(image_path.relative_to(ROOT)),'size':[image.shape[1],image.shape[0]]}


def main():
    index=get(INDEX);tags=Tags();tags.feed(index.text)
    links=[urljoin(INDEX,a['href']) for t,a in tags.tags if t=='a' and '/sehir-kameralari/' in a.get('href','')]
    jobs=[]
    for number,slug in CHOICES.items():
        candidates=[url for url in links if '/'+slug in url]
        if not candidates:raise ValueError('Municipal listing no longer includes '+slug)
        jobs.append((number,candidates[0]))
    results=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[(number,pool.submit(collect,number,url)) for number,url in jobs]
        for number,future in futures:
            try:result=future.result();results.append(result);print(json.dumps(result,ensure_ascii=False),flush=True)
            except Exception as error:
                # Public signed media links expire; never log their query strings.
                print(json.dumps({'number':number,'status':'not-collected','errorType':type(error).__name__}),flush=True)
    (ROOT/'_qa/camera-collection.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
