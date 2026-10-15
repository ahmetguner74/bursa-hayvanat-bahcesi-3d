# İlk Product Design incelemesi

Akış: genel plan → alan → hayvan → tepki/takip → alan → genel plan. Yerel AT sürümü,390×666 mobil ve normal masaüstü. Kullanıcının dört telefon görseli de kapsamı belirler.

1. **Birey seçimi / P1:** [01-once-gergedan.png](screens/01-once-gergedan.png)128×584px sağ kart ve246px sahne genişliği gösteriyor. Uzun açıklama/detaylar dikey kaydırma yaratıyor. Çözüm: mobilde kısa, sağ altta yaklaşık üçte bir alan kullanan kart; sahne tam genişlik.
2. **Penguen odağı / P1:** [02-once-penguen.png](screens/02-once-penguen.png) seçili pengueni küçük gösteriyor. Çözüm: bireye yaklaşımı artır, kolonide çevreyi koru; su takibini aynı davranışla sürdür.
3. **Flamingo tepkisi / P1:** [03-once-flamingo.png](screens/03-once-flamingo.png) dinlenme tepkisi gösteriyor. Mevcut baş hareketi çok küçük; dokunuş da Rest klibini seçebiliyor. Çözüm: dokunuşta okunur baş-boyun tepkisi, aynı beş kemik ve sabit ayaklar. Kamera kapı turu yapmadan doğrudan yaklaşmalı.
4. **Dokunmanın keşfi / P2:** hayvan gövdelerinde kalıcı işaret olmaması sakin bir görünüm sağlıyor; mobilde hover imleci yok ve dokunma ipucu eksik. Çözüm: yalnız ilk yakın alan ziyaretinde kısa, halkasız ve tıklamayı engellemeyen el/dokunma ipucu; oturumda tekrarlama. Klavye hedefleri korunur.

Erişilebilirlik: mevcut hedefler en az44px, Enter/Escape kullanılabilir. Küçük panel hedef boyutlarını küçültmemeli; kaynak bağlantısı en az24px hedef, okunabilir metin ve azaltılmış hareket tercihi korunmalı. Tam WCAG/gerçek telefon GPU denetimi iddiası yoktur.

Araştırma: NN/G kısa, ölçülü ve işlevi anlatan hareketi öneriyor; W3C hedef boyutu ve azaltılmış hareket koşullarını açıklar. WWT flamingolarda baş-boyun hareketlerini gözlemliyor. Seçilen uygulama, bunlardan türetilmiş tasarım kararıdır; yeni bir hayvan uçuşu veya bakım klibi iddiası değildir.

## Son birleşik denetim · AU

**Kapsam / hedef:** genel plan → yakın koloni/sürü → gövde seçimi → davranış/takip → geri dönüş. Amaç az kontrolle hayvana yaklaşmak ve onun gerçek hareketini anlayabilmek. Masaüstü1280×720, telefon390×666, yatay844×390 ve tablet820×1180; bu çalışmada yakalanan ekranlar kullanıldı. Klavye erişimi, hedefler, durum duyurusu, yükleme hatası ve azaltılmış hareket incelendi. Tam WCAG uygunluğu iddiası yoktur.

### Numaralı akış ve sağlık durumu

1. **Genel plan — geçti.** [15](screens/15-masaustu-genel.png) ve [08](screens/08-mobil-genel.png): yalnız dört hayvan alanı etiketi, bilgi kartı/alt hareket çubuğu yok. Alanlar hazır olduğunda özgün zemin delikleri kapanıyor; kalıcı boşluk gözlenmedi.
2. **Yakın alan — geçti.** Penguen [16](screens/16-masaustu-penguen.png), flamingo [18](screens/18-masaustu-flamingo.png), gergedan [19](screens/19-masaustu-gergedan.png), zürafa [20](screens/20-masaustu-zurafa.png). Varsayılan birey seçilmez; kart türü anlatır. Flamingo geçişi yaklaşık1,9s tek uçuş; kapı uğrağı kaldırıldı.
3. **Dokunmanın keşfi — geçti.** [04](screens/04-sonra-ipucu.png): gerçek kütüphane el simgesi ve “Dokun”, bir görünür hayvana bitişik dört saniyelik solma; halka ve yeni düğme yok. Süre sonunda ve hayvan seçilince kapanması, oturumda tekrarlamaması doğrulandı.
4. **Birey ve kart — geçti.** [05](screens/05-sonra-gergedan.png), [06](screens/06-sonra-penguen.png), [09](screens/09-sonra-flamingo.png), [17](screens/17-masaustu-birey.png). Mobilde128×171px uzun adlı kart, eski128×584px alanın%29,4'ü; canvas246px'ten390px'e çıktı. Uzun hareket adı denetiminde clientHeight=scrollHeight169px. Masaüstü uzun tür bilgisi korunur; hayvan üzerinde isim/halkalar yoktur.
5. **Davranış ve takip — geçti.** [07](screens/07-yuzucu-takip.png): yüzücüye dokunma yüzmeyi başlatır/uzatır; kamera izler. Sürüklemede takip `off`, tekrar dokunmada `penguin`. Gergedan/zürafa mevcut rotada ilerler. Flamingoda dokunuş LookAround/Settle; Rest seçmez. Gerçek skinned baş-boyun hareketi0,123m, ayak sapması ihmal edilebilir; kemik/mesh artışı yok.
6. **Geri dönüş, klavye, tam ekran — geçti.** Birey → koloni/sürü → genel plan; Enter/Escape çalışır. [11](screens/11-tam-ekran.png): tam ekran gir/çık durumu doğrulandı. Klavye odağı ince alt çizgiyle görünür; gövdeye dokunmada kaybolur. Durum duyurusu artık panelle aynı hareketi anlatır.
7. **Yükleme ve hata kurtarma — geçti.** [21](screens/21-yukleme.png) gerçek yavaşlatılmış yükleme; [12](screens/12-yukleme-hatasi.png) kontrollü site-data engeli; [13](screens/13-yeniden-yuklendi.png) tekrar yükle sonrası normal harita. Test engelleri/ağ ve medya emülasyonu temizlendi. Azaltılmış hareket tercihinde uçuş anlıktır.
8. **Ekran uyumu — geçti.** [14](screens/14-yatay-mobil.png) yatay kartta128px client/scroll eşitliği; [22](screens/22-tablet.png) tablette1075px client/scroll eşitliği ve820px sayfa genişliği. Yatay taşma/üst kontrollerin örtüşmesi gözlenmedi. Masaüstü/mobil son normal oturum konsollarında hata/uyarı yok.

