# Türk Köyü — düzenlenebilir 3B model v1

`turk-koyu.glb`, metre birimli ve glTF Y yukarı eksenindedir. [Yerel inceleme](http://127.0.0.1:8768/model-review/?model=turk-koyu) seçicisinden tek başına açılır; ana atlasta M5 yerel `[-68, 8]` konumunda bulunur.

## Kaynak ve yorum

- `model-footprints.json`: M5 verisinden yakalanan dokuz çatı bölgesi, özgün kaynak kimlikleri ve kaynak SHA256 özeti. Bitişik bölgeler dokuz bağımsız bina anlamına gelmeyebilir.
- `../kaynaklar/fotograflar/trend-insaat-2013-turk-koyu.jpg`: yapımcının tarihî havadan fotoğrafı. Taş alt duvarlar, ahşap ayrıntılar ve kiremit çatılar için referanstır. Çekim tarihi kesin değildir; URL 2013 arşivini işaret eder.
- Güncel resmî kroki #30 konumları için genel bağlam sağlar. M5 eski durumdur; bu model güncel ölçülü rölöve değildir.
- Çatı eğimleri, saçaklar, pencere/kapı yerleri ve cephe renkleri yaklaşık mimari yorumdur. Yükseklikler eski M5 kütlesinden gelir.
- Çatı ve taş malzeme görüntüleri AI ile üretilmiş döşenebilir örneklerdir; gerçek yapının fotoğraf dokusu değildir. Kaynakları `viewer/assets/asset-manifest.json` içindedir.

## Geometri

Kırma çatılar düz iskelet yöntemiyle üretilir. Çatı yüzlerinin XY izdüşümü özgün bölgelere geri kesilir; çatılar arasında pozitif alan örtüşmesi yoktur. Bitişik gövdeler ayrı kapalı kutular olarak üst üste konmaz: dış duvarlar ve yalnız yükseklik farkı olan iç basamaklar üretilir. 18 cephe açıklığı duvar yüzünden çıkarılıp gerisine panel ve ahşap çerçeve yerleştirilir.

Çatı bölgesi sayısı **9**, çatı yüzü sayısı **76**, üçgen sayısı **3.857**. Model glTF doğrulayıcısında hata/uyarı vermedi; bu, görsel hedefe ulaşıldığı veya mevcut yapının ölçülerinin doğrulandığı anlamına gelmez.

## Yeniden üretim

Proje kökünden:

```powershell
python -m pip install -r requirements.txt
python bolgeler/30-turk-koyu/model/build_village.py
python publish_local.py --local-only
```

`build_village.py` kaynak kodu ve `model-footprints.json` düzenlenebilir girdilerdir. M5 kaynak özeti değişirse üretici durur; yeni ayak izi bölümü açıkça yeniden yakalanmalıdır. `docs/` kullanılmaz.
