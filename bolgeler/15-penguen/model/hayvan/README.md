# Afrika pengueni — hareketli ilk model

[Atlasta izle](http://127.0.0.1:8768/?focus=penguin-close&revision=20261015ai) · [Animasyonları incele](http://127.0.0.1:8768/model-review/?model=penguin-animal&revision=20261015ai) · [Aynı Wi-Fi](http://192.168.0.192:8768/?focus=penguin-close&revision=20261015ai).

## Kaynak ve dosyalar

[African penguin (Spheniscus demersus) Low poly](https://sketchfab.com/3d-models/african-penguin-spheniscus-demersus-low-poly-9e59070815fe451d93398e2ebdb9bb92), **Major**, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). 15 Ekim 2026'da Sketchfab'ın resmî indirme düğmelerinden özgün FBX ZIP ve dönüştürülmüş GLB indirildi. `source/` değişmemiş kaynakları ve platform kaydını; `source-manifest.json` dosya/SHA bilgilerini; `ATTRIBUTION.txt` atfı içerir. Görünüm menüsünde ve model incelemesinde kaynak gösterilir. [Bursa'nın resmî tür kaydı](https://www.bursahayvanatbahcesi.com/hayvan/afrika-pengueni-african-penguin/).

- `african-penguin.glb`: metre, Y yukarı, yorum boyu 0,62 m; 4.124 üçgen, iki skinned mesh,64 eklem,sekiz klip,4.980.240 bayt. Boy Bursa'daki tekil bir hayvanın ölçümü değildir.
- `african-penguin-editable.blend`: aynı teslim GLB'sinden içe aktarılan düzenlenebilir iskelet,sekiz eylem ve üç paketlenmiş görüntü. Önizleme zemin/kamera/ışıkları modelden ayrıdır. Yeniden açma denetimi `blend-verification.json`.
- `colony-layout.json`: M5 kara/su maskelerinden güvenli alanlar, kotlar, başlangıçlar, hızlar ve kliplerin zemin düzeltme tablosu. Kaya/kıyı/duvar/platformdan uzak tutulur. Konumlar güncel saha ölçümü değildir.
- `source-preview.png`: gerçek GLB'nin Blender/Cycles önizlemesi. `atlas-preview.png`: çalışan WebGL sahnesinin PNG yakalaması; AI mockup değildir.

## Düzeltmeler ve davranış

Kaynak dönüştürmede glTF'nin animasyon verisinde yasakladığı gereksiz `byteStride` vardı. Sıkı paketleme doğrulanarak kaldırıldı; sıfır ağırlıklı eklem indisleri temizlendi; skinned düğümler sahne köküne taşındı; kullanılmayan UV tekrarları çıkarıldı. Geometri şekli, etkin ağırlıklar, animasyon anahtarları ve kaynak PNG pikselleri korunur. Biyolojik yüzey metalik değildir; normal harita yoğunluğu0,55'tir.

Kıyıda üç, suda iki yorum bireyi bulunur; Bursa'nın hayvan sayısı kaydı değildir. Kısa yürüyüş, bekleme, tüy bakımı, silkelenme ve yüzme/dalma davranışları farklı zamanlarda gerçekleşir. Kısa beklemeler, sınırlı dönüş/ivme ve0,55 s klip geçişi kullanılır. Kaygan görünen ayaklar için zemin tablosu gövde mesh'inden ölçülür; alfanın şeffaf tüy kenarı ayakları havada bırakmaz. İlk sürümde kıyı bordürünü aşan kara–su geçişi yapılmaz; iki ortamın bireyleri ayrıdır. İleri tırmanma, beslenme ve bireyler arası kapsamlı sosyal davranış yoktur.

## Performans ve doğrulama

Beş bağımsız iskelet geometri/malzeme/dokuları paylaşır:20.620 hayvan üçgeni ve en çok10 ana mesh çizimi; gölge/yansıma çizimleri ayrıca sayılır. Üç1024² görüntünün temel RGBA karşılığı12 MiB, miplerle yaklaşık16 MiB'dir; bütün GPU belleği değildir. Yakında masaüstü60 Hz/mobil genişlikte30 Hz, uzakta12 Hz hedeflenir. Görüş dışındaki iskeletler, bütün koloni görünmez olduğunda ve sekme gizlendiğinde hesap durur. Yeniden görünmede gizli geçen süre yakalanmaz. Ek render geçişi eklenmedi; mevcut sahne su/AO/gölge sistemi kullanılır.

`verify_penguins.mjs`:600 s / 90.000 davranış örneğinde alan dışına çıkma yok, en yakın aynı ortam mesafesi0,6400 m. Yedi kara klibinin96'şar gerçek skinned geometri örneğinde gövde zemin sınırı −0,83…+2,47 mm; bütün klip karışımlarında aynı hata sınırı garanti edilmez. İskeletler bağımsız, geometri/malzeme ortak. Khronos:0 hata/0 uyarı; dört boş kaynak düğümü bilgi düzeyindedir. `verify_runtime.mjs`: gerçek çalışma modülünde görüş dışı/gizli sekme/toggle duruşu, yeniden görünmede8,55 mm'den küçük devam adımı geçti.

İlk1280×720 tarayıcı örneğinde180 güncelleme:60,04 Hz, p95 aralık16,8 ms; animasyon ortalama CPU0,191 ms.390×844 aynı bilgisayarda:30,02 Hz,p95 aralık33,4 ms,ortalama CPU0,185 ms. Bunlar fiziksel telefon/GPU süresi veya bütün cihazlar için FPS garantisi değildir. Güncel ölçümler `browser-performance.json` içinde tutulur.

Teknik dayanaklar: [AnimationMixer](https://threejs.org/docs/pages/AnimationMixer.html), [AnimationAction](https://threejs.org/docs/pages/AnimationAction.html), [Frustum](https://threejs.org/docs/pages/Frustum.html), [Page Visibility API](https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API). Çalışan kod `viewer/penguins.js` ve `viewer/penguin-motion.js`.

## Yeniden üretim

Proje kökünden `node bolgeler/15-penguen/model/hayvan/inspect_rig.mjs`, `python bolgeler/15-penguen/model/hayvan/prepare_penguin.py`, `node bolgeler/15-penguen/model/hayvan/verify_penguins.mjs`; yerel sunucu açıkken `node bolgeler/15-penguen/model/hayvan/verify_runtime.mjs`. Blender önizlemesi `inspect_source.py`, yeniden açma `verify_blend.py`. `publish_local.py --local-only` türevi ve yerleşimi `dist/` içine alır; özgün ZIP/FBX/Blender araştırma dosyalarını yayın dizinine kopyalamaz. `docs/` değiştirilmez.
