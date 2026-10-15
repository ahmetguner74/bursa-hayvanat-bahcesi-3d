# Halkasız penguen seçimi

16 Ekim 2026 · `20261016ar` · yerel, dar kapsamlı CSS düzeltmesi.

## Bulgu ve düzeltme

- **P2 — Hover ve seçim halkaları sahneyi arayüz işaretiyle kaplıyor.** Kullanıcının reddettiği önceki halka kaldırıldı. İlk gövde dokunuşu ve sonraki bireye geçişte outline, gölge ve kenarlık yok. Kamera yaklaşımı, diğerlerinin sakinleşmesi ve sağ panel gözlenen bireyi anlatır. Yalnız klavyeyle hedefler arasında gezinirken ince alt çizgi görünür.
- Açık P0/P1/P2 bulgu kalmadı. Önceki AQ raporu [arşivlendi](design/2026-10-16-penguen-odak/qa/qa-aq.md).

## Görsel kanıt

Kaynak: `C:/Users/Scanl/AppData/Local/Temp/codex-clipboard-8bc978ca-6b42-4d9f-9953-320440b08447.png`,184×194 piksel kullanıcı kırpması; CSS boyutu/yoğunluğu bilinmiyor. Bu görsel yeni hedef değil, kaldırılması istenen durumu gösterir.

Uygulama: `http://127.0.0.1:8768/?focus=penguin&revision=20261016ar`. Gerçek tarayıcı1920×888 CSS/piksel, yoğunluk1. [İlk seçim](design/2026-10-16-penguen-odak/qa/15-halkasiz-secim-ar.png), [sonraki seçim ve bütün ekran](design/2026-10-16-penguen-odak/qa/16-halkasiz-secim-ar.png) açılıp incelendi. Kaynağın tamamı ve son ekranın180×192 gerçek piksel kırpması [tek karşılaştırma girdisinde](design/2026-10-16-penguen-odak/qa/halka-karsilastirma-ar.png) incelendi; yeniden ölçekleme yok. Birey, kamera hedefi ve animasyon fazı farklıdır; poz veya piksel eşitliği iddiası yoktur. Tam ekran kaynak verilmediği için bütün ekran eşleştirmesi yapılamaz; değişikliğin görsel hedefi yalnız halkaların kaldırılmasıdır.

## Beş görsel yüzey

- **Tipografi:** mevcut kimlik, Georgia tür başlığı, açıklama ve hareket hiyerarşisi aynı.
- **Yerleşim:** sağ kart, üst kontroller, hayvan kadrajı aynı akışta; seçim işareti artık yer kaplamıyor.
- **Renk:** krem/yeşil panel korunur; hayvan çevresindeki krem ve yeşil çizgiler kaldırıldı.
- **Görsel kalite:** mevcut gerçek GLB/doku görünür; yeni efekt veya mesh eklenmedi.
- **Metin:** hayvan üstünde isim veya düğme yok; panel seçilen Kıyı3 ve gerçek Silkeleniyor durumunu gösterdi.

## Kontrol ve sınırlar

[Tarayıcı kaydı](design/2026-10-16-penguen-odak/qa/ring-check-ar.json): ilk ve sonraki seçimde bütün sessiz hedeflerde outline/gölge yok, kenarlık0px. Tab odağında halka olmadan2px alt çizgi, gövde dokunuşundan sonra tekrar0px. Gerçek tıklama kamera ve panel seçimini değiştirdi. Konsolda hata/uyarı yok; kaynak ve yerel paket CSS/index baytları aynı. Önceki davranış testleri [AQ arşiv raporunda](design/2026-10-16-penguen-odak/qa/qa-aq.md); bu CSS değişikliğinde yeniden çalıştırılmadı. Fiziksel mobil/GPU/FPS ölçümü yapılmadı. `docs/` değişmedi; canlı yayın, commit veya push yapılmadı.

## Uygulama kontrol listesi

- Hover/seçim halkalarını kaldır: tamamlandı.
- Klavye odağını görünür tut: tamamlandı.
- İlk ve sonraki seçimi gerçek tarayıcıda doğrula: tamamlandı.

## Sonraki dar düzeltme · `20261016as`

Kullanıcının minimal yükleme isteği uygulandı: mevcut yeşil fonda15px metin ve22px Feather simge,12px aralık. “Bahçe hazırlanıyor” yerine “Hayvanat bahçesi yükleniyor…” kullanılır. [1920×888 gerçek yükleme ekranı](design/2026-10-16-penguen-odak/qa/17-minimal-yukleme-as.png) ve [480×144 özgün piksel detay](design/2026-10-16-penguen-odak/qa/18-minimal-yukleme-detay-as.png) açılıp incelendi. Yazı, renk ve boşluk mevcut tasarıma uyumlu; kesilme yok. Bu ek için yeni görsel referans verilmedi; kullanıcının dar kapsamlı tarifine göre mevcut bileşen düzeltildi.

Tarayıcıda geçici1s ağ gecikmesiyle gerçek yükleme durumu yakalandı; sahne açılınca gösterge DOM'dan kalktı. Ağ/önbellek test ayarları geri alındı. Konsol hata/uyarı yok. Kaynak/yerel paket CSS, HTML ve simge aynı. CSS azaltılmış hareket kuralı dönüşü kapatır; bu tercih fiziksel cihazda ayrıca sınanmadı. Davranış JavaScript'i değiştirilmedi; yeni bağımlılık/zamanlayıcı veya yapay bekleme yok. `docs/` değişmedi.

final result: passed
