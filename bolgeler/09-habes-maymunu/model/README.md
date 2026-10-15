# 09 · Habeş Maymunu Adası — ilk düzenlenebilir bileşen

[Yerel model incelemesi](http://127.0.0.1:8768/model-review/?model=habes) · [Atlasta aç](http://127.0.0.1:8768/?focus=region-9&perspective=65)

Bu varlık eski M5 metre geometrisi ile resmî fotoğraf/kamera bağlamının yorumudur. Güncel rölöve, imalat projesi veya tamamlanmış yaşam alanı modeli değildir.

## Kaynaklar

- `H22D01C2B:57`: ada iç sınırı, **1.331,5979435 m²**.
- `H22D01C2B:58`: dış su sınırı, **2.506,9042445 m²**; aradaki su bandı **1.175,306301 m²**.
- `H22D01C2B:149` / `150`: iki küçük sundurma izi, **7,640236 + 3,846357 m²**. İlk modelde aday yükseltilmiş ahşap platformlar olarak yorumlanır; kesin işlev/yükseklik teyitsizdir. Özgün `sourceH` metadata olarak saklanır, doğrudan model yüksekliği yapılmaz. Kimlikler ara ASCII öğe sırasıdır; özgün DGN öğe kimliği değildir.
- `641` / `642`: su katmanındaki **açık çizgiler**, kaynak bağlamında aynen saklanır. Uçları birleştirilip hayalî iç havuzlara dönüştürülmez.
- [Resmî 12 Kasım 2021 etkinlik kaydı](https://www.bursahayvanatbahcesi.com/cocuklar-hayvanlara-pasta-hzirladi/): arka planda açık toprak, yüksek ahşap direkler/halatlar, kaya kümeleri ve merdivenli alçak platform görülür. Ön plandaki ziyaretçi pergolası ve komşu kırmızı çatılı binalar bu modele atanmadı. Fotoğraf yükleme/etkinlik tarihi güncel saha durumu kanıtı değildir.
- Resmî babun yakın planı oyuk gövdenin ahşap karakterini gösterir; kesin konumu veya boyutunu sağlamaz. Belediye kamerası ayrıca kıyı bağlamı olarak kaynak klasöründe korunur; edinim zamanı çekim tarihi değildir.

Fotoğraf, HTML arşivi, URL, tarih, gözlem ve SHA kayıtları `../kaynaklar/` altındadır. Fotoğraflar GLB malzemelerine veya `dist/` paketine konmaz. Kullanılan dokular mevcut üretilmiş albedoların teknik JPEG türevleridir.

## Düzenlenebilir dosyalar

- `model-inputs.json`: değiştirilmemiş kaynak XY halkaları, metre origin'i, kaynak SHA'ları, yorumlanan elemanlar ve belirsizlikler.
- `build_habes.py`: kapalı geometri, materyal/UV ve glTF üreticisi.
- `textures/manifest.json`: dört 512² JPEG'in kaynak/türev SHA ve kodlama bilgisi.
- `habes-maymunu-adasi.glb`: **14.129 üçgen / 754.020 bayt**, metre ve glTF Y yukarı ekseni. M5 yerleştirme origin'i `[195.02630276517107, -8.041950969880599]`.
- `asset-verification.json`: gerçek dışa aktarılan geometri ve yüzey sahipliği denetimi.
- `gltf-validation.json`: gerçek GLB SHA'sına bağlı Khronos raporu.

Altı yüksek direk, on iki halat, sekiz kaya, iki çapraz ahşap eleman, bir oyuk gövde ve merdiven fotoğraftan yaklaşık yorumdur. Tekil konum, sayı, ölçü ve görünmeyen taraflar saha ölçüsü değildir. Oyuk gövde içi gerçekten boş kapalı duvar hacmidir. Ahşap birleşimleri birleştirilir; halat/ahşap/kaya gizli kesişimleri kesilir. Platform üstleri özgün iki M5 izini korur; merdivenin platform üstüne taşan kısmı kesildiği için eşdüzlem üst yüz yinelenmez.

## Atlas yüzeyleri ve doğrulama

Beton kıyı şeridi **37,425507 m²** yorum maskesiyle ortak zemin bölümünden çıkarılır; altında ikinci görünür zemin kapağı çizilmez. Kalan **1.294,172437 m²** ada toprağı tek malzeme bölgesidir. Modelin önizleme toprağı, su yatağı ve su düğümleri atlasta gizlenir; ortak bölüm bunları bir kez çizer. Ek orman bitkileri adanın dışında tutulur. Adadaki bir eski M5 ağaç sembolünün temsili ağacı bu açık ada sunumunda gizlenir; özgün nokta dosyada korunur.

Yeniden yüklenen GLB'de dokuz kapalı parça sonlu, yönleri tutarlı ve pozitif hacimlidir. Önizleme su yüzeyi bir açık düzlemdir. Kaynak izdüşümüyle fark: toprak **0,0000335275 m²**, kıyı **0,0000793075 m²**, su **0,0001074961 m²**; iki platform **0,0000025501 / 0,0000037065 m²**. Kıyının su/yol/arazi bölümüne alan örtüşmesi sıfırdır. Khronos raporu hata/uyarı/bilgi/ipucu **0**; bu saha veya görsel kabul sertifikası değildir.

Proje kökünde yeniden üretim:

```powershell
python build_surface_layers.py
python bolgeler/09-habes-maymunu/model/build_habes.py
node bolgeler/validate_models.cjs
python bolgeler/09-habes-maymunu/model/verify_habes.py
python publish_local.py --local-only
```

`capture_inputs.py` ilk kaynak yakalama içindir; mevcut girdinin üzerine yazmayı reddeder. Düzenlemeler `model-inputs.json` üzerinde bilinçli yapılır. `publish_local.py` yalnız yerel `dist/` üretir; `docs/` ve canlı site hedefi kapalıdır.
