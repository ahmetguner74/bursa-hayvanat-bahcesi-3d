# Seçilen mockup ile çalışan 3B atlas: tasarım QA

## 15 Ekim 2026 — on dördüncü yineleme: hareketli Afrika penguenleri

**Hedef aktif; genel final result: blocked.** İlk hareketli hayvan modeli yerelde çalışıyor. Bütün 1–43 alan ve genel mockup görünümü tamamlanmadı. Kullanıcının penguen ve akıcı/hafif animasyon isteği için `20261015ai` teslimi hazır.

- **[P1, giderildi] Hayvan modeli ve hareket eksikti.** 15 numaralı havuz/kıyıya üç kara, iki yüzücü yorum bireyi eklendi. Major'ın CC BY 4.0 kaynağının özgün FBX ZIP/GLB'si ve resmî platform kaydı arşivli. Teslim GLB: 4.124 üçgen, iki skinned mesh, 64 eklem, sekiz gerçek animasyon. Kısa yürüyüş, bekleme, tüy bakımı, silkelenme ve yüzme/dalma farklı zamanlarda gerçekleşir. Model/animasyon dosyaları ayrı yakın incelemede seçilebilir, duraklatılabilir.
- **[P1, giderildi] Kaynak GLB standarda uymuyordu.** Sıkı paketli animasyon verisinde yasak `byteStride`, sıfır ağırlıklı eklem indisleri ve iç içe skinned düğüm uyarıları giderildi. Şekil, etkin ağırlıklar, anahtar kareler ve PNG pikselleri korunur. Son Khronos: 0 hata / 0 uyarı; dört boş kaynak düğümü bilgi düzeyindedir. Ölçek, metalik olmayan ve daha yumuşak normal malzemesi değişiklikleri atıfta kayıtlıdır.
- **[P2, giderildi] Şeffaf tüy kenarı ayakları havada bırakıyordu.** Zemin düzeltmesi gövde mesh'inin gerçek skinned en düşük noktasından çıkarılır. Yedi kara klibinin 96'şar örneğinde −0,83…+2,47 mm. Bu, bütün karışımlar ve cihazlar için hata sınırı değildir. Kısa hareketler sınırlı ivme/dönüş ve 0,55 s geçişle yürür; 600 s / 90.000 davranış örneğinde güvenli alan dışına çıkma yok, aynı ortam bireyleri arası en düşük mesafe 0,6400 m.
- **[P2, giderildi] Görünmeyen alanda gereksiz animasyon.** Beş iskelet geometri, malzeme ve dokuları paylaşır; toplam 20.620 hayvan üçgeni / en çok 10 ana mesh çizimi. Görünmeyen iskeletler güncellenmez; bütün koloni görüş dışında veya sekme gizliyken durur. İlk kaba bölge kutusu görüş dışında kalan aktörler için yetersizdi; tekil hayvan küreleri eklendi. Gerçek çalışma modülü testinde görüş dışı, gizli sekme, katman kapatma ve yeniden görünme geçti; gizli geçen zamanı yakalama/ışınlanma yok, devam adımı 8,55 mm.
- **[P2] Performansın pratik sınırı sürüyor.** Son 1280×720 masaüstü tarayıcı örneğinde 180 güncelleme: 59,05 Hz / p95 aralık 16,8 ms / ortalama animasyon CPU 0,197 ms. Aynı bilgisayarda 390×844 viewport: 29,93 Hz / 33,5 ms / 0,133 ms; dört iskelet görünür. Bütün sahnenin 48 sıcak gönderiminde p95 CPU masaüstü 3,6 ms, mobil viewport 3,4 ms. Bunlar GPU süresi veya fiziksel telefon FPS ölçümü değildir. Fiziksel telefon ve uzun oturum kabulü bekler. Normal kullanıcı bağlantısında profil toplama kapalıdır.
- **[P2] Davranış ve saha belirsizliği.** Beş birey bir sunum kolonisidir; gerçek Bursa hayvan sayısı değildir. Kara/su bireyleri ayrıdır; dik bordürü aşan bir giriş/çıkış uydurulmadı. Güvenli maskeler eski M5 havuz/kıyı izi ve mevcut modelin kaya/duvar/platform hacimleriyle oluşturuldu; güncel saha rölövesi değildir. Sosyal etkileşim, beslenme ve bütün doğal davranışlar tamamlanmış sayılmaz.
- **[P1] Genel görsel hedef sürüyor.** Yeni hayvan, mockup'ın orman çeşitliliği, ışığı, kıyı ayrıntısı ve bütün bölge kapsamı eksiklerini kapatmaz. Alt ajan, sonraki iri tür için beyaz gergedan + #16'yı önerdi; rapor `16-gergedan/kaynaklar/flagship-research-20261015.json` içinde. Modelleri satın alınmadı veya dosya kalitesi kabul edilmedi; 2018 yapım alan rakamları gergedan–zebra ortak kompleksine aittir.

### Kanıt ve teslim

`bolgeler/15-penguen/model/hayvan/`: değişmemiş kaynaklar/SHA/atıf, üretici, güvenli yerleşim, GLB, düzenlenebilir Blender, klip/gerçek çalışma modülü testleri, Khronos raporu ve tarayıcı ölçümleri. Blender yeniden açıldı: metre, bir iskelet/64 eklem, iki gövde mesh'i, sekiz eylem, üç paketlenmiş görüntü. Kaynak önizlemesi gerçek Cycles render'ıdır; `atlas-preview.png` gerçek WebGL tuvalinden indirilen 1280×720 sahne yakalamasıdır, AI mockup değildir. Son yakalama SHA256: `dd6df9620df1fe2aa7305f4a870564bd9db40082fd8ce9b0540008621cdd88de`.

Masaüstü/mobil yakın görünüm, 15 seçimi, model inceleme bağlantısı, atıf, hayvan katmanı kapatma/açma ve animasyon seçimi kontrol edildi. Konsolda shader/animasyon hatası veya uyarısı yok. JS sözdizimi, `verify_penguins.mjs`, `verify_runtime.mjs`, `verify_blend.py`, `verify_inventory.py` ve yerel builder geçti. Native M5/QGIS SHA'ları aynı, yüzey sahipliği değişmedi; `docs/` Git durumu temiz ve canlı yayın yok.

## 15 Ekim 2026 — on üçüncü yineleme: orbit ekseni

**Hedef aktif; genel final result: blocked.** Kullanıcının orbit hatası için yerel `20261015ag` düzeltmesi yapıldı. Genel mockup/1–43 kapsamı tamamlanmadı.

- **[P1, giderildi] Düz plandan orbit hareketinde yana yatma:** Eski `af` sürümünde 1280×720 düz kafes görünümü, [630,490]→[890,260] fare sürüklemesinde yana yattı; gerçek tarayıcıda yeniden üretildi. Kameranın yatay `up` vektörü ile OrbitControls'un kurucuda sakladığı Z ekseni farklıydı. Yeni sürüm bütün kameralarda Z yukarı kullanır. Aynı sürükleme üstten planı bozmadan kaydırır; perspektif 0→65 arayüzden değiştirildi, eğik orbit sırasında ufuk yatay kaldı.
- **[P2, giderildi] Kamera geçişi/atalet çakışması:** Her görünüm veya projeksiyon değişiminde eski denetim dispose edilir; kalan dönme/öteleme ataleti yeni görünüme taşınmaz. Kontrolün `start` olayı ve yakınlaştırma düğmeleri geçişi keser. Düz planda sol fare/tek parmak kaydırma, eğik planda orbit vardır. XY düzleminde öteleme dönme merkezinin yüksekliğini korur. Mobil genel plandaki farklı yukarı vektörü kaldırıldı; eğik genel planda orbit kullanılabilir.

`verify_atlas_orbit.mjs` gerçek vendor kontrolü ve üretimdeki yardımcı işlevi çalıştırır: eski sağ eksen |Z|=0,280599; üç kamera türündeki 480 örnekte yeni en yüksek |Z|=2,78×10⁻¹⁶. Yeniden bağlanan denetimin 160 güncellemesinde en büyük konum kayması9,10×10⁻¹²m. `atlas-orbit-proof.json` sayısal kanıttır. Vendor, M5 ve QGIS yolları değiştirilmedi; ek geometri/render geçişi yok. Masaüstü gerçek sürükleme, perspektif denetimi ve mobil390×844 genel/giriş/iç/dış geçişleri kontrol edildi. Tarayıcı yakalamaları araç çıktısında, kalıcı dosya yolu dönmedi. Ana atlas hata/uyarı kaydı boş. Fiziksel telefon FPS veya bütün uzun oturum kabulü değildir.

## 15 Ekim 2026 — on ikinci yineleme: 2D bitki titreşmesi

**Hedef aktif. final result: blocked.** Kullanıcının 2D bitki titreşmesi ve hafiflik düzeltmesi önceliklendirildi. Genel mockup görünümü ve bütün 1–43 kapsamı tamamlanmadı.

- **[P2] Uygulanan düzeltme:** Kaynakta rüzgâr/bitki animasyonu yok. Alçak bitkiler üç yerine iki kart, altı 512² teknik doku, +0,65 mip bias ve alfa kapsam yumuşatması kullanır. Ekranda 4–11 CSS piksele düşen ince otlar kademeli söner. Küçük otların ayrı gölge haritası çizimleri kaldırıldı; mevcut AO temas derinliğini kullanır. Ek render geçişi yoktur.
- **[P2] Uzak atlas:** Yaklaşık 5,2° azimut toleransı ve 42°/50° eğim dönüş eşikleri eklendi. Kamera sönümlenirken iki kare arasında hızla gidip gelme engellenir; ayrık yön geçişinin bütün izleri çözülmüş sayılmaz. Yakın/uzak renk katsayısı ortaktır.
- **[P1] Görsel hedef sürüyor:** `forest=2`, dış görünüm, perspektif65 ile gerçek 1280×720 tam/odak karşılaştırma yapıldı. Taç çeşitliliği, ışık, doğal kıyı ve yakın kart görünüşü hâlâ mockup'tan geride.

**Asıl neden ve son düzeltme:** XYZ dönüş sırası aynı bitkinin kartlarını eşdüzlemli bırakıyordu; yüzeyler üst üste gelip derinlikte yarışıyordu. Son sürümde ZYX sırası, gerçek dik açı ve dik taban var. `verify_plant_cards.mjs` gerçek çizim yardımcı işlevini yedi varyantta denetler: eski normal iç çarpımı≈1, yeni≤3,89×10⁻¹⁶; taban yukarı vektörü Z≈1. Alfa/mip hafifletmeleri bu geometri düzeltmesine ek olarak korunur.

### Kaynak, yük ve doğrulama

18 değişmemiş üretilmiş raster varlığı vardır. Yeni çiçekli kaynak 1254² RGBA, son prompt manifestte/`.prompt.txt` içinde; teknik türev 512² / 298.654 bayt. Neon RGB görülen 2.061 pikselin alfa üst sınırı4; alfa kesimi bunları atar. %10 yan boşluk hedefinin karşılanmadığı kayıtlıdır. Gerçek tür veya saha fotoğrafı sayılmaz.

Yeni 3.312 yorum kümesiyle toplam 10.034 alçak bitki,599 çiçekli küme oldu. İki kartlı geometri40.136 üçgen; önceki6.722×6=40.332 üçgene yakın. Altı teknik yaprak dokusunun temel RGBA belleği37.740.384→6.291.456bayt, %83,33 azalma; bütün GPU belleği veya FPS değildir. SHA/boyut/renk modu denetimleri geçti. Kaynak M5/QGIS, yüzey sahipliği ve dokuz ilk bölgesel model grubu korunur.

`publish_local.py --local-only`, JS sözdizimi, `verify_inventory.py` ve değişmemiş CC0 atlas için `verify_tree_assets.py` geçti. Masaüstü giriş/dış görünüm ve390×844 mobil tarayıcıda sürükleme denetlendi. `profile=1` yalnız geliştirici konsoluna CPU gönderim ölçümü yazar; önceki`ad` sürümünde48 sıcak örnekte p95=8,3ms, yaklaşık1.206 çizim çağrısı/1,54milyon üçgen bütün geçişler dahil. GPU süresi veya fiziksel telefon FPS'i ölçülmedi. Son`ae` denetimi ayrıca kaydedilir. Bütün cihaz/kamera koşullarında sıfır titreşme garantisi verilmez.

