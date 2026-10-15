# Harita → koloni → birey: kullanım incelemesi

16 Ekim2026. Kapsam kullanıcının son ekranına göre penguen gezinmesi/seçimi ve genel plan etiketleri. Kanıtlar bu çalışma sırasında çalışan AP uygulamasından alındı; eski QA görüntüleri bulgu olarak kullanılmadı. Çıktı mevcut proje içinde ekranlı rapor ve yerel düzeltmedir.

## Yakalanan eski akış

1. **Genel plan — sadeleşmesi gerekiyor.** [04-once-genel.jpg](qa/04-once-genel.jpg): penguen, gergedan, zürafa ve su kuşlarının yanında hayvan modeli olmayan Boz Ayı/Lemur/Habeş Maymunu adaları ve yapı adları bulunuyor. Bunlar yapı geometrisine sahip olsa da hayvan deneyimi beklentisini karşılamıyor.
2. **Uzak alan — gereksiz basamak.** [03-once-uzak-alan.jpg](qa/03-once-uzak-alan.jpg): kullanıcı penguen etiketi sonrası hâlâ uzakta, bir Penguenler etiketi daha seçmek zorunda. Son istek doğrudan yakın koloni kadrajı.
3. **Koloni — görünüm iyi, anlatılan birey belirsiz.** [01-once-koloni.jpg](qa/01-once-koloni.jpg): krem/yeşil bilgi paneli ve etiketsiz hayvanlar sade; otomatik seçilen ilk bireyin hareketi gösteriliyor, kimin olduğu sahnede işaretlenmiyor.
4. **Bireye dokunma — odak ve izleme eksik.** [02-once-secim.jpg](qa/02-once-secim.jpg): üçüncü kıyı bireyinin gövdesine gerçek dokunma davranışı değiştiriyor; kamera aynı koloni açısında kalıyor. Görsel seçim işareti yok. Yüzücü tap davranışı yüzmeyi/dinlenmeyi değiştiriyor; kamera takip etmiyor.

## Uygulanan karşılıklar

- Haritada yalnız dört hayvan modeli alanı; salt yapı/geçici barınak etiketleri kapatıldı.
- Penguen etiketi doğrudan son kaynak ekranın yakın kıyı kadrajına uçuyor.
- Kolonide varsayılan birey seçilmiyor. Gerçek seçim yapılmadan panel bireysel hareket anlatmıyor.
- Gövde seçimi bireye daha yakın bakış, ince yazısız halka ve panelde Kıyı/Havuz numarası getiriyor. Diğer hareketler yumuşakça sakinleşiyor.
- Seçilen yüzücü ilerlerken kamera izliyor. Yeni dokunuş yüzüşü uzatıyor; elle sürükleme takibi bırakıyor.
- Yakın yüzüşte gövdenin su içinde kaybolması6cm duruş ofsetiyle giderildi; kaynak GLB, su yüzeyi ve XY yolları korunuyor.

## Erişilebilirlik ve sınırlar

Gövde hedefleri en az44px, yazısız gerçek klavye düğmeleri ve Türkçe erişilebilir adlarla korunur; Enter, Escape ve geri kontrolü gerçek tarayıcıda denendi. Hover ve seçim halkası yalnız metin/renk farkına güvenmeyi azaltır. El hareketi seçim başlatmaz. Azaltılmış hareket tercihi ve gizli/offscreen durma üretim modülü testinde kontrol edildi. Tam ekran okuyucu/WCAG uygunluğu veya fiziksel telefon FPS/pil ölçümü iddia edilmez.

Son ekranlar, karşılaştırma geçmişi ve geçiş kanıtları proje kökündeki `design-qa.md` içindedir. Çalışma yalnız yereldir; yayın yapılmadı.
