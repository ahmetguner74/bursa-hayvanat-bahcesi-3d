# St. Louis Zoo haritası — Bursa için tasarım çıkarımları

İnceleme: 14 Ekim 2026. [Etkileşimli harita](https://map.stlzoo.org/) tarayıcıda incelendi; [kurumun özellik açıklaması](https://stlzoo.org/visit/parking-and-maps/digital-map-info) olgusal özellikler için kullanıldı. Görsel düzen ve etkileşim gözlemleri, o tarihte görünen sürüme aittir.

## İşleyen fikirler

- **Harita ana ürün:** Ekranı 3B alan dolduruyor; araçlar onun üzerine yerleşiyor. Ziyaretçi sayfa metnini geçmeden noktaları keşfedebiliyor.
- **Tematik bölgeler:** Renkli alanlar hayvan yaşam alanlarını ve deneyim bölgelerini ayırıyor. Düşük ayrıntılı ağaç/yapı kütleleri ölçeği ve yönü anlatıyor; seçili noktalar simge ve kısa etiketle öne çıkıyor.
- **Kategori filtresi:** Hayvanlar, yemek, deneyimler, istasyonlar, tuvaletler, aile ve erişilebilirlik hizmetleri üstte kaydırılabilir kategoriler. Kategori seçimi haritadaki işaretleri gerçekten değiştiriyor.
- **Noktadan bilgiye:** Bir işarete dokununca kamera noktaya yaklaşıyor ve fotoğraflı bilgi kartı açılıyor. Harita arka planda görünmeye devam ediyor.
- **Arama ve keşif:** Arama panelinde yazmadan önce popüler hedefler fotoğraflı kartlar olarak sunuluyor. Kurum açıklaması canlı öneri, tamamlama ve eş anlamlıları da belirtiyor.
- **Harita kontrolleri:** 2B/3B bakış geçişi, konum, ayarlar. Ayarlarda zor geçilen yolları gösterme, yazıyı büyütme ve dil seçimi bulunuyor. Kurum, konuma göre rota hesaplamayı ve sapınca yeniden yönlendirmeyi açıklıyor.

## Bursa sahnesine uygulama sırası

1. **Şimdi — harita öncelikli mobil açılış.** Mevcut uzun başlığın yerine telefonda önce harita, küçük başlık ve açılabilir açıklama gelsin. Ana ekranı tam ekran düğmesine ihtiyaç duymadan keşfedilebilir kılalım; tam ekran seçeneği kalsın.
2. **Şimdi — nesne kartı standardı.** İşaret seçimi kamera yaklaşmasıyla birlikte kısa alt kart açsın: ad, gerçek fotoğraf, kategori, belgeli ölçüler, kaynak ve `ölçülü / eşleştirilmiş / yorum` durumu. Su Kuşları Kafesi ilk kart olsun. Kullanım hakkı doğrulanmamış fotoğrafı pakete kopyalamayalım; gerekirse kaynak bağlantısı gösterelim.
3. **Alan genişledikçe — kategori ve arama.** Önce `Yapılar`, `Hayvan alanları`, `Yeme-içme`, `Hizmetler`, `Girişler` gibi gerçekten envanteri çıkarılmış sınıflar. Az veri varken boş kategoriler gösterilmesin. İsim, alternatif ad ve türle arama eklensin.
4. **Kanıtlandıktan sonra — yollar ve rota.** DGN'deki yol kenarlarını yürünebilir ağ diye kabul etmeyelim. Bağlantı, geçiş, kapalı yol, basamak ve eğim saha/kurum verisiyle doğrulandığında rota ve erişilebilir güzergâh devreye alınsın.
5. **Daha sonra — isteğe bağlı konum.** Konum izni yalnızca ziyaretçi istediğinde, HTTPS üzerinde ve doğrulanmış yol ağıyla kullanılsın. Harita konum olmadan da tam keşif sunmalı.

## Korunacak Bursa farkı

St. Louis haritasının yoğun tematik paleti yön bulmayı güçlendiriyor; Bursa çalışmasının ana hedefi ise yapıya bakan kişiye gerçek siluet ve cephe hissini vermek. Bu yüzden nötr, kaynaklı alan zemini üzerinde ayrıntılı gerçekçi odak nesneleri kullanmak daha uygun. Renk, belgelenmemiş bir hayvan alanı veya dönem iddiası taşımamalı. Sıkışan işaretler yakınlaşma düzeyine göre azaltılmalı; 3B sahne ve bilgi kartı aynı kaynak/ölçü standardını paylaşmalı.
# Kullanıcı yönlendirmesi · 2026-10-14

St. Louis Zoo haritası yalnızca 3B kütle dili, renk ve çevre hissi için görsel esindir. Bursa modelinin ana ölçüsü, konumu ve fotoğrafları kendi kaynaklarından gelir. Bu aşamada St. Louis arayüzündeki sekmeler, işaretler veya etkileşimler modelleme hedefi değildir. Su Kuşları Kafesi'nin iç yolu, göleti, köprüsü ve bitki çevresi Bursa fotoğrafları ile M5 çizgilerinden okunup aynı stil ailesinde yorumlanır.