Ana atlas kontrolünde shader hatası/uyarısı yok. Karşılaştırma sekmesindeki eski MutationObserver hatası tekrar görüldü; sahibi belirsiz. Gerçek tarayıcı yakalamaları araç çıktısında, kalıcı JPG/PNG yolu dönmedi. Tree Small02 ikinci taç kaynağının11dosyası84,11MB/MD5/SHA ile arşivlendi; sahneye alınmadı. `docs/` Git durumu temiz; canlı yayın yapılmadı.

## 15 Ekim 2026 — on birinci yineleme: Boz Ayı havuzu ve kaya kıyısı

**Hedef aktif. final result: blocked.** Dokuzuncu ilk model grubu yerel atlasa eklendi. Bu, bütün 1–43 alan modellerinin veya beğenilen mockup görünümünün tamamlandığı anlamına gelmez. Görsel kabuldeki eksikler dış engel sayılmaz; çalışma devam edebilir.

### Bulgular ve düzeltmeler

- **[P1] Genel görsel hedef sürüyor.** Güncel eş ölçülü tam ve odak karşılaştırmada mockup'ın sık/katmanlı bitkileri, taç çeşitliliği, ince yaprak kenarları, doğal kıyı geçişleri ve orman ışığı daha güçlü. Çalışan atlasın zemin/yol ayrımları sert, orman düzeni daha seyrek ve tekrar eden taçlar belirgin. Yeni havuz alan kapsamını ilerletir; kafes çevresinin görsel kabulünü kapatmaz. Sonraki görsel ilerlemenin odağı bu farklar olmalıdır.
- **[P2, giderildi] Kayalar düzenli sıra oluşturuyordu.** İlk denemede kıyı boyunca eşit aralıklı kayalar vardı. Aynı native havuz ve kuru zemin maskesi korunarak 17 kaya üç düzensiz kümeye taşındı. Resmî fotoğraf kümeli gri kaya/beton/yeşil zemin karakterini gösterir; bu yeni tekil konumlar ölçülmüş değildir.
- **[P2, giderildi] Üstten model kadrajında başlık ayrıntıları örtüyordu.** Habeş ve Boz Ayı incelemesi gerçek model noktalarını başlık, kaynak bilgisi ve alt denetimlerin dışında kalan görünür alana sığdırır. Yeni Boz Ayı masaüstü 1280×720 üst görüntüsünde bütün çevre görünür;390×844 eğik ve üst görüntülerinde model başlık/alt bilgi altında kalmaz. Mobil DOM/canvas/scrollWidth 390×844/390×844/390.
- **[P2] Bölge kapsamı ve kaynak belirsizliği sürüyor.** Havuz 278'in 29 ile eşleşmesi yaklaşık;28/29 barınak sınırı, bugünkü şekil ve kotlar teyitsiz. Bu varlık bütün ayı barınağı değildir. Diğer bölgeler,40 işaretlemesi,31/32 kapsamı ve Savanna aday konumu bekler. Kafes öncelikli görsel geliştirme, bütün alan kapsamının yerine geçmez.
- **[P2] Gerçek cihaz ve uzun kullanım.**390×844 tarayıcı denetimi fiziksel telefon FPS/bellek ölçümü değildir. Önceki yedi bölge yükleme/yeniden yükleme denetimine ek olarak 29'un hazır durumu ve doğru inceleme bağlantısı doğrulandı; bütün 43 alanın uzun oturum kabulü yapılmış sayılmaz.
- **[P3] Arayüz:** Font/ikon eşlemesi ve kapsamlı erişilebilirlik kabulü bekler.

### Yeni varlık ve yüzey kanıtı

`bolgeler/29-boz-ayi/model/` içinde düzenlenebilir girdiler, Python üretici, kaynak yakalama/kaya kümeleri aracı, üç teknik doku türevi, GLB ve gerçek geometri doğrulaması vardır. Native gölet 488,3991195 m², yorum kıyısı 41,897033 m².17 kaya,9 bitki kümesi, kıyı genişliği/kotları ve derinlik yorumdur; eski fotoğraflar güncel ölçüm sayılmaz. Resmî2018 fotoğrafı PNG olarak özgün baytlarıyla,2016 kış fotoğrafı JPEG olarak kaynak URL/tarih/SHA ile kaydedildi;2018 haber sayfası yerel metin arşivi. Fotoğraflar GLB/dist dokularına eklenmedi. Mimari referans kaydı toplam 64; bunlar benzersiz güncel dış görünüş fotoğrafı sayısı değildir. Önceki 51 resmî tür fotoğrafı ve 86 kroki kopyası korunur.

GLB 10.278 üçgen /1.513.188 bayt. Yeniden yüklenen altı kapalı parça sonlu, doğru yönlü ve pozitif hacimli; su ve alfa kesimli bitki kartları açık yüzeydir. Sıfır alanlı veya yinelenen üçgen yok. Gerçek Float32 izdüşümü farkı su/yatak 0,0000197198 m², kıyı 0,0000337439 m², önizleme zemini 0,0000707906 m². Yalnız türetilmiş önizleme bağlamındaki mikroskobik şerit normalizasyonunun alan farkı 0,0000574641 m² ve uzanımı 0,40 m; native havuz/yol XY değişmez.

Kıyı ana çimden ayrılır; su/yol/arazi pozitif alan örtüşmesi 0. Önizleme zemini/yatağı/suyu ana atlasta gizlenir.12 gölet bir ortak mesh ve tek yansıma geçişidir. Ayı havuzu sunum rengi köşe özniteliğiyle gelir; ikinci su düzlemi eklenmedi. Düz plan malzemesi aynı rengi kullanır. Bu havuzun eski genel kıyı taş/bitkileri üretilmez; ek orman gövdeleri kayalara çarpmaz. Özgün M5 ağaç kayıtları korunur.

Yerel Blender 5.2.1 LTS, aynı GLB'yi içe alarak dokuları paketlenmiş düzenlenebilir `.blend` dosyası ve 1200×800 Cycles önizleme PNG'si üretti. Model ile önizleme kamera/ışık/arka zemin koleksiyonları ayrıdır. `preview-source.json` GLB/Blender/PNG SHA'larını kaydeder; PNG gerçekten açılıp incelendi. Bu çıktı tarayıcı yakalamasının yerine geçirilmez ve genel görsel kabulü kapatmaz.

### Güncel tarayıcı kanıtı ve karşılaştırma

Sürüm`20261015aa`. Model incelemesinin ilk eğik/üst görüntüsü, düzeltilmiş masaüstü üst görüntüsü ve ayrı 390×844 eğik/üst görüntüleri incelendi. Ana atlas 390×844 konum 29 seçili, “3 B ayrıntıları hazır” ve `model-review/?model=bear-pool` bağlantısı gösterir. Plan bakış çubuğu 65→0→65 değişti; düz görünümde havuz aynı zeytin yeşili karakterde ve tek yüzey olarak görüldü. Geçici ekran boyutları kaldırıldı; test sekmeleri kapatıldı.

İlk karşılaştırma sekmesi 557×712 döndüğü için eş viewport kanıtı kabul edilmedi. Yeni sekmede gerçek 1280×720 DOM doğrulandı: iki 1280×720 kaynak içerik 612×344 gösterildi. Aynı sekmenin odak karşılaştırması iki 650×380 penceresini 612×358 gösterdi. Kaynak `design-reference/woodland-aviary-concept.png`; çalışan sahne dış görünüm, açık tema, perspektif 65 ve `forest=2`. Tam/odak aynı tarayıcı görüntüsünde incelendi. Fotoğrafın kavramsal yerleşimine uymak için M5/QGIS kaynakları taşınmadı. Gerçek yakalamalar araç çıktısındadır; kayıtlı JPG/PNG yolu dönmediği için kalıcı ekran dosyası varmış gibi sunulmaz. Bu eksik ve P 1 farkları nedeniyle genel tasarım kapısı geçti denmez.

Yeni model/atlas kontrolünde hata/uyarı günlüğü boş. Gerçek su geometrisi günlüğü 12 kaynak gölet,1 çizilen mesh,791 üçgen; kaynak alan 6970,66036 m², çizilen Float32 alan 6970,6603552 m². Önceki karşılaştırma sekmesindeki araç kaynaklı olabilecek MutationObserver hatasının sahibi belirlenmiş değildir; bütün oturumun hatasız olduğu iddia edilmez.

### Geçen teknik kontroller ve sınırları

`publish_local.py --local-only`, JS sözdizimi, `validate_models.cjs`, `verify_inventory.py` ve gerçek `verify_bear_pool.py` geçti.10 bölgesel GLB varyantı ve ayrı CC 0 ağaç dahil 11 dosyanın biçim raporunda hata 0/uyarı 0. Yeni havuzun bilgi/ipucu sayısı 0; eski dosyaların bilgi/ipucu kayıtları kalır. Envanter 43 klasör/43 native bağlam/42 konum doğrular;40 konumsuz. Bu kontroller fotoğraf aidiyeti/güncel saha doğruluğu veya mockup görsel eşdeğerliği sağlamaz.

Kaynak M5 SHA`022a88053df75b9d755e082079ed31f6b922e79bb8bca03016890c52cc828358`, QGIS yollar SHA`d5038924b6356022b273fff88bc12ba6f3091c8df2294ca6fd64decf1a5fad56` korunur. `docs/` Git durumu temiz; canlı yayın yapılmadı. Yerel model `http://127.0.0.1:8768/model-review/?model=bear-pool`; Wi-Fi IP`192.168.0.192`, sunucu`0.0.0.0:8768`. Gerçek telefon bağlantısı bu tarayıcı kontrolüyle kanıtlanmaz.

## 15 Ekim 2026 — onuncu yineleme: Habeş Maymunu Adası

**Hedef aktif. final result: blocked.** Sekizinci ilk model grubu üretildi ve yerel atlasa eklendi. Bütün 1–43 alan modelleri ve seçilen mockup'ın görsel düzeyi tamamlanmadı. Bu kabul durumu çalışmayı durduran dış engel değildir.

### Bulgular ve önceki yinelemeye göre ilerleme

- **[P1] Genel görsel hedef sürüyor.** Aynı tam/odak karşılaştırmada taç çeşitliliği, uzak yaprak kenarları, orman ışığı ve doğal kıyı yoğunluğu hâlâ mockup'tan geride. Bu tur alan kapsamını ilerletir; yeni adanın eklenmesi kafes çevresinin görsel kabulünü kapatmaz. Önceki zemin/ortak ışık/kıyı değişiklikleri korunur.
- **[P2] Bölge kapsamı ilerledi, saha doğruluğu teyitsiz.** Habeş adası M5 ada57 / su58 ve iki aday sundurma149/150 izini korur. Yeni resmî 2021 fotoğrafı açık toprak, ahşap direk/halat, kaya ve merdivenli platform karakterini gösterir. Tekil yerleşimler, bütün yükseklikler ve platform işlevi yaklaşık; görünmeyen taraflar veya güncel durum kanıtlanmadı. Komşu binalar ve ön ziyaretçi pergolası modele atanmadı. Diğer bekleyen bölgeler, 40 işaretlemesi, 31/32 kapsamı ve Savanna aday konumu sürer.
- **[P2] İlk mobil kadraj küçüktü — düzeltildi.** İlk 390×844 model incelemesi fazla boşluk bırakıyordu. Habeş için gerçek dışa aktarılan model noktalarıyla sığdırma ve portrede daha yüksek bakış uygulandı. İkinci gerçek yakalamada ada daha büyük, başlık/durum/alt denetimlerin dışında ve tamamen çerçevede. DOM/canvas/scrollWidth390×844/390×844/390. Masaüstünde de önceki kutu kadrajı sıkılaştırıldı; eğik/üst seçili durumları karşılıklı değişiyor.
- **[P2] Uzun kullanım ve fiziksel telefon:** Yedi bölgesel varlığın gezinme/yükleme kontrolü bu tur yapıldı; uzun oturum ve gerçek cihaz FPS/bellek denetimi hâlâ bekler. Durum yazısı ve ağ kaydı, tüm geçişlerin her animasyon karesinin görsel denetimi yerine geçirilmez.
- **[P3] Arayüz:** Kaynakla font/ikon eşlemesi ve kapsamlı ekran okuyucu kabulü henüz tamamlanmadı.

### Yeni model ve kaynak kanıtı

