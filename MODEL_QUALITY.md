# 3B model kalite ilkeleri ve kaynak dayanakları

14 Ekim 2026. Bu sahne güncel ziyaretçi krokisi ile eski M5/DGN metre verisini birlikte yorumlar. Görsel ayrıntılar, ölçülmüş aplikasyon olarak sunulmaz. Her revizyonda kaynak, ölçü ve yorum ayrımı korunur.

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
- Kaynak M5 koordinatları milimetre düzeyindeyken geometrik kesişimler mikroskobik sahte şeritler üretebilir. Ortak maske/çatı/duvar temizliği kaynak hassasiyetinden ince bir toleransla yapılır; son çizilen M5 bina alanının kaynak birleşiminden farkı **0,002403 m²** olarak kaydedilir. Bina tabanı ile su/yol/çim arasında pozitif örtüşme, yakın eşdüzlem duvar çifti ve Float32 kapak/duvar üçgenlerinde sıfır alan bulunmadığı üretim sırasında sınanır. Bu sayılar yeni kaynak veya algoritma revizyonunda yeniden üretilmelidir.
- Yol birleşimleri tek bir 2B birleşik alan olarak işlenir. Kesimden sonra her dış halka ve delik geçerli, doğru yönlü ve sıfır uzunluklu kenarsız olmalıdır. Yuvarlatma sonrasında yeniden doğrulanır.
- Yüzey çakışmasını yalnız derinlik ayarıyla gizlemeyiz. Three.js'in [`polygonOffset`](https://threejs.org/docs/pages/Material.html) özelliği çıkartma veya vurgulu kenar gibi özel katmanlar içindir.
- Başka bir formata aktarım gündeme geldiğinde [glTF 2.0'ın metre, üçgen topolojisi ve dejenerasyon kuralları](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html) izlenir ve [Khronos glTF Validator](https://github.com/KhronosGroup/glTF-Validator) çalıştırılır. Bu canlı Three.js sahnesi şu anda glTF dosyası değildir; doğrulayıcı mevcut JS geometrisini kendiliğinden denetlemez.

## Görüntü ve kabul ölçütleri

Tekrarlanan çubuk, düğüm ve bordür taşları [`InstancedMesh`](https://threejs.org/docs/pages/InstancedMesh.html) ile toplu çizilir. Perspektif kameranın yakın ve uzak kesim düzlemleri bahçenin gerçek sahne boyutuna göre seçilir; [Three.js kamera rehberi](https://threejs.org/manual/pages/cameras.html) gereksiz geniş aralığın derinlik hassasiyetini düşürdüğünü açıklar.

Her sahne üretiminden sonra şu kontroller yapılır:

1. Üretilen 2B yüzeyler geçerli olur; su/yapı/yol/çim çiftleri arasında pozitif alanlı kesişim kalmaz. Çatı maskesi alanı korunur, çatılar birbirini örtmez.
2. Portal hacminde taşıyıcı veya ağ üçgeni bulunmaz.
3. Masaüstü ve mobilde genel, dış, giriş ve iç bakışlar görsel olarak incelenir; geçit, kubbe silueti, yollar ve su okunur.
4. Tarayıcıda hata, eksik kaynak ve belirgin derinlik titremesi bulunmaz; çizim çağrısı/üçgen sayısı gerekirse `renderer.info.render` ile ölçülür. `verify_building_shell.mjs` gerçek Three.js Float32 geometrisindeki dejenere üçgenleri yayın öncesi denetler.

Güncel krokideki konum eşlemesinin yaklaşık hatası ve M5 yol genişliğinin geçici durumu [CURRENT_PLAN.md](CURRENT_PLAN.md) ile [README.md](README.md) içinde ayrıca belirtilir.
