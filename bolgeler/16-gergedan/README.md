# 16 · Beyaz gergedanlar — yerel çalışma

**Güncel yerel akış ·20261015ao:** İsim/gövde seçimiyle yaklaşılır; yakında dokunmak başla bakınma, küçük kulak tepkisi veya kısa gerçek yürüyüş seçer. Rastgele yürüyüş zamanlayıcısı kaldırıldı. Dinlenmede iskelet güncellenmez. Malzemeler, yaşam alanı, rotalar ve M5 yerleşimi korundu. Ortak seçim/yükleme `viewer/tap-colony.js`, kısa davranış/rota `viewer/animal-interaction.js` içindedir. Aşağıdaki önceki sürüm kayıtları kaynak tarihçesidir.

## Güncel sürüm · 20261015al

[Atlasta yakından](http://127.0.0.1:8768/?focus=rhino-close&revision=20261015al) · [Barınak incelemesi](http://127.0.0.1:8768/model-review/rhino/?view=habitat&revision=20261015al) · [Aynı Wi-Fi](http://192.168.0.11:8768/?focus=rhino-close&revision=20261015al).

**Yalnız yerel çalışma.** Kullanıcı 15 Ekim'de yeni bir açık yayın talebine kadar canlıya almamayı istedi. `dist/` güncellendi; `docs/` ve GitHub Pages güncellenmedi.

## Hayvan ve hareket

Beyaz gergedan bir tür adıdır; doğal deri rengi açık sarımsı kahverengiden arduvaz grisine değişebilir ([SANBI](https://www.sanbi.org/animal-of-the-week/square-lipped-rhinoceros/)). Model beyaza boyanmadı. Bursa fotoğraflarına uygun açık, tozlu gri malzeme ve iki bireyde hafif ton farkı kullanıldı. Orijinal 1K doku pikselleri korunur; toz tonu çalışma anında uygulanır.

İki temsili yetişkin vardır. [22 Eylül 2026 resmî haberinde](https://www.bursahayvanatbahcesi.com/dunya-gergedan-gunu/) Amadou ve Tayo anılır; modeller bireysel portre veya güncel hayvan sayımının karşılığı değildir.

Hayvanlar yerinde adım atmak yerine avluda ilerler. Yürüyüş klibi zemin hızına bağlandı: yaklaşık 0,388 m/s; yavaş hızlanma, geniş dönüşler, farklı dinlenme süreleri ve küçük kulak/kuyruk hareketleri vardır. Gerçek kaynakta tek yürüyüş klibi bulunur. Dinlenme nötr iskeletten üretildi; otlama, yatma veya çamurda yuvarlanma animasyonu henüz yoktur. Kaynak ayakların zemindeki hareketi `stride-inspection.json` ile incelendi; bu doğal yürüyüşün veya sıfır ayak kaymasının biyomekanik onayı değildir.

Kaynak: [absol · White Rhinoceros](https://sketchfab.com/3d-models/white-rhinoceros-939baeb6d62a4824b8edb3c7f7ef54c7), **CC BY 4.0**. Türev başına 9.310 üçgen, bir skinned mesh, 46 eklem, iki 1K doku; 3,70 MB. İki hayvan aynı geometri/dokuları, ayrı iskeletleri kullanır. Atıf `model/hayvan/ATTRIBUTION.txt`, kaynak ve değişiklik özeti `source-manifest.json` içindedir.

## Barınak ve açık alan

- Resmî Eylül 2026 krokisinin 16 numaralı bölümü, mevcut yaklaşık kroki–M5 dönüşümüyle izlendi. Özgün M5 ve Dot'un QGIS yol koordinatları değiştirilmedi.
- Kavisli barınak, yeşil çatı, üç kesilmiş kapı açıklığı/çift metal kanat, iç çelik bölmeler, açık toprak avlu, beton çevre duvarı, ahşap üst korkuluk ve ayrı servis kapısı eklendi.
- Ağaç/kaya yatağı ve sığ, düzensiz çamur alanı yorumlandı. Yollar, çim ve avlu zemini aynı yüzeyi üst üste çizmez. Ağaç türü ve bu küçük öğelerin yerleri temsildir.
- [2018 belediye duyurusu](https://www.bursa.bel.tr/haber/bursa-zoonun-yeni-konuklari-gergedanlar-26077) kavisli biçimi ve yeşil çatıyı açıklar. 1.057 m² kapalı / 3.621 m² açık alan **ortak gergedan–zebra kompleksi** içindir; yalnız 16 numaralı alana zorla uygulanmadı.
- [Belediye kamerasının](https://www.bursa.bel.tr/sehir-kameralari/gergedanlar-23324) edinilen gündüz karesi toprak avlu, beton sınır, ağaç/kayalar ve metal kapılı açık renk cepheyi destekler. Akışın çekim saati bağımsız doğrulanmadı. 2018 iç mekân ve 2020/2022 resmî fotoğrafları da incelendi.

`model/gergedan-yasam-alani.glb`: 14.787 üçgen, 21 mesh, 5,11 MB. M5 yerel ankrajı `[-51.999806669, 98.853340713]`. Kroki izi yaklaşık 2.945,71 m²; bina izi 1.072,82 m². Bunlar çizim alanlarıdır; saha ölçüsü değildir. Mevcut kroki kayıt belirsizliği yaklaşık 10–25 m; kapı, çit, çamur ve kat yükseklikleri görsel yorumdur.

Zemin: Dario Barresi / Poly Haven [Gravelly Sand](https://polyhaven.com/a/gravelly_sand), CC0, 1K kaynaktan 512px teknik türev. Ağaç: Rico Cilliers / Rob Tuytel, Poly Haven [Jacaranda](https://polyhaven.com/a/jacaranda_tree), CC0, 6.942 üçgenli LOD1. Kamera yönüne dönen sprite yoktur. Tanjantı olmayan ağaç türevinde normal haritası kullanılmadı.

## Düzenlenebilir dosyalar

`model/gergedan-yasam-alani-editable.blend`: metre birimli tüm alan, iki bağımsız 46 kemikli iskelet, kaynak yürüyüş eylemleri, güzergâh kılavuzları ve 14 paketlenmiş görüntü. M5 ankrajı sahne özelliğinde tutulur; nesneler bu ankraja göre yereldir. Kamera/ışık ayrı koleksiyondadır. Çevrim içi hareket ve nötr dinlenme denetleyicisi `viewer/rhinos.js` / `viewer/rhino-motion.js` içinde düzenlenir; Blender dosyasına tüm tarayıcı davranışı bake edilmedi.

`habitat-inputs.json` kaynak/iz/ölçü yorumları; `build_habitat.py` geometri üretimi; `colony-layout.json` güvenli yollar ve temas tablosudur. `rhino-habitat-study.glb`, eski `rhino-habitat-editable.blend` ve `preview.png` önceki 14×10 m bileşen denemesidir; tam alan dosyası yerine kullanılmaz.

## Doğrulama ve performans

- İki güncel GLB: Khronos doğrulayıcıda 0 hata / 0 uyarı.
- 20 dakikalık hareket simülasyonu: sınır ihlali yok; en küçük merkez mesafesi 7,56 m. Duraklatma, görünmeyen sekme ve dönüş atlaması denetlendi.
- Gerçek skinned geometride yürüme–dinlenme geçişi: yaklaşık −0,19 / +1,39 mm temas farkı. 513×17 temas tablosu çevrim dışı hesaplanır; her karede CPU vertex skinning yapılmaz.
- Görünürlükle yükleme; ortak dokular/geometri; yakın 60 Hz masaüstü / 30 Hz küçük ekran hedefi, uzak 12 Hz; görünmeyen iskelet ve sekme durur. Fizik, yeni yansıma geçişi veya parçacık sistemi eklenmedi.
- Hedef frekans gerçek cihaz FPS garantisi değildir. Son tarayıcı ölçümü ve sınırlamaları `model/browser-performance.json` içinde tutulur; fiziksel telefon testi henüz yapılmadı.

Yeniden üretim: `python publish_local.py --local-only`. Düzenlenebilir sahne: Blender `--background --disable-autoexec --python bolgeler/16-gergedan/model/save_editable.py`. Temas tablosu, hayvan veya dinlenme klibi değişirse `prepare_blend_ground.mjs` ile yeniden hesaplanmalıdır.