`bolgeler/09-habes-maymunu/model/` içinde düzenlenebilir girdiler, Python üreticisi, dört teknik JPEG türevi, GLB ve gerçek geometri doğrulaması var. Ada1.331,5979435m²; dış su sınırı2.506,9042445m², su bandı1.175,306301m². İki aday platform toplam11,486593m². Altı direk, on iki halat, sekiz kaya, iki çapraz ahşap eleman, oyuk gövde ve merdiven görsel yorumdur. Özgün H metadata olarak korunur, model yüksekliği olarak kullanılmaz. M5'teki açık641/642 çizgileri kapatılıp hayalî iç havuz yapılmadı.

GLB14.129 üçgen /754.020bayt. Yeniden yüklenen dokuz kapalı hacim sonlu, doğru yönlü ve pozitif hacimli; önizleme suyu açık düzlemdir. Kaynak izdüşümü farkları toprak0,0000335275m², kıyı0,0000793075m², su0,0001074961m²; platformlar0,0000025501/0,0000037065m². Kıyı37,425507m² yorum maskesiyle ortak zeminden ayrılır, kalan1.294,172437m² tek toprak bölgesidir. Kıyı/su/yol/arazi alan örtüşmesi sıfır. Halat/ahşap/kaya gizli birleşimleri kesilir; merdiven platform üstüne taşmaz. Kaynak fotoğraf GLB veya dist içine kopyalanmadı.

Yeni fotoğraf/page arşivi kaynak klasörüne URL/yıl/gözlem/SHA ile işlendi. Fotoğraf1805×1205; 12 Kasım2021 etkinlik kaydı, çekim tarihi ve bugünkü durum teyitsiz. Gergedan için incelenen2018 fotoğraflar iç mekânı gösteriyor; güncel dış sınırla eşleme olmadığı için bir barınak dış modeli uydurulmadı. Habeş adası daha güçlü native geometri eşlemesiyle seçildi.

### Tarayıcı, beş görsel yüzey ve karşılaştırma

Sürüm `20261015y`. `model-review/?model=habes` masaüstü eğik/üst ve `?focus=region-9&perspective=65` atlas gerçek görüntüleri incelendi. Ana atlas menüsü09seçili, “3B ayrıntıları hazır” ve doğru `model=habes` bağlantısı gösteriyor. Yeni adada ek orman bitkileri yok; bir eski M5 ağaç sembolünün temsili ağacı gizlendi, kaynak noktası değiştirilmedi. Önizleme toprak/su/yatak düğümleri ana atlasın yüzeylerini çoğaltmaz. Mobil atlas ve düzeltilen model incelemesi ayrı390×844 yakalamalarda denetlendi; geçici ekran boyutu kaldırıldı.

Kaynak görsel doğrusu `design-reference/woodland-aviary-concept.png`,1672×941piksel. Birleşik kanıt `http://127.0.0.1:8768/design-reference/compare-local.html?forest=2`. Açık tema/dış görünüm/perspektif65; iki1280×720CSS içerik aynı oranda612×344'e küçültülerek aynı1280×720 tarayıcı yakalamasında karşılaştırıldı. Odak yakalaması aynı `[330,220,650,380]` pencerelerini612×358 gösterdi. Kaynak kavramsal peyzajdır; M5/QGIS koordinatları görsele uydurulmadı. Yakalamalar araç çıktısında; kalıcı PNG yolu dönmediği için yeni ekran dosyası adı uydurulmaz.

Yazı/typografi okunur, kaynak eşlemesiP3; aralık/kadraj mobilde düzeltildi. Renklerde ortak sıcak ışık korunuyor, yeni ada fotoğraftaki açık yaşam alanı karakterine göre toprak; malzeme/tekil prop gerçekliği hâlâ ilk yorum düzeyinde. Görsel kalite için genel taç/ışık farklarıP1. Metin/içerikte yerleşim ve güncellik sınırları açık, eksik bölgeler tamamlanmış gösterilmiyor. Habeş fotoğrafı ile model farklı kamera ve tarih içerir; fotoğraf tekil konum doğrulaması olarak kullanılmaz.

Ana atlas/model incelemesi hata/uyarı günlükleri boş. Karşılaştırma iframe'inde bir `MutationObserver.observe` TypeError kaydı var; uygulama ve karşılaştırma kaynakları bu API'yi kullanmıyor, sahibi kesin atanmadı. Birleşik görüntü ve denetimler çalışıyor; tüm tarayıcı günlükleri boş diye sunulmaz.

### Yükleme ve yerel doğrulama

Görünüm menüsünde30→15→12→11→14→13→09→30dolaşıldı. Yedi bölgesel modelin her biri DOM'da hazır durumu ve doğru inceleme bağlantısını gösterdi. Ağda dört GLB isteği görüldü; Türk Köyü iki kez istendi, önbellekten çıkarıldıktan sonra yeniden edinim gerçekleşti. Ağ yükleme hatası yok. Bu hızlı dolaşım, uzun süreli cache/bellek veya her kamera animasyonunun görsel testi değildir. Sonunda09bölgesine dönülür.

On GLB Khronos denetimi hata0/uyarı0; yeni Habeş'te bilgi/ipucu0, eski dosyaların bazı bilgi/ipuçları sürer. Envanter doğrulaması43klasör/51resmî fotoğraf kaydı/86kroki/43bağlam/dokuz bölgesel GLB varyantı/17üretilmiş raster geçti. Mimari görsel kaydı62; benzersiz veya güncel fotoğraf sayısı değildir. M5 SHA022a8805… ve QGIS yol SHAd5038924… aynı. Güncel LAN192.168.0.192:8768 üzerinden ada atlası ve model incelemesi HTTP200. `docs/` Git durumu temiz; canlı yayın yok.

**Devam:** Güçlü kaynaklı sonraki bölge bileşenleri, kalan orman/ışık görsel farkları ve gerçek cihaz denetimi. Hedef aktif kalır.

---

## 15 Ekim 2026 — dokuzuncu yineleme: zemin geçişleri, ortak ışık ve iç gölet kıyısı

**Hedef aktif. final result: blocked.** Bu tur yeni bölge eklenmedi; yedi ilk model grubu korunuyor. Çalışan görünümde somut ilerleme var, fakat bütün 1–43 model kapsamı ve mockup görsel kabulü tamamlanmadı. Görsel kabul durumu dış engel değildir.

### Önceki P1 bulgularına uygulanan değişiklikler

- Tekdüze çim: mevcut tek zemin malzemesine sayısal karışım haritası eklendi. M5/türetilmiş ağaçlar çevresinde yapraklı toprak, su kenarında nem ve yol kenarında küçük renk değişimi. 1024² RGB veri, yaklaşık 0,645×0,413 m piksel; 699 ağaç yaması. Görünür ikinci zemin yüzü yok. Mevcut üretilmiş meadow albedosu geniş ölçekte de örnekleniyor. Bu bir güncel toprak taraması değil.
- Yeni albedo Image Gen ile üretildi: değişmemiş 1254² `viewer/assets/woodland-leaf-litter-v1.png`, gerçek SHA/son prompt manifestte. Uygulama 1024² / 725.656 bayt RGB JPEG türevini kullanıyor; kaynak PNG korunur. Sayısal ağırlık haritası 329.777 bayt. Dört kenarda kusursuz dikişsiz devamlılık doğrulanmadı.
- Sert/soğuk ışık: ana sahne ve ağaç üreticisi `viewer/lighting.js` ortak ayarlarına geçti. Daha sıcak ışık, PCF gölge yoğunluğu 0,78 / yarıçap 2,25; sahne pozlaması 1,08. Aynı yakın GLB'den yeni 16 açılı uzak atlas alındı: 3.302.130 bayt. Kaynak geometri/SHA ve çözülen kare piksel eşitliği doğrulandı. Canlı yükleyici eski ışık metadata'sını reddeder; eski ağaçlar yeni deneme hazır olmadan gizlenmez.
- Kafes içi: 112 kıyı taşı daha düzensiz geometri ve renk varyantlarına geçti. İlk yakın yakalamada fazla açık/pürüzsüz taşlar görüldü; mevcut üretilmiş kaya albedosunun 512² / 111.481 bayt teknik türevi ve daha ayrıntılı geometriyle düzeltildi. Son iç görüntüde taş rengi/detayı görünür. 28 ot/eğrelti/çalı kümesi eklendi. Adayların merkez ve dört çevre noktası kuru arazide sınanır; bu sürekli ayak izi kesişiminin kesin kanıtı değildir. Altı önceki basit konik ağaç, aynı konum/yükseklikte yapraklı taç ve dallara geçti.

Göletin yorum kıyı poligonu, köprü, yollar, portal açıklıkları, kafes ana ölçüsü ve ortak metal rengi değiştirilmedi. Arazi/su/yapı/yol yüzey alanları aynı, pozitif örtüşme ve boşluk sıfır. M5 SHA `022a8805…`, QGIS SHA `d5038924…` değişmedi; `docs/` temiz.

### Görsel kanıt ve karşılaştırma geçmişi

Kaynak doğrusu `design-reference/woodland-aviary-concept.png` (1672×941 piksel). Son uygulama sürümü `20261015x`, `?focus=cage&perspective=65&forest=2`, açık tema / dış görünüm / perspektif 65. Birleşik kanıt: `http://127.0.0.1:8768/design-reference/compare-local.html?forest=2`. İki içerik 1280×720 CSS çerçeveden eşit oranda 612×344'e küçültülerek aynı 1280×720 tarayıcı yakalamasında incelendi. Odaklı ikinci karşılaştırma aynı `[330,220,650,380]` pencerelerini yaklaşık 612×358 gösterdi. Kaynak kavramsal yerleşimdir; gerçek M5/QGIS konumları görsele uydurulmadı.

Önceki sekizinci yinelemede sert gölge/tekdüze zemin/taç tekrarı P1'di. İlk `w` birleşik yakalama yapraklı toprak ve yumuşayan gölgeleri gösterdi; yakın iç görüntü taşları fazla pürüzsüz gösterince düzeltme yapıldı. Son `x` tam ve odak yakalamaları, ayrıca giriş/iç durumları tekrar incelendi. Taç kaynağı hâlâ tek; yeni malzeme ve ışık bu çeşitlilik eksikliğini çözmüş sayılmadı.

Yakalamalar bu oturumun araç çıktısında; kalıcı ekran görüntüsü dosya yolu dönmediği için yeni PNG yolu uydurulmadı. Canlı yerel karşılaştırma URL'si kanıt olarak tutuluyor.

### Beş zorunlu görsel yüzey ve kalan bulgular

- **Görsel kalite — [P1]:** Toprak ve taş geçişleri daha okunur, basit koniler kaldırıldı. Tek kaynak taç tekrarı, uzak dallı silüetlerin keskinliği, bazı yakın yaprak kartları ve geniş açık çim bölgeleri mockup'tan hâlâ geride. Sonraki düzeltme: ölçülü konumları koruyarak farklı taç yapıları, daha zengin yer örtüsü ve doğal kıyı kümeleri; aynı karşılaştırmayı tekrar et.
- **Renk/ışık — [P1]:** Sıcaklık ve gölge koyuluğu iyileşti; görüntü hâlâ mockup'ın yumuşak hacimli orman ışığı kadar doğal değil. Uzak silüet sabit kanonik aydınlık içerir; farklı dönüşlerde yakın/uzak birebir ton garantisi yok. Farklı bakışlarda taç ışığı/kenarları ve bitki malzemeleri sürmeli.
- **Düzen/aralık — [P2]:** 1280×720 masaüstü ve 390×844 mobilde üst/alt denetimler görünür. Kadraj çalışıyor; gerçek yollar/kavram yerleşimi farkı korunur. Kaynakta daha yoğun bitki kümeleri var; mevcut koordinatlar içinde bu yoğunluk/doğal dağılım geliştirilmeli.
- **Metin/kapsam — [P2]:** Yedi ilk model grubu bütün 43 alanı tamamlamaz. Alanların kaynak incelemesi/güncel aidiyetleri, 40 işaretlemesi, 31/32 kapsamı ve Savanna konumu hâlâ açık. Yeni bitki/toprak ayrıntıları saha kanıtı olarak sunulmaz.
- **Yazı/typografi — [P3]:** Mevcut okunabilir hiyerarşi/denetimler korunuyor; ayrıntılı font/ikon eşleşmesi ve kapsamlı ekran okuyucu doğrulaması bekler.

### İşlev, kaynak ve mobil denetim

