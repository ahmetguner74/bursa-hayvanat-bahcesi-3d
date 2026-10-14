# Seçilen mockup ile çalışan 3B atlas: tasarım QA

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
