# İlk 3B varlık: Su Kuşları kubbesi

15 Ekim eklemesi: Uzak sürümde 186 kalın sunum kirişi korunur; özgün yaklaşık üçgen örgü 1.962 ince çizgi parçasıyla okunur. Çizgiler glTF `LINES` türündedir, ikinci dolu yüzey değildir. Kalınlıkları ekranda bir pikseldir. Yakın ve uzak çeliğin taban rengi atlasla ortak `#aab9af`; yakın çubuk yarıçapı da birebir ölçülmüş tekil boru çapı değildir.

Bu klasör, resmî krokide #31 Pelikan Göleti işaretinin üzerinde görülen kubbenin **ilk yapı kabuğunu** içerir. #32 Su Kuşları güneyde ayrı işaretlenir; adlandırmanın fiziksel kapsamı sahada henüz doğrulanmadı. Bu nedenle varlık #31 altında üretilir ve #32 kaynak klasöründen de belgelenir.

## Kaynak ve ölçü

- [USKON yapımcı açıklaması](https://uskon.com/en/bursa-zoo-waterbird-cage-single-wall-elliptical-dome/): 70 m uzunluk, 40 m genişlik, 20 m yükseklik, eliptik yarım kubbe, 2.029 çelik boru, 700 düğüm, 5 × 5 cm naylon ağ.
- `../kaynaklar/fotograflar/uskon-plan.jpg`, `uskon-entrance-1.jpg`, `uskon-exterior-1998.jpg`: yerel çalışma kopyaları; cephe, portal ve ana siluet referansı.
- M5 konum yorumu: merkez `[-30, -64]` yerel metre, ana aks yaklaşık `+9°`. Krokiden M5'e genel eşleme hatası yaklaşık 10–25 m olduğundan bu yerleşim aplikasyon sayılmaz.

## Dosyalar

- `build_dome.py`: parametreli, düzenlenebilir üretici.
- `su-kuslari-kubbesi-yakin.glb`: yakın detay için 1.962 görsel çubuk, düğümler ve iki açık portal.
- `su-kuslari-kubbesi-uzak.glb`: uzak sunum için 186 daha kalın kiriş, aynı çelik rengi ve portal açıklığı.
- `model-report.json`: ölçü, geometri, köken ve belirsizlik kaydı.
- [Yerel model incelemesi](http://127.0.0.1:8768/model-review/): yakın/uzak ve üstten denetim.

İki model de glTF 2.0 / Y-yukarıdır; Python kaynağında Z-yukarı kurulan ölçüler dışa aktarımda çevrilir. Khronos glTF doğrulamasında iki dosyada da hata ve uyarı yoktur. Uzaktaki 0,18 m çubuk **yalnız okunurluk için sunum kalınlığıdır**; yapımcı çapı değildir. İç gölet, köprü, bitkiler ve yol ayrı sahne katmanlarındadır; bu varlık yalnız çelik kabuk ve girişleri içerir. Fotoğraf pikselleri doku olarak kullanılmadı.