Giriş ve iç kamera seçimleri gerçek tarayıcıda çalıştı; geçit içinde çubuk/ağ geçişi görünmedi. Ana atlas hata/uyarı günlükleri boş. Karşılaştırma sekmesinde iki `MutationObserver.observe` TypeError kaydı görüldü; uygulama/karşılaştırma kaynakları bu API'yi kullanmıyor, hata sahibi kesin atanmadı. Birleşik görüntü ve denetimler çalışıyor; bütün tarayıcı günlükleri boş diye sunulmaz. Yeni shader gerçek WebGL derlemesinden geçti; bekleme göstergesi kaldırıldı. Son mobil deneme taze sekmede 390×844 viewport/canvas ve kaydırma genişliği 390 olarak doğrulandı; bütün denetimler ve kafes görünür. Geçici ekran boyutu sıfırlandı. Fiziksel telefon FPS/bellek testi yapılmadı.

`python bolgeler/verify_inventory.py` kaynaklar, gerçek dışa aktarılan modeller ve yeni malzeme kaynak/çıktı SHA'larını geçti: 43 klasör, 51 resmî fotoğraf kaydı, 86 kroki, 43 bağlam, sekiz bölgesel GLB varyantı, 17 üretilmiş raster. Ortak ağaç ayrı CC0 varlığıdır; güncel atlas geometri/kare eşitliği denetimi de geçti. Bu sayılar fotoğrafların güncel saha ölçümü olduğunu göstermez. Yerel paket üreticisi yeni sayısal malzemeyi yeniden üretir; SciPy 1.15.3 gereksinime eklendi. Canlı yayın yapılmadı.

**Devam:** Önce taç çeşitliliği/orman ışığı ve güçlü kaynaklı sonraki bölge modelleri; fiziksel telefon ve uzun bölge geçişi denetimi. Hedef aktif kalır.

---

## 15 Ekim 2026 — sekizinci yineleme: Afrika Kafe, ortak ağaç kaynağı ve bölgesel yükleme

**Hedef aktif. final result: blocked.** Yedi ilk model grubu yerelde hazır; bütün 1–43 alanın modelleri ve mockup görsel kabulü tamamlanmadı. Bu durum görsel kabulün geçmediğini belirtir; çalışmayı durduran dış engel değildir. Aşağıdaki önceki yinelemeler tarihçedir; eski ağaç sayıları ve `.11` LAN adresi güncel değildir.

### Bulgular

- **[P1] Bitki, ışık ve yakın çevre:** Aynı ölçekteki birleşik karşılaştırmada yeni taçlar eski seyrek sürümden daha dolu; fakat tek ağaç kaynağının tekrarı, sert gölgeler, ayrık yaprak silüetleri ve tekdüze zemin mockup'tan belirgin biçimde farklı. Kafes çevresi daha doğal kıyı/zemin geçişlerine ve çeşitli bitki kümelerine ihtiyaç duyuyor. Yakın ve uzak ağaç aynı kaynak geometri/rengi paylaşsa da önceden aydınlatılmış uzak silüet bütün bakışlarda eş görünüm garantisi vermez. Sonraki düzeltme: kaynak konumlarını koruyarak taç çeşitliliği, daha yumuşak ışık ve yer örtüsü geçişleri; sonra aynı kadrajda tekrar karşılaştırma.
- **[P2] Bölge kapsamı ve kanıt:** Afrika Kafe altı aday M5 izini kullanıyor; 2011 fotoğrafları kesin güncel aidiyet, yükseklik veya cephe ölçüsü sağlamıyor. Yedi ilk model grubu bütün alanların bittiği anlamına gelmiyor. 40 için kullanıcının işaretleyeceği kroki beklenir; konum tahmin edilmez. 31/32 kapsamı ve Savanna bileşeninin aday konumu da teyitsiz. Sonraki düzeltme: güçlü yeni fotoğraf/kroki eşlemesiyle kalan alanlar.
- **[P2] Mobil performans kapsamı:** Bölgeye göre yükleme ve yeniden deneme artık uygulandı. 390×844 gerçek tarayıcı boyutunda kafe ve güncel ağaç denemesinin denetimleri görünür, yatay taşma yok. Fiziksel telefon FPS/bellek ve bütün bölgelere ardışık geçişte önbellek davranışı henüz doğrulanmadı. Bu nedenle emülasyon başarısı gerçek cihaz performansı sayılmaz.
- **[P3] Arayüz:** Yazı ailesi/ağırlık ve ikonların kaynakla ayrıntılı eşlemesi, ekran okuyucu denetimi bekler. Ana üst/alt denetimlerin konumu ve açık arka planı korunur.

### Önceki bulgulara uygulanan değişiklikler

Afrika Kafe: altı özgün M5 yapı/sundurma izi, 40 ahşap dikme, gerçek duvar açıklıkları, açık kameriyeler ve çok bölümlü kırma çatı yorumu. 6.724 üçgen / 899.196 bayt. Gerçek GLB'de 21 kapalı, yönleri tutarlı, pozitif hacimli geometri parçası; çatı izdüşümü farkı 0,0000330576 m², döşeme farkı 0,0000329234 m². Yalnız köşede temas eden tabanlar ayrı kapalı parçalardır. 570,101484 m² döşeme yol/çimden ayrıldı; eski 243 geçici bina kutusu kaldırıldı. Kaynak QGIS yolları değiştirilmedi. Yeni taban ayrımıyla görünür yol poligonu bileşeni yedi; önceki beş sayısı bu sürüm için geçerli değildir. Yüzeylerin tamamında boşluk ve pozitif alanlı örtüşme sıfır; gerçek kafe taban/yol farkı yalnız kayan nokta toleransında.

Ağaç: kaynak uç dal yaprak aşaması eklendi ve ikinci gövde kaldırıldı. Güncel yakın model 122.245, uzak 3B 6.942 üçgen; GLB 12.206.208 bayt. Uzak atlas artık aynı yakın GLB'den Three.js r186 ve sahne ışıklarıyla üretiliyor. 16 açı, kareler 512², atlas 2048² / 3.323.778 bayt. Yakın/uzak kaynak GLB SHA'sı, renk faktörü, gerçek kodlanmış PNG SHA'sı ve yeniden çözülen kare piksel eşitliği doğrulandı. Canvas ham RGBA ile PNG kodlayıcı yuvarlamasının özdeşliği iddia edilmez. Cycles ayrı açık yedek yol olarak kaldı. Deneme hâlâ `forest=2` ile açılır; varsayılan yapılmadı.

Bölgesel modeller: gerçek sınırlar/kamera görünürlüğü ve seçili alan önceliği, iki eşzamanlı yükleme, görünmeyen varlıklar için dört model / yaklaşık 96 MiB yumuşak önbellek hedefi eklendi. Önceki denetimde engellenmiş Afrika Köyü aktarımı hata/yeniden deneme durumuna geçti; engel kaldırılıp düğmeye basılınca yedi yapı yüklendi ve kamera kullanılabilir kaldı. Güncel kafe bölgesinde “3B ayrıntıları hazır” ve doğru model bağlantısı doğrulandı. Tüm alanlara uzun kullanım/perf kabulü henüz verilmedi.

### Tarayıcı kanıtı ve karşılaştırma koşulları

- Kaynak: `design-reference/woodland-aviary-concept.png`, 1672×941 kaynak piksel. Uygulama: `?focus=cage&perspective=65&forest=2`, sürüm `20261015v`.
- Birleşik kanıt: `http://127.0.0.1:8768/design-reference/compare-local.html?forest=2`. Açık tema / dış görünüm / perspektif 65. İki içerik 1280×720 CSS çerçevelerden aynı oranda 612×344'e küçültülerek aynı 1280×720 tarayıcı yakalamasında incelendi. İkinci yakalama `[330,220,650,380]` odak pencerelerini yaklaşık 612×358 olarak birlikte gösterdi. Kadraj ölçekleri eşit; mockup'ın kavramsal peyzaj yerleşimi ölçülü M5 yerleşimiyle birebir değildir ve kaynak koordinatları görsele uydurulmadı.
- Gerçek yakalamalar bu oturumun araç çıktısında; kalıcı PNG dosya yolu dönmedi. Yeni dosya adı uydurulmaz. Bu bağlantı canlı yerel karşılaştırmayı açar.
- `model-review/?model=african-cafe`: eğik ve üst düğmeleri karşılıklı 1/0, ardından 0/1; model tamamen kadrajda. Ana atlas `?focus=region-13&perspective=65`: altı çatı ve çevresi, doğru bölge adı/model bağlantısı görünür.
- Kafe atlası ve güncel `forest=2` ayrı ayrı 390×844 boyutta yakalandı. DOM/canvas 390×844, kaydırma genişliği 390, üst/alt denetimler görünür. İlk doğrudan CDP yakalamasında oluşan bölünmüş/ölçeklenmiş araç görüntüleri kanıt sayılmadı; taze sekmede doğru viewport yakalaması kullanıldı. Geçici emülasyon/viewport kaldırıldı. Bu fiziksel telefon testi değildir.
- Ana atlas, model incelemesi ve mobil deneme hata/uyarı günlükleri boş. Karşılaştırma sekmesinde bir `MutationObserver.observe` TypeError kaydı var; uygulama ve karşılaştırma kaynakları bu API'yi kullanmıyor, sahibi kesin atanmadı. Karşılaştırma görüntüsü çalışıyor; bütün tarayıcı günlükleri boş diye sunulmaz.

### Beş görsel yüzey

Yazı/typografi: okunabilir üst/alt kontroller korunuyor; kaynak font/ikon eşlemesi ayrıntılı kabul almadı. Düzen/aralık: masaüstü ve mobil denetimler görünür, model kadrajları çalışıyor; gerçek yerleşim ile kavramsal kaynak farkı korunuyor. Renk: kafes metali ortak, ağaç kaynak rengi ortak; genel ışık hâlâ daha sert ve soğuk. Görsel kalite: yeni taç dolgunluğu ilerledi, doğal bitki/kıyı çeşitliliği ve yakın ayrıntı eksik. Metin/içerik: model belirsizlikleri incelemede açık, 43 alan listesi korunuyor; eksik bölgeler tamamlanmış gösterilmiyor.

### Kaynak ve yerel erişim

43 kaynak klasörü, 51 resmî fotoğraf kaydı, 86 kroki, 43 özgün M5 bağlamı, sekiz bölgesel GLB varyantı ve ortak ağaç kaynağı doğrulandı. 16 AI raster varlığı ayrı envanterde; CC0 ağaç ayrı lisanslı varlık. Dokuz GLB son Khronos kontrolünde hata 0 / uyarı 0; eski varlıkların bazı bilgi/ipucu kayıtları devam eder. Özgün M5 SHA `022a8805…`, QGIS yol SHA `d5038924…` aynı. `docs/` Git durumu temiz, canlı yayın yapılmadı.

Sunucu 0.0.0.0:8768 üzerinde. Güncel Wi-Fi IP **192.168.0.192**; atlas ve kafe model incelemesi bu LAN adresinden HTTP 200. Bilgisayardan LAN yanıtı fiziksel telefondan bağlanma kanıtı değildir.

**Sıradaki uygulama:** Önce mockup'tan kalan bitki/ışık/kıyı farkları ve güçlü kaynaklı sonraki alan; gerçek telefon performansı ile bölge geçişi denetimi. Bütün hedef tamamlanana kadar aktif kalır.

---

## 15 Ekim 2026 — yedinci yineleme: düzenlenebilir ağaç ve uzak taç denemesi

**Hedef aktif. final result: blocked.** Bu bir peyzaj varlığı denemesidir; yedinci bölgenin tamamlandığı veya mockup düzeyine ulaşıldığı anlamına gelmez. Varsayılan ağaç görünümü korunur. Görsel kabulün geçmemesi çalışmayı durduran dış engel değildir.

### Araştırma, kaynak ve gerçek varlık

