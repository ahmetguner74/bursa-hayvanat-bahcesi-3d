# 3B model kalite ilkeleri ve kaynak dayanakları

## Hareketli Afrika pengueni — on dördüncü yineleme

`20261015ai`: [Kaynak, üretim ve doğrulama](bolgeler/15-penguen/model/hayvan/README.md). Major'ın CC BY4.0 GLB/FBX kaynağı değişmeden arşivli; teslimde0,62 m yorum boyu ve daha yumuşak normal malzemesi var. Geometri, etkin skin ağırlıkları, anahtar kareler ve PNG pikselleri korunur. Kaynak dönüştürmesinin animasyon `byteStride`, sıfır ağırlık indisi ve skinned düğüm hiyerarşisi sorunları giderildi; Khronos0 hata/0 uyarı.

Üç kara,iki yüzücü yorum bireyi; toplam20.620 üçgen,tek ortak geometri/doku seti ve beş bağımsız 64 eklemli iskelet. Normalde hazır sekiz klipten beşi davranışta kullanılır; ayrı incelemede sekizi de seçilebilir.0,55 s karışım, kademeli hız/dönüş, farklı dinlenme zamanları, sınır/mesafe kontrolü vardır. Tüy kenarı zemin referansı değildir; gövde mesh'i tablosu ayakların havada kalmasını giderir. Su–kara geçişi ilk kapsamda yok; dik bordürden geçiş uydurulmaz.

600 s / 90.000 davranış örneği, bağımsız iskelet/paylaşılan kaynak, gerçek kliplerin skinned zemin geometrisi ve çalışma modülündeki görüş dışı/gizli sekme/toggle/yeniden görünme testleri geçti. İlk masaüstü1280×720 örneği60,04 Hz,p95 güncelleme aralığı16,8 ms, ortalama animasyonCPU0,191 ms;390×844 aynı bilgisayar örneği30,02 Hz/33,4 ms/0,185 ms. Bunlar fiziksel telefon veya GPU zamanlaması değildir. Yakın60/30 Hz, uzak12 Hz hedefi; görünmeyen iskelet hesabı durur, ek render geçişi yok. Genel mockup/43 alan kabulü sürer.

## Orbit kararlılığı — on üçüncü yineleme

`20261015ag`: `camera.up` bütün kamera ve projeksiyonlarda sabit Z'dir. Önceki düz plan yatay up vektörü ile OrbitControls'un kurucuda sakladığı Z ekseni farklıydı; düz plandan orbit hareketine geçince yana yatma oluşuyordu. Mobil genel plandaki farklı up vektörü kaldırıldı. Düz plan çok küçük, 0,0001 radyan eğimle yönünü korur, sol fare/tek parmak kaydırır; eğik görünüm dünya Z etrafında döner. Öteleme XY düzlemindedir. Kamera/projeksiyon değişiminde yeni denetim örneği eski ataleti ve dinleyicileri temizler; kullanıcı etkileşimi geçiş animasyonunu keser. Vendor dosyası değişmez, yeni çizim geçişi veya geometri eklenmez.

