# Bursa Hayvanat Bahçesi — ortak model standardı

Bu dosya, alanın tamamı adım adım üretilirken her nesnenin aynı sahnede ve aynı kanıt düzeyinde değerlendirilmesi içindir.

## Koordinat ve ölçek

- Birim **metre**. Yerleşim, yerel M5 ED50/TM30 XY çizgilerine ve `site-data.json` içindeki `originEd50` noktasına bağlanır. Dışa aktarılan web sahnesinin yatay eksenleri bu düzlemi korur.
- Güncel düzenin ilk görsel referansı [Eylül 2026 yerleşim krokisidir](CURRENT_PLAN.md). Krokideki yollar, göletler, yapı ve barınaklar M5 metre düzlemine kontrol noktalarıyla yaklaşık eşlenir. Krokide ölçek/koordinat bulunmadığından çizim ölçülü aplikasyon yerine geçmez.
- Bahçe dış sınırı OSM'den alınan geçici kesme sınırıdır; aplikasyon çizgisi sayılmaz. DGN'deki yol, su, yapı ve çevre çizgileri ayrı kaynak katmanları olarak kalır.
- Yapı oturumu ve yönü, önce DGN/ortofoto eşleşmesiyle; yükseklik, bağımsız ölçü veya güvenilir çizimle doğrulanır. Görsel tahminler ölçü alanlarına yazılmaz. Küçük çevre unsurlarında, kaynaktaki görsel hissi yakalamak için dar kapsamlı ölçü sapması yapılabilir; her sapma kaynak fişinde yorum olarak tutulur.
- Modelin sahnedeki hedefi, ziyaretçi gözünün yaklaşık 1,6 m yüksekliğinden bakıldığında ana siluet, giriş yönü, malzeme rengi, açıklık ritmi ve çevresel ilişkide gerçek yapıya benzemesidir.

## Her nesnenin kaynak fişi

Her ayrıntılı nesne için `model-sources.json` biçiminde şu bilgiler tutulur: ad, koordinat referansı, kaynak URL/dosya ve tarihi, fotoğrafın baktığı cephe, kaynakta açıkça yazan ölçüler, DGN ayak izi eşleşmesi, modelde yorumlanan unsurlar ve henüz doğrulanmamış unsurlar. Görsel kaynakların lisansı ayrı kontrol edilir; izin doğrulanmadan fotoğraf pikselleri kamuya açık doku paketine kopyalanmaz.

Kanıt düzeyi alanı şu değerlerden biri olmalıdır:

1. **Ölçülü:** Yapımcı planı, survey/DGN veya doğrulanmış ölçü.
2. **Eşleştirilmiş:** Birden fazla fotoğraf ve konum verisiyle desteklenen, fakat ölçüsü eksik ayrıntı.
3. **Yorum:** Görsel süreklilik için üretilen yaklaşık ayrıntı. Kaynak fişinde tahmin olarak etiketlenir.

## Geometri ve görünüm

- Önce alan planı: yol/su aksları, sınır, yapı oturumları ve ana ağaç kütleleri. Sonra tekil yapılar. Önceki alan katmanları silinmeden yeni nesne aynı koordinatlarda eklenir.
- Ayrıntılı nesne sırası: oturum ve ölçü → ana siluet/çatı → giriş ve cephe oranları → malzeme ve renk → yakın bakış ayrıntıları. Fotoğrafla karşılaştırma en az iki bakış açısından yapılır.
- Genel plan için hafif geometri, yaklaşma için daha ayrıntılı geometri kullanılır. Telefon ekranında dokunma, yakınlaştırma, görünüm seçimi ve tam ekran çalışmalıdır.
- Ağaç türü, su rengi, yol kaplaması, insan/hayvan ve tanımsız yapı yüksekliği kaynaklanmadıkça stilize bağlam olarak kalır; gerçekçi nesneyle karıştırılmayacak biçimde sunulur.

## İlk denemenin durumu

Su Kuşları Kafesi'nin 70 × 40 × 20 m ana kabuğu **ölçülü**. Eylül 2026 krokisinde kubbenin üzerinde **#31 Pelikan Göleti**, hemen güneyinde ayrı **#32 Su Kuşları** etiketi bulunur; yapı ve alan adlarının kapsamı ayrıca doğrulanmalıdır. M5'teki eliptik tel çit (`H22D01C2B:3908`) ve yapımcı ölçüleri modele yaklaşık merkez `[-30,-64] m` ve yön `+9°` verir; bu hâlâ **eşleştirilmiş geçici adaydır**. Kroki kubbe merkezi yaklaşık 13 m farklı çıkar. Önce kafesle ilişkilendirilen iki M5 su kenarı güneybatıdaki **Alligatör alanı göletine** aittir; kafes iç göletinin kıyısı kroki ve fotoğraflardan **yorum** olarak çizilir. Girişlerin biçimi, açık çelik tonu ve bitkili çevre **fotoğraf eşleştirmesi**; iç gezi yolu, köprü, ahşap yapı, kıyı taşları ve çalıların tekil yerleri **yorum** düzeyindedir. Giriş ve iç mekân için yaklaşık 1,7 m göz hizası, dış görünüm ve kubbe için ayrı bakışlar sunulur. Kaynak ve belirsizlik `viewer/model-sources.json` ile `current-plan-data.json` içinde tutulur. Sonraki doğrulama güncel ortofoto/saha görüntüsüyle oturumu ve ziyaretçi bakışını karşılaştırmaktır.
