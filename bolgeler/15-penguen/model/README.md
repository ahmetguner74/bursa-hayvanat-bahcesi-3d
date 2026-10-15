# Penguen havuzu — düzenlenebilir 3B model v1

`penguen-havuzu.glb` metre birimli ve glTF Y yukarı eksenindedir. M5 yerel ankrajı `[-14,134]`. [Ayrı model incelemesi](http://127.0.0.1:8768/model-review/?model=penguin) ve [atlas içindeki görünüm](http://127.0.0.1:8768/?focus=penguin&perspective=65) yerelde çalışır.

## Dayanak

- `model-inputs.json` eski M5 `H22D01C2B:64` su poligonunu korur: **204,74 m²**. Kaynak veri SHA256 özeti kaydedilir; veri değişirse üretici durur.
- Belediye yapım/hizmete açılma kayıtları ve on mimari bağlam fotoğrafı `../kaynaklar/` içinde. Fotoğraflar **2017** dönemine ait; mevcut 2026 durumunu tek başına kanıtlamaz.
- [24 Haziran 2017 belediye duyurusu](https://www.bursa.bel.tr/haber/bursa-zoo-nun-yeni-misafirleri-fok-ve-penguen-24148) penguenler için 300 m² havuz ve 300 m² kara alanı bildirir. Eski M5 su iziyle fark çözümlenmedi. Model, bu sayıya ulaşmak için zorla ölçeklenmedi.
- Fotoğraflardaki koyu mavi bordür, gri drenaj bandı, açık çakıl kıyı, gri yapay kaya duvarlar, alçak iç kayalar ve ahşap seyir platformu yeniden yorumlandı. Komşu fok havuzu fotoğrafları manifestte ayrı rol taşır.
- Duvar yükseklikleri, platform ölçüsü/konumu, su içi taş konumları ve **1,5 m taban kotu** ölçülmüş değerler değildir. Bunlar kaynak kodundaki düzenlenebilir yorum parametreleridir. Model güncel rölöve veya imalat projesi değildir.

## Geometri ve yüzey sahipliği

Modelde 14.413 üçgen var. Havuz gövdesi, yapay kaya duvar, çakıl tabanı ve drenaj halkası kaynak üretiminde kapalı, tutarlı yönlenmiş ve pozitif hacimli olarak sınanır. Su yüzeyi ayrı tek yüzdür; şeffaf su gölge haritasına opak yüz gibi yazılmaz.

Ana atlas `pool_water` ve `gravel_ground` düğümlerini gizler. Su, mevcut düzlemsel bölümden bir kez çizilir. Çakıl alanı çimden geometrik olarak bölünerek **183,13 m²** ayrı malzeme bölgesi olur; üstüne ikinci çakıl kapak konmaz. Modelden yalnız bordür, kaya ve yükseltilmiş platform gibi gerçek hacimli parçalar eklenir. Bağımsız incelemede bu iki düğüm de görünür.

Kaya ve çakıl taban renk görüntüleri AI ile üretildi; gerçek fotoğraf pikselleri doku olarak kullanılmadı. Kayıtları `viewer/assets/asset-manifest.json` içinde. Aynı görüntü ve doku kaynakları farklı renkli parçalarda ortak kullanılır.

## Yeniden üretim

Proje kökünden:

```powershell
python -m pip install -r requirements.txt
python publish_local.py --local-only
python bolgeler/verify_inventory.py
```

`build_penguin.py`, `model-inputs.json` ve `model-report.json` düzenlenebilir kaynak/sonuç kayıtlarıdır. `docs/` veya uzak yayın kullanılmaz. [Hareketli Afrika pengueni ilk modeli](hayvan/README.md) eklendi: üç kıyı ve iki yüzücü birey; kaynaklı GLB/Blender, gerçek iskelet animasyonları ve güvenli dolaşım alanları. Ayrıntılı drenaj ızgarası ve güncel saha fotoğrafı ile son doğrulama bekler.

## Yerel havuz düzeltmesi · 20261015al

Bordür ve drenajın 57 cm'lik izi ortak yol/çim bölümünden çıkarıldı. Yol dere taşları yalnız gerçek yol–kara sınırında üretilir; su ve modele ait kenarlarda boşluk bırakılır. `verify_pool_fixes.py`: kenar–yol/çim çakışması sıfır, havuz kenarının 65 cm yakınında yol taşı sıfır. İki iç kayanın görünen tepesi korunup su altı gövdesi −1,49 m'ye, yorum taban kotu −1,45 m'nin altına uzatıldı.

Yapay kaya duvar tek kapalı gövde olarak, tekrarlanan sinüs tepesi yerine kırık üst çizgi ve farklı eğimli yüzlerle düzenlendi. Kaynak 2017 fotoğrafındaki yapay kaya panelleri referanstır; birebir güncel rölöve değildir. Penguen su yansıması mevcut tek su mesh'i üzerinde azaltıldı; yeni yansıma geçişi eklenmedi. Kamera başlığındaki sabit “yakından” ifadesi kaldırıldı, alan/yakın düğmeleri eklendi ve mobil yükseklik değişiminde kamera konumu korunur. Fiziksel iPhone doğrulaması henüz yapılmadı. Bu değişiklikler yalnız `dist/` içindedir; canlıya yayınlanmadı.

Yakın penguen kamerası çalı içinde kalan eski noktadan açık çakıl kıyısına taşındı. Yerel son görünüm `pool-webgl-20261015al.png` gerçek atlas/WebGL çıktısıdır.
