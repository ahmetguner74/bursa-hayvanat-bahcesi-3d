# Boz Ayı havuzu ve kaya kıyısı — ilk bileşen

[Yerel modeli incele](http://127.0.0.1:8768/model-review/?model=bear-pool) · [Atlasta aç](http://127.0.0.1:8768/?focus=region-29&perspective=65) · [Aynı Wi-Fi üzerinden aç](http://192.168.0.192:8768/?focus=region-29&perspective=65)

## Kaynak ve yorum ayrımı

- M5 `H22D01C2B:278` kapalı gölet çizgisi, özgün XY noktalarıyla korunur: **488,3991195 m²**. Yerel metre orijini `[-125,75360413783568; -71,13040925566855]`. Kaynak H metadata olarak saklanır; sunum kotu değildir.
- Resmî Eylül krokisindeki 29 etiketi ve havuz yaklaşık eşleşir. Göletin 28/29 bölgeleriyle kesin ilişkisi, barınak sınırı ve mevcut durum **teyitsizdir**. Bu varlık bütün Boz Ayı barınağı sayılmaz.
- [2018 resmî haber fotoğrafı](https://www.bursahayvanatbahcesi.com/karin-gec-gelmesi-ayilari-uykusuz-birakti/) gri kaya kümeleri, beton havuz kenarı ve yeşil zemin geçişini gösterir. Fotoğraf tek kıyıyı kapsar; ölçü veya güncel saha kaydı değildir. Kış fotoğrafı kaya karakteri için ikinci eski referanstır. Özgün dosyalar, URL/tarih/SHA ve açıklamalar `../kaynaklar/` altında.
- 40 cm kıyı genişliği, kotlar, derinlik, 17 kayanın üç kümeye yerleşimi ve 9 bitki kümesi görsel yorumdur. Zeytin yeşili su rengi sunum kararıdır; mevcut su rengi ölçülmedi. Kapalı barınak, hayvan, servis yapısı veya görünmeyen çevre çiti üretilmedi.

## Düzenlenebilir dosyalar

- `model-inputs.json`: native gölet, değişmemiş kaynak özetleri, yorum ölçüleri ve M5 XY konumlu varlıklar.
- `capture_inputs.py`: ilk kaynak ve kuru zemin maskesi yakalaması; mevcut girdiyi ezmeyi reddeder. Kıyı maskesi kaynak yol/su/bina yüzeylerinden ayrılmış eski kuru zeminden dondurulmuştur; çıktıdan tekrar yakalanmaz.
- `compose_rock_clusters.py`: yerleşimi üç düzensiz kümeye dönüştüren sabit tohumlu yorum aracı. Kaynak gölet/maskelerini değiştirmez. Düzenlenmiş girdiyi tekrar yazdığı için yalnız bu yorumu yeniden üretmek istendiğinde çalıştırılır.
- `build_bear_pool.py`: girdiden metre ölçeğinde, glTF Y yukarı eksenli GLB üretir. Ana atlasta X/Z dönüşümü ve kayıtlı M5 orijini uygulanır.
- `boz-ayi-havuz-kiyisi.glb`: **10.278 üçgen, 1.513.188 bayt**. Altı kapalı hacim parçası; bir açık su düzlemi ve standart alfa kesimli bitki kartları.
- `boz-ayi-havuz-kiyisi.blend`: aynı gerçek GLB'den içe alınmış, metre birimli düzenlenebilir Blender dosyası. Model nesneleri ayrı koleksiyonda; önizleme kamerası/ışıkları/arka zemin başka koleksiyondadır. Dokular paketlenmiştir; M5 orijini ve kaynak SHA sahne özelliklerinde kayıtlıdır.
- `preview.png`, `preview-source.json`, `render_preview.py`: gerçek GLB'nin Blender 5.2.1 LTS / Cycles 32 örnek / 1200×800 önizlemesi ve dosya SHA kayıtları. Tarayıcı ekran görüntüsü veya yeni konsept görseli değildir.
- `textures/manifest.json`: mevcut üretilmiş üç kaynağın 512 piksel teknik JPEG/PNG türevleri, gerçek boyut/renk modu ve dosya SHA'ları. Saha fotoğrafı doku olarak kullanılmaz.
- `gltf-validation.json`, `asset-verification.json`: gerçek dışa aktarılan dosyanın biçim, kapalı hacim ve kaynak izdüşümü denetimleri.

## Yüzey sahipliği

41,897033 m² yorum kıyısı ortak bina dışlama maskesine eklenir; çim, yol ve suyla pozitif alan örtüşmesi yoktur. Önizleme zemin/yatak/su düğümleri ana atlasta gizlenir. Bütün göletler tek ortak su geometrisinde, tek yansıma geçişiyle çizilir; ayı göleti rengi köşe özniteliğidir, ikinci su düzlemi değildir. Ek orman ağaçlarının gövdeleri kaya hacimlerinden uzak tutulur; özgün M5 ağaç kayıtları değişmez.

Yalnız türetilmiş önizleme zemini 0,000001 m hassasiyetle normalize edilir. Mikroskobik şeridin çökmesi yaklaşık 0,40 m uzunluğa ulaşır, toplam alan farkı **0,0000574641 m²**'dir; bu native gölet veya QGIS yolu üzerinde bir değişiklik değildir. Gerçek Float32 dışa aktarım farkları su/yatak 0,0000197198 m², kıyı 0,0000337439 m² ve önizleme zemini 0,0000707906 m².

## Yeniden üretim ve denetim

Proje kökünde `python publish_local.py --local-only`, ardından `node bolgeler/validate_models.cjs` ve `python bolgeler/verify_inventory.py`. Yalnız bu varlık için üretici ve `verify_bear_pool.py` çalıştırılabilir; doğrulama güncel ortak yüzey/katalog ve Khronos raporunu bekler.

Khronos raporunda hata/uyarı/bilgi/ipucu **0**. Kapalı hacimler sonlu, doğru yönlü ve pozitif hacimli; sıfır alanlı veya yinelenen üçgen yok. Bu denetim saha doğruluğunu veya bütün atlasın görsel kabulünü kanıtlamaz. Yerel çalışma; `docs/` ve canlı yayın değiştirilmez.
