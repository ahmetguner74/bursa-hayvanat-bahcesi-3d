# Baringo tarzı zürafalar ve açık Savanna bölümü — yerel v1

**Güncel yerel akış ·20261015ao:** Tür etiketi veya hayvanın gövdesiyle yaklaşılır; yakında dokunmak kaynak bakınma veya kısa gerçek yürüyüş seçer. Yürüme zamanlayıcıyla başlamaz; sekiz saniyelik istek ivmelenir ve durur. Geometri, rotalar, M5 konumu ve çevrimdışı temas tabloları değişmedi. Ortak davranış/yükleme `viewer/animal-interaction.js` ve `tap-colony.js` içindedir. Aşağıdaki model/araştırma ve eski ölçümler önceki aşamayı açıklar.

İki temsili yetişkin, BlueMesh’in CC BY4.0 kaynak modeliyle üretildi. Bursa’daki resmî Baringo referansı için alt bacaklar lekesiz, açık tonlu teknik doku türevine geçti. Kalan benek dağılımı ve kafatası genel kaynak modele dayanır; tam alt tür anatomisi veya birey portresi iddiası yoktur.

## Hayvan

- `baringo-giraffe.glb`:15.236 üçgen,49 eklem,iki skinned mesh (gövde/göz);2.010.284bayt. İki birey geometri/dokuları paylaşır, bağımsız iskelet/zamanlayıcı kullanır.
- BlueMesh’in hazır4sn klibinde bacaklar sabitti. `Idle_Source_BlueMesh` adıyla boyun/kuyruk dinlenme klibi olarak korunur.
- `Walk_Authored_LateralSequence` bu projede üretildi. Primer zürafa yürüyüş araştırmasına uygun, aynı tarafta arka ardından ön ayak, karşı taraf yarım dönem sonra basar. Seçilen0,12 dönem ofseti,4sn dönem,%70 basma ve0,48m/sn hız görsel yorumdur; hareket yakalama veya Bursa bireyinin ölçülmüş gait’i değildir.
- İki segmentli IK ve gerçek skin tabanına üç adımlı düzeltme çevrimdışı hesaplanır. Tarayıcıda vertex döngüsü/fizik hesabı yoktur. Son basan toynak sapması≤0,000091m; blend tablosu bağımsız örneklerinde en kötü0,000501m.
- Kaynak GLB, UV adası sınırlarında ayrık vertex içeriyordu. Subdiv’in yarattığı boyun/sırt dikişleri yalnız çakışık vertexlerin2152→1780 birleştirilmesiyle düzeltildi. UV loop sınırları korunur. Bir subdiv ve%70 gövde azaltma sonrası15.236tri; gözler özgün360tri.
- Hızla eşleşen klip, kademeli durma, bağımsız dinlenme ve küçük kulak hareketleri vardır. Yakın masaüstü60Hz/mobil görünüm30Hz, uzak12Hz; görüş dışı/gizli sekme/kapalı hayvan katmanında durur. Bunlar hedef güncelleme oranları; fiziksel telefon FPS ölçümü değildir. Dönüş hız sınırı var; tüm ayaklar için gerçek zamanlı sürtünme/foot-lock çözümü yoktur.

## Açık yaşam alanı

`zurafa-acik-yasam-alani.glb`:17.795tri,12 mesh,5.075.884bayt. Resmî2017/2018 fotoğraflarındaki yeşil yatay ziyaretçi rayları, alçak taş sınır, kumlu toprak, dal yemleme ve ağaç/kaya karakteri yorumlanır. Yüksek ısıtmalı barınağın varlığı resmî2018 yazısında doğrulanır; cephe/konum yeterli olmadığı için yeni bir ahır uydurulmadı. Mevcut ahşap platform aynen korunur.

M5 yerel origin `[60,48]`,metre,Z yukarı. Tek floorOwnershipMasks alanı1611,349391m²; toprak1598,238198m² ve taş sınır13,111192m² birbirinden ayrıdır. Önceden üretilen yol/su/yapı alanlarına pozitif kesişim yoktur. Atlas maskeyi ortak zeminden çıkarır; ikinci kapak yığılmaz. Sonraki rebuild’de atlasın kendi floor maskesi tekrar çıkarılmaz; donmuş habitat girdisi kullanılır.

`habitat-inputs.json` ve `model-sources.json` kaynak/yorum ayrımını tutar. Mevcut kroki eşlemesinin10–25m konum belirsizliği devam eder. Çit/yemlik/ağaç yerleri ve yükseklikler yorumdur; tüm Savanna’nın rölövesi değildir. İki9m CC0 Jacaranda ağacı gösterim ağacıdır, Bursa ağaç türü tespiti değildir.

## Düzenlenebilir kaynaklar

- `source/`:özgün indirmeler ve yerel açılan Blender/doku dosyaları; kaynakSHA’ları `source-manifest.json`.
- `baringo-giraffe-editable.blend`:metrik hayvan, özgün idle ve üretilmiş walk eylemleri.
- `savanna-giraffes-editable.blend`:açık alan,iki bağımsız49eklemli rig, paketli dokular; M5 origin korunur. Önizleme ışığı/kamerası GLB runtime paketine eklenmez.
- `giraffe-colony.json`:M5 güvenli rotalar,ölçek,hız,çevrimdışı temas tablosu. Hayvan sayısı gerçek güncel envanter olarak sunulmaz.

## Yeniden üretim

Blender5.2.1LTS, Python3.12(numpy/trimesh/shapely/Pillow/OpenCV), Node24, proje vendor Three.js ve yerel Khronos glTF validator:

1. Blender `--background --factory-startup --disable-autoexec --python prepare_blender.py`
2. Python `adapt_texture.py`
3. Blender aynı güvenli seçeneklerle `author_walk.py`
4. Python `post_pack.py`
5. Node `inspect_delivery.mjs`, ardından `verify_contact.mjs`
6. Python `build_habitat.py`; Node `verify_colony.mjs`
7. Blender aynı seçeneklerle `save_editable_scene.py`

Betikler bu klasörden çağrılabilir; iç yollar dosya konumuna göre çözülür. Kök dosyalara/canlı yayına bu alt işlem yazmaz.

## Son kontroller

`contact-verification.json`:gerçek GLB validator0hata/0uyarı, basma ve blend temas ölçümü.
`colony-verification.json`:1200sn/144.000güncelleme,iki birey arasında en az11,6437m,güvenli alan dışına çıkış yok, bağımsız rig/ortak geometri, gizli sekme/duraklat/devam testi.
`editable-scene-verification.json`:iki rig/98kemik,paketli görseller,metrik kaynak.
Ana tarayıcı görünümü/kare süreleri kök ajan tarafından ayrıca doğrulanır. [Atıf ve lisanslar](ATTRIBUTION.txt).