- Poly Haven Jacaranda ve Island Tree03 kaynakları, CC0 lisansı ve güncel API açıklaması incelendi. Çok milyon üçgenli glTF'leri doğrudan park boyunca çoğaltma seçilmedi. Jacaranda özgün 180.228.496 bayt Blender dosyası ve 10 kaynak doku URL/MD5/SHA ile doğrulandı. Website örnek render'ı kopyalanmadı; model Bursa'da aynı türün bulunduğu kanıtı sayılmaz. Özgün dosyalar `_qa/tree-assets/jacaranda-source/` içinde, kalıcı URL/SHA manifesti ortak peyzaj klasöründe.
- Kurulu Blender 5.2.1 LTS gerçek RNA arayüzüyle incelendi. Yeni Geometry Nodes modifier değerleri `properties.inputs` içindedir; arayüzün socket default'ları gerçek modifier değeri yerine kullanılmadı. Özgün `leaves_main` öznitelik maskesi korundu. Kaynak betikleri/otomatik çalıştırma kapalı; yalnız bizim üreticilerimiz çalıştırıldı.
- Yaprak prototipleri ayrı UV yüzeylerine ayrılıp hafifletildi; kabuk UV'si yaprak yüzeyine katılmadı. Çok ince dallar kaynak radius özniteliğinden budandı, yalnız ahşap geometri sadeleştirildi. Düzenlenebilir `.blend`, GLB, üreticiler, sanatsal taç oranı girdisi ve tek yerel PowerShell üretim betiği `bolgeler/_ortak/peyzaj/model/` içinde. Yakın 37.393 ve alternatif uzak 3B 6.942 üçgen; GLB 6.091.700 bayt. Kaynak tür, güncel ölçüm veya kapalı CAD sertifikası değildir.
- Normal haritaları 512 px, roughness 256 px, yaprak renk/alpha 1024 px teknik türevlerdir; kaynak dosyalar değişmedi. RGBA gerçek alfa kesimi kullanır, GLB tangent özniteliklerini taşır. Bir dejenere UV kutbuna normale dik birim tangent yedeği gerekti. Son gerçek GLB Khronos denetiminde hata 0/uyarı 0/bilgi 0/ipucu 0. Eski bölge dosyalarının bazı ipucu/bilgi kayıtları devam eder; bütün dosyalara ipucu 0 denmez.

### Denemede öğrenilen ve değiştirilen

İlk yalnız üç küçük yaprak prototipli sürüm ve ilk tam park denemesi fazla seyrekti. Bu görünüm varsayılan yapılmadı. Kaynağın beş yaprak grubunun hafifletilmiş biçimleri eklendi. Eski `r` parametresini tam taç sınırı gibi ele almak da taçları küçültüyordu: önceki kartlı silüet yaklaşık 1,6r'ye ulaşıyordu. Aynı görsel açıklık geri verildi; ağaç XY noktaları ve eski yükseklik parametreleri yerinden oynatılmadı. Bu bir gerçek botanik yarıçap iddiası değildir.

Uzak görünümde tam ayrıntılı kaynak modelin 16 gerçek Cycles render'ı alındı: sekiz azimut, 32/60 derece iki yükseliş, 512² RGBA. Sanatsal taç yüksekliği sıkıştırması hem 3B türeve hem render kaynağına uygulanır. Kareler tek 2048² atlasa piksel değiştirmeden paketlendi; atlas 3.440.649 bayt. Yeniden okunan gerçek geometri, bütün türev SHA'ları, atlas/kare piksel eşitliği ve özgün M5/QGIS değişmezliği doğrulandı.

`?forest=1` iki 3B ayrıntı düzeyini dener. `?forest=2` yakında 3B, uzakta ağaç başına 2 üçgenlik açı seçilen silüet kullanır. Bir ağaç için aynı anda yalnız bir düzey çizilir; önceki yedekler ancak yeni varlıklar tamamen yüklenince gizlenir. Yeni ağaçlar ana Ağaçlar katmanının içindedir. Küçük giriş bitkileri, palmiye ve kafes içi mevcut ağaçlar korunur. Ekran boyutuna göre eşik ve 96/120 px histerezis var. Uzak silüetin sınırlı paralaksı, önceden hesaplanan aydınlığı, açı geçişi ve yakın 3B ile taç farkı henüz görsel kabul almadı.

### Tarayıcı ve yerel erişim kanıtı

Sürüm `20261015r`. Deneme atlası Dış/Giriş/Üst kameralarında yakalandı; yakın dallar ve uzak taçlar görüntülendi. Ağaçlar katmanı 0 ve1 durumları hem erişilebilir ağaç hem gerçek görüntüyle denetlendi; yeni/yedek modeller aynı anda görünür bırakılmadı. Sonunda katmanlar açık, perspektif 65, kroki opaklığı 52 durumları korundu ve ana sekme varsayılan kafes görünümüne döndürüldü.

390×844 emülasyonda deneme hazır, DOM ve canvas 390×844, yatay kaydırma390; yükleme göstergesi yok. Alt/üst denetimler ve kafes çerçeve içinde. Emülasyon kapatıldı. Bu gerçek telefon FPS/bellek ölçümü değildir. Wi-Fi 192.168.0.11 üzerinden atlas, model incelemesi, 6.091.700 bayt GLB, 3.440.649 bayt atlas ve metadata HTTP200.

Mockup ve deneme 1280×720 içerikten 612×344 tam ve 612×358 odak pencerelerinde karşılaştırıldı. Yakalamalar araç çıktısında; kalıcı ekran PNG yolu dönmediği için dosya bağlantısı uydurulmaz. Ana atlas/model günlükleri boş. Karşılaştırma sekmesinde bir MutationObserver TypeError görüldü; uygulama kaynakları bu API'yi kullanmıyor, hatanın sahibi kesin atanmadı. Karşılaştırmanın önce varsayılanı sonra denemeyi yükleyen çift iframe navigasyonu kaldırıldı. Son tek yükleme sonrası yeni hata/uyarı günlükleri boş.

Sekiz GLB biçim doğrulaması hata 0/uyarı 0. Bölge envanteri 43 klasör / 51 resmî fotoğraf kaydı / 86 kroki / 43 özgün bağlam / 7 bölge GLB varyantı; 16 AI raster varlığı aynı kaldı. CC0 peyzaj modeli ayrı varlık setidir. `docs/` Git durumu temiz; canlı yayın yok.

### Kalan kabul işleri

- **[P1] Görsel hedef:** Yeni dal yapısı ve uzak taç bütünlüğü incelenebilir; tek kaynak ağaç tekrarı, düzleşen uzak yaprak biçimi, yakın–uzak taç/ışık uyumu ve mockup'ın sıcak yumuşak ışığı hâlâ karşılanmıyor. Bu nedenle deneme varsayılan yapılmadı. Kafes içi, kıyı/zemin geçişleri ve yakın bitki kartları da sürmeli.
- **[P2] Performans ve kaynak:** Gerçek telefonda FPS/bellek, bölgeye göre model yükleme, farklı ağaç taçları ve LOD geçişi geliştirilmeli. Altı bölge varlığı 1–43 hedefini tamamlamaz; bekleyen bölge modelleri ve saha belirsizlikleri sürer.
- **[P3] Arayüz:** Yazı/ikon eşlemesi ve kapsamlı ekran okuyucu denetimi tamamlanmadı.

Deneme bağlantıları ve yeniden üretim betiği README/kalite kaydında. Hedef aktif kalır.

---

## 15 Ekim 2026 — altıncı yineleme: Afrika Köyü ve yeni tarihî kaynaklar

**Hedef aktif. final result: blocked.** Altıncı bölge varlığı yerel atlas ve model incelemesine eklendi. Bütün1–43 alanın modelleri ve mockup görsel kabulü tamamlanmadı; bu görsel kabul durumu dış engel değildir.

### Kaynak ve model

- Belediye2012 faaliyet raporunun117. sayfası görsel olarak incelendi; Afrika Köyü Barınakları başlıklı327×198 JPEG özgün baytlarıyla çıkarıldı. Tam40,96MB PDF, özgün JPEG, URL/yıl/sayfa/SHA bölge14 kaynaklarında. Fotoğrafın küçük ve tarihî olduğu açık;2026 saha kanıtı olarak sunulmaz.
- M5 dairesel sundurma/saçak izleri3007–3013 fotoğraftaki/krokideki sıra ile yaklaşık eşleştirildi. Yedi saçak toplam546,244784m². Her alt saçak halkasının özgün1080 XY noktası korunur; yorumlanan üst halkalar90 örnek kullanır. Tek kapalı kademeli çatı hacmi, beyaz sekizgen duvar, gerçek kapı açıklığı ve koyu çerçeve var. Bütün yükseklik/duvar yarıçapı/kademe/kapı konumu yaklaşık; M5H değeri geometri yüksekliği yerine geçirilmedi. İç mekân, hayvanlar, arka bağlantı ve ön çit bu ilk bileşende yok.
- GLB52.856 üçgen,7,90MB. Yeniden yüklenen28 geometri sonlu, yönleri tutarlı, kapalı ve pozitif hacimli. Dışa aktarılan yedi çatı izdüşümünün kaynakla toplam simetrik farkı0,0000683835m². Khronos doğrulaması hata0/uyarı0/ipucu0; bir1254² NPOT görsel bilgi kaydı. Gerçek varlık SHA'sı raporda.
- Üretilmiş tek koyu gri-kahverengi ahşap şingıl PNG tüm çatılarda paylaşılır; alan fotoğrafı dokuya yapıştırılmadı.16. varlığın boyut/SHA/son araç promptu ve dikiş/gömülü gölge sınırlamaları `viewer/assets/asset-manifest.json` içinde.

### Yol/yüzey ve kaynak değişmezliği

Yorumlanan363,730171m² taban izi ortak bina maskesine eklendi. Altındaki yol ve çim tekil bölümden çıkarılır; görünür eşdüzlem üst yüz çoğaltılmaz. Bu işlem bir58,405m² avlu parçasını ayırıyordu. Yeni yapıların dışında kalan küçük yorum geçişi yalnız0,24695m² ek kaplama ile bağlantıyı geri verdi. Yol poligon bileşeni sayısı önceki5 düzeyinde, avlu kontrol noktası ana yol bileşeninde. Kaynak QGIS dosyası değiştirilmedi. M5 SHA022a8805… korunuyor; bütün yüzeyler161.120,398859m² sınırı boşluk/çakışma olmadan kaplıyor.

### Ek kaynak incelemesi

Belediye2018 galerisindeki17 özgün fotoğraf indirildi ve temas sayfasında incelendi.16'sı içeriğine göre Amur Kaplanı2, Gergedan3, Penguen2, Savanna3, Lemur5 ve sürüngen iç mekân adayı1 olarak klasörlendi. Son sürüngen görüntüsünün türü/10 alana aidiyeti teyitsiz; ayrı alanın doğrulanmış fotoğrafı diye sunulmaz. Bir genel gölet/araç görüntüsü kesin alana atanmadı. Gergedan başlıklı galerideki bütün fotoğraflar gergedan modeli kanıtı sayılmadı.

Gergedan haberindeki2017–2018 yapım, yeşil çatı ve alan bilgisi kaydedildi; eski M5 izini güncel barınak saymak için yeterli eşleme yok. Envanterde61 mimari görsel kaydı var; bunlar61 benzersiz veya güncel yapı fotoğrafı değildir.43 kaynak klasörü,51 resmî fotoğraf kaydı,86 kroki ve43 özgün M5 bağlamı doğrulaması geçti.

### Tarayıcı kanıtı ve kalan bulgular

Sürüm `20261015n`. `model-review/?model=african-village` eğik ve üst durumları0/1 karşılıklı denetlendi. Eğik kamera ön kapı tarafına bakar. Ana atlas `?focus=region-14&perspective=65` yedi yapının gerçek ayrı sınırlarına göre kadrajlanır; uzun çapraz sıra için tek büyük kutunun fazla boşluğu kaldırıldı ve kamera bahçe içine bakar.390×844 görüntüde yedi yapı/denetimler görünür; canvas ve DOM390×844, yatay taşma yok, yükleme göstergesi kaldırılmış. Geçici emülasyon kapatıldı; bu gerçek telefon kare hızı testi değildir. Görünüm menüsü14 alanını seçili ve doğru model bağlantısını görünür gösteriyor.

Mockup ve çalışan1280×720 sahne,612×344 tam ve612×358 odak penceresinde yeniden yakalanarak karşılaştırıldı. Ana atlas ve model incelemesi hata/uyarı günlükleri boş. Yeni model genel atlası ilerletiyor; kafes çevresinin doğal görünümü hâlâ kabul geçmedi. Yakalamalar araç çıktısında; yeni kalıcı PNG yolu dönmediği için dosya adı uydurulmaz.

