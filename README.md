# Bursa Hayvanat Bahçesi — 3B modelleme ön araştırması

14 Ekim 2026. Bu kayıt, kaynak araştırmasını ve ilk coğrafi yerleşimli 3B denemeyi belgeler. Sahne ölçülü DGN çizgileriyle kurulmuştur; henüz doğrulanmış aplikasyon veya güncel ortofoto eşleşmesi değildir.

## Yer ve kapsam

- [Bursa Büyükşehir Belediyesi'nin Mayıs 2026 açıklaması](https://www.bursa.bel.tr/haber/bursa-hayvanat-bahcesine-bayramda-ziyaretci-akini-37224), Soğanlı'daki tesisin yaklaşık **206.000 m²** olduğunu ve 1998'den beri hizmet verdiğini bildirir.
- [Millî Eğitim Bakanlığı tanıtımı](https://okuldisiogrenme.eba.gov.tr/mekan-detay/bursa-hayvanat-bahcesi-720), adresi **1. Nilüfer Caddesi, Soğanlı, Osmangazi** olarak verir. İlk kurulan bölümleri Türk köyü, ayı-kurt, yırtıcı kuş, su kuşları, lama, yaban eşeği ve deve alanları olarak sayar; köy evi biçimindeki yapılardan da söz eder.
- [OpenStreetMap bahçe sınırı — way 26445905](https://www.openstreetmap.org/way/26445905) için [OSM API'den](https://api.openstreetmap.org/api/0.6/way/26445905/full) 14 Ekim 2026'da okunan yaklaşık zarf: **40.2175439–40.2213186 K, 29.0426188–29.050353 D**. Bu topluluk haritası sınırıdır; kadastro veya aplikasyon kontrolü değildir. OSM'de aynı zarfın taramasında iç yapı ayak izleri bulunmadı.
- `source-dgn/` içindeki **H22D01C2A, H22D01C2B, H22D01C2C ve H22D01C2D** DGN paftaları özgün `m5/1000` arşivinden değiştirilmeden kopyalandı; böylece bu proje tek klasörden yeniden üretilebilir. `source-ascii/` ara çıktıları ve `site-data.json` bu dört paftanın yol, havuz, yapı, sundurma, sınır ve ağaç katmanlarını OSM sınırına kırpar. DGN XY konumları metre biriminde korunur. SIMPLE_ASCII ara çıktısındaki öğe sıra numarası özgün DGN kimliği değildir.

## Model adayları ve kanıt düzeyi

| Öncelik | Öğe | Mevcut kanıt | Model öncesi açık iş |
| --- | --- | --- | --- |
| 1 | **Su Kuşları Kafesi / uzay kafesi** | Yapımcı [USKON'un proje kaydı](https://uskon.com/en/bursa-zoo-waterbird-cage-single-wall-elliptical-dome/) gerçek yapı için plan, görünüş ve fotoğrafları içerir: eliptik tabanlı yarım kubbe, **70 × 40 × 20 m**, çelik uzay kafes ve ağ örtüsü. [Şekil 5](https://uskon.com/wp-content/uploads/2021/07/SEKIL5.jpg) ölçüleri; [Şekil 12](https://uskon.com/wp-content/uploads/2021/07/SEKIL12.jpg) iç görünüşü gösterir. | Güncel hava fotoğrafıyla kesin oturum, yön ve zemin kotunu bağlamak; 1998 görüntüsündeki iç peyzajı güncel saymamak. |
| 2 | **Türk Köyü yapı grubu** | [MEB](https://okuldisiogrenme.eba.gov.tr/mekan-detay/bursa-hayvanat-bahcesi-720) köy evi olarak düzenlenmiş binaları doğrular. [Ziyaretçi krokisi](https://karesiturizm.com/images/tour/2809_b.jpg) grubun yerini şematik gösterir. | Her evi ayrı teşhis eden güncel, çok açılı cephe fotoğrafları ve DGN/hava görüntüsünde ayak izleri. Komşu Botanik Park veya Aktopraklık fotoğraflarıyla karıştırılmamalı. |
| 3 | **Afrika Kafe ve Afrika Köyü** | [Belediyenin 2010 proje gerçekleşme belgesi](https://www.bursa.bel.tr/dosyalar/birimek/faaliyet-ve-proje-bilgileri.faaliyet-ve-proje.LBHrSHmzhz.pdf) Afrika Savana Kafeteryası inşasını kaydeder; [ziyaretçi krokisi](https://karesiturizm.com/images/tour/2809_b.jpg) Afrika Kafe ve Köyü işaretler. | Güncel işletme/yapı durumu, cephe ve çatı fotoğrafları, ayrı yapıların oturumu. |
| 4 | **Giriş–idari bina ve giriş göleti** | [Ziyaretçi krokisinde](https://karesiturizm.com/images/tour/2809_b.jpg) giriş, idari bina ve giriş göleti adlandırılmıştır. | Kapı ve bina için güncel cephe fotoğrafları, ölçü ve konum. |

Kroki, [Karesi Turizm'in sayfasında](https://www.karesiturizm.com/tur-659-bursa-extrempark---misi-koyu---hayvanat-bahcesi-turu) yayımlanan **ziyaretçi yön bulma görselidir**; çizimde ölçek, koordinat ve tarih bulunmadığı için geometri çıkarmaya elverişli değildir. USKON'un [genel yerleşim görseli](https://uskon.com/wp-content/uploads/2021/07/SEKIL4.jpg) Su Kuşları Kafesi çevresinde ikinci bir tarihî plan sağlar, ancak güncel yapı yerleşimini tek başına doğrulamaz.

## Fotoğraf ve kullanım notu

Yapımcı çizimleri ve haber/ziyaretçi görselleri **geometriyi incelemek için kaynak** olarak bağlantıyla tutulur; lisansları doğrulanmadan görüntülerin model dokusuna veya halka açık pakete kopyalanması planlanmaz. [Wikimedia Commons Bursa Zoo kategorisindeki](https://commons.wikimedia.org/wiki/Category:Bursa_Zoo) dört yer fotoğrafı yaklaşık 2010 çekimlidir ve çoğunlukla hayvanları gösterir; yapıların güncel cephesini kanıtlamaz. Her üretilen öğede önceki Bursa bina çalışmalarındaki gibi kaynak URL'si, yıl, kullanılan ayrıntı ve belirsizlik ayrı kayda geçmelidir.

İlk kafes revizyonunda [USKON dış ve iç fotoğrafları](https://uskon.com/en/bursa-zoo-waterbird-cage-single-wall-elliptical-dome/), [GeziBilen giriş görüntüsü](https://gezibilen.com/de/travelpoint/bursa/bursa-hayvanat-bahcesi) ve [Trend İnşaat havadan görünümü](https://www.trendinsaat.com.tr/tr/projeler/kent-parklari) ayrı açılardan incelendi. Metalin açık tonu, iki uçtaki beşik çatılı geçit, iç ahşap yapı ve yoğun çevre bitkisi bu kaynaklardaki görsel karakteri izler. Gölet sınırı iki birleşen M5 su kenarından gelir. Köprü, iç yol, kıyı taşı ve çalıların tekil yerleri görsel yorumdur. St. Louis Zoo ekran görüntüleri yalnızca düşük ayrıntılı 3B renk ve sahne dili için esindir; Bursa geometrisinin kaynağı değildir.

## Üretime geçiş sırası

1. `viewer/` içinde bütün alanın etkileşimli ilk sahnesi ve **70 × 40 × 20 m** Su Kuşları Kafesi yorumu üretildi. `publish_local.py` bağımsız `dist/` önizlemesini oluşturur; başka bir Bursa projesine bağlı değildir. Giriş ve iç mekân için yaklaşık göz hizası, telefonda dikey genel plan, dokunulabilir kaynak kartı ve tam ekran seçimi eklenmiştir.
2. Kafesin merkez ve yönü, DGN'deki havuz ve sınır çizgilerine göre **geçici adaydır**. Güncel ortofoto veya saha ölçüsüyle kesinleştirilmelidir. Çelik modüllerin tekil birleşimleri, ağ deseni, iç gezi yolu, köprü, ahşap yapının boyutları ve zemin yüksekliği yaklaşık görselleştirmedir. Ana 70 × 40 × 20 m kabuk korunur; küçük çevre parçalarında görsel his için dar kapsamlı ölçü esnekliği vardır.
3. Yolların çizgi konumları DGN'den gelir; görünen açık renk yüzeyler yol kenarı çizgilerinin **3 m tamponlanmış görsel önizlemesidir**, ölçülü kaplama genişliği değildir. Diğer binalar ve sundurmalar yalnızca kaynak ayak izi üzerinden üretilmiş geçici kütlelerdir; cephe ve yükseklikleri kabul edilmiş ölçü değildir.
4. Türk Köyü, Afrika Kafe, giriş ve diğer yaşam alanlarının her birinde önce tekil DGN ayak izi, güncel çok açılı fotoğraf ve mümkünse ölçü doğrulanacak; sonra aynı metre koordinatı, kaynak kaydı ve belirsizlik sınıflarıyla ayrıntı modeli eklenecek.

## Bağımsız yerel önizleme

Proje klasöründe `python publish_local.py` çalıştırın. Ardından `python -m http.server 8768 --bind 0.0.0.0 --directory dist` komutuyla önizlemeyi açın. Aynı işi Windows'ta `BASLAT.cmd` başlatır. Bilgisayarda `http://127.0.0.1:8768/?focus=cage`; aynı yerel ağdaki telefonda bilgisayarın IP adresiyle `http://<bilgisayar-IP>:8768/?focus=cage` kullanılır. `reference-photos-private/`, `source-ascii/` ve `source-dgn/` kamuya açık `dist/` veya `docs/` klasörüne kopyalanmaz.

## GitHub Pages yayını

[Canlı 3B atlası aç](https://ahmetguner74.github.io/bursa-hayvanat-bahcesi-3d/?focus=cage).

`python publish_local.py` aynı yayın paketini yerel `dist/` ve GitHub Pages için `docs/` klasörlerine üretir. `main` dalındaki `docs/` klasörü canlı sitenin yayın kaynağıdır. Sonraki değişikliklerde komutu yeniden çalıştırıp kaynak dosyaları ile `docs/` çıktısını birlikte kaydedin. Özgün DGN paftaları, ara ASCII dosyaları, özel referans fotoğrafları ve denetim görselleri yalnızca yerel klasörde kalır; GitHub deposuna dahil edilmez.
