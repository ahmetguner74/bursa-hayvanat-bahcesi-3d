# Ortak hayvan keşfi · gergedan, zürafa ve flamingo

16 Ekim 2026 · `20261016at` · yalnız yerel çalışma.

## Bulgular ve düzeltmeler

1. **P1 — Diğer türlerde uzak ara ekran, grup/birey yazıları ve bireye ait olmayan deneyim.** Penguenin yakın alan → gövdeye dokunma → birey odağı düzeni üç türe aktarıldı. Alan girişinde varsayılan birey yok; hareket bölümü seçimden sonra açılır. Üstte tek geri dönüş ve tam ekran kontrolü vardır. Hayvan üstünde yazı, hover/seçim halkası veya hareket düğmesi yoktur.
2. **P1 — Tür ve gözlenen birey paneli eksik.** `animal-info.js` ve `animal-profiles.js` dört türün aynı salt bilgi kartını kullanmasını sağlar. Şu anda bölümü gerçek seçili denetleyiciyi anlatır. Başka bireye geçince diğerleri yumuşakça sakinleşir. Gergedan/zürafa yürüyüşünde aynı kamera takip sistemi kullanılır; sürükleme takibi bırakır.
3. **P2 — İlk mobil gergedan odağı küçük.** [İlk telefon odağı](design/2026-10-16-penguen-odak/qa/26-mobil-gergedan-odak-at.png) sonrasında kare yatay sınır yerine kaynak GLB metaverisindeki gerçek uzunluk/en/yükseklik ve yön kullanıldı. [Son telefon odağı](design/2026-10-16-penguen-odak/qa/27-mobil-gergedan-son-at.png) ve [son masaüstü](design/2026-10-16-penguen-odak/qa/30-gergedan-son-at.png) incelendi: gövde daha okunur ve kadraja sığar. Mevcut modellerin ölçüsü/rotası değiştirilmedi.

4. **P2 — Flamingo odağından koloniye dönüşte gereksiz kapı çıkışı.** Ortak geçişte kapıdan çıkış yalnız başka alana/haritaya giderken kullanılır. Aynı flamingo kolonisine dönüş içeride kalır; son tarayıcı kontrolünde yakın koloniye doğrudan geri dönüş tamamlandı.

İlk görsel inceleme sonrası mobil odak ve kafes içi geri dönüş düzeltildi; son birlikte karşılaştırmada kapsam içinde açık P0/P1/P2 kalmadı. Eski AS raporu [arşivdedir](design/2026-10-16-penguen-odak/qa/qa-as.md).

## Kaynak ve karşılaştırma

Aktarılan tasarım referansı: mevcut halkasız penguen akışının [AR ekranı](design/2026-10-16-penguen-odak/qa/16-halkasiz-secim-ar.png),1920×888 CSS/piksel. Kaynak, `C:/Users/Scanl/AppData/Local/Temp/codex-clipboard-5394cc8e-c387-44f1-a837-dd5aa517ab7b.png` ile önceki tasarım çalışmasına dayanır; son halka kaldırma kullanıcı düzeltmesidir. Uygulama: `http://127.0.0.1:8768/?revision=20261016at`.

Son gergedan/zürafa/flamingo ekranları1280×720 CSS/piksel, mobil ekranlar390×844 CSS/piksel; yoğunluk1. [Tam görünüm birlikte karşılaştırması](design/2026-10-16-penguen-odak/qa/ortak-kesif-karsilastirma-at.jpg)1280×776 levhadadır; her kaynak oran korunarak640×360 hücreye sığdırılır, kaynak penguenin farklı en-boy oranı boşlukla korunur. Türler ve kamera konumları farklıdır: bu aktarımda habitat kompozisyonunu piksel eşleştirmek hedef değildir. Sağ panelin [özgün piksel karşılaştırması](design/2026-10-16-penguen-odak/qa/ortak-panel-karsilastirma-at.png) dört240×540 gerçek kırpmayı tek girdide gösterir; ölçeklenmez. İki levha da açılıp birlikte incelendi.

## Beş görsel yüzey