- **[P1] Görsel hedef:** Ağaç taçları/kart tekrarları, uzak yaprak pikselleşmesi ve yumuşak sıcak ışık hâlâ mockup'tan geride. Kıyı/zemin doğal geçişleri ve kafes iç ayrıntıları sürmeli.
- **[P2] Alan kapsamı/doğruluk:** Altı varlık bütün atlası tamamlamaz. Afrika Köyü tarihî küçük fotoğraf yorumu; yeni çok açılı kaynak/güncel durum gerekir. Diğer bekleyen alanlar,40 konumu,31/32 kapsamı ve Savanna aday konumu çözülmedi. Yeni2018 Lemur fotoğraflarındaki olgun ağaç/kaya bağlamı sonraki ada revizyonunda karşılaştırılmalı.
- **[P2] Mobil ölçek:** Modeller başlangıçta topluca yükleniyor; artan varlık sayısı için görünürlük/bölgeye göre yükleme geliştirilmeli. Gerçek telefonda süre/bellek/kare hızı henüz yok.
- **[P3] Arayüz:** Yazı/ikon eşleşmesi ve kapsamlı ekran okuyucu kontrolü henüz tamamlanmadı.

LAN192.168.0.11:8768 üzerinden atlas, model incelemesi ve GLB HTTP200; `docs/` Git durumu temiz. Canlı yayın yapılmadı. **Sıradaki çalışma:** doğal taç/ışık ve model yükleme ölçeği; güçlü kaynaklı sonraki alanlar. Hedef aktif kalır.

---

## 15 Ekim 2026 — beşinci yineleme: Lemur Adası ve bitki çeşitliliği

**Hedef aktif. final result: blocked.** Beşinci bölge varlığı üretildi; bütün 1–43 alanın modelleri ve mockup görsel düzeyi henüz tamamlanmadı. Buradaki blocked görsel kabul durumudur; hedef çalışmasını durduran bir dış engel değildir.

### Değişiklik ve gerçek kanıt

- **11 · Lemur:** M5 ada60 ve dış hendek61 koordinatları korunarak düzenlenebilir `model-inputs.json`, Python üreticisi ve `lemur-adasi.glb` eklendi. Ada759,8995695m², su bandı877,242573m². 8 kaya,13 ahşap eleman ve2 ince halatın sayısı/ölçüsü/konumu kamera yorumudur; halat yorumu düşük güvenlidir. Kamera karesinin edinim zamanı kayıtlı, çekim tarihi teyitsiz. Komşu yeşil bina bu varlığa atanmadı.
- Model7.170 üçgen. Gerçek dışa aktarılan ada üst yüzünün kaynakla simetrik farkı0,0000212965m²; su bandı adaya taşmıyor ve ortak-0,32m sunum kotunda. Kapalı hacimler kaynak raporu yerine yeniden yüklenen GLB üzerinden sonlu, pozitif hacimli ve tutarlı yönlü olarak denetlendi. Ahşap UV yönü dalların eksenlerini takip eder. Ana atlas GLB'nin önizleme zemini/su/tabanını gizler; tekil yüzey bölümünü çoğaltmaz.
- Khronos glTF doğrulayıcısı2.0.0-dev.3.10 ile altı GLB tekrar denetlendi: hata0, uyarı0. Lemur için3 NPOT görsel bilgi kaydı, ipucu0; ilk üç varlıkta GPU buffer target ipuçları ve bazı kullanılmayan öznitelik bilgi kayıtları kalıyor. Her raporda gerçek GLB SHA'sı var; bu sonuç tüm modellerin sanat/saha doğruluğunu kanıtlamaz.
- Üç değişmemiş Image Gen PNG eklendi: kavisli palmiye frond'u, ince ot kümesi, oval küçük yapraklı çalı. Boyut, SHA, seçilen son araç promptu ve kenar/alfa sınırlamaları `viewer/assets/asset-manifest.json` içinde. Uygulamada alfa kesimi gerçek boşlukları korur. Radyal kavisli palmiye taçları yalnız yorum amaçlı ek bitkilerde; eski M5 ağaç noktaları tür olarak yeniden sınıflandırılmadı.
- Yol kenarındaki basit yedi üçgen yaprak/çokgen tümsekler bu varlıklarla değiştirildi. Kafes çevresi, orman altı ve kıyıda tür biçimi çeşitlendirildi. Yeni ek bitki sayısı6.844; ek ağaç499, kıyı taşı784, kıyı bitkisi230. Savanna ve Lemur ada içi ek orman bitkilerinden arındırıldı; kaynak M5 verisi aynı SHA ile korunuyor.

### Tarayıcı denetimi

`20261015m` ana atlası, `model-review/?model=lemur` eğik/üst ve `?focus=region-11&perspective=65` yerleşimi gerçek tarayıcı görüntüleriyle incelendi. Üstten/Eğik seçili durumları karşılıklı0/1 değişiyor;11 bölge seçimi model bağlantısını açıyor. Ada çim içi açık, kıyı tek ve tırmanma elemanları görünür.

`design-reference/compare-local.html` içinde mockup ve çalışan1280×720 sahne,612×344 tam çerçevede ve `[330,220,650,380]` odak penceresinde612×358 olarak eşit ölçekte tekrar yakalandı. Artan bitki çeşitliliği/yoğunluğu görünür. Bu oturumun görüntüleri araç çıktısında; kalıcı dosya bağlantısı döndürülmediği için yeni PNG adı uydurulmadı. Canlı yerel karşılaştırma sayfası korunuyor.

390×844 emülasyonda Lemur incelemesi hazır, DOM ve çizim tamponu390×844; yatay taşma yok ve bütün alt denetimler çerçeve içinde. İlk model kadrajı gereğinden küçüktü; küre yerine sekiz köşenin kamera izdüşümüne göre sığdırma uygulandı. Düzeltilen kadrajla390×844 görüntü yeniden yakalandı; model ve kontroller görünür. Geçici emülasyon kapatıldı. Gerçek telefon performansı henüz sınanmadı. Wi-Fi192.168.0.11:8768 üzerinden ana atlas, Lemur incelemesi ve11,35MB GLB HTTP200 döndü. `docs/` Git durumu temiz.

### Kalan bulgular

- **[P1] Doğal bitki/ışık:** Yaprak kartları ve taçların tekrarları hâlâ belirgin; küçük yapraklarda uzak pikselleşme var. Mockup'ın dolgun ve yumuşak orman katmanları, farklı dallanma ve sıcak yerel ışık karşılanmıyor. Yoğunluk artışı tek başına kabul değildir.
- **[P1] Yakın çevre:** Kafes içi, kıyı geçişleri ve çevre yapı malzemeleri hâlâ yaklaşık/sade. Ana metal rengi ve portal kesimleri korunuyor; yakın ve uzak yerel görüntü kabulü devam etmeli.
- **[P2] Kapsam/kaynak:** 43 kaynak klasörü ve5 bölge varlığı tüm atlası tamamlamaz. Lemur görünmeyen tarafı, Savanna bileşeninin aday konumu,31/32 kapsamı ve40 konumu teyitsiz. Kaynak incelemesi ve diğer bölgelerin modelleri sürmeli.
- **[P3] Arayüz/cihaz:** Yazı/ikon eşleşmesi, ekran okuyucu ve gerçek telefon kare hızı tamamlanmadı. Mobil yerel erişim sunucudan doğrulandı; fiziksel telefondan bağlantı kanıtı yok.

**Sıradaki çalışma:** Taç ve kıyı doğal görünümünü geliştirmek; güçlü fotoğraf referanslı sonraki bölge bileşenlerini modellemek. Canlı yayın yapılmaz.

---

## 15 Ekim 2026 — dördüncü yineleme: su, temas gölgeleri, yakın yol ve yeni kaynaklar

**Hedef aktif. final result: blocked.** Yeni bölge modeli bu turda üretilmedi; dört bölge varlığı ve1–43 kaynak kapsamı korunuyor. Bitki ve bütün atlas ayrıntısı mockup seviyesinde değil.

### Güncel görüntü kanıtı

Kaynak: `design-reference/woodland-aviary-concept.png` (1672 × 941). Uygulama: `http://127.0.0.1:8768/?focus=cage&perspective=65`, sürüm `20261015l`. Birleşik karşılaştırma: `http://127.0.0.1:8768/design-reference/compare-local.html`. Kaynak ve çalışan3B sahne1280 × 720 CSS çerçevelerde,1280 × 720 tarayıcı görüntüsünde612 × 344 boyuta eşit oranda küçültülerek birlikte incelendi. Aynı durum/açık tema/perspektif%65 kullanıldı. Odaklı karşılaştırma iki çerçevenin `[330,220,650,380]` penceresini yaklaşık612 × 358 gösterdi. Su, kafes çizgileri, kıyı ve bitki tekrarları ayrıca bu görüntüde incelendi. Yakın yol taşları ayrı giriş görünümünde karşılaştırıldı.

Bu oturumun tarayıcı yakalamaları araç çıktısında incelendi; kalıcı JPEG dosyası yazan bir API sunulmadığı için yeni ekran görüntüsü dosya yolu yok. Canlı karşılaştırma URL'si ve bu oturum görüntüleri kullanıldı; eski PNG'ler güncel sürümün kaydı olarak sunulmaz.

### Önceki bulgulara uygulanan değişiklikler

- Önceki düz su ve zayıf temas hissi için GTAO ve yansımalı su eklendi. Alfa boşluklarını gerçek renk geçişinin derinliği korur; yapraklar opak dikdörtgen normal kartına dönüştürülmez. Mevcut cihazın RGBA16F,4 örnekli renk hedefi ve768piksel AO üst sınırı konsolda doğrulandı. Değişince çizim korunur. Desteklemeyen donanım için doğrudan çizim yolu var; `finish=0` ile zorlanan yol ayrıca tarayıcıda görünür ve hatasız sınandı. Bu test gerçek eski telefon donanımı testi değildir.
- Su12 poligon yerine tek geometri/yansıma geçişinde çizilir. Gerçek çizilen791 üçgenden alan6970,6603552m²; kaynak6970,66036m². Aynı görünür su bölgesi iki kez çizilmez. Yeni yansıma ve dalga normalleri odaklı karşılaştırmada görünür; ilk renksiz/gri deneme geri çekilip turkuaz saçılma düzeltildi. Ortografik bakışta aynı geometri mat malzeme kullanır. Bakış açısı0→100→65 işlendi; hata/uyarı yok.
- Sunum su kotu-0,32, arazi-0,24. Bu düzen suyu arazi altında tutar; ölçülmüş M5/H kotu değildir. Penguenin bağımsız GLB su seviyesi aynı kaynaktan gelir, ihraç edilen gerçek düğüm yüksekliği doğrulanır.
- Tek yol yüzeyinde küçük bump yorumu var; kaynak albedodan veri kanalı, genlik0,035m. Ölçülmüş yükseklik haritası olarak sunulmaz.10.045 kenar taşı55 mekânsal partide; yakında80, uzakta20 yüzlü şekil. Aynı dönüşüm ve renkler paylaşılır, bir partide tek LOD çizilir. Giriş görüntüsünde eski köşeli taşlar yerini daha yumuşak taşlara bıraktı; yol XY geometrisi değiştirilmedi.
- Kroki yerel dosyadan yükleniyor. DOM'da yerel `reference-maps/2026-09-resmi-kroki.jpg`,1600 × 864 doğal boyut ve%52 opaklık doğrulandı. Paket kopyasının SHA'sı özgün resmî dosyayla aynı. Katman kapatılıp ilk duruma döndürüldü; kaynak bağlantısı korunuyor. Araştırma fotoğrafları yayın paketine taşınmadı, `docs/` değiştirilmedi.
-390 × 844 mobil emülasyonda DOM/sahne/çizim tamponu aynı boyutta; yatay taşma yok. Kafes ve alt kontroller tümüyle kadrajda. Gerçek telefonda kare hızı veya bağlantı testi yapılmadı. LAN adresinden atlas ve yerel kroki HTTP200 döndü. Geçici emülasyon kapatıldı.
- Model incelemesi yalnız değişince çiziyor. Savanna üstten/eğik düğmelerinin karşılıklı seçili durumu düzeltildi; son tarayıcı durumu Üstten1/Eğik0 ve ardından Üstten0/Eğik1 olarak doğrulandı. Ana atlas ve model incelemesinin hata/uyarı günlükleri boş.

### Kaynak envanteri ilerlemesi

