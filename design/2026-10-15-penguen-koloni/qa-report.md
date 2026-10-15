# Penguen koloni deneyimi — görsel ve işlevsel kontrol

Revizyon: `20261015ap`. Kapsam: kullanıcının iki yeni telefon görüntüsüne göre yalnız penguenlerin yakın deneyimi. Diğer türler AO akışını sürdürür. Canlıya yayınlanmadı.

## Kaynak ve gerçek ekranlar

- [Tasarım sözleşmesi](design/2026-10-15-penguen-koloni/design-spec.json): özgün kullanıcı fotoğraflarının tam dosya yolları, kamera ve panel sözleşmesi.
- [Kaynaklarla birlikte karşılaştırma](design/2026-10-15-penguen-koloni/qa/referans-karsilastirma.jpg): kaynak1/yerel alan ve kaynak2/yerel koloni aynı görüntüde incelendi.
- [Gerçek telefon alanı390×844](design/2026-10-15-penguen-koloni/qa/alan-390x844.jpg)
- [Gerçek telefon kolonisi390×844](design/2026-10-15-penguen-koloni/qa/koloni-390x844.jpg)
- [Gerçek masaüstü1280×720](design/2026-10-15-penguen-koloni/qa/koloni-1280x720.jpg)
- [Gerçek yatay ekran844×390](design/2026-10-15-penguen-koloni/qa/koloni-844x390.jpg)

Görüntüler çalışan yerel WebGL uygulamasından alındı. Karşılaştırma levhasında yalnız kaynak telefon fotoğraflarının tarayıcı/status çerçeveleri kırpıldı: x0–590,y82–1090; ardından oran korunarak390×844 hücreye yerleştirildi. Gerçek AP görüntüleri390×844 CSS/pikseldir. Kaynak tarayıcının CSS viewport'u bilinmediği için birebir piksel eşitliği iddia edilmez. Yeni sağ panel kullanıcının yazılı ek isteğidir; kaynak2'de mevcut değildir.

## Karşılaştırma sonucu

1. Alan görünümünde tek **Penguenler** etiketi korunur; yakına geçince kamera bir bireyi büyütmek yerine üç kıyı bireyi ve havuzu birlikte gösterir.
2. Yakın görünümde bireysel adlar/ipucu/eylem düğmeleri bulunmaz. Dokunma gerçek gövde seçimidir; klavye için yazısız ve yalnız odakta halkası beliren hedefler korunur.
3. Sağdaki128px mobil/240px masaüstü panel sahnenin üstünü örtmez; sahne ve ray koordinatları kalan genişlikle hesaplanır. Tür tanıtımı ile **Şu anda** bölümü ince ayırıcıyla ayrılır. Üst kimlik/geri/tam ekran kontrolleri korunur.
4. İlk kontrolde uzun **Genel plana dön** yazısından ölçülen başlık, kısa **Alana dön** yazısı sonrası paneli gereksiz aşağıda bırakıyordu. Sıra düzeltildi; son390px ekranda başlık altı56px, panel üstü74px.
5. Kısa yatay ekranda tanıtım iki satıra kısalır, ek tür ölçüleri gizlenir; davranış başlığı ve açıklaması kaydırma gerektirmeden görünür. Son844×390 ekranda panel293px iç yükseklik/293px içerik.

## Beş görsel yüzey

- **Yazı:** mevcut Inter/Arial arayüzü ve Georgia tür başlığı; bilimsel ad italik.128px kartta metin taşmaz; uzun hareket adları satıra bölünür.
- **Yerleşim:** tek sahne, sağ bilgi kartı, üst geri kontrolü. Alt panel ve davranış seçicisi yoktur. Panel telefonda alt çekmeceye dönüşmez.
- **Renk:** mevcut krem/koyu yeşil dil, düşük kontrastlı ayırıcılar ve hafif gölge. Klavye odağı yalnız renkle anlatılmaz.
- **Görsel kalite:** kaynak iskeletli GLB/dokular ve M5 yerleşim korunur. Yeni ağır efekt, mesh veya ek render geçişi eklenmedi. Kuşların üstünde yazı yoktur.
- **Metin:** türün yaşam alanı/beslenmesi/boyu [San Diego Zoo](https://animals.sandiegozoo.org/animals/african-penguin) üzerinden kontrol edildi. Hareket bölümü gözlenen denetleyicinin gerçek durumunu anlatır; komut listesi veya kullanıcıya hayvan besleme/sevme çağrısı içermez.

## İşlev ve performans

[Gerçek üretim modülü/GLB testi](verification/penguin-discovery.json): beş birey kendiliğinden sırayla kısa davranış yapar;25 hızlı dokunuş son istekle yönetilir; karede en fazla iki görünür rig örneklenir. Yüzücüler kaynak havuz maskesinde kalır. Görünmeyen yüzücüler görünür kıyı bireylerini engellemez; gizli/offscreen görünüm donar. Azaltılmış hareket tercihinde otomatik davranış yoktur, açık dokunma çalışır.

[Dört tür regresyon kontrolü](verification/explorer-interactions.json): gerçek mesh seçimi,30Hz dokunmatik örnekleme, zemin teması, ayrı iskelet/ortak geometri ve sonlu hareketler geçti. Yeni kamera/panel bu revizyonda yalnız penguenlere uygulanır.

[Tarayıcı kaydı](design/2026-10-15-penguen-koloni/qa/browser-checks.json): gerçek gövdeye dokunma davranışı değiştirdi; kamera `resting` kaldı. Enter çalıştı. Geri dönüş paneli gizledi ve390px sahne genişliğini geri getirdi. Yakından çıkış sonrası üç5s kayıtta0 pose güncellemesi,0 aktif hayvan ve0 sahne çizimi görüldü; konsolda hata/uyarı yoktu. Fiziksel telefon GPU/FPS/pil ölçümü yapılmadı.

`docs/` farkı yok; HEAD `5e4a223` kaldı. M5 `site-data.json` ve `v2/manual-roads-metric.json` SHA-256 değerleri değişmedi. Yalnız `publish_local.py --local-only --runtime-only` çalıştırıldı.

Final result: **passed** — bu revizyonun penguen arayüzü ve davranış kapsamı için;43 alanın modellemesinin bittiği veya fiziksel telefon performansının ölçüldüğü anlamına gelmez.
