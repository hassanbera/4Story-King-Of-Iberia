# Yesode Acemisi — Caelen

29 Ekim 2026: mevcut PhilipMorris oyununa, 30 sakinden ayrı tek asker prototipi eklendi. Yeni hesap veya yeni veritabanı oluşturulmadı.

Caelen insan erkek Warrior, Derion üyesi ve seviye 1. Unvanı `Yesode Acemisi`. Görünüşü kabul edilen insan erkek şablonundan türetildi. Ekipman: One Handed Sword (121), Wooden Shield (1021), Bronze Lightweight Helm/Armor/Leggings/Gauntlets/Greaves (4601–4605). Yedi eşyanın ülke, seviye ve Warrior sınıf maskesi mevcut veritabanından doğrulandı; geliştirme seviyesi eklenmedi.

## Yol ve davranış

- Marad: istemcide görünen ad; sunucu tablosunda Marat, NPC 20058.
- Remings: istemcide görünen ad; sunucu tablosunda Lemmings, NPC 20065.
- Başlangıç Marad'ın önündeki kabul edilmiş rota noktası; bitiş Remings'in önüne ayrılmış nokta.
- `bRoamType=6`: sıralı noktalardan yürür, son noktada ayakta bekler. Döngüye girmez, rastgele hedef seçmez.
- Mevcut sakinlerin `bRoamType=5` grafiği değiştirilmedi.
- Sunucu/varlık yeniden doğduğunda yürüyüş başlangıçtan başlar. Bu ilk prototip kalıcı görev ilerlemesi tutmaz.
- Mevcut oyun motorunda hareket, yakındaki oyuncunun varlık simülasyonuna bağlıdır. İlk kontrol sırasında Caelen'e eşlik edilmelidir; uzaklaşınca simülasyon duraklayabilir.

Yol ara noktaları mevcut haritadaki spawn koordinatlarından seçildi. Bu, aradaki engellerin geçilebilirliğini kanıtlamaz. Marad–Remings yürüyüşünün ve ekipman çiziminin oyuncu tarafından görsel kabulü henüz bekleniyor.

## Dosyalar ve geri alma

- `world/yesode/soldiers/caelen.json`: kimlik, ekipman, koordinatlar ve davranış tanımı.
- `scripts/prepare_soldier.py`: mevcut TMon'u okuyarak tek kayıt ekleyen aday ve doğrulamalı SQL üretir. Mevcut 2.359 kayıt bayt düzeyinde korunur.
- `scripts/Install-YesodeSoldier.ps1`: kapalı istemciyi şart koşar; dört mevcut sunucuyu durdurur; COPY_ONLY/CHECKSUM yedeği ve RESTORE VERIFYONLY kontrolü alır; işlemi mevcut LocalDB üzerinde uygular.
- Aynı betiğin `-Rollback` seçeneği yalnız askerin 32700 kimlikli kayıtlarını kaldırır, önceki TMon ve Map EXE'sini hash kontrollü geri getirir. Oyun kapalı olmalıdır.
- Yedekler, aday dosyalar, kurulum manifesti ve SQL yedeği Git dışında `runtime/soldier-caelen/` altında tutulur.

## Doğrulama

Kaynak Map derlemesi başarıyla bağlandı. Kurulum sonrası SQL kontrolü: 1 asker, 9 yol noktası, önceki 30 sakin korunmuş. TMon adayı tekrar ayrıştırıldı, önceki tüm kayıtlar birebir karşılaştırıldı. İlk Map açılışında Windows C++ exception (0xe06d7363) kaydetti; yeniden başlatmada dört yerel port açıldı. İlk açılış hatasının kök nedeni belirlenmiş değildir; tekrar ederse ayrıca incelenmelidir. Oyun içi görsel yürüyüş kabulü bu kontrollerden ayrı tutulur.
