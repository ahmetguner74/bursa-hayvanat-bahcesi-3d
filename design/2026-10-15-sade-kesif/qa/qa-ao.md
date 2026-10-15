# Sade keşif akışı — görsel ve işlevsel kontrol

Revizyon: `20261015ao`. Yalnız yerel uygulama; tüm hayvanat bahçesinin modelleme hedefinin tamamlandığı iddiası değildir.

## Kaynak ve karşılaştırma

- Görsel hedef: [tek tasarım panosu](design/2026-10-15-sade-kesif/sade-kesif-mockup.png), [tasarım sözleşmesi](design/2026-10-15-sade-kesif/design-spec.json) ve kullanıcının üç gerçek uygulama ekranı.
- Uygulama: `http://127.0.0.1:8768/?revision=20261015ao`.
- [Birleşik tam görünüm karşılaştırması](design/2026-10-15-sade-kesif/qa/comparison-full.jpg): her satır aynı durumun kaynak ve gerçek tarayıcı görüntüsünü birlikte gösterir.
- [Birleşik yakın UI karşılaştırması](design/2026-10-15-sade-kesif/qa/comparison-ui.jpg): kimlik/geri kontrolü ve isim etiketi, kaynak ve tarayıcıdan birlikte açılıp incelendi.

Kaynak pano1448×1086 piksel; üst sunum çerçevesi1432×511, alt çerçeveler712×478. Bunlar tek bir gerçek CSS viewport'u değildir. Masaüstü uygulama görüntüleri1280×720 CSS/piksel; ekran görüntüsü yoğunluğu1, WebGL çizim yoğunluğu en çok1,6. Birleşik görüntüde kaynak kareler oranları korunarak1280×720 alana yerleştirilir; boşluklar karşılaştırma payıdır, uygulama boşluğu sayılmaz. Yakın UI örnekleri kendi özgün piksellerinde karşılaştırıldı. Bu bir yapay görselin geometrisini/piksellerini birebir kopyalama iddiası değildir; mevcut kaynak modellerin korunduğu, seçilen sade arayüz ve üç kamera durumunun kontrolüdür.

## Ekran kanıtları

- [Genel plan,1280×720](design/2026-10-15-sade-kesif/qa/overview-desktop.jpg)
- [Kafes dışı,1280×720](design/2026-10-15-sade-kesif/qa/aviary-desktop.jpg)
- [Kuş seviyesi,1280×720](design/2026-10-15-sade-kesif/qa/flamingo-desktop.jpg)
- [Penguen,390×844](design/2026-10-15-sade-kesif/qa/penguin-mobile.jpg)
- [Penguen alanının tür etiketi,390×844](design/2026-10-15-sade-kesif/qa/penguin-habitat-mobile.jpg)
- [Flamingo son kadraj,390×844](design/2026-10-15-sade-kesif/qa/flamingo-mobile.jpg)
- [Zürafa,390×844](design/2026-10-15-sade-kesif/qa/giraffe-mobile.jpg)
- [Zürafa yatay,844×390](design/2026-10-15-sade-kesif/qa/giraffe-landscape.jpg)
- [Gergedan örnek kadraj,390×844](design/2026-10-15-sade-kesif/qa/rhino-mobile.jpg). Kamera açısı seçilen bireyin yönüne ve manuel orbite göre değişebilir.

## Karşılaştırma geçmişi

İlk denemelerde aşağıdaki bulgular çözülene kadar sonuç blocked olarak değerlendirildi. İlk durumlar konuşmadaki gerçek tarayıcı ekranlarında görüldü; son durumlar yukarıdaki dosyalarda ve birleşik karşılaştırmalarda saklandı.

1. **P1 — Genel plan fazla çapraz/küçük:** kamera yönü ve kadraj ölçeği ayarlandı. Son kanıt: overview-desktop ve comparison-full üst satırı.
2. **P1 — Telefonda tür etiketi kayboluyor:** küçük hayvan piksel eşiği grup etiketini gizliyordu. Grup etiketi sürekli erişilebilir yapıldı. Son kanıt: penguin-habitat-mobile; gerçek düğmeyle yakın görünüme geçiş.
3. **P2 — Aynı türün etiketleri alan görünümünü kapatıyor:** alan seviyesinde tek tür adı, yakın seviyede bireysel hedefler kullanıldı. Son kanıt: aviary-desktop/flamingo-desktop.
4. **P2 — Kısa yatay ekranda ipucu zürafanın başını kapatıyor:** kısa ekranlarda yardımcı ipucu gizlendi; yön değişiminde otomatik kadraj hesaplandı. Son kanıt: giraffe-landscape, baş/toynaklar ve geri kontrolü görünür.
5. **P2 — Yakın kuş kadrajı panoya göre uzak:** kamera yaklaştırıldı, yüksekliği1,05m ve FOV64° ile yeniden dengelendi. İlk yakınlaştırmadaki kesilen barınak çatısı da düzeltildi. Son kanıt: flamingo-desktop ve comparison-full alt satırı; ayaklar, dört kuş ve ahşap barınak görünür.
6. **P2 — Çakışma çözümü bir hayvanın adını gövdeye indiriyor:** hayvan etiketlerinde aşağı kaydırma kaldırıldı. Son kanıt: flamingo-desktop; isimler üstte.

