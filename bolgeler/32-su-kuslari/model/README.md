# Su kuşları kubbesi — ilk sakin kuş kolonisi

**Güncel yerel akış ·20261015ao:** Tür etiketi veya kuşun gövdesiyle yaklaşılır; yakında dokunmak mevcut Rest/LookAround/Settle kliplerinden kısa bir tepki seçer. Otomatik davranış değiştirme zamanlayıcısı ve hayvan panelleri kaldırıldı. Dinlenmede iskelet güncellenmez. Ortak seçim/yükleme `viewer/tap-colony.js`, kamera/isimler `viewer/explorer-*.js` içindedir. Aşağıdaki kaynak/model bilgileri korunur; önceki performans notları tarihseldir.

Yerel sürüm `20261015am`. Dört **temsili büyük flamingo** kıyıda dinlenir, başını yavaşça çevirir ve duruşunu küçük hareketlerle değiştirir. Uçuş, yüzme, yürüme, beslenme veya gerçek tüy bakımı klibi yoktur; sabit ayaklı varlık bunları yapıyormuş gibi sürüklenmez.

## Kanıt ve kapsam

- [Bursa Zoo tür sayfası](https://www.bursahayvanatbahcesi.com/hayvan/flamingo-greater-flamingo/) büyük flamingonun bahçedeki varlığını doğrular; güncel kafes içi koordinatı veya sayısını belirtmez.
- [3 Nisan 2026 resmî eğitim yazısının görselinde](https://www.bursahayvanatbahcesi.com/sulari-temiz-tut-ekosistemi-yasat/) flamingolar, beyaz kuğu ve pelikanlar görünür. Görselin çekim yeri/tarihi doğrulanmadı. Açık pembe/beyaz gövde için renk referansıdır; pikselleri model dokusuna kopyalanmadı.
- [USKON imalatçı açıklaması](https://uskon.com/en/bursa-zoo-waterbird-cage-single-wall-elliptical-dome/) ve bölgenin `kaynaklar/fotograflar/uskon-interior-1.jpg`, `uskon-interior-2.jpg` fotoğrafları kubbenin içinde kıyı/su ve kuşları doğrudan gösterir. Tarihî fotoğraflarda leylek/beyaz balıkçıl biçimleri ayırt edilir; güncel flamingo nüfusu kanıtı değildir.
- Bu yüzden dört bireyin sayısı, yeri ve baş yönleri **Yorum** düzeyindedir. `aviary-birds-layout.json:evidenceLabel` aynı belirsizliği arayüze taşır.

## Varlık ve gerçek dosya incelemesi

Kaynak: [Greater Flamingo – Resting Rigged Bird, Pigcraft](https://sketchfab.com/3d-models/greater-flamingo-resting-rigged-bird-1c54310c3877422497d37512f0ba33dc), [CC BY4.0](https://creativecommons.org/licenses/by/4.0/). Üretici AI destekli 3B üretimi açıklar. Bursa'daki belirli bir hayvanın taraması değildir. Dosya resmî indirme düğmesinden ücretsiz edinildi.

Kaynak başlığındaki “rigged” ve açıklamadaki “one leg” gerçek GLB'de karşılanmıyordu: **iskelet 0, animasyon 0, iki ayak**, 1.954.986 üçgen / 120.532.604 bayt. Gerçek dosya üç açıdan render edilerek incelendi. İndirilen başka bir leylek adayı gagasında bebek torbası taşıdığı için, köşeli leylek ve lisansı belirsiz yeniden yüklenmiş egret adayları da kalite/kaynak gerekçeleriyle elendi.

`hayvan/prepare_flamingo.py` şu düzenlenebilir türevi üretir:

- 1,30 m yorum yetişkin boyu; [San Diego Zoo](https://animals.sandiegozoo.org/animals/flamingo) büyük flamingo için 120–145 cm aralığı verir.
- 12.000 gövde üçgeni + 40 ayak perdesi üçgeni. Kaynak parmaklar korunur; aralarına ince, dış kenarı içbükey perde eklenir. Bu ayak ayrıntısı görsel yorumdur. Aynalı iki kapalı zarın dış yüz yönleri düzeltilmiştir; sıfır alanlı yüz yoktur. `hayvan/foot-geometry-verification.json` yalnız bu yeni parçalara aittir; kaynak gövde/tüy yüzeyleri kapalı imalat katısı olarak sunulmaz.
- Boyun yüzeyindeki büyük kaynak yumruları maskeli altı yumuşatma geçişiyle azaltılır; normal yoğunluğu 0,12 olur.
- Kaynağın 1K malzeme/UV setleri korunur. Üst gövde için renk düzeltme malzemesi 1K albedoya bake edilir: doygunluk 0,35 / açık renk karışımı 0,28. Kırmızı bacak ve koyu gaga/göz maskeyle korunur. Özgün kaynak değişmez.
- Beş kemikli özgün dinlenme iskeleti ve üç 6 s klip: `Rest`, `LookAround`, `Settle`. Hareket yakalama ya da kaynaktan hazır klip olarak tanıtılmaz. Temsili baş hareketleri etolojik ölçüm değildir.
- glTF skin düğümü sahne köküne alınır; atıf/lisans/değişiklikler GLB asset extras'a da yazılır.

## Performans

Tek kuş GLB yaklaşık 3,46 MiB; dört birey toplam 48.160 üçgen, 20 kemik ve sekiz ana çizim. Aynı iki geometri, malzemeler ve üç 1K doku paylaşılır; her bireyin iskeleti/mixer'ı ayrıdır. Doku setinin nominal RGBA+mip boyutu 16 MiB'dir; bütün GPU belleği değildir.

Görüş dışındaki bireyin mixer/karar saati durur. Gizli sekme, kapalı hayvan katmanı ve duraklatmada bütün güncelleme durur. Yakın masaüstü 60 / mobil eşik 30, uzak 12 Hz hedefi; yeniden görünmede delta sıfırlanır, en çok 0,08 s ilerler. Fizik motoru, tüy simülasyonu veya ek render/yansıma geçişi yoktur.

[SkeletonUtils.clone](https://threejs.org/docs/pages/module-SkeletonUtils.html) ayrı kemikler ile paylaşılan geometri/malzeme üretir; [AnimationMixer](https://threejs.org/docs/pages/AnimationMixer.html) bağımsız varlık başına kullanılır. Gerçek telefon FPS/GPU zamanlaması henüz ölçülmedi.

## Yerleşim ve kontroller

`build_bird_layout.py`, değişmemiş mevcut `current-plan-data.json:modelAnchor` üzerinden cage-localXY→M5 dönüşümü yapar. Native koordinatları değiştirmez. Mevcut bölünmüş kuru zeminde 0,65 m yarıçapı, yol/su/bina ve `viewer/model.js` iç kıyı/çalı kümelerinin yaklaşık sınırlarını denetler. En düşük bitki sınırı açıklığı 0,720 m'dir. Köprü/değirmen ve ağaçlardan ayrı güney kıyısındadır.

`node bolgeler/32-su-kuslari/model/verify_birds.mjs` gerçek teslim GLB'sini üretim GLTFLoader'ı ile okur. Üç klip × 145 pozda zemin minimum/maksimum 0 m ve ayak kayması 0 m; döngü farkı 1,9×10⁻⁸ m. 120 s gerçek modül akışı, bağımsız iskelet/paylaşılan kaynak, farklı durum geçişleri ve gizli/pause/toggle/görüş dışı donma geçti. Khronos Validator: 0 hata / 0 uyarı; kullanılmayan UV accessor için bir bilgi kaydı var.

Bu kontroller anatomik veya veterinerlik doğrulaması değildir. Son atlas görünümü ve fiziksel telefon performansı ayrıca incelenmelidir.

## Dosyalar / yeniden üretim

- `hayvan/greater-flamingo.glb`: çalışan hafif varlık.
- `hayvan/greater-flamingo-editable.blend`: metre birimli gövde/perde, beş kemik, üç özgün NLA klibi; açılışta NLA izleri sessize alınmıştır, düzenleme için açılabilir.
- `hayvan/asset-manifest.json`: kaynak ve teslim SHA'ları, lisans, türev işlemler ve maliyet.
- `hayvan/source/flamingo-original.glb`: yerel arşivlenmiş büyük kaynak; nested `.gitignore` ile yayın paketinden ve Git'ten hariçtir.
- `hayvan/source/flamingo-source-metadata.json`: resmî model API metadata arşivi.
- `hayvan/flamingo-source-*.png` / `flamingo-delivery-*.png`: gerçek dosyanın önce/sonra kanıt renderları.
- `aviary-birds-layout.json`: yorum yerleşimi ve kaynak/atıf/UI açıklaması.
- `bird-verification.json` / `hayvan/gltf-validation.json`: gerçek dosya kontrolleri.
- `viewer/aviary-birds.js`: bağımsız çalışma modülü; başka bölgenin hayvanlarını değiştirmez.

Yeniden üretim: Blender 5.2 ile `hayvan/prepare_flamingo.py`, ardından Python 3.12 ile `build_bird_layout.py`, ardından Node ile `verify_birds.mjs` ve Python ile `hayvan/verify_foot_geometry.py`. Kaynak SHA eşleşmesi zorunludur. Builder önbellekteki teslim SHA'sını kontrol ederek büyük ham dosyayı yeniden işlemekten kaçınabilir.

## Ana atlas entegrasyonu

```js
const birds=createAviaryBirds(footprints,onChange,{base:'./models/',anchor:CAGE,surfaceData:S});
birds.update(now,camera,viewportHeight,region);
```

API: `status()`, `setEnabled(bool)`, `setPaused(bool)`, `retry()`, `metadata()`, `focusPoint()` (M5XYZ). UI'de `metadata().evidenceLabel` ve `metadata().credits` gösterilir. Yakın kamera önerisi cage-local eye[-7,-18,2.4], target[-7,-11.1,.5]; ikisi de mevcut `CAGE` dönüşümüyle M5'e çevrilir.

Yerel builder yalnız `greater-flamingo.glb`→`dist/models/greater-flamingo.glb`, `aviary-birds-layout.json`→`dist/models/aviary-birds-layout.json`, `viewer/aviary-birds.js`→`dist/aviary-birds.js` kopyalar. `docs/` ve canlı yayın bu çalışma kapsamında değiştirilmez.
