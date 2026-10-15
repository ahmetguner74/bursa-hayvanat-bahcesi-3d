# Savanna ahşap yapı — ilk bileşen

`savanna-ahsap-platform.glb` metre biriminde, glTF Y yukarı ekseninde düzenlenebilir modeldir. `model-inputs.json` ayak izi ve varsayımları, `build_platform.py` parametrik üretimi, `model-report.json` geometri kontrollerini tutar. Yeniden üretim: `python bolgeler/12-afrika-savana/model/build_platform.py`.

## Kaynak ve belirsizlik

- Belediye 2 Şubat 2017 haberinin `23247_YHG_8895_201702021252.jpg` fotoğrafında beşik çatılı, çapraz taşıyıcılı, yükseltilmiş ahşap yapı, eğimli yaklaşımlar ve tel sepetler görülür. Fotoğrafın çekim tarihi ve 2026 durumu ayrıca doğrulanmadı.
- M5 `H22D01C2B:145`, 33,448255 m² çatı izi için **aday eşleşmedir**. Fotoğraftaki yapının bu konumda bulunduğu teyit edilmedi. Eski M5 yüksekliğinin mahya yüksekliği olduğu da kesin değil; bu ilk yorumda datum 93,5 m çıkarıldı.
- Yapının seyir platformu, barınak veya yemleme yapısı olarak kesin işlevi teyitsizdir. `23247_YHG_8948_201702021252.jpg` başka açıdan bu yapıyı göstermez; taş sınırda zürafa beslenmesini gösterir. Kaynak rolleri düzeltildi.
- Taşıyıcı kesitleri, döşeme kotu, rampalar, sepet konumları ve görünmeyen yüz fotoğraftan yaklaşık yorumdur. Bu model Afrika Savana'nın tümünü tamamlamaz.

## Geometri ve malzeme

Çatı özgün M5 XY izini korur. Tek kapalı çatı hacmi var; ahşap birleşimler boolean union ile birleştirilir, çatı/taşıyıcı/döşeme arasındaki saklı hacimler malzeme sahipliğine göre kesilir. Her malzeme grubu kapalı, tutarlı yönlü ve pozitif hacimli olarak doğrulanır. Zemin yüzeyi eklenmez; genel bina kabuğu bu sundurmayı ayrıca çizmez.

Ahşap albedo AI ile üretilmiş sunum malzemesidir; kaynak fotoğraf değildir. Asıl PNG ve SHA256 `viewer/assets/asset-manifest.json` kaydındadır. Sadece yerelde kullanılır.
