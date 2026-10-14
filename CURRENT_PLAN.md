# Güncel yerleşim planı — çalışma dayanağı

14 Ekim 2026. Bursa Büyükşehir Belediyesi'nin [Hayvanat Bahçesi Şube Müdürlüğü sayfası](https://www.bursa.bel.tr/idari/hayvanat-bahcesi-sube-mudurlugu-74), `bursahayvanatbahcesi.com` alan adını bahçenin sitesi olarak bağlantılar. Bu sitenin medya kitaplığındaki [15 Eylül 2026 krokisi](https://www.bursahayvanatbahcesi.com/wp-content/uploads/2026/09/kroki.jpg) bulunabilen en yeni yerleşim görselidir. Görsel 1600 × 864 piksel ve 43 maddelik lejant içerir. [31 Mart 2026 sürümü](https://www.bursahayvanatbahcesi.com/wp-content/uploads/2026/03/kroki-1920x1080-1.jpg), aynı ana çizimi 1921 × 1081 piksel olarak gösterir; çizgi ve biçim eşleştirmesi için daha elverişlidir. Yükleme tarihleri sitenin medya kayıtları [Eylül](https://www.bursahayvanatbahcesi.com/wp-json/wp/v2/media/4039) ve [Mart](https://www.bursahayvanatbahcesi.com/wp-json/wp/v2/media/3876) girdilerindedir. Krokilerin üzerinde çizim/ölçüm tarihi, koordinat ızgarası, ölçek veya kuzey oku yoktur.

## Kaynak önceliği

1. Güncel ziyaretçi düzenini ve nesne adlarını yorumlarken Eylül 2026 krokisi esas alınır. Mart sürümü aynı çizimin ayrıntılarını okumak için kullanılır.
2. `source-dgn/` içindeki M5 paftaları metre cinsinden koordinat ve eski durumun ölçülü izleri için tutulur. Kaynak 2016 görüntüsü / 2018 bütünlemesidir; güncel krokiyle çelişen yolu, kaldırım veya yapıyı otomatik olarak bugünkü durum saymayız.
3. Kafesin 70 × 40 × 20 m ana ölçüsü gibi bağımsız yapımcı verileri korunur. Krokiden yorumlanan yerleşim, güncel ortofoto veya saha görüntüsüyle karşılaştırılana kadar **yaklaşık** olarak etiketlenir.

## Yerleştirme ve üretim sırası

Krokinin belirgin gölet, kafes, giriş, ana yol kavşağı ve dış sınır noktaları M5 yerel XY düzlemine eşlenir. Kontrol noktaları, dönüşüm ve sapmalar ayrı kayıt altında tutulur. Şematik çizim esnetilebileceği için tek bir piksel dönüşümü tüm bahçede aplikasyon doğruluğu vermez. Eski `site-data.json` silinmez; yeni plan yorumu ayrı bir katman olarak tutulur. İlk aşama genel yol ağı, büyük su alanları ve kafes yerini karşılaştırır. Yapı ve barınaklar, fotoğraf ve mümkünse saha ölçüsü geldikçe tek tek güncellenir.

## İlk eşleme ve sahneye aktarım

`current-plan-registration.json`, Eylül krokisindeki 12 ortak noktadan M5 yerel metre düzlemine yaklaşık afin dönüşümü kaydeder. Kontrol noktalarında RMS sapma **10,7 m**, en büyük sapma **22,64 m**; farklı bölgelerde yaklaşık 10–25 m belirsizlik beklenir. Daha büyük Mart çiziminden izlenen sekiz öğe `current-plan-trace-pixels.json` içindedir. `build_current_plan.py` bunları `current-plan-data.json` metre katmanına dönüştürür. İlk iki dosya araştırma/yeniden üretim kaydıdır; sahne ve yayın paketi yalnız son metre katmanını okur.

Krokide ağ kubbe **#31 Pelikan Göleti** etiketi üzerindedir; **#32 Su Kuşları** hemen güneyde ayrı işaretlenir. Bu yüzden iki etiketin fiziksel kapsamı kesinleştirilene kadar kubbenin konum ve ölçeği için M5'teki eliptik çit izi (`H22D01C2B:3908`) ile yapımcının 70 × 40 m ölçüsü kullanılır. Kroki kubbe merkezi ile M5 çit merkezi arasında yaklaşık **13 m** vardır; bu fark dönüşüm belirsizliği içinde kaydedilir.

İlk güncellemede resmî krokideki **#5 Giriş Göleti** yaklaşık kıyısıyla sahneye eklendi. M5'teki iki açık su kenarı eski göletin izini verir, ancak kapalı yüzey olarak görünmüyordu. Krokideki kuzeydoğu ikiz göletler M5 dış kıyılarıyla büyük ölçüde örtüştüğü için çift çizilmez; içteki `H22D01C2B:57` ve `:60` halkaları artık su yerine ada boşluğu olarak işlenir. Güncel krokiden izlenen savan gezi halkasının yaklaşık %85'i eski yol yüzeylerinin 3 m yakınındadır; şimdilik doğrulama referansıdır. Farklı görünen kesimler, güncel ortofoto veya sahadan görüntü geldikçe tek tek yeniden çizilecektir.

Krokilerin kopyaları yalnız `reference-maps-private/` içindedir; `dist/`, `docs/` ve GitHub deposuna dahil edilmez. Canlı atlas yalnız kaynak bağlantılarını ve özgün olarak çizilmiş yorum geometrisini kullanır.