Dört belediye akışından birer kare: Habeş640 × 360, Lemur1920 × 1080, Savanna640 × 360, Gergedan640 × 360. Edinim zamanı/URL/SHA, ayrı sayfa arşivleri ve görsel rol kaydedildi. Çekim zamanı veya görüntünün güncel saha durumunu temsil ettiği teyit edilmedi. Lemur karesinde ada kıyısı, kayalar, ahşap tırmanma elemanları ve komşu kırma çatılı yeşil yapı görülüyor; komşu yapının aidiyeti belirsiz. Bu, sonraki lemur ada bileşeni için en güçlü yeni bağlamdır. Penguen ve su kuşları akışında bu denemede kare edinilemedi; yokluk kaydı var, veri varmış gibi sunulmaz.

Afrika Kafe'nin2011 açılış kaydından9 küçük150² fotoğraf ve2 kaynak sayfası arşivlendi. Bir tam boy fotoğraf ve haber videosu404 döndü; diğer tam boy dosyalar ayrı ayrı doğrulanmadı. Küçük tören fotoğrafları tam mimari ölçü veya2026 durumu kanıtı değildir. Mimari/çevre bağlamı kaydı toplam44; hepsi benzersiz mimari görünüm anlamına gelmez.43 alan,51 resmî fotoğraf kaydı,86 yerel kroki ve tüm kayıtlı dosya SHA'ları doğrulandı.

### Kalan bulgular / beş zorunlu yüzey

- **[P1] Görüntü ve varlık kalitesi:** Taçlar, bitki kümeleri ve kıyı varlıkları hâlâ tekrar ediyor. Kaynağın palmiye/çalı/yer örtüsü çeşitliliği ve doğal dallanması eksik. Yakın yaprak kartları kâğıt gibi okunabiliyor; gölge efekti bu geometri farkını çözmüyor. Yeni botanik varlıklar ve yakın LOD ayrıntısı gerekir.
- **[P1] Renk ve ışık:** Su/temas/taş hissi ilerledi; genel çayır hâlâ tek tonlu, ışık ve malzeme çeşitliliği mockup kadar doğal değil. Su saçılması, bitki tonları ve yerel nem/taş geçişleri yinelemeli karşılaştırılmalı. İlk gri su denemesi güncel sürüm değildir.
- **[P2] Yerleşim ve aralık ritmi:** UI ve ana kadraj korunur. Mockup'taki peyzaj kümeleri ile gerçek M5/kroki yerleşimi farklı; ölçülü ana konumlar mockup'a benzetmek için oynatılmaz. Aynı koordinatların içinde daha iyi varlık/malzeme ve çevre ayrıntısı gerekir.
- **[P2] Metin/içerik ve kapsam:** Tüm43 kaynak klasörü ve konum durumu listeleniyor; dört bölge modeli bütün atlası tamamlamaz.40 numara konumu ve bazı yapı aidiyetleri belirsiz. Kamera edinim tarihi çekim tarihi değildir; kaynak metinleri bu sınırları açıkça korur.
- **[P3] Yazı:** Krem/yeşil UI, Inter/Arial yazı yığını ve beşli çubuk korunur. Mockup'ın küçük yazı biçimiyle tam font eşlemesi ve kapsamlı ekran okuyucu denetimi yapılmadı. Mobil taşma ve temel model seçim durumları kontrol edildi.

**Sonraki çalışma:** Yeni lemur referansından ada/kaya/tırmanma bileşeni; kaynak mockup'taki farklı botanik siluetler ve yakın bitki ayrıntıları; materyal/ışık karşılaştırması. **final result: blocked.** Görsel kabul geçmedi; geliştirme hedefi aktif, dış bir engel nedeniyle durmuyor.

---

## 15 Ekim 2026 — üçüncü yineleme: 43 bölge bağlamı ve dördüncü model

**Durum: hedef aktif. final result: blocked.** Bu bir ara geliştirme kaydıdır; bütün alanların modeli ve mockup düzeyi tamamlanmadı.

### Bu yinelemenin kanıtı

Kaynak `design-reference/woodland-aviary-concept.png` (1672 × 941). Yerel uygulama `http://127.0.0.1:8768/?focus=cage&perspective=65`. Karşılaştırma `http://127.0.0.1:8768/design-reference/compare-local.html` içinde tek tarayıcı görüntüsünde yan yana incelendi. İki içerik de 1280 × 720 CSS çerçevede; 1280 × 720 tarayıcı görüntüsünde yaklaşık 612 × 344 boyuta eşit oranda küçültüldü. Durum: kafes dışı, açık tema, perspektif %65. Yakın ayrıntı karşılaştırması aynı iki çerçevenin `[330,220,650,380]` piksel penceresini yaklaşık 612 × 358 gösterdi. Kafes ağı, bitki tekrarları, su ve yol kenarı bu odaklı görüntüde ayrıca incelendi.

Güncel tarayıcı görüntüleri araç çıktısında incelendi; bu oturum için kalıcı PNG ekran görüntüsü dosyası sağlanmadı. Eski 14 Ekim PNG'leri bu sürümün kanıtı değildir. Canlı karşılaştırma URL'si, güncel dosyalar ve bu yinelemenin tarayıcı yakalamaları kanıttır; kalıcı ekran kaydı dosyası olmadığı ayrıca kabul sınırıdır.

- 43 alanın kroki kesit görünümü, konum JSON'u ve eski M5 bağlam JSON'u üretildi. Kaynak koordinatları ve öğe özellikleri aynen korunduğu doğrulandı. 42 alan konumlu; 40 numaralı çocuk oyun alanı belirsiz. Arayüz 43 alanı listeliyor, belirsiz alanı konum seçimi için devre dışı gösteriyor. 42 numara seçildiğinde altı kroki noktası birlikte kadraja girdi. Bölge12 seçiminde bağımsız model bağlantısı çalıştı.
- İkinci koyu yaprak türü, geniş yapraklı alçak rozet ve ağaç kabuğu dokusu eklendi. Görsel yorum yerleşimi 496 ek ağaç, 4.631 bitki, 934 kıyı taşı ve 279 kıyı bitkisi içerir. Yeni ağaç ve alçak bitkiler açık Savanna içinden çıkarıldı; kaynak M5 ağaçları silinmedi. Üreticide araziye yerleşim kontrolleri geçti.
- Işık oranı değiştirildi. Yaprak kartlarını doğrudan StandardMaterial ile aydınlatma denemesi koyu lekeler ürettiği için geri alındı; sınırlı yön tonlamalı alfa kartları kullanılıyor. Bu, fiziksel yaprak saçılma modeli olarak sunulmaz. Odaklı son karşılaştırmada siyah lekeli ara deneme bulunmuyor.
- Dördüncü varlık Savanna ahşap yapının ilk bileşeni: 7.676 üçgen, M5 aday sundurma145 için 33,448255 m² çatı izi. Fotoğrafla konum ve kesin işlev teyitsiz. Dışa aktarılan GLB'den geri ölçülen ayak izi farkı 0,00000115 m². Dört malzeme grubunda kapalı hacim/tutarlı yön/pozitif hacim doğrulandı. Çatı/ahşap/döşeme saklı birleşimleri kesildi; format doğrulayıcı sonucu 0 hata, 0 uyarı, 0 ipucu, yalnız NPOT boyut bilgisi. Aynı ahşap haritası tek resim/tek doku olarak paylaşılır.
- Önceki “iki zürafa barınağı fotoğrafı” tanımı düzeltildi. 8895 yükseltilmiş ahşap yapıyı gösterir; 8948 taş sınırda zürafa beslenmesini gösterir ve yapının başka açısı değildir. Kaynak rolleri, üretici ve model girdileri düzeltildi.
- 390 × 844 emülasyonda ana bölge menüsü yatay taşma yapmadı. Savanna modeli bu boyutta kadrajda, alt üç görünüm düğmesi tamamen görünür kaldı. Kısa tarayıcı yüzeyinin doğrudan yakalamasında oluşan tekrar artefaktı daha yüksek yüzeyde yeniden yakalanarak ayrıştırıldı; DOM'da ikinci başlık bulunmuyordu. Üstten→eğik dönüşünde eski seçili üstten durumu düzeltildi ve son ARIA durumu doğrulandı. Geçici emülasyonlar kapatıldı.
- Ana atlas ve model incelemesinin hata/uyarı günlükleri boş. LAN adresinden ana sayfa ve model incelemesi HTTP200 döndü. Bu, gerçek telefon performansının veya telefonun Wi-Fi bağlantısının sınandığı anlamına gelmez.

### Kalan bulgular ve gerekli yüzeyler

- **[P1] Görüntü kalitesi / varlıklar:** Koyu ve açık taç ayrımı ilerleme; kart tekrarları, eşit taç biçimleri ve yapay düşük bitki kümeleri odaklı karşılaştırmada görünür. Kaynaktaki palmiye, geniş yapraklı çalı, değişken dallanma ve katmanlı kıyı bitkileri henüz karşılanmıyor. Geniş yaprak kartının ince kenar rengi sonraki yakın görünümde iyileştirilmeli.
- **[P1] Renk / malzeme / ışık:** Yol sıcak, çelik ortak gri-yeşil; su hâlâ düz turkuaz, zemin tek tonlu ve temas gölgeleri kaynak kadar zengin değil. Kaynağın doğal ışık/yerel gölge hissi geçmedi. Yeni doku kullanımı tek başına kabul değildir.
- **[P2] Yerleşim / ritim:** Kubbe boyutları ve M5/kroki yolu öncelikli. Kaynağın çevre yapı ve bitki kompozisyonu birebir değil; sahne ortasında daha fazla açık çim var. Gerçek veriyi mockup uğruna değiştirmeden varlık ve malzeme ayrıntısı geliştirilmeli.
- **[P2] İçerik / kapsam:** 43 kaynak klasörü var, dört bölge varlığı bütün alanların modellerini tamamlamaz. Savanna'nın yalnız bir bileşeni var; aday yerleşim teyitsiz. Model durumu kullanıcıya açıklanır.40 konumu çözülmedi.
- **[P3] Yazı / arayüz:** Krem-yeşil denetimler ve beşli çubuk korunuyor; yazı ailesi Inter/Arial, mockup'taki küçük yazı biçimiyle tam eşleşme doğrulanmadı. Temel menü, bölge seçimi ve model görünüm durumları kontrol edildi; kapsamlı ekran okuyucu testi ve gerçek telefon kare hızı henüz yok.

**Sıradaki uygulama:** Doğal taç/dal ve kıyı varlıkları; su ve temas gölgeleri; iyi mimari fotoğrafları olan sonraki bölgeler. Yerel karşılaştırma yinelenmeli. **final result: blocked**; bu görsel kabul durumu hedefi durduran bir dış engel değildir.

---

## 15 Ekim 2026 — güncel ara sürüm

### İkinci yineleme: üçüncü bölge modeli ve uzak örgü

Penguen havuzu üçüncü bölge varlığı olarak eklendi. On belediye fotoğrafı ve üç yerel belge kaydı kaynak manifestinde doğrulandı; Afrika Savana için ayrıca iki zürafa barınağı fotoğrafı ayrıldı. Penguen modelinde 15.425 üçgen, kapalı havuz gövdesi, kaya duvar, açık çakıl kıyı ve ahşap seyir platformu var. Ana atlasın su/çakıl yüzeyleri tekil kalır; bağımsız varlığın karşılık gelen düğümleri atlasta gizlenir. Model 2017 fotoğraf yorumudur; M5 204,74 m² su izi ile tarihî duyurunun 300 m² değeri arasındaki fark çözülmedi.

Uzak kafeste 186 kalın kirişin arasına 1.962 ince çizgi parçasıyla yaklaşık tam örgü temsili eklendi. Yakın/uzak GLB ve atlas aynı çelik taban rengini kullanır. Uzak GLB doğrulayıcısında hata/uyarı yok; önizlemede çizgiler ve portal açıklıkları görüldü. Dış kamera daha geniş yan profilden bakacak şekilde değiştirildi. Kaynak ve çalışan sahne yine 1280 × 720 çerçevelerde birlikte yakalandı: kubbe oranı ve ağın devamlılığı önceki ara sürüme göre hedefe daha yakın. Örgü hâlâ çok düzenli ve yer yer parlak; nihai görsel kabul değildir.

Meşe yaprak kartlarına ayrı eğrelti alfa kartı eklendi; bitki türü silueti çeşitlendi. Güncel görsel yerleşimde 436 ilave ağaç, 3.158 bitki, 934 kıyı taşı ve 296 kıyı bitkisi var. Penguen çakıl bölgesi bitkilendirmeden çıkarıldı. Çim ile çakıl malzeme bölgeleri arasında pozitif örtüşme **0 m²**; bütün yüzey bölümü kapsama/örtüşme kontrolleri geçti.

