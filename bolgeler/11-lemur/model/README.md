# Lemur Adası · model 05

Yerel önizleme: <http://127.0.0.1:8768/model-review/?model=lemur>.

`python bolgeler/11-lemur/model/build_lemur.py` ile `lemur-adasi.glb` ve `model-report.json` yeniden oluşturulur. Düzenlenebilir yerleşim ve ölçüler `model-inputs.json` içindedir; ortak kapalı geometri/glTF yardımcıları `bolgeler/model_tools.py` içindedir. Birim metre, glTF Y yukarı; ana atlas yüklerken M5 Z yukarı çerçevesine döner.

## Kaynak ve yorum

- **M5:** `H22D01C2B:60` ada (759,90 m²) ve `H22D01C2B:61` dış hendek (1.637,14 m²). Özgün XY koordinatları korunur. Su bandı 877,24 m²; merkez `[271.59204047156146, -14.260351774594822]`. Bunlar eski harita izleridir; 2026 ölçümü değildir.
- **Fotoğraf:** [Belediye Lemur kamerası](https://www.bursa.bel.tr/sehir-kameralari/lemurlar-23322), yerel dosya `../kaynaklar/fotograflar/belediye-kamera-20261015T005923Z.png`. Edinim zamanı 15 Ekim 2026 00:59:23 UTC; görüntünün çekim tarihi teyitsiz. Dosya özeti ve kaynak sayfası `model-inputs.json` ve kaynakçada kayıtlıdır.
- Görüntüdeki açık çim, beton kıyı, kaya yığını ve yatık/dik ahşap elemanlar referanstır. **8 kaya, 13 ahşap eleman, 2 ince sarkık halatın kesin sayısı, yerleri, ölçüleri ve görünmeyen taraf yaklaşık yorumdur.** Halat yorumu düşük güvenlidir.
- Arkadaki yeşil kırma çatılı yapının işlevi/aidiyeti belirsizdir; bu varlığa eklenmemiştir. Hayvan modelleri bu ilk sürümde yoktur.
- Çim, kaya ve kabuk dokuları üretilmiş sunum varlıklarıdır; saha fotoğrafı veya taraması değildir. Su ve zemin kotu atlasın ortak görsel kararıdır.

## Yüzey sahipliği

Önizleme için ada zemini, su ve hendek tabanı GLB içindedir. Ana atlas bu üç düğümü gizler; tekil zemin/su bölümü bunları zaten çizer. Beton kıyı kapalı hacimdir. Aynı malzemeli kesişen kayalar/ahşaplar birleştirilir; ahşap-kaya ve halat-ahşap gizli birleşim hacimleri kesilir. Kabuk UV yönü her dalın eksenini takip eder. Kaynak M5 dosyası değiştirilmez.

GLB denetimi ve görüntülü değerlendirme `model-report.json` / kök `design-qa.md` içindedir. Bu sürüm tüm yaşam alanının veya güncel saha durumunun eksiksiz modeli değildir. Yalnız yerel inceleme; canlıya yayınlanmaz.
