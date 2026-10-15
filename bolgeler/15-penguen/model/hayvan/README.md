# Afrika penguenleri — koloni deneyimi

Yerel sürüm `20261016at`. [Alanı aç](http://127.0.0.1:8768/?area=penguinPool&revision=20261016at) · [Aynı Wi-Fi'deki telefon](http://192.168.0.11:8768/?area=penguinPool&revision=20261016at) · [Özgün klipleri incele](http://127.0.0.1:8768/model-review/?model=penguin-animal).

## Ziyaretçi akışı

Haritadaki Penguenler etiketi doğrudan koloni/havuz kıyısı kadrajını açar. Birey seçilene kadar panel yalnız türü tanıtır. Gövdeye dokunmak o bireye biraz daha yaklaşır; kamera ve paneldeki Kıyı/Havuz birey numarası gözleneni belirtir. Hover ve seçim halkaları yoktur. Yalnız klavyeyle gezinirken hedefin altında ince bir odak çizgisi görünür. Hayvanların üzerinde isim veya hareket düğmesi yoktur. Enter/Space seçim/tepki, Escape geri dönüş sağlar. Sürükleme veya çoklu işaretçi seçime dönüşmez. **Koloniye dön** seçimi bırakır; kolonideki **Genel plana dön** haritayı açar.

Kıyıdaki üç yorum bireyinde bakınma, silkelenme, tüy bakımı ve uyku/uyanma; havuzdaki iki bireyde kısa yüzme ve dinlenme vardır. Koloni görünümünde hareketler molalarla kendiliğinden başlar. Birey seçildiğinde diğer hareketler sakinleşir, otomatik zamanlama yalnız gözlenen bireyde sürer. Kıyıda art arda aynı tepki seçilmez. Uyuyana dokunmak uyandırır. Gözlenen yüzücüye dokunmak yüzmeyi başlatır veya klip fazını/konumunu sıfırlamadan yüzme süresini uzatır; kamera takip eder. Elle orbit takibi bırakır; tekrar dokunmak geri açar. Azaltılmış hareket tercihinde otomatik hareket başlamaz; açık dokunuş kullanılabilir.

Uyku oturma/uyuma klipleri, uyanma ters duruş geçişleridir. Kara/su geçişi yoktur: dik kıyıyı aşan uygun klip veya geçit modellenmedi. Suda bekleme kaynak Idle duruşunun yorumlanan su kotuna oturtulmasıdır; fiziksel yüzdürme değildir. Beş birey ve yerleşim güncel Bursa sayımı değildir.

Karede en fazla iki görünür iskelet örneklenir. İki yuva doluyken yeni bir gövdeye dokunmak önceki hareketlerden birinin yumuşakça sonlanmasını ister; dokunulan birey ilk boşalan yuvada başlar. İstekler sonsuz kuyruk oluşturmaz. Görünmeyen yüzücü görünür bireylerin yuvasını işgal etmez; tekrar göründüğünde zaman atlamadan devam eder. Alandan çıkmak otomatik zamanlamayı kapatır. Yüzme yerleşim ofseti−0,29m'den−0,23m'ye alınarak yakın takipteki gövde okunurluğu iyileştirildi; fiziksel yüzdürme veya ölçülmüş su hattı iddiası değildir.

## Kaynak ve düzenlenebilir model

[African penguin (Spheniscus demersus) Low poly](https://sketchfab.com/3d-models/african-penguin-spheniscus-demersus-low-poly-9e59070815fe451d93398e2ebdb9bb92), **Major**, [CC BY4.0](https://creativecommons.org/licenses/by/4.0/). Özgün GLB/FBX ZIP/dokular `source/`, teslim SHA'ları `source-manifest.json` içindedir.

`african-penguin.glb`:4.124 üçgen, iki skinned mesh,64 eklem, sekiz özgün klip,4.980.240 bayt; yorumlanan boy0,62m. `african-penguin-editable.blend` metrik kaynak, sekiz eylem ve paketli dokuları içerir. Davranış JavaScript'te düzenlenir; Blender'a uzun ziyaretçi senaryosu olarak fırınlanmaz. Kaynak Walk/Bray model inceleyicide korunur.

Kaynak glTF'nin gereksiz animasyon byteStride, yinelenen UV referansları ve sıfır ağırlıklı eklem indisleri önceden düzeltildi. Etkin ağırlıklar, geometri biçimi, özgün anahtar kareler ve PNG pikselleri korunur. Tüyler metalik değildir; normal yoğunluğu0,55. Zemin referansı gövde/ayak meshidir; transparan tüy kartlarının boş kenarları ayakları havada bırakacak şekilde referans alınmaz.

## Kod ve performans

- `viewer/penguin-motion.js`: sınırlı uyku/tüy bakımı/bakınma ve güvenli yüzme sıraları. Otomatik dolaşma, dalma veya aralıklı bakınma zamanlayıcısı yoktur.
- `viewer/penguins.js`: kaynak yükleme, ayrı iskelet/ortak geometri-doku, görünürlük, sınırlı koloni zamanlaması, dokunma ve klip örnekleme.
- `viewer/animal-info.js` ve `animal-profiles.js`: dört türde ortak salt bilgi görünümü ve tür/klip açıklamaları; kamera veya animasyon komutu içermez. Önceki tek tür paneli kaldırıldı. Tür bilgisi San Diego Zoo kaynağına bağlanır.
- `viewer/penguin-views.js`: kaynak ekranın koloni kadrajı, bireye yaklaşma ve takip hedefi; uygulama ile CPU kamera testi aynı fonksiyonları kullanır.
- `viewer/explorer-labels.js`, `explorer-camera.js`: bütün türlerin ortak isim/kamera akışı. Eski `penguin-interaction-ui.js` kaynak ve yerel paketten kaldırıldı.
- `colony-layout.json`: metrik başlangıçlar, kara/su maskeleri, iki elips rota ve zemin düzeltmeleri.
- `bake_transitions.mjs` / `penguin-transitions.json`: gerçek GLB'den çevrimdışı10 geçiş tablosu,128 faz/16 ağırlık aralığı,176.928 bayt. Tarayıcı iki boyutlu enterpolasyon yapar; kare başına vertex taraması yoktur. Gerçek dokunmada mesh seçim sınırları yeniden hesaplanır.

Sakin duruş iskeleti güncellemez veya sahne çizimi istemez. Kamera, yeni kaynak veya açık hareket yeniden çizim gerektirir. Yakın masaüstü en çok60Hz, dar ekran/birincil dokunmatik30Hz; uzakta12Hz. Görüş dışı, gizli sekme veya kapalı modelde hareket durur. Model/doku belleği bu arayüzle küçülmüş sayılmaz. Fiziksel telefon FPS/GPU/pil ölçümü yapılmadı.

## Doğrulama ve araştırma

`verify_penguins.mjs`:1200 saniyelik komut senaryoları/180.000 örnek; geçerli alan, güvenli ayrım, sınırlı adım, sonlanan kesintiler; GLB0 hata/0 uyarı.

`verify_runtime.mjs`: gerçek üretim modülü ve GLB ile mesh dokunma, sakin/uykuda0 güncelleme, gerçek yüzme, görüş dışı/gizli sekmede durma,7,3mm'den küçük tekrar görünme adımı, azaltılmış hareket,30Hz ve geçişlerde yaklaşık−0,1…+2,02mm zemin sapması.

`verification/explorer-interactions.mjs`: dört türde ortak ziyaretçi akışı için gerçek runtime/model kontrolleri. Tarayıcı ekranları ve görsel kontrol proje kökündeki `design-qa.md` içindedir.

[Araştırma kaydı](interaction-research.json): Three.js AnimationAction/Raycaster/değişiklikte çizim belgeleri ve San Diego Zoo'nun Afrika pengueni/bakım kaynakları. Süre, su duruşu ve rotalar görsel yorumdur.

## Yeniden üretim

`python publish_local.py --local-only` metrik model/girdileri ve geçiş tablosunu üretip yalnız `dist/` içine kopyalar. Yalnız arayüz için `--runtime-only` eklenebilir. Tekil kontroller: `node bolgeler/15-penguen/model/hayvan/verify_penguins.mjs`, yerel sunucu açıkken `node bolgeler/15-penguen/model/hayvan/verify_runtime.mjs`. Yeni açık talep gelmeden docs/commit/push/canlı yayın kullanılmaz.
