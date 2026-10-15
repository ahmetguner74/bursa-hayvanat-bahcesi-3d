# V2: rektifiye krokiden yol ağı

**15 Ekim 2026 güncellemesi:** Yerel V2 önizlemesi artık `manual-roads-metric.json` içindeki Dot'un QGIS ile elle yeniden çizdiği 85 eğrisel merkez hattından üretilmiş iki yol yüzeyini kullanır. `roads-metric.json` ve `extract_roads.py` önceki otomatik/kırıklı denemenin karşılaştırma kayıtlarıdır; `build_local.py` bunları yayın verisi olarak almaz. Özgün QGIS proje ve GeoPackage dosyaları çalışma dizininin kardeş `Bursa-Hayvanat-Bahcesi-QGIS-Delivery-2026-10-14/Bursa-Zoo-V2-Manual-QGIS/v2/qgis/` klasöründe tutulur. Yollar hâlâ şematik krokiden türetildiği için kesin aplikasyon değildir.

Bu ilk aşama yol yüzeylerini ve açılıp kapatılabilen gerçek krokiyi gösterir. Eylül 2026 tarihli [resmî Bursa Zoo ziyaretçi krokisi](https://www.bursahayvanatbahcesi.com/wp-content/uploads/2026/09/kroki.jpg) güncel yerleşim referansıdır. Aynı çizimin daha keskin [Mart 2026 sürümü](https://www.bursahayvanatbahcesi.com/wp-content/uploads/2026/03/kroki-1920x1080-1.jpg) yol kenarlarını ayırmak için kullanıldı; izler Eylül görseline, oradan `current-plan-registration.json` içindeki 12 noktalı afin dönüşümle M5 yerel metre koordinatlarına aktarıldı.

## Açma ve veriler

Proje kökünde `python v2/build_local.py` çalıştırıp `dist/` klasörünü yerel HTTP sunucusuyla açın. Sayfa adresi `http://127.0.0.1:8768/v2/` olur. Windows'ta `BASLAT.cmd` bunu hazırlar. Sayfa `roads-metric.json` vektörlerini, `rectification.json` ızgarasını ve yerel önizlemeye kopyalanan rektifiye krokiyi okur. **Gerçek kroki** kutusu yalnız yollar ile kroki+yollar arasında geçiş yapar; **Saydamlık** kaydırıcısı %0–100 arasındadır ve açılışta %45'tir. Binalar, su, çim ve V1'in eski yol katmanı ayrı model katmanları olarak çizilmez. Sürükleme, yakınlaştırma ve tüm yolları gösterme denetimleri vardır.

- `roads-source-pixels.json`: Eylül krokisinin piksel koordinatlarındaki izler; kaynak görselle kontrol için.
- `roads-metric.json`: aynı izlerin M5 yerel metre koordinatları; V2 ekranının veri kaynağı.
- `rectification.json`: kroki ve M5 arasındaki dönüşüm, ızgara, kaynak özeti ve hata kaydı.
- `roads-qa.png`: yalnız türetilmiş yollarla hazırlanmış görsel denetim.
- `private/`: krokiyle üst üste denetim ve rektifiye raster; Git dışında. `build_local.py`, rektifiye rasteri yalnız yok sayılan `dist/v2/` yerel önizlemesine kopyalar.

## Yol sürekliliği denetimi

İlk renk seçimi, gölgeli kenarlarda yolları çok inceltiyor ve ağaçların veya işaretlerin altında görünmeyen kısa parçaları koparıyordu. Üretim betiği şimdi açık renkli yol çekirdeğini çevresinde en fazla 3 kaynak piksel genişletilen yerel bir GrabCut sınıflamasıyla iyileştirir; yeşil bitki, kırmızı çatı ve mavi su renklerini yeni eklenen piksellerden dışlar. Kroki üzerinde izlenebilen kısa bağlantıların ara noktaları, genişlikleri ve güven düzeyleri `extract_roads.py` ile çıktı JSON'unda açıkça kayıtlıdır. Bu bağlantılar otomatik olarak keşfedilmiş veya sahada ölçülmüş çizgiler değildir.

Yaya ve araç yüzeylerinin her biri çıktı vektöründe birer bağlı alandır ve birbirleriyle alan olarak çakışmaz. `roads-source-pixels.json` içindeki `metrics` bölümü sınıflandırma ve bağlantı ekleme sayılarını, `private/roads-source-qa.png` ise izlerin gerçek krokiyle görsel karşılaştırmasını verir. Ağaç örtüsü altında yolun tam orta hattı görülemeyen servis–penguen bağlantısı düşük güvenlidir. Giriş binalarının çatıları altındaki eşikler kesin güzergâh olarak yorumlanmamalıdır.

Kaynak görüntüler makinede `reference-maps-private/` altında varsa, geliştirme bağımlılıklarını `python -m pip install -r v2/requirements.txt` ile kurup sırasıyla `python v2/rectify_plan.py` ve `python v2/extract_roads.py` çalıştırarak verileri yeniden üretebilirsiniz. Depo içindeki vektörler tek başına yol görünümüne yeterlidir. Özel rektifiye görsel bulunmazsa yerel derleme kroki katmanını devre dışı bırakır ve resmî kaynak bağlantısını gösterir.

## Doğruluk sınırı

Bu yüzeyler resmî fakat şematik ziyaretçi krokisinin yorumudur; aplikasyon veya ölçülmüş bordür çizgisi değildir. On iki elle eşlenmiş kontrol noktasında rektifikasyonun RMS hatası 10,7 m, en büyük hatası 22,64 m; ayrıntılı nesnelerin yerleri için yaklaşık 10–25 m belirsizlik kabul edilmelidir. Ağaç ve kuzeybatı servis yapıları altında kalan kısa yol bağlantıları, giriş binası eşikleri ve ön yolun yumuşak kenarı tam seçilemez. Bir sonraki aşamada bu yerler güncel ortofoto veya saha fotoğrafıyla düzeltilebilir.

Bu V2 yerel çalışmadır. `v2/build_local.py` kamuya açık `docs/` klasörüne yazmaz.
