# Afrika Köyü · model 06

[Yerel 3B inceleme](http://127.0.0.1:8768/model-review/?model=african-village). Ana atlasta görünüm menüsünden **14 · Afrika Köyü** seçilir. Canlıya yayınlanmaz.

## Kaynak

Belediyenin [2012 faaliyet raporunun117. sayfasında](https://www.bursa.bel.tr/dosyalar/yayinlar/faaliyet_2012.pdf#page=117) fotoğraf “Afrika Köyü Barınakları” olarak adlandırılır. Özgün PDF `../kaynaklar/belgeler/belediye-faaliyet-2012.pdf` içinde;327×198 gömülü JPEG `../kaynaklar/fotograflar/belediye-2012-afrika-koyu-xref1747.jpeg` içine değiştirilmeden çıkarıldı. Dosya özetleri kaynakçada ve model girdilerinde kayıtlı. Bu tarihî görüntü2026 durumunu doğrulamaz.

Eski M5'teki `H22D01C2B:3007`–`:3013` dairesel sundurma/saçak izleri, kroki ve fotoğraftaki sıra ile yaklaşık eşleştirildi. Yedi çatı toplam546,244784m². Özgün eave/saçak XY noktalarının tamamı korunur; M5 verisi değiştirilmez. Merkez `[100.71515985586787,96.67671636694187]` yerel metre.

## Düzenleme ve sınırlar

Modelin kullandığı yedi özgün M5 öğesi [ayrı kaynak dosyasında](../kaynaklar/harita-verisi/model-kaynak-m5.json). Genel kroki bağlamının dışında kalan ilk iki saçak da burada; bütün kaynak alanları/koordinatları değiştirilmeden bulunur.

Üretilmiş [çatı dokusu PNG](../../../viewer/assets/afrika-koyu-roof-shingles-v1.png) ve [tam son prompt/üretim kaydı](../../../viewer/assets/asset-manifest.json) proje içinde. Built-in Image Gen ile tek üretim;1254×1254 opak RGB dosyası değiştirilmeden kullanıldı. Malzemenin tam dikişsizliği teyitsiz, sıra altlarında gömülü koyu gölge bulunur.

`model-inputs.json` her çatının kaynak izini ve ayrı duvar/kapı parametrelerini taşır. `python bolgeler/14-afrika-koyu/model/build_african_village.py` GLB'yi yeniden oluşturur. Model glTF Y yukarı; atlas yüklerken M5 Z yukarı çerçevesine döner.

Fotoğraftaki beyaz düz yüzlü duvar, koyu kademeli konik çatı, sivri tepe ve koyu dikdörtgen giriş karakteri izlendi. **Sekizgen duvar, saçak yarıçapının%86'sı kadar duvar, bütün yükseklikler, kapı yönleri ve çatı kademe sayısı yaklaşık yorumdur.** M5 kaynakH değeri yalnız metadata; saçak/mahya/saha kotu anlamı teyitsiz. Şingıl dokusu Image Gen sunum materyalidir, çatı taraması değildir; malzemenin türü/yapım tekniği kesinleştirilmedi.

İç odalar, hayvanlar, arka bağlantılar ve fotoğraftaki ön çit bu ilk bileşende yok. Bütün bölgenin veya güncel saha durumunun tamamlanmış modeli değildir.

## Geometri ve yüzey sahipliği

Her çatı tek kapalı kademeli hacimdir; üst kademe çemberleri90 örnek, alttaki iki saçak çemberi özgün1080 noktadır. Eşit olmayan halkalar arasında bağlantı üçgenleri vardır; üst üste koni kopyaları kullanılmaz. Duvar girişleri gerçek kesilmiş açıklıklardır. Duvar tabanı tek döşemenin üstünde başlar; ortak hacim yoktur.

Yorumlanan363,730171m² duvar/döşeme izi ortak yüzey bölümünde bina maskesidir. Altındaki yol/çim bir kez kaldırılır; kaynak QGIS dosyası değişmez. Yeni yapı tabanının ayırdığı avluya, yapıların dışında kalan küçük bir yorum geçişi eklendi; bunun özgün QGIS yolu veya ölçülmüş aplikasyon olduğu iddia edilmez. Yol bileşeni sayısı önceki5 düzeyinde korundu.

Gerçek dışa aktarılan GLB kontrolü `bolgeler/verify_inventory.py`, Khronos biçim kontrolü `node bolgeler/validate_models.cjs`, sonuçlar `model-report.json` ve `gltf-validation.json` içinde. Görüntülü inceleme/kalan bulgular kök `design-qa.md` içinde.