Penguen odağı için tarayıcı emülasyonunda hem DOM hem sahne boyutu **390 × 844** olarak doğrulandı ve doğrudan tarayıcı görüntüsü incelendi; model ve kontroller kadrajda kaldı. Geçici emülasyon kapatıldı. Bu, gerçek telefonda performans veya Wi-Fi bağlantı testi yerine geçmez. Ayrı model incelemesindeki su gölge çizgileri giderildi: şeffaf su opak gölge olarak yazılmıyor; uygun gölge ofseti ve havuz tabanı var. Ana atlas ve model incelemesinin hata/uyarı günlükleri temizdi.

**Güncel kabul: final result: blocked.** P1 bitki/malzeme/ışık farkları sürüyor; üç bölgeye ait ilk modeller bütün 1–43 kapsamını tamamlamıyor. Geliştirme hedefi aktif.

**Durum: hedef aktif, görsel kabul geçmedi.** Son karşılaştırma `design-reference/compare-local.html` üzerinden tarayıcıda yan yana yapıldı. Kaynak görsel ve gerçek 3B iframe, ayrı ayrı 1280 × 720 çerçevede aynı ölçekte küçültüldü. Durum: kafes dışı, perspektif %65. Bu oturumda yakalanan tarayıcı görüntüsü incelendi; aşağıdaki 14 Ekim PNG dosyaları yeni sürümün ekran kaydı değildir.

### Değişiklikler ve kanıt

- Geometrik ağaç taçları alfa kesimli yaprak kümelerine dönüştürüldü. Ana dallar, farklı taç boyutları ve siluet değişimleri eklendi. Zemin altında kalan çalı kartlarının yerleşimi düzeltildi. İlave 436 ağaç, 3.161 bitki, 968 kıyı taşı ve 307 kıyı bitkisi görsel yorum olarak kaynak kaydına işlendi; merkezlerinin tekil arazi alanında bulunduğu üreticide doğrulandı.
- Tek yol yüzeyine sıcak taş, tek arazi yüzeyine çayır görüntüsü atandı. Yeni eşdüzlem üst yüz eklenmedi. Su/yapı/yol/arazi arasında pozitif alan örtüşmesi **0 m²**, açıkta kalan alan **0 m²**.
- Türk Köyü ikinci model olarak eklendi: dokuz çatı bölgesi, taş alt duvar, ahşap ayrıntılar, kiremit kırma çatı ve 18 gerçek cephe açıklığı. Model genel bina kabuğundan çıkarıldı; çift bina çizilmiyor. Pencereler ve çatı eğimleri yorumdur. glTF hata/uyarı yok; format doğrulaması görsel kabul değildir.
- Bağımsız model incelemesinde model seçimi, kubbe yakın/uzak geçişi ve Türk Köyü üstten görünümü çalıştı. Ana perspektif kontrolünün %0 ve %100 uçları işlendi; eğik görünüm ekranda doğrulandı ve %65'e geri alındı. Ana atlas hata günlüğü boştu. Karşılaştırma sayfasının günlüğünde kaynağı belirtilmeyen bir `MutationObserver.observe` hatası görüldü; proje kaynaklarında MutationObserver kullanılmıyor, kökeni kesinleştirilmedi.
- 43 kaynak manifesti ve dosya özetleri doğrulandı. 51 resmî fotoğraf kaydı, 86 yerel kroki kopyası ve ayrı mimari referanslar var. Yanlış türle eşleşen yedi kayıt ilgili alana ayrıldı. Fotoğraf kayıtları aynı görüntünün farklı çözünürlüklerini içerebilir; belge bağlantıları arama adayıdır.

### Açık görsel bulgular

- **[P1] Bitki ve zemin çeşitliliği:** Daha yoğun taçlar ve görünür çalılar ilerleme sağladı; kaynakta görülen farklı bitki türleri, dallanma, yer örtüsü ve katmanlı orman hissi henüz karşılanmıyor. Yaprak kartları özellikle yakın görünümde tekrar ediyor. Alfa kartların kullanılması tek başına doğal görünüm kabulü değildir.
- **[P1] Malzeme ve ışık:** Taş yol, kıyı taşları ve kiremitler görünür; sahne hâlâ düz ve tek tonlu alanlar içeriyor. Mockup'ın yerel gölgeleri, nemli kıyı geçişi ve zengin yeşil/kahverengi malzeme çeşitliliği eksik. Yol şekli ve yapı konumları görsel hedef uğruna değiştirilmez; güncel kroki/M5 eşlemesi önceliklidir.
- **[P2] Uzak kafes ağı:** Ortak çelik tonu ve kalın seyrek kirişler okunuyor; hedefteki sürekli ince ağ silueti henüz yok. İki uçtaki portal açıklıkları korunarak uzak sunumun iyileştirilmesi gerekiyor.
- **[P2] Bölge kapsamı:** İki bölgeye ait ilk varlıklar var; 1–43 alanın tamamı modellenmedi. Diğer bina kütleleri temel kabuk düzeyinde. Türk Köyü'nün tarihî referansı güncel çok açılı fotoğrafla desteklenmeli.
- **[P3] Arayüz:** Ana yerleşim, krem/yeşil tonlar ve görünüm çubuğu tutarlı; küçük metin ve ikon biçimleri kaynakla bire bir değil. Bu turda kapsamlı klavye/ekran okuyucu kontrolü yapılmadı. Gerçek telefonda kare hızı ve bağlantı sınanmadı.

**final result: blocked** — açık P1/P2 görsel farklar nedeniyle tamamlanmış tasarım devri yapılmaz. Bu durum uygulama çalışmasını durduran bir engel veya hedefin `blocked` statüsüne geçirilmesi değildir; geliştirme hedefi aktiftir.

---

## 14 Ekim 2026 — önceki karşılaştırma ve geçmiş bulgular

**Kaynak görsel:** `design-reference/woodland-aviary-concept.png` (AI ile üretilmiş tasarım mockup'ı; 1672 × 941 piksel).

**Çalışan uygulama:** `http://127.0.0.1:8768/?focus=cage`, `design-reference/live-3d-outside-2026-10-14.png` (1280 × 720 CSS piksel ve ekran pikseli).

**Durum:** Kafes dışı; masaüstü 1280 × 720, perspektif %45, açık tema.
**Normalizasyon:** İki görüntü, oranları korunarak tarayıcı karşılaştırmasında 1220 × 686 CSS piksele ölçeklendi. Birlikte görüntü: `design-reference/mockup-vs-live-2026-10-14.png` (2496 × 754 ekran pikseli; iki içeriğin tamamı görünür). Yerel `audit-2026-10-14/product-design/21-mockup-canli-karsilastirma.png` ilk ara sürümle karşılaştırmaydı.

## Bulgular

- **[P1] Peyzajın görsel yoğunluğu ve varlık kalitesi farklı.** Kaynakta çeşitli boylarda doğal ağaçlar, çalılar ve yer örtüsü alanı dolduruyor. Çalışan sahnede tekrarlanan geometrik taçlar ve seyrek çalılar büyük düz çim alanları bırakıyor (`38` yan yana görsel). Sonuç, kullanıcının beğendiği orman hissine ulaşmıyor. Sonraki görsel aşamada kaynak M5 ağaç konumlarını koruyarak birkaç doğal siluet, yaprak dokusu ve mesafeye göre LOD eklenmeli; yeni gerçek dünya konumu uydurulmamalı.
- **[P1] Yol ve kıyı yüzeyi mockup'ın dokusuna ulaşmıyor.** Kaynakta sıcak taş/toprak ayrıntısı, kıvrımlı ve bitkilerle yumuşak kenarlar var. Canlı yolda tek sahip yüzey ve taş bordür uygulansa da geniş açık bej kaplama hâlâ düz; su kıyısı da az ayrıntılı (`38`). Var olan bölünmüş yol/su geometrisinin malzemesi ve 3B kenar parçaları geliştirilmeli; ikinci çakışan üst yüz eklenmemeli.
- **[P2] Kafesin uzak kabuk okuması farklı.** Kaynakta ince, gri, sürekli ağ silueti var; canlı sahnede seçilmiş, daha kalın açık çubuklar ve büyük boşluklar var (`38`). Çubuklar kullanıcı isteğiyle seyrek bırakılıp 9 cm yarıçapa kalınlaştırıldı; yakın ve uzak LOD aynı çelik malzemeyi paylaşıyor. Kaynağa yaklaşmak için tek uzak LOD içinde açıklıkları gerçekten kesilmiş hafif ağ yorumu ve daha doğal ton/ışık denenebilir. Bu, ölçülü boru çapı olarak sunulmamalı.
- **[P2] Kütleler ve ışık karakteri farklı.** Mockup'taki binalar çevre peyzajına gömülü, sıcak gölgeli; canlı binalar ayak izi doğru olsa da yalın bloklar. Cephe/çatı ayrıntısı ancak güncel çok açılı fotoğrafla doğrulanınca eklenmeli. Işık ve malzeme tonları da aynı aşamada yakınlaştırılmalı.

## Beş görsel yüzeyin kontrolü

- **Tipografi:** Sol marka, üst kontroller ve alt görünüm çubuğunun hiyerarşisi kaynağa yakın. Küçük metinlerde biçim farkı var; P3.
- **Boşluk ve yerleşim:** Arayüz konumları benzer, kafes ve komşu yollar yaklaşık aynı görsel bölgede. Kamera açısı bire bir aynı değil; bu karşılaştırmada kompozisyon farkı P2, peyzaj ayrıntısı farkı daha baskın.
- **Renkler:** Arayüzün krem ve koyu yeşil token'ları yakın; sahne kaynaktaki zengin sıcak yeşil/kahverengi yerine pastel ve soluk. P1/P2 görsel bulgularına dahil.
- **Görüntü ve varlık kalitesi:** Kaynağın fotoğraf hissindeki bitki ve yol ayrıntıları çalışan 3B geometrik varlıklarla eşdeğer değil; ana P1 farkı.
- **Metin ve içerik:** Bahçe adı, Su Kuşları Kafesi bağlamı ve görünüm kontrolleri tutarlı. Kaynak yalnız dış görünümü gösterdiği için diğer durumların metni kaynakla bire bir değerlendirilemez.

## İşlev ve önceki yinelemeler

İlk denetimde kapı açıklığından geçen teller, mobil yakın kadraj, uzak kafes okuması, ham yol yüzeyi ve etkisiz perspektif kontrolü bulundu (`audit-2026-10-14/product-design/REPORT.md`, ekran 01–10). Kapı hacmi çubuk/düğüm/ağdan kesildi (`23`, `31`); mobil içeride köprü, su ve ahşap yapının bir bölümü birlikte görünüyor (`25`). Uzak LOD seyrek ve kalın, yakın LOD tam örgü; iki LOD aynı anda çizilmiyor. Perspektif %0 üstten, %100 okunur eğik plan veriyor; Giriş/İç sabit göz hizasında slider pasif ve açıklamalı (`35`, `36`). Geometri denetimi 0 katman örtüşmesi, 0 yakın eşdüzlem bina duvarı ve 0 dejenere Float32 üçgen raporladı. Tarayıcı hata günlüğü boştu.

Giriş (`31`) ve mobil ekranlar (`23`–`25`, `35`–`36`) odak kanıtıdır; dış görünümdeki en önemli ayrıntılar yan yana tam görünümde okunabildiği için ayrıca kırpılmış kafes görüntüsü gerekmedi. Klavye odağı, ekran okuyucuyla kullanım ve düşük güçlü telefonda kare hızı bu turda ölçülmedi.

## Sonraki uygulama sırası

1. Kaynak konumları koruyan doğal ağaç/çalı varlıkları ve mesafe LOD'ları.
2. Tekil yol yüzeyine sıcak taş/toprak malzemesi; kıyı ve bordürde 3B çeşitlilik.
3. Uzak kafes siluetine açıklıkları kesilmiş hafif ağ yorumu ve iki mesafede ortak ton testi.
4. Doğrulanmış cephe fotoğraflarıyla bina ayrıntıları; masaüstü/mobil ekran, çizim çağrısı ve çakışma testleri.

**final result: blocked** — seçilen mockup'ın görsel yoğunluğu ve malzeme/varlık kalitesiyle ilgili P1 farklar sürüyor. Mevcut sürüm teknik ve etkileşimsel bir ara aşamadır; mockup'ın sadık uygulaması olarak devredilmez.
