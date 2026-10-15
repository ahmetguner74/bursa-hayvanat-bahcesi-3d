"""Apply pixel-reviewed corrections without changing downloaded originals.

The WordPress title search is a candidate finder: several animal photos have
unrelated reused news titles. Corrections below came from the local contact
sheet, not from those titles. Running this script again is safe.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from build_inventory import link_local

ROOT = Path(__file__).resolve().parent
REASSIGN = [
    (7, 15, 3538, "Fotoğrafta penguenler ve havuz kıyısı görülüyor; haber başlığı aslan/kaplan olarak hatalı eşleşmiş."),
    (7, 15, 3537, "Fotoğrafta penguenler görülüyor; aslan alanına mimari kanıt değildir."),
    (7, 35, 3536, "Fotoğrafta kaplan görülüyor; aslan başlığına rağmen Amur Kaplanı için hayvan/çevre adayı."),
    (18, 29, 1671, "Fotoğrafta su içindeki ayı görülüyor; deve barınağı referansı değildir."),
    (18, 12, 1620, "Fotoğrafta devekuşu görülüyor. Savana için tür/çevre adayı; tam çekim konumu teyitsiz."),
    (20, 26, 1678, "Fotoğrafta lama ve yavrusu görülüyor; alageyik barınağı kanıtı değildir."),
    (20, 26, 1677, "Fotoğrafta lama ve yavrusu görülüyor; Güney Amerika tür/çevre adayı."),
]


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def review():
    index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    folders = {area["number"]: ROOT / area["folder"] for area in index["areas"]}
    manifests = {number: json.loads((folder / "kaynaklar/kaynakca.json").read_text(encoding="utf-8"))
                 for number, folder in folders.items()}
    for old, new, media_id, reason in REASSIGN:
        origin, target = manifests[old], manifests[new]
        photo = next((item for item in origin["photos"] if item.get("mediaId") == media_id), None)
        if photo is None:
            photo = next((item for item in origin.get("rejectedPhotos", []) if item.get("mediaId") == media_id), None)
        if photo is None:
            raise ValueError(f"Missing reviewed original {old}/{media_id}")
        origin["photos"] = [item for item in origin["photos"] if item.get("mediaId") != media_id]
        rejected = copy.deepcopy(photo)
        rejected.update({"reason": reason, "reassignedArea": new})
        origin.setdefault("rejectedPhotos", [])
        origin["rejectedPhotos"] = [item for item in origin["rejectedPhotos"] if item.get("mediaId") != media_id] + [rejected]
        path = folders[old] / photo["file"]
        destination = folders[new] / "kaynaklar/fotograflar" / path.name
        link_local(path, destination)
        corrected = copy.deepcopy(photo)
        corrected.pop("reason", None)
        corrected.pop("reassignedArea", None)
        corrected.update({"file": destination.relative_to(folders[new]).as_posix(),
            "role": "İçerik gözlemiyle ayrılmış hayvan/çevre referansı; ölçekli yapı fotoğrafı değildir",
            "contentReview": {"date": "2026-10-15", "observation": reason,
                              "originalSearchArea": old, "exactCameraPosition": "teyitsiz"}})
        target["photos"] = [item for item in target["photos"] if item.get("mediaId") != media_id] + [corrected]

    for photo in manifests[30]["photos"]:
        if photo.get("mediaId") == 1561:
            photo["role"] = "Tavus kuşu yakın planı; Türk Köyü cephe veya çatı referansı değildir"
            photo["contentReview"] = {"date": "2026-10-15", "observation": "230 × 153 piksel tavus kuşu; dosya adındaki Türk Köyü etiketi mimari içerik anlamına gelmiyor."}
        if photo.get("mediaId") in (3508, 3507, 2850, 2849):
            photo["role"] = "Türk Köyü koyun/keçi yakın planı; cephe veya çatı ölçüsü doğrulanamaz"
        if photo.get("mediaId") in (2850, 2849):
            photo["sameViewAsMediaId"] = {2850: 3508, 2849: 3507}[photo["mediaId"]]

    for number, data in manifests.items():
        data["contentReview"] = {"date": "2026-10-15", "status": "kısmi",
            "method": "Yerel fotoğraf temas sayfası; yanlış tür eşleşmeleri ayrı kaydedildi",
            "limitation": "İçerik gözlemi çekim yerini, tarihini veya mevcut yapı ölçülerini doğrulamaz. Belge bağlantıları hâlâ arama adayıdır."}
        save(folders[number] / "kaynaklar/kaynakca.json", data)
    for area in index["areas"]:
        data = manifests[area["number"]]
        area["officialPhotos"] = len(data["photos"])
        area["architecturalReferences"] = len(data.get("architecturalReferences", []))
        if area["number"] == 29 and (folders[29] / "model/boz-ayi-havuz-kiyisi.glb").exists():
            area["modelStatus"] = "Boz Ayı havuz bileşeni v1 · M5 izi; kaya kıyısı fotoğraf yorumu, 28/29 kapsamı teyitsiz"
        if area["number"] == 30 and (folders[30] / "model/turk-koyu.glb").exists():
            area["modelStatus"] = "Türk Köyü v1 · 9 M5 çatı bölgesi · glTF"
        if area["number"] == 15 and (folders[15] / "model/penguen-havuzu.glb").exists():
            area["modelStatus"] = "Penguen havuzu v1 · M5 izi ve tarihî fotoğraf yorumu · glTF"
        if area["number"] == 13 and (folders[13] / "model/afrika-kafe.glb").exists():
            area["modelStatus"] = "Afrika Kafe v1 · 6 aday M5 izi; tarihî fotoğraf yorumu"
        if area["number"] == 9 and (folders[9] / "model/habes-maymunu-adasi.glb").exists():
            area["modelStatus"] = "Habeş Maymunu Adası v1 · M5 izi; 2021 fotoğrafından yaklaşık tırmanma elemanları"
    save(ROOT / "index.json", index)
    rows = ["# Bursa Zoo 1–43 alan envanteri", "",
        "Resmî Eylül 2026 krokisinin bütün lejant maddeleri. Fotoğraf sayısı yerel dosya kaydıdır; bazıları aynı görünümün farklı çözünürlükleri veya hayvan yakın planlarıdır. Belge sayısı henüz incelenmemiş resmî arama bağlantısıdır. Mimari referanslar ayrıca kaydedilir.", "",
        "| No | Alan | Fotoğraf kaydı | Belge adayı | Mimari referans | Model |",
        "|---:|---|---:|---:|---:|---|"]
    rows.extend(f"| {a['number']} | [{a['name']}]({a['folder']}/README.md) | {a['officialPhotos']} | {a['officialDocuments']} | {a['architecturalReferences']} | {a['modelStatus']} |" for a in index["areas"])
    (ROOT / "README.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(json.dumps({"reviewedReassignments": len(REASSIGN),
                      "officialPhotoEntries": sum(a["officialPhotos"] for a in index["areas"])}))


if __name__ == "__main__":
    review()