`node bolgeler/_qa/verify_atlas_orbit.mjs` gerçek r186 OrbitControls ve gerçek `atlas-orbit.js` yardımcısını çalıştırır. Eski hatada kamera sağ ekseni |Z|=0,280599; perspektif, düz plan ve göz hizası için 480 dönüş örneğinde yeni en yüksek |Z|=2,78×10⁻¹⁶. Yeniden bağlamadan sonraki 160 adımda en büyük konum kayması 9,10×10⁻¹² m. Bu hesap kamera roll ve eski ataleti denetler; fiziksel telefon FPS ölçümü değildir. [Three.js OrbitControls belgesi](https://threejs.org/docs/pages/OrbitControls.html).

## 2D bitki kararlılığı — on ikinci yineleme

Asıl geometri hatası: XYZ Euler sırası düşük bitki kartlarını aynı dikey düzlemde bırakıyordu; farklı yaw değerleri görüntüyü o düzlem içinde döndürüyordu. `plant-cards.js` ZYX sırasıyla kartları gerçekten dik açıya getirir ve tabanları dik tutar. Gerçek yardımcı işlevin yedi varyantında eski normal iç çarpımı≈1, yeni iç çarpım≤3,89×10⁻¹⁶ ve yukarı vektörü Z≈1. `node bolgeler/_qa/verify_plant_cards.mjs` bu geometri koşulunu doğrular.

`20261015af`: Alçak bitki başına üç yerine iki çapraz kart, bu geometrilerde %33 azalma. Altı 512² RGBA teknik türev 1.355.487 bayt ağ dosyası ve 6.291.456 bayt temel çözümlenmiş RGBA'dır; önceki temel RGBA 37.740.384 bayttır. Bütün GPU belleği veya FPS ölçümü değildir. Özgün PNG'ler ve kaynak/türev SHA'ları korunur; türevler envanter doğrulamasına eklendi.

[Three.js Texture belgesi](https://threejs.org/docs/pages/Texture.html) mip filtreleri ve anizotropinin maliyetini, [Material belgesi](https://threejs.org/docs/pages/Material.html) alfa kesimi ve MSAA kapsamını açıklar. Mevcut trilinear mipmaps ve alpha-to-coverage ile +0,65 mip bias kullanılır. Alçak otlar gerçek projeksiyon/kart yüksekliğiyle 4–11 CSS piksel aralığında kademeli söner. Ayrı küçük ot gölge çizimleri kaldırıldı; mevcut AO görünür derinlikten temas gölgesini hesaplar. Ek render geçişi veya yüksek çözünürlükte yeniden örnekleme yoktur. Uzak CC0 ağaç atlasının yön/eğim eşiklerinde tolerans vardır; yakın/uzak tint aynı kayıttan gelir.

Kafes çevresine 3.312 yorum kümesi eklendi: toplam 10.034, bunların 599'u çiçekli. İki kartlı toplam 40.136 üçgen, önceki 6.722×6=40.332 üçgene yakındır. Yeni çiçekli varlık son prompt/değişmemiş PNG/SHA ile arşivli; 298.654 bayt teknik türevi kullanılır. Gerçek botanik envanteri değildir. İkinci CC0 taç kaynağı [Tree Small 02](https://polyhaven.com/a/tree_small_02) için 11 dosya, 84.114.593 bayt, MD5/SHA ile arşivlendi; henüz çalışan sahnede kullanılmaz. Genel mockup kabulü ve bütün bölge modelleri bekler.

## Boz Ayı havuzu — on birinci yineleme

[Kaynak ve düzenlenebilir üretim](bolgeler/29-boz-ayi/model/README.md). M5 gölet 278'in özgün XY izi korunur, 488,3991195 m². Eski resmî fotoğraflardaki kaya/beton/yeşil zemin karakteri yorumlanır; kesin 28/29 bölge kapsamı veya güncel barınak sınırı kanıtlanmadı. Kıyı genişliği/kot, derinlik, 17 kayanın üç düzensiz kümesi ve dokuz bitki kümesi sunum tahminidir. Fotoğraflar GLB dokusuna kopyalanmadı.

Gerçek GLB 10.278 üçgen / 1.513.188 bayt; altı kapalı hacim parçası ve standart açık su/bitki yüzeyleri. Kapalı parçalar sonlu, doğru yönlü, pozitif hacimli; sıfır alanlı veya yinelenen üçgen yok. Khronos hata/uyarı/bilgi/ipucu 0. Su/yatak izdüşüm farkı 0,0000197198 m², kıyı 0,0000337439 m². 41,897033 m² kıyı ortak zeminden ayrılır; su/yol/arazi örtüşmesi sıfır. Preview zemininin sıfıra yakın bir şeridi normalize edilir; yalnız bu türetilmiş bağlamın alan farkı 0,0000574641 m² ve çöken şeridin uzanımı 0,40 m, native veriler değişmez.

Ana sahnede modelin zemin/yatak/su düğümleri gizlenir. Ortak 12 gölet tek mesh ve tek yansıma geçişidir; ayı havuzunun örnek rengi köşe özniteliğiyle atanır. Düz plan malzemesi de aynı özniteliği kullanır. Genel kıyı taş/bitki yorumları bu havuzda üretilmez; ek orman gövdeleri yeni kayalara çarpmaz. Kaynak M5 ağaç noktaları korunur. Doğrulayıcı artık gerçek dosya listesinden on bölgesel GLB varyantı sayar; CC 0 ağaç ayrı varlıktır. Toplam 11 GLB biçim raporunun hata/uyarı sayısı 0; eski bilgi/ipuçları devam eder.

`20261015aa` yerel sürümde model masaüstü ve 390×844 eğik/üst görüntülerinde incelendi. Başlık ve alt bilgi nedeniyle kapanan düz model ayrıntıları için güvenli görünür alan hesabı eklendi; aynı hesap Habeş incelemesine de uygulanır. Fiziksel telefon kare hızı/belleği ve bütün 1–43 kapsamı bekler; mockup görsel kabulü henüz geçmedi.

## Habeş Maymunu Adası — onuncu yineleme

[Kaynaklar, düzenlenebilir girdiler ve üretim adımları](bolgeler/09-habes-maymunu/model/README.md). M5 ada57 / dış su58 ve aday sundurma149/150 izleri korunur. 2021 resmî fotoğrafındaki kaya, direk, halat, platform ve oyuk gövde karakteri yaklaşık yorumdur; kesin konum/yükseklik veya güncel durum teyidi değildir. Su katmanındaki açık641/642 çizgileri kaynağa aynen alınır, kapatılıp uydurma havuz yapılmaz.

GLB14.129 üçgen /754.020 bayt. Gerçek dosyadan yeniden yüklenen dokuz kapalı hacim sonlu, yönleri tutarlı, pozitif hacimli; önizleme suyu açık düzlemdir. Toprak/kıyı/su izdüşümü farkları sırasıyla0,0000335275 /0,0000793075 /0,0001074961m²; iki platformun farkı0,0000025501 /0,0000037065m². Khronos hata/uyarı/bilgi/ipucu0. Format/kapalı hacim denetimi saha veya görsel kalite sertifikası değildir.

37,425507m² yorum beton kıyı ortak zemin bölümünden çıkarılır; kalan1.294,172437m² ada tek toprak bölgesidir. Önizleme zemin/su/yatak düğümleri atlasta gizlenir. Ek peyzaj adanın dışında tutulur; bir eski M5 ağaç sembolünün temsili ağacı bu açık ada görünümünde gizlenir, kaynak noktası değişmez. Dört512² JPEG mevcut üretilmiş albedoların kaynak SHA kayıtlı teknik türevleridir; kaynak saha fotoğrafı dokuya yapıştırılmadı.

Gerçek model noktalarıyla sıkılaştırılmış masaüstü ve mobil kadraj vardır; kapalı geometri, iki platform üst izi, kıyı sahipliği ve bütün kaynak/türev SHA denetimi `verify_habes.py` içindedir. Yeni ada ayrımı sonrası ek peyzaj472ağaç /6727alçak bitki /573kıyı taşı /169kıyı bitkisi; ortak zemin ağırlığı697ağaç yaması oldu. Önceki yineleme sayıları tarihçedir.

## Zemin, ortak ışık ve iç kıyı — dokuzuncu yineleme

`build_ground_material.py` özgün M5/QGIS ve türetilmiş yüzey/peyzaj verisini salt okuyarak sayısal malzeme ağırlıkları üretir. 1024² RGB haritada R mevcut ağaçların çevresindeki yorum yaprak dökümü, G su sınırından 2,8 m sönüm, B yol sınırından 1,45 m sönümdür. Yaklaşık piksel boyutu 0,645×0,413 m; ağaç yaması sayısı 699. Bunlar malzeme sunum ağırlıklarıdır, toprak veya ağaç türü envanteri değildir. Harita `NoColorSpace` verisi olarak okunur. Dünya XY koordinatlarıyla mevcut tek çim malzemesinde örneklenir; ikinci yüzey/decal/çim kapağı eklenmez ve kaynak yol/su poligonları değişmez.

Üretilen `woodland-leaf-litter-v1.png` değişmeden korunur; tam son araç promptu/SHA manifestte. 1024² RGB JPEG türevi 725.656 bayt, 512² kaya albedosu türevi 111.481 bayt. İkisi yalnız boyut/kodlama dönüşümüdür; kaynak kaydı `ground-material-layout.json`. Kaya görüntüsü mevcut üretilmiş yapay kaya albedosunun görsel yeniden kullanımıdır; gerçek doğal kaya taraması diye sunulmaz. Yeni albedodan normal/yükseklik haritası çıkarılmadı. Dört kenarda tam dikişsiz devamlılık kanıtlanmadı. 17 AI raster varlığı CC0 ağaç kaynağından ayrı sayılır.

`viewer/lighting.js` ana sahne ve uzak ağaç üreticisinin ortak ayarlarıdır. Daha sıcak ışık, PCF gölge yoğunluğu 0,78 ve yarıçap 2,25 kullanılır. Bunlar seçilmiş sunum ayarlarıdır; ölçülmüş güneş/ışık değildir. [Three.js LightShadow belgesi](https://threejs.org/docs/pages/LightShadow.html) yoğunluk aralığı ve gölge yarıçapının kenara etkisini açıklar; yüksek yarıçapların bant oluşturabileceği için gerçek görüntü kontrol edilir. Aynı yakın GLB yeni ışıkla 16 açıdan tekrar üretildi. Uzak atlas 3.302.130 bayt; veri kaydı, piksel eşitliği ve kaynak SHA kontrolü geçti. Canlı ağaç yükleyicisi ışık metadata'sı ortak ayarla eşleşmezse denemeyi yüklemez ve mevcut ağaçları korur. Bu, bütün döndürülmüş örneklerde birebir aydınlık garantisi değildir.

İç gölette 112 kıyı taşı 320 üçgenli paylaşılan, hafifçe düzensiz hacimden örneklenir; 28 ot/eğrelti/çalı kümesi mevcut alfa varlıklarını kullanır. Her bitki adayının merkez ve dört çevre noktası kuru araziyle sınanır; bu örnekleme sürekli bütün ayak izinin kesin kesişim testi değildir. Altı önceki basit konik ağaç aynı konum ve yüksekliklerde yapraklı küçük ağaç yorumuna geçti. Gölet sınırı, köprü/portal geometri ve kafesin yakın/uzak ortak metal rengi değiştirilmedi. Genel ışık/bitki çeşitliliği hâlâ mockup kabulü almadı.

## Afrika Kafe — sekizinci yerel yineleme

[Model, girdiler ve yeniden üretim](bolgeler/13-afrika-kafe/model/README.md). Altı özgün M5 yapı/sundurma izi (152–156, 243) korunur. 2011 açılış fotoğraflarından yorumlanan kırma çatı bölümleri, ahşap cephe ve açık kameriyeler vardır. Kesin aidiyet, güncel durum, bütün yükseklikler ve açıklık konumları teyitsizdir. Fotoğraflar dokuya kopyalanmadı; üç mevcut üretilmiş dokunun SHA kayıtlı teknik JPEG türevi kullanılır.

6 çatı, 40 dikme, 21 kapalı geometri parçası; 6.724 üçgen / 899.196 bayt GLB. Gerçek dışa aktarılan çatı izdüşümü farkı 0,0000330576 m², döşeme farkı 0,0000329234 m². 570,101484 m² taban yol/çimden ayrılır; yalnız köşede birleşen döşemeler ayrı kapalı parçalar olarak korunur. Duvar açıklıkları gerçek kesimdir; çatıda yinelenen iç kapak yüzleri bulunmaz. Eski 243 numaralı geçici kütle kaldırıldı. Khronos denetimi hata/uyarı/bilgi/ipucu 0; bu saha doğruluğu sertifikası değildir.

On GLB'nin son biçim denetimi hata 0 / uyarı 0; eski dosyaların bazı bilgi/ipucu kayıtları devam eder. Envanter doğrulaması dokuz bölgesel GLB varyantını ve ortak ağaç varlığını ayrı sayar. Özgün M5 ve QGIS dosyalarının SHA'ları korunur.

## Peyzaj ağacı — güncel yerel deneme

[Üretim ve kaynak kaydı](bolgeler/_ortak/peyzaj/model/pipeline.json). Poly Haven Jacaranda CC0 kaynağının 180,23MB özgün Blender dosyası ve 10 doku dosyası URL/MD5/SHA ile doğrulandı; asıllar yerel araştırma klasöründe korunur. Önizleme render'ı siteden kopyalanmadı. Özgün model yerel Blender 5.2.1 LTS'de otomatik kaynak betikleri kapalı açıldı; yalnız bizim üreticilerimiz çalıştırıldı.

Beş yaprak prototipinin her ayrı yaprak yüzeyi UV sınırında hafifletildi; karışık kabuk UV'si yaprak kartına katılmadı. Kaynak radius özniteliğiyle çok ince dal budaması, yalnız ahşapta sadeleştirme, gerçek alfa kesimi, OpenGL normal haritaları ve tangent öznitelikleri var. Kaynağın uç dal yaprak aşaması da alınır; ikinci gövde kopyası kaldırıldı. Bir dejenere UV kutbuna normalle dik birim tangent yedeği gerekti; gerçek GLB Khronos denetiminde hata 0/uyarı 0/bilgi 0/ipucu 0. Yakın 122.245, uzak 3B 6.942 üçgen; GLB 12.206.208 bayt. Bu biçim denetimi bitki kabuğunu kapalı CAD veya saha doğruluğu olarak sertifikalandırmaz.

`tree-shape.json` yüksek gövde ve sıkışık taç oranını sanatsal yorum olarak ayrı kaydeder. Güncel uzak atlas aynı yakın GLB'den Three.js r186 ile, sahnenin ışıkları altında üretildi: 16 adet 512² kare, 2048² atlas, 3.302.130 bayt. Renk lineer ışık hesabından sRGB PNG'ye kodlanır; ACES sahnede bir kez uygulanır. PNG'nin gerçek kodlanmış bayt SHA'sı, kaynak GLB SHA'sı ve yeniden çözülen karelerin piksel eşitliği denetlenir. Canvas RGBA okumasının PNG kodlayıcı yuvarlamasıyla birebir aynı olduğu iddia edilmez. Cycles yalnız açık seçilen yedek üretim yoludur. Yakında alfa kesimi 0,1 ve alpha-to-coverage; atlas üretiminde 2× örnekleme kullanılır. Yakın ve uzak ağaç aynı anda çizilmez; yedek taçlar yalnız yeni model tamamen hazır olduğunda gizlenir. Palmiye, küçük giriş bitkileri ve kafes içi ağaçlar bu denemede korunur. Aynı ağaç noktaları ve yükseklik parametreleri kullanılır; eski r küme-yerleşim parametresi olduğu için önceki görünür taç genişliği 1,6r ile korunur. Bu gerçek ölçülmüş taç yarıçapı değildir.

## Bölgesel yükleme

`viewer/region-models.js` gerçek model sınırları ve kamera kesişimine göre ayrıntıları yükler; seçili bölge önceliklidir. En çok iki eşzamanlı aktarım, görünmeyenler için dört varlık / yaklaşık 96 MiB önbellek hedefi ve gerçek GPU kaynaklarını serbest bırakma vardır. Görünür varlıklar yumuşak sınırı aşabilir. Hata durumu kamerayı engellemez; bölge menüsünde yeniden deneme sunulur. Fiziksel telefon performansı ve tüm alanlar arasında uzun kullanım doğrulaması henüz tamamlanmadı.

`forest=2` uzakta ağaç başına 2 üçgenlik açı seçilen silüet kullanır; yakında düzenlenebilir 3B geometriye geçer. Sınırlı paralaks, önceden render edilmiş ışık, açı/LOD geçişi ve yakın–uzak taç farkı hâlâ görsel kabul konusudur. `forest=1` alternatif uzak 3B denemesidir. Varsayılan atlas değişmedi. 17 AI raster varlığına bu CC0 kaynak seti eklenerek tek lisans/sayı altında sunulmaz.


## Afrika Köyü — altıncı yerel yineleme

[Düzenlenebilir model ve kaynak sınırları](bolgeler/14-afrika-koyu/model/README.md). Yedi M5 saçak izi özgün XY noktalarını korur; sekizgen duvar, kapı ve yükseklikler2012 belediye fotoğrafının yorumudur. Eski kaynak güncel ölçüm olarak sunulmaz. Yeniden yüklenen GLB kapalı hacimleri ve kaynak izdüşümleri denetlendi; yedi çatı toplam simetrik fark0,0000683835m². Khronos biçim raporunda hata0/uyarı0/ipucu0 ve bir NPOT görsel bilgi kaydı var. Biçim denetimi gerçek saha doğruluğu değildir.

Yorumlanan363,730171m² taban ortak bina maskesinde yol/çimi ayırır. Fotoğrafı bilinmeyen kapı/yükseklik/kademe kararları girdide ayrı; kaynakH yalnız metadata. Kapı açıklıkları kesilmiş, her çatı tek kapalı kademeli hacim, duvarlar tek döşemenin üstünde başlar. Yedi çatı bir üretilmiş şingıl dokusunu paylaşır; özgün fotoğraf malzeme olarak kopyalanmaz.

Yeni tabanın ayırdığı avlu için0,24695m² ek görsel yol bağlantısı var. Bu, kaynak QGIS verisini değiştirmez; yeni yerel yorumdur. Kaynak veri/alan ayrımı ve bütün yüzeylerin sıfır boşluk/örtüşme denetimi korunur. Yeni yedi çatı fotoğraftaki kesin ölçü veya güncel yapım ayrıntısı sayılmaz.

## Lemur Adası ve bitki varlıkları — beşinci yerel yineleme

`bolgeler/11-lemur/model/` içindeki ilk ada bileşeni M5 ada60 ve hendek61'in özgün XY izlerini korur. Kamera karesi kaya/dal/ahşap karakterini gösterir; kesin yerleşim ve ölçü sağlamaz. Komşu yeşil bina atanmaz. Kaynak fotoğraf SHA'sı üreticide denetlenir; çekim tarihi teyitsiz. GLB kapalı hacimleri yeniden yüklenip kontrol edilir; ada izdüşümü kaynakla0,0000212965m² fark, su/adada alan örtüşmesi<0,0001m². Ana atlas önizleme çim/su/taban düğümlerini gizler; tekil bölüm bunları çizer. Kabuk UV yönü her dalın eksenini izler.

[Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator) format/buffer/görsel denetiminde kullanılır. `node bolgeler/validate_models.cjs` güncel on bir GLB için ayrı JSON raporu ve gerçek varlık SHA'sı üretir. Kurulum: `npm install --prefix bolgeler/_qa/gltf-check --ignore-scripts --no-audit --no-fund gltf-validator@2.0.0-dev.3.10`. Sonuçlar hata0/uyarı0; Lemur3 NPOT bilgisi, ipucu0. İlk üç varlıkta eksik buffer target ipuçları kalıyor. Biçim doğrulaması, saha doğruluğu veya görsel kabul anlamına gelmez. Ardından `python bolgeler/verify_inventory.py` kaynak özetlerini ve gerçekten dışa aktarılan yüzey/kapalı hacimleri denetler.

Üç yeni değişmemiş alfa PNG ve seçilen son promptları `viewer/assets/asset-manifest.json` içinde. Palmiye yaprakları kavisli radyal geometri üzerinde; alçak ot/çalı/eğrelti biçimleri yol, kıyı ve orman altında karışır. Bunlar üretilmiş görsel varlıklar, gerçek botanik envanteri değildir. Alçak bitki yoğunluğu kafes çevresinde artırılır; açık Savanna ve Lemur ada içi korunur. Uzak yaprak pikselleşmesi ve kart tekrarı henüz çözülmedi.

15 Ekim 2026. Bu sahne güncel ziyaretçi krokisi, manuel QGIS yol yüzeyleri ve eski M5/DGN metre verisini birlikte yorumlar. Görsel ayrıntılar, ölçülmüş aplikasyon olarak sunulmaz. Her revizyonda kaynak, ölçü ve yorum ayrımı korunur.

## Su Kuşları Kafesi

[Yapımcı USKON'un teknik açıklamasına](https://uskon.com/en/bursa-zoo-waterbird-cage-single-wall-elliptical-dome/) göre yapı 70 × 40 × 20 m tek cidarlı yarım yumurta biçimli çelik uzay kafestir. Kaynak 2.029 boru (Ø42,4–139,7 mm), 700 düğüm (Ø75–160 mm), 5 × 5 cm gözlü naylon ağ ve iki uçta giriş/çıkış boşlukları bildirir. Modelin 36 × 18 bölümlü yakın örgüsü bu taşıyıcı yoğunluğunun yaklaşık yorumudur; imalat çizimi veya statik model değildir. Kaynaktaki her tekil elemanın konumu bilinmediğinden çubuk sayısını tam eşitlemek hedef değildir.

- Ana kabuk ve metre koordinatı değişmeden korunur.
- Portalın insan geçiş hacminde çubuk, düğüm ve ağ üçgeni bulunmaz; kesimler yalnız açıklıkta yapılır.
- Yakında yaklaşık tam çelik örgü gösterilir. Uzakta yalnız sunum amaçlı bir [ayrıntı düzeyi (LOD)](https://threejs.org/docs/pages/LOD.html) kullanılır; fiziksel modelin çubuk sayısı azaltılmaz. Aynı anda iki LOD çizilmez.
- Uzak LOD'daki daha seyrek ve ekranda okunacak kadar kalınlaştırılmış çubuklar çizim tekniğidir. Bunların sunum çapı USKON'un gerçek çelik boru çapı veya imalat ölçüsü olarak kullanılmaz; iki LOD aynı açık metal malzemeyi paylaşır.
- Naylon ağın 5 cm gözü uzak ekranda tek tek temsil edilmez. [Şeffaf yüzey sıralamasının sınırları](https://threejs.org/manual/pages/transparency.html) nedeniyle ağ, çeliği veya girişi örtmeyecek kadar kontrollü tutulur.

## Zemin ve geometri

- Görünür çim, yaya yolu, su ve yapı ayak izi aynı XY alanını paylaşmaz. Öncelik: **su → yapı → yol → çim**. Kesişen kaynak poligonları metre koordinatlarında bölünür; her konumda tek görünür üst yüz üretilir.
- Eski M5 bina izleri iç içe geçebilir. `build_building_shell.py` bunları çatı kotuna göre 2,5B dış kabuğa böler; en yüksek çatı her XY konumunda bir kez, duvar yalnız dış sınır veya kot farkında çizilir. Alt kapak bina alanında kalır. Bu web sahnesi için çakışmayan yüzeydir; kaynaklı, birleşik ve manifold glTF varlığı dışa aktarılmamıştır.
- Kaynak M5 koordinatları milimetre düzeyindeyken geometrik kesişimler mikroskobik sahte şeritler üretebilir. Ortak maske/çatı/duvar temizliği kaynak hassasiyetinden ince bir toleransla yapılır; son çizilen M5 bina alanının kaynak birleşiminden farkı [building-shell.json](building-shell.json) içindeki `precisionAdjustmentAreaM2` alanına kaydedilir (bu ara sürümde **0,001502 m²**). Bina tabanı ile su/yol/çim arasında pozitif örtüşme, yakın eşdüzlem duvar çifti ve Float32 kapak/duvar üçgenlerinde sıfır alan bulunmadığı üretim sırasında sınanır. Bu sayılar yeni kaynak veya algoritma revizyonunda yeniden üretilmelidir.
- Yol birleşimleri tek bir 2B birleşik alan olarak işlenir. Kesimden sonra her dış halka ve delik geçerli, doğru yönlü ve sıfır uzunluklu kenarsız olmalıdır. Yuvarlatma sonrasında yeniden doğrulanır.
- Yüzey çakışmasını yalnız derinlik ayarıyla gizlemeyiz. Three.js'in [`polygonOffset`](https://threejs.org/docs/pages/Material.html) özelliği çıkartma veya vurgulu kenar gibi özel katmanlar içindir.
- İlk [kubbe kabuğu glTF modeli](bolgeler/31-pelikan-goleti/model/README.md) yakın/uzak LOD olarak ayrıca dışa aktarıldı; iki dosya Khronos doğrulamasından hata ve uyarı olmadan geçti. Bütün canlı Three.js sahnesi hâlâ ayrı bir glTF dosyası değildir; doğrulayıcı mevcut JS geometrisini kendiliğinden denetlemez.
- [Türk Köyü glTF modeli](bolgeler/30-turk-koyu/model/README.md) dokuz M5 çatı bölgesini korur. Kırma çatılar düz iskeletle bölünür, açıklıklar duvardan kesilir. Bu yapılar genel bina kabuğundan çıkarıldığı için ana sahnede aynı yapı üst üste çizilmez. Cephe ve çatı ayrıntıları tarihî fotoğraf yorumudur; mevcut rölöve değildir.
- Ağaçların taçları ve çalılar alfa kesimli yaprak kartlarıyla toplu çizilir. Çim ve yol malzemesi mevcut tek yüzeye atanır. Üretilmiş malzemelerin kaynak ve SHA256 kayıtları `viewer/assets/asset-manifest.json` içindedir. İlave ağaç/çalı yerleri görsel yorumdur; kaydedilmiş M5 ağaç konumları değiştirilmez. Yeni yol veya su yüzeyine denk gelen eski ağaç sembolleri çizilmez.
- [Penguen havuzu modeli](bolgeler/15-penguen/model/README.md), M5 `H22D01C2B:64` su izini ve 2017 belediye fotoğraflarını kullanır. Ana sahnede varlığın su/zemin düğümleri gizlenir; mevcut düzlemsel bölüm suyu ve bölünmüş çakıl alanını bir kez çizer. Havuz gövdesi, kaya duvar, çakıl tabanı ve drenaj parçası kapalı, tutarlı yönlenmiş pozitif hacim olarak doğrulanır. Bu kontrol, bütün bölgenin güncel saha durumunun ölçüldüğünü göstermez.
- Uzak kafeste 186 kalın sunum kirişi korunur; tam üçgen örgü tek piksel çizgi temsiliyle aralarında okunur. [LineBasicMaterial](https://threejs.org/docs/pages/LineBasicMaterial.html) WebGL çizgilerini bir piksel genişlikte çizer. Bu çizgilerin genişliği fiziksel çubuk çapı değildir; açıklıklar yine kesilir, ikinci dolu kabuk yüzeyi eklenmez.

## Görüntü ve kabul ölçütleri

Tekrarlanan çubuk, düğüm ve bordür taşları [`InstancedMesh`](https://threejs.org/docs/pages/InstancedMesh.html) ile toplu çizilir. Perspektif kameranın yakın ve uzak kesim düzlemleri bahçenin gerçek sahne boyutuna göre seçilir; [Three.js kamera rehberi](https://threejs.org/manual/pages/cameras.html) gereksiz geniş aralığın derinlik hassasiyetini düşürdüğünü açıklar.

Her sahne üretiminden sonra şu kontroller yapılır:

1. Üretilen 2B yüzeyler geçerli olur; su/yapı/yol/çim çiftleri arasında pozitif alanlı kesişim kalmaz. Çatı maskesi alanı korunur, çatılar birbirini örtmez.
2. Portal hacminde taşıyıcı veya ağ üçgeni bulunmaz.
3. Masaüstü ve mobilde genel, dış, giriş ve iç bakışlar görsel olarak incelenir; geçit, kubbe silueti, yollar ve su okunur.
4. Tarayıcıda hata, eksik kaynak ve belirgin derinlik titremesi bulunmaz; çizim çağrısı/üçgen sayısı gerekirse `renderer.info.render` ile ölçülür. `verify_building_shell.mjs` gerçek Three.js Float32 geometrisindeki dejenere üçgenleri yayın öncesi denetler.

Güncel krokideki konum eşlemesinin yaklaşık hatası ve M5 yol genişliğinin geçici durumu [CURRENT_PLAN.md](CURRENT_PLAN.md) ile [README.md](README.md) içinde ayrıca belirtilir.

## Savanna ahşap yapı — 15 Ekim ara sürümü

Dördüncü bölge varlığı [12 numaralı alandaki ahşap yapı bileşenidir](bolgeler/12-afrika-savana/model/README.md). M5 sundurma145 yalnız aday konumdur. 2017 fotoğrafıyla konum ve işlev eşleşmesi teyitsizdir. 33,448255m² çatı izi korunur; glTF dışa aktarımından geri ölçülen iz farkı 0,00000115m² düzeyindedir. 7.676 üçgenli dört malzeme grubu kapalı ve tutarlı yönlüdür. Aynı malzemedeki kesişen taşıyıcılar birleştirildi; çatı/ahşap/döşeme arasında gizli birleşim hacimleri kesildi. Format doğrulayıcısı0 hata,0 uyarı,0 ipucu bildirdi; yalnız 1254² görsel için iki kuvveti olmayan boyut bilgisi kaldı. Ahşap görüntüsü üç renk varyantında tek resim/tek doku olarak paylaşılır.

43 alanın kroki konum kaydı ve eski M5 bağlam seçimi üretildi. Kaynak öğelerin tüm özgün koordinatları ve özellikleri aynen korunur; bu seçim bölge sınırını veya öğenin kesin aidiyetini kanıtlamaz.40 numaralı alanın konumu belirsiz bırakıldı. Ana arayüzde42 alanın yaklaşık bağlamına gidilir,42/43 numaralı tekrarlar birlikte gösterilir.

## Su, temas gölgeleri ve yakın yol taşları — 15 Ekim dördüncü yineleme

- Three.js r186 [GTAOPass](https://threejs.org/docs/pages/GTAOPass.html) ve [OutputPass](https://threejs.org/docs/pages/OutputPass.html) eklendi. Derinlik gerçek renk geçişinden alınır; böylece yaprakların alfa boşlukları korunur. Normal malzeme ile opak dikdörtgen yaprak kartları üretmeyiz. AO en uzun kenarda768piksel ile sınırlı; sahne yalnız değiştiğinde yeniden çizilir. Bu masaüstü çalışma gerçek telefon kare hızı doğrulaması değildir.
- [Water](https://threejs.org/docs/pages/Water.html) mevcut12 göletin tek birleşik üst yüzünde kullanılır. Mevcut XY poligonları/delikleri korunur. Aynı karede12 ayrı yansıma yerine ortak512² yansıma hedefi vardır. r186 normal haritası resmî örnekten alınmıştır; SHA/URL `vendor/scene-effects-sources.json` içinde. Z yukarı sahne için shader ekseni uyarlandı; küçük dalga ve Fresnel su yorumu ölçülmüş malzeme değildir. Düz ortografik planda aynı geometri mat su malzemesine geçer; stok perspektif yansıma kamerası kullanılmaz.
- Tarayıcıda gerçek su üçgenlerinden ölçülen alan6970,6603552m², kaynak bölümü6970,66036m²;12 kaynak poligonu,1 görünür su ağı,791 üçgen. Yeni ikinci su katmanı eklenmedi.
- Ortak su sunum seviyesi `surface-layers.json:renderLevels.waterZ=-0.32`, arazi=-0.24 olarak belirlendi. Böylece su arazi altında kalır; bu kotlar M5/H değerinin yerine geçen saha ölçüleri değildir. Penguen GLB'sinin bağımsız su seviyesi de aynı kaynaktan üretilir.
- Yolun tekil taş malzemesine3,5cm genlikli küçük bump yorumu eklendi; albedo örneğinin veri kanalı kullanılır, ölçülmüş yükseklik haritası değildir.10.045 kenar taşı55 mekânsal partide çizilir. Yakın düzey80 yüz ve yumuşak normal, uzak düzey20 yüz kullanır; iki düzey renk ve dönüşüm verisini paylaşır. Bir partide aynı anda tek düzey görünür, eşdüzlem yol kapağı eklenmez.
- Resmî Eylül krokisinin değişmemiş yerel kopyası sadece `dist/reference-maps/` altında paketlenir. Kaynak bağlantısı korunur; `docs/` hedefi hâlâ kapalıdır.
