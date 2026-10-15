# Mobil hayvan keşfi · Product Design QA

16 Ekim2026 · `20261016au` · yerel yayın öncesi denetim.

## Kapsam ve bulgular

Kullanıcının dört telefon ekranı ve mobil düzeltme isteği referanstır. Penguen, gergedan, zürafa ve flamingonun genel plan → yakın alan → birey → tepki/takip → geri dönüş akışları incelendi. [Numaralı akış ve bulgular](design/2026-10-16-mobil-denetim/audit.md), [plan](design/2026-10-16-mobil-denetim/plan.md), [tarayıcı ölçümleri](design/2026-10-16-mobil-denetim/browser-checks-au.json). Önceki AT raporu [arşivdedir](design/2026-10-16-mobil-denetim/qa-at.md).

P1 geniş mobil kart, uzak penguen odağı ve belirsiz flamingo tepkisi giderildi. Flamingo giriş/çıkışındaki kapı rotası kaldırıldı. P2 mobil dokunma keşfi, uzun hareket adı taşması, erişilebilir durum duyurusu ve yayın SVG eksikliği düzeltildi. Kök yükleme hatasında çalışan tekrar yükle yolu eklendi. Kapsam içinde açık P0/P1/P2 kalmadı.

## Birlikte görsel karşılaştırma

[Referans ve AU tam görünüm levhası](design/2026-10-16-mobil-denetim/reference-comparison-au.jpg) aynı girdide açılıp incelendi. Kullanıcı dosyaları590×1280px; uygulama alanı yaklaşık `(0,81)-(590,1090)` kırpılıp oran korunarak390×666 hücreye sığdırıldı. Yoğunluk bilinmediği için bu, CSS piksel eşitliği iddiası değildir. Alt sıradaki AU yakalamaları390×666 CSS/piksel, yoğunluk1; masaüstü1280×720, yatay844×390, tablet820×1180. Farklı gerçek hareket anları karşılaştırılır; modelin pozunu piksel eşleştirmek hedef değildir. [Kart kırpmaları](design/2026-10-16-mobil-denetim/panel-comparison-au.png) ölçeklenmeden özgün piksellerle yan yana incelendi.

## Beş görsel yüzey

- **Yazı:** Georgia tür başlığı ve mevcut gövde fontu korundu. Mobil tür18px, hareket15px, kısa açıklama11px; uzun başlık doğal sarılır. Boşluklar azaltıldı; uzun hareket adıyla171px kartta kaydırma yok. Kaynak bağlantısı24px hedefini korur. Masaüstü ayrıntılı açıklama/bilimsel ad/faktlar yerinde.
- **Yerleşim:** sağ altta içerik boyunda128px kart; sahne mobilde tam390px genişlikte. Uzun adlı kart önceki alanın%29,4'ünü kullanır. Üst geri kontrolü gerektiğinde ikinci satıra geçer. Tablet, yatay mobil ve masaüstünde kontroller örtüşmez; sayfa yatay taşmaz. Alt panel, hayvan üstünde isim/halkalar ve ek hareket butonları yoktur.
- **Renk/simgeler:** krem yüzey, koyu yeşil hiyerarşi ve ince ayırıcılar korunur. El gerçek Lucide pointer simgesidir; kaynak/ISC lisansı kayıtlıdır. Geri/tam ekran/yükleme simgeleri gerçek SVG varlıkları olarak paketlenir. Yeni seçim rengi, parıltı veya sahne postprocess'i yoktur.
- **Görsel kalite:** aynı lisanslı üretim GLB/dokuları korunur; penguen birey odağı yakındır, yüzücü kısmen su altında görünür. Flamingo baş-boyun hareketi aynı beş kemikte0,123m okunur seyahat verir; ayaklar zeminde, yeni geometri yoktur. Hayvanı tanıtmak için sahte raster/vektör hayvan kullanılmaz.
- **Metin/durum:** mobil tür özeti ve gerçek seçili bireyin kısa hareket açıklaması okunur. Birey seçilmeden hareket bölümü yoktur. Yükleme mesajı anlaşılır; hata ekranında yeniden deneme çalışır. Erişilebilir duyuru da paneldeki güncel hareket adını kullanır.

## İşlev ve performans

- [Dört tür regresyonu](verification/explorer-interactions.json): gerçek mesh seçimi, bağımsız iskelet/ortak geometri, dokunmatik yakın30Hz örnekleme, zemin teması, gizli/görünmeyen durma ve hızlı dokunuşların sonlanması geçti.
- [Ortak keşif](verification/animal-discovery.json): görünür bireylerin otomatik sırası, seçimde yalnız gözlenen bireyin devamı, iki iskelet sınırı, rota/takip ve azaltılmış hareket kontrolleri geçti.
- [Penguen odağı](verification/penguin-focus.json): yüzücü3s içinde1,464m ilerler; tekrar dokunuş konum/faz sıfırlamaz. Kamera en büyük adımı0,00927m/kare, hedef sapması13,29px altındadır. Bunlar CPU/sabit adım ölçüleridir, fiziksel GPU/FPS ölçüsü değildir.
- [Mobil keşif](verification/mobile-discovery.json): gerçek flamingo skin hareketi/zemin, dokunuşta Rest seçilmeme,4s ipucu ve aynı oturumda tekrarlamama geçti. Ek mesh/kemik0.
- Tarayıcıda dört alan, gövde seçimi, tekrar dokunma, su takibi/orbit, iki seviyeli geri dönüş, Enter/Escape, tam ekran, yükleme/hata kurtarma ve azaltılmış harekette anlık uçuş doğrulandı. Normal masaüstü/mobil konsollarında hata/uyarı yok. M5 kaynak ve yol hashleri değişmedi.

## Sınırlar ve sonuç

Fiziksel telefon FPS/GPU/pil, tüm ekran okuyucular ve büyütülmüş metin kontrolü yapılmadı; tam WCAG uygunluğu iddia edilmez. Flamingonun mevcut modeli uçuş/yürüyüş klibi içermez; mevcut baş-boyun/duruş hareketleri kullanılır. Bütün43 bölgenin modelleme hedefi bu mobil yayın denetiminin kapsamı değildir.

## Yayın sonucu

AU GitHub Pages'te yayımlandı; dört alan canlı tarayıcıda yüklenir. [Canlı mobil ekran](design/2026-10-16-mobil-denetim/screens/24-canli-mobil.png), gövde seçimi, geri dönüş ve doğrudan flamingo geçişi doğrulandı. Konsol hata/uyarı yok. Yayın metinlerinde LF standardı ve Git öznitelikleriyle153 staged dosyanın hashleri manifestle,15 kritik canlı dosyanın hashleri HTTP üzerinden eşleşti. [Yayın kaydı](design/2026-10-16-mobil-denetim/live-release-au.json). Paket180,78MiB; özgün/özel kaynak arşivleri dahil değil.

final result: passed
