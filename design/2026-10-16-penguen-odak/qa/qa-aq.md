# Penguenlerde doğrudan koloni, birey ve yüzücü takibi

16 Ekim2026 · revizyon `20261016aq` · yalnız yerel çalışma. Kapsam genel plandaki hayvan etiketleri ve penguen akışıdır; diğer türlerin davranış/kamera deneyimi bu revizyonda değiştirilmez.

## Kaynak ve karşılaştırma

- Kaynak: `C:/Users/Scanl/AppData/Local/Temp/codex-clipboard-5394cc8e-c387-44f1-a837-dd5aa517ab7b.png`.
- Uygulama: `http://127.0.0.1:8768/?revision=20261016aq`, doğrudan ikinci ekran `?focus=penguin&revision=20261016aq`.
- [Son birlikte karşılaştırma](design/2026-10-16-penguen-odak/qa/karsilastirma-son.jpg) ve [okunur boyutta panel karşılaştırması](design/2026-10-16-penguen-odak/qa/panel-karsilastirma.jpg) aynı inceleme girdisinde açıldı.

Kaynak tam ekran1928×1088 piksel. Tarayıcı/debug çubuğu ve görev çubuğu x4,y148–x1924,y1036 kırpılarak1920×888 uygulama bölgesi alındı. Kaynağın CSS yoğunluğu bilinmiyor; uygulama1920×888 CSS/piksel, ekran görüntüsü yoğunluğu1. Tam levha iki960×444 kareye oran korunarak küçültülür; panel kırpması özgün piksellerindedir. Mobil gerçek390×844 CSS/pikseldir. Kaynak rastgele hayvan pozları ve önceden seçilmiş yüzücü içerir; yeni koloni girişinde bireysel hareket bölümünün boş kalması bilinçli seçimdir. Kamera yaklaşık referans açısına uyar; birebir ölçülmüş kamera/alan iddiası değildir.

## Bulgular ve düzeltme geçmişi

1. **P1 — Genel plan yanlış hayvan beklentisi veriyor.** Bu çalışmanın [ilk genel ekranında](design/2026-10-16-penguen-odak/qa/04-once-genel.jpg) yapı modelleri hayvan deneyimi gibi etiketleniyordu. Harita dört gerçek hayvan çalışma zamanına indirildi. [Son masaüstü](design/2026-10-16-penguen-odak/qa/05-sonra-genel.jpg), [son telefon](design/2026-10-16-penguen-odak/qa/14-mobil-genel.jpg).
2. **P1 — Gereksiz uzak ara ekran.** [Önceki uzak alan](design/2026-10-16-penguen-odak/qa/03-once-uzak-alan.jpg) kaldırıldı. Tek etiket doğrudan yakın koloniye uçuyor. [Son koloni](design/2026-10-16-penguen-odak/qa/06-sonra-direkt-koloni-son.jpg).
3. **P1 — Panelin anlattığı birey belirsiz, seçim odaklamıyor.** [Önceki gerçek gövde dokunuşunda](design/2026-10-16-penguen-odak/qa/02-once-secim.jpg) kamera değişmiyordu. Şimdi daha yakın kadraj, ince halka ve Kıyı/Havuz numarası vardır; diğer hareketler sakinleşir. [Son kıyı odağı](design/2026-10-16-penguen-odak/qa/07-sonra-kiyi-odak-son.jpg), [mobil](design/2026-10-16-penguen-odak/qa/12-mobil-kiyi-odak.jpg).
4. **P1 — Yüzücüye dokunma onu durdurabiliyor, kamera izlemiyor.** Gözlenen yüzücüye dokunmak yüzmeyi başlatır/uzatır, kamera izler. [Son yüzücü](design/2026-10-16-penguen-odak/qa/09-sonra-yuzucu-son.jpg), [tekrar dokunuş](design/2026-10-16-penguen-odak/qa/10-sonra-yuzucu-tekrar.jpg), [mobil yüzücü](design/2026-10-16-penguen-odak/qa/13-mobil-yuzucu.jpg). Elle orbit izlemeyi bırakır.
5. **P2 — İlk yeni koloni kadrajı hâlâ uzak.** [İlk aynı viewport karşılaştırması](design/2026-10-16-penguen-odak/qa/karsilastirma-1.jpg) kaynak sahneyi daha yakın gösterdi. Masaüstü kamera yaklaşımı/yönü düzeltildi; son levhada havuz, üç kıyı bireyi ve köprü benzer görsel ağırlıkta. Telefon tüm kıyı bireylerini koruyan daha geniş açıyı kullanır.
6. **P2 — Seçim çerçevesi düğme gibi.** [İlk kıyı odağındaki](design/2026-10-16-penguen-odak/qa/07-sonra-kiyi-odak.jpg) yuvarlatılmış kare yerine ince dairesel odak halkası kullanıldı. Son kıyı/mobil görüntüler bu düzeltmeden sonradır.
7. **P2 — Yakın yüzücü gövdesi su içinde kayboluyor.** [İlk takip](design/2026-10-16-penguen-odak/qa/08-sonra-yuzucu-a.jpg) sonrası yüzme ofseti6cm yükseltildi. Son yüzücü/mobil görüntüde gövde okunur; su yüzeyi ve rota değişmez. Gerçek skinned gövdenin bir bölümü hâlâ su altındadır.

