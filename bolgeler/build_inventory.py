"""Build the local, source-attributed research folders for all 43 map entries.

The downloaded reference pixels stay local. The generated index and source
manifests are editable text, while the public ``docs/`` tree is never touched.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
API = "https://www.bursahayvanatbahcesi.com/wp-json/wp/v2"
AREAS = [
    (1, "İdari Bina ve Gösteri Merkezi", "tesis", "gösteri merkezi"),
    (2, "Hediyelik Eşya Marketi", "tesis", "hediyelik eşya"),
    (3, "Safari Kafe", "tesis", "safari kafe"),
    (4, "Mescid", "tesis", "mescid"),
    (5, "Giriş Göleti", "su", "giriş göleti"),
    (6, "Pers Leoparı", "yaşam alanı", "pers leoparı"),
    (7, "Afrika Aslanı", "yaşam alanı", "aslan"),
    (8, "Benekli Sırtlan", "yaşam alanı", "sırtlan"),
    (9, "Habeş Maymunu", "yaşam alanı", "habeş maymunu"),
    (10, "Boa Yılanı", "yaşam alanı", "boa"),
    (11, "Lemur", "yaşam alanı", "lemur"),
    (12, "Afrika Savana", "yaşam alanı", "afrika savana"),
    (13, "Afrika Kafe", "tesis", "afrika kafe"),
    (14, "Afrika Köyü", "tesis", "afrika köyü"),
    (15, "Penguen", "yaşam alanı", "penguen"),
    (16, "Gergedan", "yaşam alanı", "gergedan"),
    (17, "Yaban Eşeği", "yaşam alanı", "yaban eşeği"),
    (18, "Deve", "yaşam alanı", "deve"),
    (19, "Yaban Domuzu", "yaşam alanı", "yaban domuzu"),
    (20, "Ala Geyik", "yaşam alanı", "alageyik"),
    (21, "Kızıl Geyik", "yaşam alanı", "kızıl geyik"),
    (22, "Avustralya Hayvanları", "yaşam alanı", "avustralya hayvanları"),
    (23, "Gülen Kuş", "yaşam alanı", "gülen kuş"),
    (24, "Saman Boyunlu İbis", "yaşam alanı", "saman boyunlu ibis"),
    (25, "Yırtıcı Kuşlar", "yaşam alanı", "yırtıcı kuşlar"),
    (26, "Güney Amerika Hayvanları", "yaşam alanı", "güney amerika"),
    (27, "Alligatör", "yaşam alanı", "alligatör"),
    (28, "Boz Kurt", "yaşam alanı", "boz kurt"),
    (29, "Boz Ayı", "yaşam alanı", "boz ayı"),
    (30, "Türk Köyü", "tesis", "türk köyü"),
    (31, "Pelikan Göleti", "su ve kafes", "pelikan göleti"),
    (32, "Su Kuşları", "yaşam alanı", "su kuşları"),
    (33, "Kırmızı Panda", "yaşam alanı", "kırmızı panda"),
    (34, "Vaşak", "yaşam alanı", "vaşak"),
    (35, "Amur Kaplanı", "yaşam alanı", "amur kaplanı"),
    (36, "Sülün Kuşları", "yaşam alanı", "sülün"),
    (37, "Servis Binaları", "tesis", "servis binaları"),
    (38, "Karantina ve Kurtarma Merkezi", "tesis", "karantina"),
    (39, "Isı Merkezi", "tesis", "ısı merkezi"),
    (40, "Çocuk Oyun Alanı", "tesis", "çocuk oyun alanı"),
    (41, "Otopark", "ulaşım", "otopark"),
    (42, "Acil Toplanma Merkezleri", "güvenlik", "acil toplanma"),
    (43, "Acil Çıkış Noktaları", "güvenlik", "acil çıkış"),
]

MAPS = [
    ("2026-09-resmi-kroki.jpg", PROJECT / "reference-maps-private/2026-09-kroki.jpg",
     "https://www.bursahayvanatbahcesi.com/wp-content/uploads/2026/09/kroki.jpg", "2026-09-15"),
    ("2026-03-yuksek-cozunurluk-kroki.jpg", PROJECT / "reference-maps-private/2026-03-kroki.jpg",
     "https://www.bursahayvanatbahcesi.com/wp-content/uploads/2026/03/kroki-1920x1080-1.jpg", "2026-03-31"),
]


def slug(value: str) -> str:
    value = value.replace("ı", "i").replace("İ", "i")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def link_local(source: Path, target: Path) -> None:
    if target.exists():
        if digest(source) != digest(target):
            raise RuntimeError(f"Existing reference differs: {target}")
        return
    try:
        os.link(source, target)
    except OSError:
        shutil.copy2(source, target)


def api_search(area: tuple) -> tuple[int, list, list]:
    number, _, _, term = area
    try:
        media_response = requests.get(f"{API}/media", params={"search": term, "per_page": 12,
            "orderby": "date", "order": "desc"}, timeout=20)
        media_response.raise_for_status()
        media = media_response.json()
        post_response = requests.get(f"{API}/search", params={"search": term, "per_page": 8,
            "type": "post"}, timeout=20)
        post_response.raise_for_status()
        posts = post_response.json()
        return number, media, posts
    except requests.RequestException as exc:
        return number, [], [{"error": str(exc)}]


def download_photo(item: dict, destination: Path) -> dict | None:
    url = item.get("source_url", "")
    extension = Path(urlparse(url).path).suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        return None
    filename = f"resmi-site-{item['id']}{extension}"
    path = destination / filename
    if not path.exists():
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            if len(response.content) > 12_000_000:
                return None
            path.write_bytes(response.content)
        except requests.RequestException:
            return None
    return {"file": str(path.relative_to(destination.parent.parent)), "url": url,
        "mediaId": item["id"], "uploaded": item.get("date"),
        "title": re.sub(r"<[^>]+>", "", item.get("title", {}).get("rendered", "")),
        "sha256": digest(path), "role": "Görsel araştırma; yapının güncel ölçüsünü tek başına doğrulamaz",
        "publication": "yerel kaynak; model dokusu veya canlı yayın için izin teyidi gerekir"}


def build() -> None:
    if len(AREAS) != 43 or [item[0] for item in AREAS] != list(range(1, 44)):
        raise RuntimeError("Official legend must have exactly the numbers 1–43")
    for _, original, _, _ in MAPS:
        if not original.is_file():
            raise FileNotFoundError(original)
    results = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for number, media, posts in as_completed_map(pool):
            results[number] = (media, posts)
            print(f"Kaynak taraması: {number:02d} — {len(media)} görsel, {len(posts)} kayıt", flush=True)

    index = []
    for area in AREAS:
        number, title, kind, term = area
        folder = ROOT / f"{number:02d}-{slug(title)}"
        maps_folder = folder / "kaynaklar/krokiler"
        photo_folder = folder / "kaynaklar/fotograflar"
        documents_folder = folder / "kaynaklar/belgeler"
        model_folder = folder / "model"
        for path in (maps_folder, photo_folder, documents_folder, model_folder):
            path.mkdir(parents=True, exist_ok=True)
        sources = []
        for filename, original, url, date in MAPS:
            target = maps_folder / filename
            link_local(original, target)
            sources.append({"file": str(target.relative_to(folder)), "url": url,
                "date": date, "sha256": digest(target), "role": "Resmî ziyaretçi krokisi; ölçekli aplikasyon değil"})
        media, posts = results.get(number, ([], []))
        photos = []
        for item in media:
            if len(photos) >= 4:
                break
            photo = download_photo(item, photo_folder)
            if photo:
                photos.append(photo)
        # The shared M5/QGIS files retain their native coordinate systems and
        # are linked rather than copied or cut into unverified exhibit shapes.
        document = {
            "schema": "bursa-zoo-area-sources/v1", "number": number, "name": title,
            "type": kind, "searched": term, "mapSources": sources,
            "photos": photos,
            "documents": [{"title": x.get("title"), "url": x.get("url"),
                "type": x.get("subtype", "post")} for x in posts if x.get("url")],
            "sharedMetricSources": [
                "../../source-dgn/ — 2016/2018 M5 paftaları, geçmiş durum",
                "../../current-plan-registration.json — kroki→M5 yaklaşık eşleme, 10,7 m RMS",
                "../../v2/manual-roads-metric.json — geçici manuel QGIS yolları",
                "../../../Bursa-Hayvanat-Bahcesi-QGIS-Delivery-2026-10-14/Bursa-Zoo-V2-Manual-QGIS/v2/qgis/Bursa-Zoo-V2.qgz — özgün manuel QGIS projesi"
            ],
            "geometryStatus": "Alan sınırı ve yapı izi henüz tek tek doğrulanmadı",
            "licensing": "Fotoğraf ve kroki dosyaları sadece yerel araştırma; yayıma veya dokuya izin varsayılmadı",
        }
        prior_source = folder / "kaynaklar/kaynakca.json"
        if prior_source.exists():
            previous = json.loads(prior_source.read_text(encoding="utf-8"))
            for key in ("architecturalReferences", "architecturalDocument", "architecturalDocuments", "rejectedPhotos", "contentReview", "areaContext", "unavailableReferences"):
                if key in previous:
                    document[key] = previous[key]
            # Keep downloaded and manually reviewed references across new API
            # searches; a changing search ranking must not erase local work.
            merged = {item.get("url", item["file"]): item for item in document["photos"]}
            merged.update({item.get("url", item["file"]): item for item in previous.get("photos", [])})
            document["photos"] = list(merged.values())
        (folder / "kaynaklar/kaynakca.json").write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
        (documents_folder / "kaynak-baglantilari.md").write_text(
            f"# {number:02d} {title} — belge bağlantıları\n\n" +
            ("\n".join(f"- [{x.get('title', 'Resmî site kaydı')}]({x['url']})" for x in document["documents"])
             or "Bu adla resmî sitede ayrı yazılı belge bulunamadı.\n"), encoding="utf-8")
        dome_note = ("\nKubbenin ilk parametreli glTF kabuğu [#31 model klasöründe](../31-pelikan-goleti/model/README.md). "
                     "#31/#32 etiketlerinin fiziksel kapsamı henüz doğrulanmadı.\n") if number in (31, 32) else ""
        if not (folder / "README.md").exists():
            (folder / "README.md").write_text(
                f"# {number:02d} {title}\n\nResmî 2026 krokisindeki `{number}` numaralı {kind}. "
                "Krokiler ve araştırma fotoğrafları `kaynaklar/` altında; URL, yükleme tarihi ve dosya özeti "
                "`kaynaklar/kaynakca.json` içinde. Fotoğrafın yükleme tarihi çekim tarihi olmayabilir. "
                "M5/DGN eski durumdur; mevcut geometri için doğrudan kabul edilmez. "
                "`model/` alanı düzenlenebilir 3B varlıklar içindir.\n" + dome_note, encoding="utf-8")
        model_status = "kubbe kabuğu v1 · kaynak kodu ve iki glTF LOD" if number == 31 and (
            model_folder / "su-kuslari-kubbesi-yakin.glb").exists() else "bekliyor"
        model_files={9:('habes-maymunu-adasi.glb','Habeş Maymunu Adası v1 · M5 izi; 2021 fotoğrafından yaklaşık tırmanma elemanları'),
                     11:('lemur-adasi.glb','Lemur Adası v1 · M5 izi; kaya/dal yerleşimi kamera yorumu'),
                     13:('afrika-kafe.glb','Afrika Kafe v1 · 6 aday M5 izi; tarihî fotoğraf yorumu'),
                     12:('savanna-ahsap-platform.glb','ahşap yapı bileşeni v1; aday konum teyitsiz'),
                     14:('afrika-koyu.glb','Afrika Köyü v1 ·7 M5 çatı izi; tarihî fotoğraf yorumu'),
                     15:('penguen-havuzu.glb','Penguen havuzu v1 · M5 izi ve tarihî fotoğraf yorumu · glTF'),
                     29:('boz-ayi-havuz-kiyisi.glb','Boz Ayı havuz bileşeni v1 · M5 izi; kaya kıyısı fotoğraf yorumu, 28/29 kapsamı teyitsiz'),
                     30:('turk-koyu.glb','Türk Köyü v1 · 9 M5 çatı bölgesi · glTF')}
        if number in model_files:
            file,status=model_files[number]
            if (model_folder/file).is_file():model_status=status
        index.append({"number": number, "name": title, "type": kind,
            "folder": folder.name, "officialPhotos": len(photos),
            "officialDocuments": len(document["documents"]), "modelStatus": model_status,
            "architecturalReferences":len(document.get('architecturalReferences',[]))})
        print(f"Klasör: {folder.name} — {len(photos)} fotoğraf", flush=True)
    (ROOT / "index.json").write_text(json.dumps({"schema": "bursa-zoo-area-index/v1",
        "officialLegend": MAPS[0][2], "areas": index}, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Bursa Zoo 1–43 alan envanteri", "", "Resmî Eylül 2026 krokisinin bütün lejant maddeleri. "
        "Fotoğraf ve kroki kopyaları yerel araştırma içindir; `docs/` klasörüne kopyalanmaz.", "",
        "| No | Alan | Tür | Fotoğraf | Belge | Model |", "|---:|---|---|---:|---:|---|"]
    lines += [f"| {x['number']} | [{x['name']}]({x['folder']}/README.md) | {x['type']} | "
              f"{x['officialPhotos']} | {x['officialDocuments']} | {x['modelStatus']} |" for x in index]
    (ROOT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    from review_sources import review
    review()


def as_completed_map(pool):
    futures = [pool.submit(api_search, area) for area in AREAS]
    for future in as_completed(futures):
        yield future.result()


if __name__ == "__main__":
    build()