### Ek bulgular ve giderilen riskler

- **P1 / hata kurtarma:** kök yükleme hatası ham hata yazısı bırakıyordu. `viewer/app.js` anlaşılır mesaj ve sayfayı gerçekten yeniden yükleyen kontrol kullanır.
- **P2 / yerleşim:** tüy bakımı gibi uzun hareket adları mobil kartı kaydırıyordu.15px hareket/18px tür başlığı korunup padding/gap azaltıldı; uzun başlık tekrar kontrol edildi.
- **P2 / durum açıklığı:** ekran okuyucu duyurusu dokunuşun ilk dinlenme durumunda kalabiliyordu. `animal-info.js` yalnız anlamlı hareket değişiminde panelle aynı durum duyurusunu günceller.
- **P2 / simgeler:** yayın izin listesi SVG içermiyordu. Kaynak simge/loader/dokunma SVG'leri ve lisansları artık `build_public.py` ile taşınır; eski tek tür panel modülleri temizlenir.

### Güçlü yanlar ve sınırlar

Akış tek sahne ve iki seviyeli geri dönüşle tutarlıdır. Seçilen bireyin hareketi kartla eşleşir; mobil kart gereksiz tür ayrıntılarıyla sahneyi daraltmaz. Kısa ipucu, NNG/W3C araştırmasından türetilmiş tasarım kararıdır; kullanıcı testiyle keşfedilebilirlik oranı ölçülmedi. Fiziksel iPhone GPU/FPS/pil, tam ekran okuyucu ve büyütülmüş metin denetimi yapılmadı. Flamingo modelinde uçuş/yürüyüş klibi yoktur; mevcut duruş/baş-boyun tepkileri kullanılır. İlk model yüklemeleri asenkrondur; bölge hazırlanıyor durumu gösterilir.

Kapsam içinde açık P0/P1/P2 kalmadı. [Araştırma](research.json), [tarayıcı kaydı](browser-checks-au.json), [görsel karşılaştırma](reference-comparison-au.jpg), [QA](../../design-qa.md) ve `verification/` üretim modeli kontrolleri tamamlandı.

## Canlı yayın kontrolü

AU sürümü [GitHub Pages'te](https://ahmetguner74.github.io/bursa-hayvanat-bahcesi-3d/?revision=20261016au) yayımlandı. [Genel plan](screens/23-canli-genel.png), [telefon penguen odağı](screens/24-canli-mobil.png), [doğrudan flamingo](screens/25-canli-flamingo.png), [gergedan](screens/26-canli-gergedan.png) ve [zürafa](screens/27-canli-zurafa.png) bu çalışmada gerçek canlı adresten yakalandı. Normal canlı konsolda hata/uyarı yok. Telefon seçili kartında151px client/scroll eşitliği ve390px canvas doğrulandı.

Yayın bütünlüğü kontrolünde Windows/Git satır sonu dönüşümü CSS ve el SVG'sinin manifest hashini değiştiriyordu. `build_public.py` public metinleri LF olarak üretir; `docs/` Git özniteliği LF'yi korur.153 dosyanın tamamında staged Git blobu/manifest,15 kritik dosyada gerçek HTTP/manifest hash eşliği doğrulandı. [Yayın kaydı](live-release-au.json):153 dosya,180,78MiB; özel/orijinal kaynak girişi yok. Bu düzeltme sahne geometrisini veya animasyon davranışını değiştirmez.