Son birleşik karşılaştırmada yeni P0/P1/P2 bulgusu kalmadı.

## Beş görsel yüzey

- **Yazı:** mevcut Inter/Arial ailesi, Georgia B·H işareti korundu; kimlik13px, ikincil metin11px, isimler11–12px. Mobilde mevcut kimlik ölçeği küçülür. Yakın UI karşılaştırmasında taşma/kırpılma yok; sunum panosunun minyatür font ölçeği gerçek CSS ölçüsü kabul edilmedi.
- **Yerleşim:** tek sahne, üst kimlik/geri/tam ekran; alt kontrol veya iç içe kategori paneli yok.44px ve üzeri ana hedefler; isimler sahneye bağlı ve çakışma denetimli. Telefon ve yatay ekran kontrol edildi.
- **Renk/token:** krem `#f8f7ef`, koyu yeşil `#1d4d3e`, kahverengi marka; opaklığa yakın isim yüzeyi ve hafif gölge. Hover/seçim aynı yeşil dili kullanır; yalnız renge bağlı olmayan yazı/fare imleci/klavye odağı vardır.
- **Görsel kalite:** gerçek yerel GLB ve dokular kullanılır; mockup sahnesi arka plan resmi yapılmadı. Kaynak geometri/M5 yerleşimi korunur. Ek outline/bloom çizim geçişi yerine isim vurgusu kullanıldı; kullanıcı hover veya başka bir belirtiye izin vermişti. Feather ikonları gerçek kütüphane dosyalarıdır, lisansı assets/ altında.
- **Metin:** Türkçe isimler, Genel plana dön/Alana dön ve tek satırlık ipuçları. Proje/klip/performans ayrıntıları ziyaretçi ekranına taşınmadı. B·H kaynak bağlantısı model yazar/lisans kayıtlarını açar.

## İşlev ve performans kanıtı

Gerçek tarayıcıda isim→alan→hayvan, penguen/flamingo gövdesine doğrudan dokunma, tür ve birey etiketleri, Enter/Escape, geri dönüş, sürüklemenin tepki başlatmaması ve tam ekran giriş/çıkış kontrol edildi. Kuş kafesinde kapı ara noktalarıyla uçuş tamamlandı; mevcut bakış yukarı ekseni Z olarak kalır.

[Üretim modülü/gerçek GLB kontrolleri](verification/explorer-interactions.json):5 penguen,2 gergedan,2 zürafa,4 flamingo; bağımsız iskelet/ortak geometri, gerçek mesh seçimi, boşta0 güncelleme, kısa yürüyüşün gerçek ilerlemesi, hızlı dokunuşların sonlanması, gizli sekme/dönüş ve dokunmatik30Hz sınırı. Kaynak penguenin transparan tüy kartı boşlukları zemin referansı değildir; gövde/ayak referansı kullanılır. Ayrı penguen testinde uyku/geçiş zemini yaklaşık−0,1…+2,02mm.

[Tarayıcı kayıtları](design/2026-10-15-sade-kesif/qa/browser-checks.json): üç yaklaşık5 saniyelik sakin genel plan örneğinde0 yeni sahne çizimi,0 iskelet güncellemesi,0 aktif hayvan; uyarı/hata kaydı boş. Bu, genel JavaScript döngüsünün durduğu veya GPU/enerji/FPS'nin fiziksel telefonda ölçüldüğü anlamına gelmez.

Envanter/zemin kontrolleri geçti; mevcut yol, havuz, habitat ve M5 kaynakları korunur. Eski penguen DOM modülü, alt panel/katman menüsü HTML/CSS/olayları ve otomatik hayvan dolaşma zamanlayıcıları kaldırıldı. Yerel paket yeni modülleri içerir. docs/ ve Git HEAD değişmedi.

## Kalan sınırlar ve küçük iyileştirmeler

- Yoğun uzak planda bazı ikincil yapı isimleri geçici gizlenir; yakınlaşınca açılır. Bu, seçilen çakışma/sadelik kuralıdır. Daha ayrıntılı etiket yerleşimi P3 düzeyinde geliştirilebilir.
- Mevcut flamingo riginde gerçek tüy bakımı/uçuş/yüzme yoktur; yalnız desteklenen sakin tepkiler oynatılır. Hayvan sayıları/yerleşimleri güncel hayvan nüfusu değildir.
- Fiziksel telefon GPU/FPS/pil ölçümü ayrıca yapılmalıdır. Tarayıcı viewport kontrolleri fiziksel cihaz testi diye sunulmaz.

## Uygulama listesi

- [x] Eski ziyaretçi panellerini ve ilgili kodu kaldır.
- [x] Dört türde doğrudan seçim ve kısa davranışı bağla.
- [x] Kademeli kamera, kapı yolu ve tek geri kontrolünü doğrula.
- [x] Masaüstü/telefon/yatay ekran düzeltmelerini yeniden karşılaştır.
- [x] Yerelde bırak; yayın/commit/push yapma.

final result: passed
