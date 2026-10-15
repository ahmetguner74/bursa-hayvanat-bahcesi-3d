# Bursa Hayvanat Bahçesi — 3B modelleme ön araştırması

## Mobil keşif ve doğrulanmış yayın · `20261016au`

[Canlı atlas](https://ahmetguner74.github.io/bursa-hayvanat-bahcesi-3d/?revision=20261016au) · [Yerel atlas](http://127.0.0.1:8768/?revision=20261016au) · [Aynı Wi-Fi'deki telefon](http://192.168.0.11:8768/?revision=20261016au).

Mobil sağ kart kısa ve içerik boyundadır; sahne tam genişlik kullanır.390×666 denetiminde uzun hareket adıyla128×171px kart, önceki128×584px alanın%29,4'üdür. Tür ve gözlenen bireyin hareketi korunur; uzun tanıtım ve ölçüler masaüstünde kalır. İlk yakın ziyarette hayvana bitişik el/“Dokun” ipucu dört saniye içinde söner ve aynı oturumda tekrarlanmaz. Hayvan üstünde kalıcı yazı, halka veya hareket düğmesi yoktur.

Penguen birey odağı yakınlaştırıldı; yüzücü kamera takibi, orbit ile serbest kalma ve tekrar dokunuşla takip korunur. Flamingo alanına giriş/çıkış kapı turu yapmadan doğrudandır. Mevcut beş kemikli modelin baş-boyun tepkisi okunur hale getirildi; ayaklar sabit, yeni mesh/kemik/render pass yoktur. Dokunuş belirsiz Rest klibini seçmez. Yükleme hatasında çalışan “Tekrar yükle” yolu ve panelle eşleşen erişilebilir hareket duyurusu vardır.

[Product Design denetimi](design/2026-10-16-mobil-denetim/audit.md), [görsel QA](design-qa.md), [tarayıcı kanıtı](design/2026-10-16-mobil-denetim/browser-checks-au.json) ve dört üretim GLB/runtime testi geçti. Fiziksel telefon FPS/GPU/pil ölçümü yapılmadı; tam WCAG uygunluğu iddiası yoktur. M5 kaynak ve yol verileri değişmedi. Kullanıcının açık yayın isteğiyle `python build_public.py --publish`, doğrulanmış `dist/` paketini GitHub Pages'in `main:/docs` kaynağına hazırlar. Özgün indirmeler, özel araştırma fotoğrafları ve düzenlenebilir çalışma sahneleri yerelde kalır; türetilmiş modeller, üretim kodu ve lisans kayıtları sürümlenir. Aşağıdaki notlar önceki sürümlerin tarihçesidir.

## Dört türde ortak keşif · `20261016at`

[Yerel harita](http://127.0.0.1:8768/?revision=20261016at) · [Telefon](http://192.168.0.11:8768/?revision=20261016at) · [Gergedan](http://127.0.0.1:8768/?focus=rhino-close&revision=20261016at) · [Zürafa](http://127.0.0.1:8768/?focus=giraffe-close&revision=20261016at) · [Flamingolar](http://127.0.0.1:8768/?focus=aviary-close&revision=20261016at).

Penguenin yakın alan → gövdeye dokunma → birey odağı akışı diğer üç türe aktarıldı. Birey seçilene kadar sağ panel yalnız türü tanıtır; sonra gerçek gözlenen bireyin hareketini anlatır. Hayvan üstünde yazı, hover/seçim halkası ve hareket düğmesi yoktur. Gergedan/zürafa yürüyüşünde kamera izler; sürükleme takibi bırakır. Seçimde diğerleri sakinleşir; sürü/koloniye dönüş otomatik sıralamayı yeniden açar. Genel haritada yalnız dört hayvan deneyimi adlandırılır.

Gergedan bakınma/kulak/yürüyüş; zürafa mevcut baş-boyun klibi/yürüyüş; flamingo mevcut baş-boyun/dinlenme kliplerini kullanır. Flamingo modeli uçuş/yürüyüş desteklemez. Yeni hayvan mesh'i, bağımlılık veya GPU efekti yoktur. Her kolonide en fazla iki görünür iskelet örneklenir; dokunmatik yakın örnekleme30Hz, gizli/görünmeyen/dinlenenlerde durma vardır. Gerçek gergedan/zürafa GLB ölçüleri yakın kadrajda kullanılır.

`animal-info.js`, `animal-profiles.js`, `animal-views.js` ortak deneyimi; `tap-colony.js` üç türün sınırlı zamanlamasını yönetir. Eski `penguin-info.js` ve grup/uzak hayvan ekranı dalları kaldırıldı. [Üç tür doğrulaması](verification/animal-discovery.json), [dört tür regresyonu](verification/explorer-interactions.json), [penguen takibi](verification/penguin-focus.json) ve [görsel kontrol](design-qa.md) geçti. Fiziksel telefon FPS/GPU/pil ölçümü yapılmadı. Yalnız `dist/` yenilendi; `docs/`, M5/yollar, canlı yayın, commit/push kullanılmadı. Aşağıdaki notlar önceki sürümlerdir.

## Minimal yükleme göstergesi · `20261016as`

[Yerelde aç](http://127.0.0.1:8768/?revision=20261016as) · [Aynı Wi-Fi'deki telefon](http://192.168.0.11:8768/?revision=20261016as).

Başlangıçta “Hayvanat bahçesi yükleniyor…” ve22px Feather yükleme simgesi görünür. Sahne hazır olduğunda mevcut akış ikisini kaldırır; yapay bekleme/yüzde, yeni bağımlılık veya JavaScript zamanlayıcısı yoktur. Simge CSS transform ile döner; azaltılmış hareket tercihinde sabittir. Yavaş bağlantıda gerçek yükleme görünümü ve ardından kapanması doğrulandı; konsol hata/uyarı yok. [Görünüm](design/2026-10-16-penguen-odak/qa/17-minimal-yukleme-as.png). Yalnız yerel paket güncellendi.

## Doğrudan koloni ve bireye odak · `20261016ar`

[Haritayı aç](http://127.0.0.1:8768/?revision=20261016ar) · [Penguenlere doğrudan gir](http://127.0.0.1:8768/?focus=penguin&revision=20261016ar) · [Aynı Wi-Fi'deki telefon](http://192.168.0.11:8768/?revision=20261016ar).

Genel planda yalnız hayvan modeli bulunan **Penguenler, Gergedanlar, Zürafalar ve Su Kuşları Kafesi** adlandırılır. Yalnız barınak/yapı düzeyindeki diğer etiketler kaldırıldı; sahne geometrileri korunur. Penguen etiketi doğrudan kullanıcının yakın koloni/havuz kadrajını açar; uzak alan ekranı ve ikinci grup etiketi aradan çıkarıldı.

Kolonide birey seçili değildir; panel türü tanıtır ve henüz bir hayvana ait hareket göstermeye çalışmaz. Gövdeye dokunmak o bireye yumuşakça yaklaşır. Kamera odağı ve paneldeki **Şu anda / Kıyı2 veya Havuz1** gözleneni anlatır; hover ve seçim halkaları kaldırıldı. Yalnız klavyeyle gezinirken hedefin altında ince bir odak çizgisi görünür. Gözlem sırasında diğer bireylerin hareketleri yumuşakça sakinleşir. Yüzücüye dokunmak yüzmeyi başlatır/uzatır; kamera onu takip eder. Sürükleme takibi bırakır, tekrar hayvana dokunmak geri açar. **Koloniye dön → Genel plana dön** geri akışıdır.

Yüzme duruşu suya göre6cm yükseltildi; sırt/gövde yakın takipte daha okunur, su yüzeyi ve XY rotaları değişmez. Kaynak klipler/GLB değiştirilmedi. `penguin-views.js` koloni/odak/izleme hedeflerini tek yerde tutar; eski penguen koloniye yaklaşma dalı kaldırıldı. En fazla iki görünür iskelet örneklenir, dokunmatik yakın hareket30Hz ile sınırlıdır; değişmeyen sahne çizilmez.

[Gerçek modül, GLB ve OrbitControls ile odak/takip doğrulaması](verification/penguin-focus.json) · [Kullanım incelemesi](design/2026-10-16-penguen-odak/audit.md) · [Son görsel kontrol](design-qa.md). Mobil ve masaüstü düzeni incelendi; fiziksel telefon FPS/GPU/pil ölçümü yapılmadı. Yerel `dist/` yenilendi; `docs/`, canlı yayın ve GitHub'a gönderim yapılmadı. Aşağıdaki notlar önceki aşamalardır.

## Penguen kolonisinde keşif · `20261015ap`

[Alanı aç](http://127.0.0.1:8768/?focus=penguin&revision=20261015ap) · [Aynı Wi-Fi'deki telefon](http://192.168.0.11:8768/?focus=penguin&revision=20261015ap) · [Doğrudan koloniye yaklaş](http://127.0.0.1:8768/?focus=penguin-close&revision=20261015ap).

Son iki telefon referansına göre yalnız penguen deneyimi değiştirildi. Alan görünümündeki **Penguenler** etiketi koloniyi/havuzu birlikte gösteren sabit kıyı kadrajına yaklaşır. Yakında hayvanların üstünde yazı veya hareket düğmesi bulunmaz. Görünür penguenler aralıklı bakınma, silkelenme, tüy bakımı, uyku/uyanma ve güvenli yüzme hareketleri yapar; gövdeye dokunmak farklı davranış ister. Kamera sonraki dokunuşlarda bireyin peşine gitmez.

Sağdaki dar krem panel türü tanıtır; **Şu anda** bölümünde izlenen penguenin gerçek denetleyici durumu ve kısa açıklaması gösterilir. Panel davranış seçmez. Telefonda da sağdadır; sahne genişliği buna göre hesaplanır. Klavye kullanıcıları gövde üstündeki görünmez, odakta halkası beliren hedefleri kullanır. Geri dönüş paneli kapatıp sahneyi tam genişliğe getirir.

Otomatik davranış yalnız yakın penguen görünümünde açıktır; görünmeyen/gizli sekmedeki iskeletler donar. Karede en fazla iki görünür iskelet örneklenir; dokunmatik yakın görünüm30Hz ile sınırlıdır. Arada dinlenen iskeletler güncellenmez. Azaltılmış hareket tercihinde otomatik davranış kapalı, açık dokunuş kullanılabilir. Fiziksel telefon FPS/pil ölçümü yapılmadı.

Kod: `viewer/penguins.js` sınırlı koloni zamanlaması; `penguin-motion.js` sonlu hareket/geçişler; `penguin-info.js` salt bilgi paneli; `app.js` sabit kamera ve geri dönüş. `node verification/penguin-discovery.mjs` gerçek üretim GLB'siyle beş bireyin davranışını,25 hızlı dokunuşu, iki iskelet sınırını, kıyı/su güvenliğini, görünmeyen yüzücünün kıyıyı durdurmamasını ve çıkışta durmayı doğrular. [Ekranlar ve tasarım](design/2026-10-15-penguen-koloni/) · [Görsel kontrol](design-qa.md).

Yalnız yerel `dist/` yenilendi; canlı yayın/commit/push yapılmadı, `docs/` ve M5 yol/kroki verileri korunur. Diğer türlerin `20261015ao` etkileşimi sürer. Aşağıdaki notlar önceki sürümlerin kaydıdır.

## Sade sahne üzerinde keşif · `20261015ao`

[Bilgisayarda aç](http://127.0.0.1:8768/?revision=20261015ao) · [Aynı Wi-Fi'deki telefon](http://192.168.0.11:8768/?revision=20261015ao).

İsim etiketi → yaşam alanı → hayvan seviyesine yaklaşım → hayvana dokunarak kısa davranış. Penguen, flamingo, zürafa ve beyaz gergedanda aynı akış kullanılır. Tepkiler tür ve ortama göre, art arda tekrarı azaltılarak seçilir. Alt açı/zoom çubukları, kategori/katman menüsü ve penguen seçim/davranış paneli ile eski DOM modülü kaldırıldı. Orbit/zoom fare ve dokunma hareketleriyle, geri dönüş tek üst kontrolle yapılır. Kroki/yol çalışma aracı `v2/` altında korunur.

Katalogdaki hazır barınak/yapılar ve kuş kafesi isimlendirilir. Uzakta çakışan ikincil etiketler sadeleşir, yaklaşınca açılır. Alan görünümünde aynı tür tek etikette, yakında bireyler ayrı hedeflerdedir. Kamera tek perspektif sistemi kullanır; kafese giriş/çıkışta kapıdan geçen ara noktalar vardır. Ekran yönü değişince otomatik kadraj hesaplanır; sürükleme uçuşu keser.

Kod: `explorer-camera.js` kamera; `explorer-labels.js` erişilebilir isimler; `tap-colony.js` ortak hayvan yaşam döngüsü; `animal-interaction.js` kısa tepkiler ve sınırlı yürüyüş. Tür dosyaları kaynak klip, malzeme ve yerleşimi tanımlar. Penguenin uyku/yüzme denetleyicisi korunur; kendiliğinden hareket başlatan zamanlayıcı kaldırıldı. Dinlenmede iskelet güncellemesi yoktur; sahne değişmedikçe GPU çizimi istenmez.

Kontroller: `node verification/explorer-interactions.mjs` dört gerçek üretim modülü/GLB ile dokunma, yürüyüş, zemin teması, gizli sekmede durma, kesintilerin sonlanması, ortak geometri/ayrı iskelet ve dokunmatik30Hz sınırını doğrular. Fiziksel telefon FPS/GPU/pil ölçümü değildir. [Tasarım/ekran kanıtları](design/2026-10-15-sade-kesif/) · [Görsel kontrol](design-qa.md).

Arayüzü mevcut yerel pakete geçirmek: `python publish_local.py --local-only --runtime-only`. Tüm geometrileri yeniden üretmek: `python publish_local.py --local-only`. Canlıya yayınlanmadı; `docs/`, commit ve push kullanılmadı. Aşağıdaki sürüm notları önceki aşamaların tarihsel kaydıdır.

## Penguenlerde dokunarak etkileşim · `20261015an`

[Yerelde dene](http://127.0.0.1:8768/?focus=penguin-close&revision=20261015an) · [Aynı Wi-Fi'deki telefon](http://192.168.0.11:8768/?focus=penguin-close&revision=20261015an). Kıyıdaki penguenlerde bakınma, tüy bakımı ve uyuma/uyanma; havuzdakilerde kısa yüzme ve bekleme. Penguene dokunmak ve erişilebilir seçim düğmeleri aynı akışı kullanır. Rastgele dolaşan eski penguen denetleyicisi kaldırıldı; [davranış, görünüm ve DOM denetimleri ayrıldı](bolgeler/15-penguen/model/hayvan/README.md).

Sakin/uyku duruşunda iskelet ve sahne çizimi güncellenmez; seçilmiş uyanık kıyı bireyinde aralıklı kısa bakınma olabilir. Penguen görünümünde diğer hayvan animasyonları geçici durur. Gerçek GLB geçişlerindeki zemin teması çevrimdışı tabloyla düzeltilir; kare başına vertex döngüsü yoktur. Kara/su geçişi veya besleme sahnesi eklenmedi. Fiziksel telefon GPU/FPS ve enerji tüketimi henüz ölçülmedi. Çalışma yalnız yereldir; `docs/` ve canlı sürüm değişmedi.

## Güncel yerel çalışma · `20261015am`

Kullanıcının son talimatı gereği geliştirmeler yalnız yerelde yapılır; yeni bir açık yayın talebi olmadan GitHub'a gönderilmez ve `docs/` değiştirilmez. Aşağıdaki eski yayın ve IP notları tarihsel kayıttır. Güncel Wi-Fi adresi **192.168.0.11**; bilgisayar ve yerel sunucu açık olmalıdır.

- [Kafes içindeki dört temsili flamingo](http://127.0.0.1:8768/?focus=aviary-close&revision=20261015am): ayrı sakin duruş, çevreye bakma ve duruş değiştirme klipleri. Tür Bursa'da doğrulanır; bu dört bireyin güncel kubbe içi yerleşimi doğrulanmadı. [Kaynak, düzenlenebilir model ve kontroller](bolgeler/32-su-kuslari/model/README.md).
- [İki temsili Baringo zürafası](http://127.0.0.1:8768/?focus=giraffe-close&revision=20261015am): özgün yavaş yürüyüş, kaynak dinlenme klibi; fotoğraflara göre yorumlanan kumlu açık bölüm, taş sınır, yeşil korkuluk ve dal yemlikleri. Tam Savanna veya teyitsiz ahır cephesi tamamlanmış sayılmaz. [Ayrı model incelemesi](http://127.0.0.1:8768/model-review/giraffe/?view=animal).

Zürafa modelinin kendi zemini atlasın çim/yol katmanından ayrılır. Hayvanlar ayrı iskeletler, paylaşılan geometri ve dokular kullanır; görünmeyen hareketler durur, uzak görünümde güncelleme azalır. Gerçek telefon GPU/FPS ölçümü ayrıca yapılmalıdır. Penguen ve gergedanın önceki yerel düzeltmeleri korunur.

## Canlı sürüm · 15 Ekim 2026

Kullanıcının GitHub'a yükleme ve ardından canlıya alma talebiyle `20261015ai` sürümü GitHub Pages için hazırlandı. [3B atlas](https://ahmetguner74.github.io/bursa-hayvanat-bahcesi-3d/) · [Hareketli penguenler](https://ahmetguner74.github.io/bursa-hayvanat-bahcesi-3d/?focus=penguin-close&revision=20261015ai) · [V2 yollar ve kroki](https://ahmetguner74.github.io/bursa-hayvanat-bahcesi-3d/v2/).

`publish_local.py --local-only` ve `v2/build_local.py` yalnız yerel `dist/` çıktısını üretir. Açık yayın komutu `python build_public.py --publish`, doğrulanmış `dist/` içinden tarayıcı dosyalarını `docs/` altına kopyalar; GitHub Pages `main/docs` kullanır. `git push origin main` yayını tetikler. Araştırma fotoğraf arşivleri, özel DGN kaynakları ve Blender yedekleri siteye kopyalanmaz. Kaynak modellerin lisans ve atıfları kendi klasörlerinde; penguen atfı arayüzde ve `models/penguin-ATTRIBUTION.txt` içindedir. `docs/publication.json` yayın dosyalarının SHA-256 özetlerini kaydeder.

Aşağıdaki yerel çalışma notları önceki aşamaların kaydıdır; bu açık yayın talebi önceki canlıya almama sınırını bu sürüm için kaldırır. Beyaz gergedan ve 16 numaralı yaşam alanı sonraki modelleme çalışmasıdır.

**15 Ekim 2026 yerel çalışma:** Resmî krokinin 1–43 numaralı alanı [bölge kaynak envanterinde](bolgeler/README.md) ayrı klasörlere ayrıldı. #31/#32 kubbesi için yapımcı kaynaklarına dayanan ilk düzenlenebilir [glTF kabuk modeli](bolgeler/31-pelikan-goleti/model/README.md) üretildi. [Türk Köyü](bolgeler/30-turk-koyu/model/README.md), [Penguen havuzu](bolgeler/15-penguen/model/README.md) ve [Savanna ahşap yapı bileşeni](bolgeler/12-afrika-savana/model/README.md) ilk modelleri de eklendi. Görünüm menüsünde 43 alan listelenir; 42 alanın yaklaşık kroki konumuna gidilir, 40 numaralı alanın konumu teyitsizdir. Mockup hedefiyle karşılaştırılan 3B sahne ve [model incelemesi](http://127.0.0.1:8768/model-review/) yalnız `dist/` altında yerel olarak açılır. 3B sahnenin yol yüzeyleri, Dot'un manuel QGIS paketinden alınan `v2/manual-roads-metric.json` verisine geçti; 2016/2018 M5 çizgileri kaynak olarak saklanır. Aşağıdaki ilk araştırma ve eski M5 yol açıklamaları tarihsel aşama notlarıdır. `docs/` ve canlı yayın bu çalışma kapsamında değiştirilmez.

## Güncel ilerleme · 15 Ekim 2026

**Yerel geliştirme `20261015al`:** İki hareketli beyaz gergedan, kaynaklı kavisli barınak/yeşil çatı, kapılar, iç bölmeler, çevre duvarı/çit, toprak avlu ve çamur alanı eklendi. Penguen havuzu kenar/yol yüzey çakışması, yanlış kıyı yol taşları ve su altı kaya destekleri düzeltildi. [Gergedan](http://127.0.0.1:8768/?focus=rhino-close&revision=20261015al) · [Penguen havuzu](http://127.0.0.1:8768/?focus=penguin&perspective=65&revision=20261015al). Kullanıcı yeni açık talep gelmeden yayınlamamayı istedi; **`docs/` ve canlı Pages sürümü 20261015ai olarak kaldı.**

**Hareketli Afrika penguenleri, `20261015ai`:** 15 numaralı havuz/kıyıya üç kara ve iki yüzücü yorum bireyi eklendi. Gerçek iskelet animasyonları, farklı bekleme/tüy bakımı/yürüyüş/yüzme zamanları, sınır ve mesafe kontrolü vardır. Beş hayvan 20.620 üçgen; geometri/dokular ortaktır, görünmeyen iskeletler durur. Kaynak Major · CC BY4.0; özgün FBX/GLB, düzenlenebilir Blender ve doğrulama kayıtları [hayvan klasöründe](bolgeler/15-penguen/model/hayvan/README.md). [Yerelde izle](http://127.0.0.1:8768/?focus=penguin-close&revision=20261015ai) · [Animasyonları incele](http://127.0.0.1:8768/model-review/?model=penguin-animal&revision=20261015ai) · [Aynı Wi-Fi](http://192.168.0.192:8768/?focus=penguin-close&revision=20261015ai). İlk tarayıcı ölçümleri masaüstü60 Hz/mobil genişlikte30 Hz güncelleme; fiziksel telefon FPS ölçümü değildir.

**Orbit düzeltmesi, `20261015ag`:** Bütün atlas kameraları sabit M5 Z yukarı ekseni kullanır. Düz planda sürükleme kaydırır; eğik görünümde orbit yapar. Görünüm/projeksiyon değişiminde eski dönme ataleti temizlenir; sürükleme veya yakınlaştırma devam eden kamera geçişini keser. [Yerelde aç](http://127.0.0.1:8768/?focus=cage&perspective=65&revision=20261015ag) · [Aynı Wi-Fi'den aç](http://192.168.0.192:8768/?focus=cage&perspective=65&revision=20261015ag).

**2D bitki kararlılığı, `20261015af`:** Alçak bitkiler üç yerine iki çapraz kart kullanır. Altı yaprak kaynağının 512 piksel teknik türevleriyle hesaplanan temel RGBA belleği 37,74 MB'den 6,29 MB'ye iner. Hafif mip örneklemesi, ekranda 4–11 piksele düşen otların kademeli sönmesi ve küçük kartların ayrı gölge çizimlerinin kaldırılması titreşmeyi azaltır; ek çizim geçişi yoktur. Uzak CC0 atlasında yön/eğim toleransı vardır. [Yerelde aç](http://127.0.0.1:8768/?focus=cage&perspective=65&revision=20261015af) · [Telefonda aç](http://192.168.0.192:8768/?focus=cage&perspective=65&revision=20261015af).

3.312 yeni yorum kümesiyle toplam 10.034 alçak bitki, 599 çiçekli küme oldu. İki kart sayesinde toplam bitki geometrisi önceki 6.722 kümeli sürüme yakındır. Özgün üretilmiş raster sayısı 18; prompt/SHA/teknik türev kayıtları `viewer/assets/` altında. Genel mockup kabulü, fiziksel telefon FPS denetimi ve bütün 43 alan modelleri tamamlanmadı.

**Dokuzuncu model grubu, `20261015aa`:** [Boz Ayı havuzu ve kaya kıyısı](bolgeler/29-boz-ayi/model/README.md) eklendi. 488,40 m² özgün M5 gölet izi; 17 kaya üç düzensiz kümede, dokuz bitki kümesi ve yaklaşık beton kıyı. **10.278 üçgen / 1.513.188 bayt.** Kaya/kıyı ölçüleri 2018 resmî fotoğrafından yorumdur; 28/29 bölge kapsamı ve bugünkü durum teyitsiz. [Modeli incele](http://127.0.0.1:8768/model-review/?model=bear-pool) · [Atlasta aç](http://127.0.0.1:8768/?focus=region-29&perspective=65) · [Aynı Wi-Fi'den aç](http://192.168.0.192:8768/?focus=region-29&perspective=65). Ortak zemin kıyıdan ayrılır; tek gölet geometrisi renk özniteliği kullanır. Model incelemesinde Habeş ve Boz Ayı kadrajları başlık/alt bilgi alanlarının dışında kalacak şekilde ayarlanır.

**Önceki, sekizinci model grubu, `20261015y`:** [Habeş Maymunu Adası](bolgeler/09-habes-maymunu/model/README.md) eklendi. Ada ve su bandı ile iki aday ahşap platformun özgün M5 XY izleri korunur; direk/halat/kaya/oyuk gövde/merdiven 2021 resmî fotoğrafından yaklaşık yorumdur. **14.129 üçgen / 754.020 bayt.** Beton kıyı ortak zeminden ayrılır, ada tek toprak malzemesiyle çizilir. [Modeli incele](http://127.0.0.1:8768/model-review/?model=habes) · [Atlasta aç](http://127.0.0.1:8768/?focus=region-9&perspective=65).

**Son görünüm, `20261015x`:** Ağaç diplerinde yapraklı toprak, kıyıda nem ve yol kenarında ince renk geçişleri mevcut tek çim malzemesine eklendi; ikinci zemin mesh'i yok. [Malzeme veri kaydı](ground-material-layout.json) kaynak SHA'larını, 1024² sayısal karışım haritasını ve teknik JPEG türevlerini içerir. Yeni üretilmiş dokunun değişmemiş PNG'si ve son Image Gen promptu [varlık manifestinde](viewer/assets/asset-manifest.json); sahne 725.656 bayt JPEG türevini kullanır. Kıyı taşları mevcut üretilmiş kaya dokusundan 111.481 bayt teknik türev kullanır. Yeni sahne/uzak ağaç üretimi ortak [ışık ayarlarını](viewer/lighting.js) paylaşır; uzak atlas yeni ışıkla tekrar üretildi. İç gölette 112 taş ve 28 küçük bitki kümesi, altı önceki konik yorum ağacının yerine aynı konum/yükseklikte yapraklı taçlar var. Bunlar saha ölçümü değildir. [Güncel denemeyi aç](http://127.0.0.1:8768/?focus=cage&perspective=65&forest=2).

Hedef tamamlanmadı. Dokuz ilk model grubu yerelde incelenebilir: Su Kuşları Kubbesi, Türk Köyü, Penguen havuzu, Savanna ahşap yapı bileşeni, Lemur Adası, Afrika Köyü, [Afrika Kafe](bolgeler/13-afrika-kafe/model/README.md), [Habeş Maymunu Adası](bolgeler/09-habes-maymunu/model/README.md) ve [Boz Ayı havuz bileşeni](bolgeler/29-boz-ayi/model/README.md). Bunlar bütün bölgelerin tamamlanmış modelleri değildir; kaynak belirsizlikleri her modelde kayıtlıdır. 40 numaralı alan için kullanıcının işaretleyeceği kroki beklenir; diğer alanların çalışması buna bağlı değildir.

[Afrika Kafe'yi atlasta aç](http://127.0.0.1:8768/?focus=region-13&perspective=65) · [modeli yakından incele](http://127.0.0.1:8768/model-review/?model=african-cafe). Altı aday M5 izi, 40 dikme, 6.724 üçgen ve 899.196 bayt GLB. Çatı ve döşeme izdüşümleri kaynakla yaklaşık 0,000033 m² fark içinde; görünür zemin sahipliği bölündü ve eski 243 numaralı geçici bina kaldırıldı. Yükseklik, cephe ve güncel yapı aidiyeti saha ölçümüyle doğrulanmadı.

Atlas bölge modellerini kamera görünümüne göre, en çok iki eşzamanlı yüklemeyle getirir. Görünmeyen modeller için dört varlık / yaklaşık 96 MiB önbellek hedefi vardır; görünür varlıklar gerektiğinde bu sınırı aşabilir. Hata durumunda yeniden deneme sunulur. Gerçek telefon bellek/kare hızı ölçümü ve bütün bölgeler arasında uzun kullanım denetimi bekler.

**Aynı Wi-Fi'deki telefon:** [yerel atlas](http://192.168.0.192:8768/?focus=cage&perspective=65) · [Afrika Kafe](http://192.168.0.192:8768/?focus=region-13&perspective=65). Bu IP 15 Ekim'de tekrar doğrulandı; önceki `.11` adresi güncel değildir. Bilgisayar ve yerel sunucu açık olmalıdır. Canlı yayın yapılmadı; `docs/` değişmedi.

## Peyzaj ağacı · yerel deneme

Poly Haven CC0 kaynağından düzenlenebilir [ağaç varlığı](bolgeler/_ortak/peyzaj/model/pipeline.json) eklendi. Güncel yakın sürüm 122.245, alternatif uzak 3B sürüm 6.942 üçgen; GLB 12.206.208 bayt. Uzak silüet, aynı yakın GLB'nin Three.js ile alınmış 16 açılı görüntüsünden oluşur ve ağaç başına 2 üçgen kullanır; 2048² atlas 3.302.130 bayttır. Kaynak geometrisi ve yaprak rengi yakın/uzak için ortak, paketlenen karelerin gerçek piksel/SHA denetimleri kayıtlıdır. Blender kaynağı, üreticiler ve özgün URL/SHA bilgileri aynı klasördedir. Kaynak gerçek bir Bursa tür veya ağaç ölçüsü kaydı değildir.

[Ağaç denemesini atlas üzerinde aç](http://127.0.0.1:8768/?focus=cage&perspective=65&forest=2) · [düzenlenebilir modeli incele](http://127.0.0.1:8768/model-review/?model=forest) · [mockup ile karşılaştır](http://127.0.0.1:8768/design-reference/compare-local.html?forest=2). Varsayılan taç görünümü korunur; deneme henüz görsel kabul almadı. Aynı Wi-Fi bağlantısı: `http://192.168.0.192:8768/?focus=cage&perspective=65&forest=2`. Yerel IP 15 Ekim 2026'da doğrulandı; ağ değişirse değişebilir. Gerçek telefon kare hızı ölçülmedi.

## V2 · Yollar ve resmî kroki (yerel önizleme)

V2'nin ilk katmanı, rektifiye edilmiş Eylül 2026 ziyaretçi krokisinden çıkarılan **yaya yollarını** ve **ön araç/otopark yüzeyini** gösterir. Gerçek kroki katmanı açılıp kapatılır; saydamlığı %0–100 arasında ayarlanır. [V2 haritasını yerelde aç](http://127.0.0.1:8768/v2/). `python v2/build_local.py` yalnız `dist/v2/` klasörünü üretir; `docs/` veya canlı siteye yazmaz. Mevcut yerel sunucu açıksa sayfayı yenilemek yeterlidir; kapalıysa `BASLAT.cmd` hem V1 hem V2 önizlemesini hazırlar. Yöntem ve belirsizlikler [V2 notlarında](v2/README.md) kayıtlıdır.

14 Ekim 2026. Bu kayıt, kaynak araştırmasını ve ilk coğrafi yerleşimli 3B denemeyi belgeler. Sahne ölçülü DGN çizgileriyle kurulmuştur; henüz doğrulanmış aplikasyon veya güncel ortofoto eşleşmesi değildir.

**Güncel yerleşim dayanağı:** Belediye bağlantısıyla doğrulanan 2026 Bursa Zoo krokisi ve M5/DGN'nin birlikte kullanımı [CURRENT_PLAN.md](CURRENT_PLAN.md) içinde kayıtlıdır. Krokiden seçilen sekiz referans öğesi `current-plan-data.json` metre katmanına eşlendi; sahne bu katmanı M5 ile birlikte okur. Bundan sonraki yol, su ve yapı yerleşimi çalışmaları krokideki mevcut düzeni önceleyerek aşama aşama yürütülür; DGN metre ölçeği ve eski durum kanıtı olarak korunur.

**Model kalitesi:** [MODEL_QUALITY.md](MODEL_QUALITY.md), yapımcı ölçülerini ve Three.js/glTF kaynaklı geometri ilkelerini kaydeder. `build_surface_layers.py`, eski M5 yol halkasındaki geçersiz geometriyi onarır; su, bina, yol ve çim için çakışmasız üst yüz bölgelerini `surface-layers.json` dosyasına üretir. `build_building_shell.py`, iç içe geçen eski bina izlerini tekil çatı ve dış duvar yüzeylerine dönüştürür. `publish_local.py` yüzey, bölge varlıkları, bina kabuğu ve peyzaj üreticilerini yerel paketleme sırasında çalıştırır.

**Seçilen görsel yön:** [Orman içindeki kafes mockup'ı](design-reference/woodland-aviary-concept.png) kullanıcı tarafından beğenilen tasarım hedefidir. Yapay zekâ ile üretilmiş kavramsal görseldir; çalışan 3B atlasın ekran görüntüsü veya güncel yerleşimin ölçülü kanıtı değildir. [Referans notu](design-reference/README.md), sahneye aşama aşama aktarılacak özellikleri açıklar.

## Yer ve kapsam

- [Bursa Büyükşehir Belediyesi'nin Mayıs 2026 açıklaması](https://www.bursa.bel.tr/haber/bursa-hayvanat-bahcesine-bayramda-ziyaretci-akini-37224), Soğanlı'daki tesisin yaklaşık **206.000 m²** olduğunu ve 1998'den beri hizmet verdiğini bildirir.
- [Millî Eğitim Bakanlığı tanıtımı](https://okuldisiogrenme.eba.gov.tr/mekan-detay/bursa-hayvanat-bahcesi-720), adresi **1. Nilüfer Caddesi, Soğanlı, Osmangazi** olarak verir. İlk kurulan bölümleri Türk köyü, ayı-kurt, yırtıcı kuş, su kuşları, lama, yaban eşeği ve deve alanları olarak sayar; köy evi biçimindeki yapılardan da söz eder.
- [OpenStreetMap bahçe sınırı — way 26445905](https://www.openstreetmap.org/way/26445905) için [OSM API'den](https://api.openstreetmap.org/api/0.6/way/26445905/full) 14 Ekim 2026'da okunan yaklaşık zarf: **40.2175439–40.2213186 K, 29.0426188–29.050353 D**. Bu topluluk haritası sınırıdır; kadastro veya aplikasyon kontrolü değildir. OSM'de aynı zarfın taramasında iç yapı ayak izleri bulunmadı.
- `source-dgn/` içindeki **H22D01C2A, H22D01C2B, H22D01C2C ve H22D01C2D** DGN paftaları özgün `m5/1000` arşivinden değiştirilmeden kopyalandı; böylece bu proje tek klasörden yeniden üretilebilir. `source-ascii/` ara çıktıları ve `site-data.json` bu dört paftanın yol, havuz, yapı, sundurma, sınır ve ağaç katmanlarını OSM sınırına kırpar. DGN XY konumları metre biriminde korunur. SIMPLE_ASCII ara çıktısındaki öğe sıra numarası özgün DGN kimliği değildir.

## Model adayları ve kanıt düzeyi

| Öncelik | Öğe | Mevcut kanıt | Model öncesi açık iş |
| --- | --- | --- | --- |
| 1 | **Su Kuşları Kafesi / uzay kafesi** | Yapımcı [USKON'un proje kaydı](https://uskon.com/en/bursa-zoo-waterbird-cage-single-wall-elliptical-dome/) gerçek yapı için plan, görünüş ve fotoğrafları içerir: eliptik tabanlı yarım kubbe, **70 × 40 × 20 m**, çelik uzay kafes ve ağ örtüsü. [Şekil 5](https://uskon.com/wp-content/uploads/2021/07/SEKIL5.jpg) ölçüleri; [Şekil 12](https://uskon.com/wp-content/uploads/2021/07/SEKIL12.jpg) iç görünüşü gösterir. | Güncel hava fotoğrafıyla kesin oturum, yön ve zemin kotunu bağlamak; 1998 görüntüsündeki iç peyzajı güncel saymamak. |
| 2 | **Türk Köyü yapı grubu** | [MEB](https://okuldisiogrenme.eba.gov.tr/mekan-detay/bursa-hayvanat-bahcesi-720) köy evi olarak düzenlenmiş binaları doğrular. [Ziyaretçi krokisi](https://karesiturizm.com/images/tour/2809_b.jpg) grubun yerini şematik gösterir. | Her evi ayrı teşhis eden güncel, çok açılı cephe fotoğrafları ve DGN/hava görüntüsünde ayak izleri. Komşu Botanik Park veya Aktopraklık fotoğraflarıyla karıştırılmamalı. |
| 3 | **Afrika Kafe ve Afrika Köyü** | [Belediyenin 2010 proje gerçekleşme belgesi](https://www.bursa.bel.tr/dosyalar/birimek/faaliyet-ve-proje-bilgileri.faaliyet-ve-proje.LBHrSHmzhz.pdf) Afrika Savana Kafeteryası inşasını kaydeder; [ziyaretçi krokisi](https://karesiturizm.com/images/tour/2809_b.jpg) Afrika Kafe ve Köyü işaretler. | Güncel işletme/yapı durumu, cephe ve çatı fotoğrafları, ayrı yapıların oturumu. |
| 4 | **Giriş–idari bina ve giriş göleti** | [Ziyaretçi krokisinde](https://karesiturizm.com/images/tour/2809_b.jpg) giriş, idari bina ve giriş göleti adlandırılmıştır. | Kapı ve bina için güncel cephe fotoğrafları, ölçü ve konum. |

Kroki, [Karesi Turizm'in sayfasında](https://www.karesiturizm.com/tur-659-bursa-extrempark---misi-koyu---hayvanat-bahcesi-turu) yayımlanan **ziyaretçi yön bulma görselidir**; çizimde ölçek, koordinat ve tarih bulunmadığı için geometri çıkarmaya elverişli değildir. USKON'un [genel yerleşim görseli](https://uskon.com/wp-content/uploads/2021/07/SEKIL4.jpg) Su Kuşları Kafesi çevresinde ikinci bir tarihî plan sağlar, ancak güncel yapı yerleşimini tek başına doğrulamaz.

## Fotoğraf ve kullanım notu

Yapımcı çizimleri ve haber/ziyaretçi görselleri **geometriyi incelemek için kaynak** olarak bağlantıyla tutulur; lisansları doğrulanmadan görüntülerin model dokusuna veya halka açık pakete kopyalanması planlanmaz. [Wikimedia Commons Bursa Zoo kategorisindeki](https://commons.wikimedia.org/wiki/Category:Bursa_Zoo) dört yer fotoğrafı yaklaşık 2010 çekimlidir ve çoğunlukla hayvanları gösterir; yapıların güncel cephesini kanıtlamaz. Her üretilen öğede önceki Bursa bina çalışmalarındaki gibi kaynak URL'si, yıl, kullanılan ayrıntı ve belirsizlik ayrı kayda geçmelidir.

İlk kafes revizyonunda [USKON dış ve iç fotoğrafları](https://uskon.com/en/bursa-zoo-waterbird-cage-single-wall-elliptical-dome/), [GeziBilen giriş görüntüsü](https://gezibilen.com/de/travelpoint/bursa/bursa-hayvanat-bahcesi) ve [Trend İnşaat havadan görünümü](https://www.trendinsaat.com.tr/tr/projeler/kent-parklari) ayrı açılardan incelendi. Metalin açık tonu, iki uçtaki beşik çatılı geçit, iç ahşap yapı ve yoğun çevre bitkisi bu kaynaklardaki görsel karakteri izler. Önce kafese bağlanan iki M5 su kenarı, güncel kroki karşılaştırmasında **Alligatör alanı göletine** karşılık geldi; kafes iç göletinin kıyısı ölçülü değildir. Köprü, iç yol, kıyı ve çalıların tekil yerleri görsel yorumdur. St. Louis Zoo ekran görüntüleri yalnızca düşük ayrıntılı 3B renk ve sahne dili için esindir; Bursa geometrisinin kaynağı değildir.

## Üretime geçiş sırası

1. `viewer/` içinde bütün alanın etkileşimli ilk sahnesi ve **70 × 40 × 20 m** Su Kuşları Kafesi yorumu üretildi. `publish_local.py` bağımsız `dist/` önizlemesini oluşturur; başka bir Bursa projesine bağlı değildir. Giriş ve iç mekân için yaklaşık göz hizası, telefonda dikey genel plan, tam ekran seçimi ve genel planda ayarlanabilir perspektif vardır. Kaynak fişi geliştirme klasöründe tutulur.
2. Kafesin merkez ve yönü, Eylül 2026 krokisiyle eşlenen M5 eliptik tel çit yayına göre yaklaşık **[-30,-64] m ve +9°** olarak düzeltildi. Kroki-M5 eşlemesinin genel hatası yaklaşık 11 m'dir; oturum güncel ortofoto veya saha ölçüsüyle kesinleştirilmelidir. Krokide kubbe **#31 Pelikan Göleti**, hemen güneyindeki ayrı alan **#32 Su Kuşları** ile işaretli olduğundan bu iki adın fiziksel kapsamı da doğrulanacaktır. Çelik modüllerin tekil birleşimleri, ağ deseni, iç gezi yolu, köprü, iç gölet kıyısı, ahşap yapının boyutları ve zemin yüksekliği yaklaşık görselleştirmedir. Ana 70 × 40 × 20 m kabuk korunur; küçük çevre parçalarında görsel his için dar kapsamlı ölçü esnekliği vardır.
3. Yolların çizgi konumları DGN'den gelir; görünen taş dokulu, alçak yüzeyler yol kenarı çizgilerinin **3 m tamponlanmış görsel önizlemesidir**, ölçülü kaplama genişliği değildir. Kaplamanın yan yüzü sınırlı bir yükseklik etkisi verir. Güncel krokiden yaklaşık **#5 Giriş Göleti** eklendi; iki büyük gölette M5 iç halkaları ada olarak düzeltildi. Ham bordür/yol/çit/duvar/su çizgileri ve sundurma kayıtları veride korunur, sahnede ayrı çizgi veya düz sundurma levhası olarak gösterilmez. Diğer binalar yalnızca kaynak ayak izi üzerinden üretilmiş geçici kütlelerdir; cephe ve yükseklikleri kabul edilmiş ölçü değildir.
4. Türk Köyü, Afrika Kafe, giriş ve diğer yaşam alanlarının her birinde önce 2026 krokisindeki güncel yerleşim, sonra uyumlu DGN ayak izi, çok açılı fotoğraf ve mümkünse saha ölçüsü karşılaştırılacak; ardından aynı metre koordinatı, kaynak kaydı ve belirsizlik sınıflarıyla ayrıntı modeli eklenecek.

## Bağımsız yerel önizleme

Yerel üretim için Python, `requirements.txt` içindeki kütüphaneler ve bina geometrisi doğrulamasında kullanılan Node.js gerekir. Proje klasöründe önce `python -m pip install -r requirements.txt`, sonra yalnız yerel paket için `python publish_local.py --local-only` çalıştırın. Ardından `python -m http.server 8768 --bind 0.0.0.0 --directory dist` komutuyla önizlemeyi açın. Aynı işi Windows'ta `BASLAT.cmd` başlatır. Bilgisayarda `http://127.0.0.1:8768/?focus=site&overlay=1`; aynı yerel ağdaki telefonda bilgisayarın IP adresiyle `http://<bilgisayar-IP>:8768/?focus=site&overlay=1` kullanılır. Görünüm menüsündeki **Ziyaretçi krokisi** düğmesi katmanı açar/kapatır; **Kroki opaklığı** %0–100 arasında ayarlanır. Katman, Eylül 2026 resmî görselinin değişmemiş yerel kopyasını `dist/reference-maps/2026-09-resmi-kroki.jpg` üzerinden yükler; bu katmanı görmek için internet gerekmez. Özgün resmî kaynak bağlantısı korunur. Eşleme şematik krokiden üretildiği için yaklaşık 10–25 m belirsizlik taşır. Araştırma fotoğrafları, DGN/ASCII kaynakları ve özel kroki arşivi klasör olarak `dist/` veya `docs/` içine kopyalanmaz. Yalnız yukarıda belirtilen Eylül kroki görseli yerel `dist/` paketine eklenir.

## GitHub Pages yayını

[Canlı 3B atlası aç](https://ahmetguner74.github.io/bursa-hayvanat-bahcesi-3d/?focus=cage).

`python publish_local.py` ve `--local-only` seçeneği yalnız yerel `dist/` paketini üretir. Açık yayın isteği sonrasında `python build_public.py --publish`, izin listesiyle `docs/` paketini hazırlar; commit/push yapmaz. GitHub Pages kaynağı `main:/docs` klasörüdür. Özgün DGN paftaları, ara ASCII dosyaları ve özel referans fotoğrafları GitHub deposuna dahil edilmez. Uygulama ekranlarından oluşan tasarım denetim kanıtları geliştirme dosyaları arasındadır.

Canlı arayüz tek bir sahnedir: yaşam alanı etiketine ve ardından hayvanın gövdesine dokunulur. Bireye tekrar dokunmak türe uygun davranış ister. Geri dönüş ve tam ekran dışında hareket düğmesi veya iç içe menü yoktur. V2 yol/kroki çalışma aracı ayrı `v2/` adresinde korunur. Model kaynakları ve lisanslar kimlik işaretinden açılır.

## Su ve yol görünümü — yerel ara sürüm

Altıncı bölge varlığı [Afrika Köyü](bolgeler/14-afrika-koyu/model/README.md): yedi özgün M5 dairesel saçak izi, tarihî fotoğrafa göre yaklaşık duvar/kapı/kademeli çatı. [Yerel model incelemesi](http://127.0.0.1:8768/model-review/?model=african-village). Yorumlanan taban, yol/çim yüzeyinden ayrılır ve küçük avlu bağlantısı korunur.16 ek2018 galeri fotoğrafı ve bir2012 rapor fotoğrafı ilgili kaynak klasörlerine işlendi. Bütün1–43 model ve mockup kabulü tamamlanmadı; `design-qa.md` güncel eksikleri kaydeder.

Beşinci bölge varlığı Lemur Adası'dır: [kaynak ve düzenlenebilir model](bolgeler/11-lemur/model/README.md), [yerel inceleme](http://127.0.0.1:8768/model-review/?model=lemur). Ada/hendek M5 izi korunur; kaya, dal ve düşük güvenli halat yerleşimi kamera yorumudur. Yeni palmiye, ot ve oval yapraklı çalı varlıklarıyla bitki çeşitliliği/yoğunluğu artırıldı; bütün1–43 model kapsamı ve mockup görsel kabulü hâlâ tamamlanmadı. Biçim denetimi `node bolgeler/validate_models.cjs`, kaynak/geometri denetimi `python bolgeler/verify_inventory.py`; kurulum ayrıntıları `MODEL_QUALITY.md` içinde.

Temas gölgeleri, ortak gölet yansıması, küçük taş yüzey kabartması ve yakın yol taşı LOD'si eklendi. Zemin/su/yapı/yol üst yüz sahipliği korunur. Kroki artık yerel kopyadan yüklenir. Dört belediye kamera karesi (Habeş, Lemur, Savanna, Gergedan) ve Afrika Kafe'nin dokuz küçük tarihî fotoğrafı kaynak klasörlerine eklendi. Çekim tarihleri ve görüntülerin güncel saha durumunu temsil ettiği teyit edilmedi; lemur karesinden ada/kaya/tırmanma modelinin ilk yorumu üretildi. Mockup görsel kabulü henüz geçmedi.
