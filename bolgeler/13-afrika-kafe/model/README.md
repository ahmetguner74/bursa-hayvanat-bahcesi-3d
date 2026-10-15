# Afrika Kafe · ilk yerel 3B yorum

[Modeli incele](http://127.0.0.1:8768/model-review/?model=african-cafe) · [Atlas üzerinde aç](http://127.0.0.1:8768/?focus=region-13&perspective=65)

Altı aday M5 yapı/sundurma izi: `152–156,243`. Toplam özgün çatı alanı570,1022m²; yalnız türevde çıkarılan küçük152/153 çakışmasından sonra tek sahipli taban570,101484m². Bu rakamlar güncel tesis alanı ölçümü değildir. Lejant13 ile eşleşme, krokiden yaklaşık10–25m belirsizlikle yapılır.

2011 resmî açılış fotoğraflarındaki koyu ahşap cephe, açık kenarlı kameriyeler ve sıcak kahverengi kırma çatı biçimi yorumlandı. Tüm yükseklikler, sekiz birleşik çatı bölmesinin mahya yerleri,40 dikme ve kapı/pencere yerleri yaklaşık. Güncel saha durumu, iç mekân, mobilya ve işletme düzeni doğrulanmadı.

## Dosyalar ve düzenleme

- `model-inputs.json`: özgün M5 koordinatları, yerel orijin, yorumlanan ölçüler ve kaynak SHA'ları. Değişikliklerin ana girdisi.
- `build_cafe.py`: altı kapalı çatı, açık ahşap taşıyıcılar, gerçek duvar boşlukları ve tek sahipli döşeme üreticisi.
- `afrika-kafe.glb`: metre biriminde, glTF Y yukarı; sahnede+90°X dönüşü ve kayıtlı M5 yerel orijiniyle yerleşir.6.724 üçgen,899.196 bayt.
- `../kaynaklar/harita-verisi/model-kaynak-m5.json`: altı tam özgün M5 öğesi; kırpılmış veya yeniden çizilmiş kaynak değildir.
- `textures/manifest.json`: mevcut üretilmiş sunum dokularının512px JPEG teknik türevleri; özgün raster varlıklar değiştirilmedi, araştırma fotoğrafları doku yapılmadı.
- `model-report.json`, `gltf-validation.json`, `asset-verification.json`: gerçek üretilen dosya/geometri denetimleri.

Proje kökünde `python bolgeler/13-afrika-kafe/model/prepare_cafe_textures.py`, ardından `python bolgeler/13-afrika-kafe/model/build_cafe.py` çalışır. Yerel sahne için `python publish_local.py --local-only`; biçim denetimi `node bolgeler/validate_models.cjs`, yerleşim/yüzey denetimi `python bolgeler/13-afrika-kafe/model/verify_cafe.py`.

## Yüzey sahipliği

Ana243 geçici bina kutusu kaldırılır. Kafe tabanı ortak bölünmüş yüzeyde yol/çimden çıkarılır; altında ikinci yatay kapak çizilmez. Köşede değen iki yerel döşeme bileşeni ayrı kapalı katı tutulur; tek kenarda dört yüz birleşmesi oluşturulmaz. Çatı bölmeleri tek katıda birleşir, içeride yinelenen düşey çatı yüzü kalmaz. Dikme/kiriş/duvarların fiziksel temasları normal birleşim noktalarıdır.

Kaynak M5, QGIS yolları ve `docs/` değişmez; yalnız yerel çalışma. Biçim/geometri kontrolü, saha doğruluğu veya bütün atlasın görsel kabulü değildir.