- **Yazı:** mevcut Georgia tür başlığı, Inter/Arial metin, bilimsel ad ve hareket hiyerarşisi aynıdır. Panel levhasında yazı ölçüleri eşleşir; mobilde Beyaz gergedan ve uzun hareketler doğal biçimde sarılır.
- **Yerleşim:** aynı240px masaüstü /128px telefon kartı; sahne genişliği ayrılır. Geri kontrolü gerektiğinde üstte ikinci satıra geçer, kart onun altından başlar. Hayvan başı/ayakları yakın kadraja sığar. Alt panel yoktur.
- **Renk:** krem kart, koyu yeşil yazı ve ince ayırıcılar korunur; hayvan üzerinde seçim rengi yoktur.
- **Görsel kalite:** mevcut kaynak GLB/dokular kullanılır. Yeni mesh, render pass veya resimden sahte hayvan yoktur. Model boyutu ve dokusu değiştirilmez. Kamera gerçek gergedan/zürafa gövde metaverisine göre kadrajlar.
- **Metin:** her türün adı/bilimsel adı/yaşam ve beslenme bilgisi farklıdır; hareketin adı ve kısa açıklaması mevcut klibin gerçek durumundan gelir. Grup girişinde bir bireyin hareketini anlatmaz. Tür bilgilerinin kaynakları kartta ve [araştırma kaydında](design/2026-10-16-penguen-odak/animal-discovery-research.json) bağlantılıdır.

## İşlev ve performans kanıtı

- [Yeni üç tür testi](verification/animal-discovery.json): her görünür birey otomatik hareket sırası alır; varsayılan seçim yok; gözlemde yalnız seçilenin yeni hareketleri sürer. Her kolonide en fazla iki örneklenen iskelet; gizli/görünmeyenlerde durma;25 hızlı birey değişiminin sonlanması; çıkışta örneklemenin durması; azaltılmış harekette otomatik davranışın kapalı, açık dokunuşun kullanılabilir olması.
- Aynı testte gerçek rota ilerlemesi3s için gergedan0,57m, zürafa0,60m. Takipte en büyük kare adımı0,0085m altında, hedef sapması6,35px altında. Bunlar CPU/sabit zaman adımı ölçüleridir; fiziksel FPS/GPU garantisi değildir. Flamingo koloni kamerasının masaüstü/portrede kubbe içinde kaldığı sınandı.
- [Dört tür regresyonu](verification/explorer-interactions.json): gerçek mesh seçimi, ortak geometri/bağımsız iskelet, dokunmatik yakın örnekleme30Hz, gerçek skinned zemin temasları, gizli sekme ve sonlanan hızlı dokunuşlar geçti.
- [Penguen takip regresyonu](verification/penguin-focus.json) geçti: yüzücünün ilerlemesi, tekrar dokunuşta faz/konumun sıfırlanmaması, iki iskelet sınırı ve kısmi su altında kalma korunur. [Ortak panelde penguen](design/2026-10-16-penguen-odak/qa/33-penguen-ortak-panel-at.png) ayrıca tarayıcıda incelendi.
- Gerçek tarayıcıda üç türün gövde seçimi, telefon sürü→harita→gergedan ve harita→kapıdan geçiş→flamingo akışı, Enter/Escape kontrol edildi. [Tarayıcı kaydı](design/2026-10-16-penguen-odak/qa/browser-checks-at.json): masaüstü/mobil hata/uyarı yok; görünür hayvan yazısı, halka ve taşma yok. Mobil görüntüler [yan yana](design/2026-10-16-penguen-odak/qa/uc-tur-mobil-at.jpg).

## Sınırlar ve temizlik

Flamingonun mevcut dinlenme modeli yalnız baş-boyun/duruş hareketlerini destekler; uçuş, yürüyüş ve gerçek tüy bakım klibi eklenmedi. Modelin desteklemediği bir hareket panelde gösterilmez. Gergedan ve zürafa mevcut doğrulanmış rotalarını kullanır. Fiziksel telefon FPS/GPU/pil ve tam ekran okuyucu denetimi yapılmadı. Önceki penguen Kıyı1 kadrajında tüy bakımının bazı anlarında mevcut çalı örtüşmesi görülebilir; bu aktarım peyzaj konumlarını değiştirmez.

Tek tür paneli `penguin-info.js` kaynak ve yerel paketten kaldırıldı; HTML/CSS genel hayvan bileşenine taşındı. Eski grup etiketi/uzak hayvan ekranı ve varsayılan birey seçimi dalları kaldırıldı. Üç tür aynı yaşam döngüsü/zamanlayıcıyı kullanır; hover sırasında skinned mesh sınırları yeniden hesaplanmaz. Paket/kaynak modülleri aynı; M5 ve yol hashleri değişmedi. `docs/`, canlı yayın, commit/push yok.

## Uygulama kontrol listesi

- Yakın alan, yazısız gövde seçimi ve ortak panel: tamamlandı.
- Türe uygun aralıklı hareket, birey odağı ve yürüyüş takibi: tamamlandı.
- Mobil kadraj, geri dönüşler, klavye ve penguen regresyonu: tamamlandı.
- Eski panel/dalların temizlenmesi ve yerel paket eşliği: tamamlandı.

final result: passed
