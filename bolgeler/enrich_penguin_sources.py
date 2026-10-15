"""Archive inspected municipal architectural references, locally only."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import requests

ROOT=Path(__file__).resolve().parent
PAGES={
    24148:('https://www.bursa.bel.tr/haber/bursa-zoo-nun-yeni-misafirleri-fok-ve-penguen-24148','2017-06-24'),
    23247:('https://www.bursa.bel.tr/haber/fok-baligi-ve-penguenler-icin-geri-sayim-23247','2017-02-02'),
}
SELECTION={15:[
    ('24148_MST_8045_201706220833.jpg','Penguen havuzunun genel görünümü; koyu mavi bordür, açık çakıl, gri yapay kaya, su içi alçak taş ve ahşap seyir platformu'),
    ('24148_MST_8002_201706220833.jpg','Penguen kıyısındaki açık çakıl, alçak kayalar ve arka yapay kaya duvarı'),
    ('24148_MST_8011_201706220833.jpg','Penguen havuzundaki taş, kıyı ve ahşap seyir platformu'),
    ('24148_MST_7985_201706220833.jpg','Penguen havuzu su ve kıyı bağlamı'),
    ('24148_MST_7927_201706220833.jpg','Komşu fok havuzunun yapay kaya duvarı; penguen havuzunun birebir planı değildir'),
    ('24148_MST_8097_201706220834.jpg','Kompleksin su altı seyir penceresi; fotoğrafta fok görülüyor, penguen penceresinin konumunu tek başına doğrulamaz'),
    ('23247_YHG_9117_201702021252.jpg','Yapım döneminde iki havuzun ve kıyıların genel geometrisi'),
    ('23247_YHG_9119_201702021252.jpg','Yapım döneminde fok/penguen kompleksi ve yapay kaya duvarları'),
    ('23247_YHG_9138_201702021252.jpg','Yapım dönemindeki küçük havuzun kıvrımlı çeperi, alçak iç kayaları ve arka duvarı'),
    ('23247_YHG_9144_201702021252.jpg','Küçük havuz yapımı, su hattı ve arka yapay kaya duvarı'),
],12:[
    ('23247_YHG_8895_201702021252.jpg','Yükseltilmiş ahşap yapı: beşik çatı, çapraz taşıyıcı, eğimli döşeme yaklaşımı ve tel sepetler. Seyir/barınak/yemleme işlevinin kesin ayrımı teyitsiz'),
    ('23247_YHG_8948_201702021252.jpg','Taş savanna sınırında ziyaretçilerin zürafa beslediği görünüm; yeşil korkuluk ve taş duvar. Ahşap yapının diğer açısı değildir'),
]}


def download(url,path):
    if not path.exists():
        r=requests.get(url,timeout=30);r.raise_for_status()
        path.write_bytes(r.content)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for number,items in SELECTION.items():
        folder=next(ROOT.glob(f'{number:02d}-*'))
        manifest_path=folder/'kaynaklar/kaynakca.json'
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        refs={item['url']:item for item in manifest.get('architecturalReferences',[])}
        for name,role in items:
            page_id=int(name.split('_')[0]);page,date=PAGES[page_id]
            url='https://www.bursa.bel.tr/dosyalar/resimler/haberler/'+name
            destination=folder/'kaynaklar/fotograflar'/name
            staged=ROOT/'_qa/penguin-construction'/name
            if staged.exists() and not destination.exists():
                shutil.copy2(staged,destination)
            sha=download(url,destination)
            refs[url]={'file':destination.relative_to(folder).as_posix(),'url':url,
                'sourcePage':page,'sourcePublished':date,'captureDate':'Yayın tarihiyle aynı olduğu teyitsiz',
                'sha256':sha,'role':role,'reviewed':'2026-10-15','publication':'yalnız yerel araştırma'}
        manifest['architecturalReferences']=list(refs.values())
        if number==15:
            documents=[]
            for page_id,(page,date) in PAGES.items():
                snapshot=folder/f'kaynaklar/belgeler/belediye-{page_id}-2017.html.txt'
                download(page,snapshot)
                documents.append({'file':snapshot.relative_to(folder).as_posix(),'url':page,
                    'sourcePublished':date,'sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                    'role':'Resmî yapım/hizmete açılma duyurusu; HTML metin arşivi, çalıştırılmaz'})
            facts={'schema':'bursa-zoo-penguin-source-facts/v1','reviewed':'2026-10-15',
                'sourcePage':PAGES[24148][0],'sourcePublished':'2017-06-24',
                'historicalDocumentAreasM2':{'penguinPool':300,'penguinLand':300,'sealPool':400,'sealLand':200},
                'constructionAreaM2':3000,'underwaterViewing':'2017 duyurusu su altı seyir bölümlerini bildiriyor',
                'photoObservations':['Küçük havuz çevresinde koyu mavi bordür ve gri drenaj bandı',
                    'Açık gri-beyaz-bej çakıl kıyı','Gri yapay kaya duvar ve alçak iç kayalar',
                    'Ahşap seyir platformu; yeşil alt paneller'],
                'limits':['2017 kaydı güncel 2026 durumunun tam doğrulaması değildir',
                    'Komşu fok havuzu ile penguen havuzu ayrımı fotoğraf rolünde korunur',
                    'M5 küçük su izi yaklaşık205m²; duyurudaki300m² farkı çözümlenmedi',
                    'Duvar yüksekliği, platform boyutu ve küçük ayrıntı konumları fotoğraftan yorumdur']}
            facts_path=folder/'kaynaklar/belgeler/yapim-kaydi-ozeti.json'
            facts_path.write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            documents.append({'file':facts_path.relative_to(folder).as_posix(),'url':PAGES[24148][0],
                'sha256':hashlib.sha256(facts_path.read_bytes()).hexdigest(),'role':'Kaynak bilgisi ve fotoğraf gözlemleri; özet, ölçülü rölöve değil'})
            manifest['architecturalDocuments']=documents
        manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Archived: 10 penguin-complex and 2 giraffe-viewing/feeding-platform references; 3 source documents')


if __name__=='__main__':
    main()