Son birlikte karşılaştırma ve seçim ekranlarında açık P0/P1/P2 kalmadı. Rastgele pozlar, başlangıçta bireysel hareket göstermeme ve yeni geri kontrolü metinleri istenen akış değişiklikleridir.

## Beş görsel yüzey

- **Yazı:** mevcut Inter/Arial ve Georgia tür başlığı korunur. Panelin ad/bilimsel ad/paragraf/ölçüleri özgün piksel karşılaştırmasında aynı tipografiyi kullanır. Mobil uzun hareket adı iki satırda, açıklama kırpılmadan görünür.
- **Yerleşim:** harita→koloni→birey. Alt düğme/kategori menüsü yoktur. Sağ kart240px masaüstü,128px telefon; canvas buna göre ayrılır. Dar telefonda üst geri kontrolü ikinci satıra geçer, kart onun altından başlar; kalıcı kontroller görünür kalır.
- **Renk/token:** krem `#f8f7ef`, koyu yeşil `#1d4d3e`, ince sıcak odak çizgisi; kaynak panel rengi, kenarları ve ayırıcıları korunur.
- **Görsel kalite:** gerçek kaynak GLB, dokular ve M5 sahnesi kullanılır. Ek hayvan mesh'i veya efekt geçişi yoktur. Halka mevcut erişilebilir DOM hedefinin seçim durumudur; sahneye sahte ikon/model çizilmez.
- **Metin:** genel harita yalnız hayvan modeli olan alanları adlandırır. Hayvan üstünde ad yoktur; hareket açıklaması gerçek gözlenen denetleyiciden gelir. Kaynak panelin tür bilgisi değişmez.

## İşlev, performans ve sınırlar

[Üretim GLB/ExplorerCamera/OrbitControls testi](verification/penguin-focus.json): varsayılan seçim yok; gözlenen birey dışındaki hareketler sonlanır; yüzücü gerçek rota üzerinde ilerler, yeniden dokunma faz/konumu sıfırlamaz. Bir takip örneğinde3s ilerleme1,46m, en büyük kamera adımı0,009m/kare ve hedef merkezi sapması9,65px. Bunlar sabit zaman adımlı CPU model ölçüleridir, fiziksel cihaz FPS testi değildir.

[Koloni testi](verification/penguin-discovery.json), [dört tür regresyonu](verification/explorer-interactions.json) ve [penguen geçiş/zemin testi](bolgeler/15-penguen/model/hayvan/runtime-verification.json) geçti: en fazla iki görünür iskelet örnekleme, dokunmatik30Hz, ortak geometri/ayrı iskeletler, görünmeyen/gizli sekmede durma, güvenli su maskesi ve eski tür akışları.

Gerçek tarayıcıda model etiketi→doğrudan koloni, kıyı/yüzücü gövdesine tıklama, tekrar yüzme, elle orbitte takibi bırakma, Enter/Escape ve iki seviyeli geri dönüş kontrol edildi. Mobilde harita390px genişliğe geri döndü ve dört ad göründü. [Tarayıcı kanıtı](design/2026-10-16-penguen-odak/qa/browser-checks.json) konsol, takip ve dönüş kayıtlarını içerir. Tam WCAG/ekran okuyucu denetimi, fiziksel telefon GPU/FPS/pil ölçümü yapılmadı.

Kamera hedefinin birlikte taşınması ve `controls.update()` davranışı [Three.js OrbitControls](https://threejs.org/docs/pages/OrbitControls.html) belgesiyle kontrol edildi. Çalışma yalnız `dist/` altında; `docs/`, commit/push ve M5 yol/kroki verileri değiştirilmedi.

final result: passed
