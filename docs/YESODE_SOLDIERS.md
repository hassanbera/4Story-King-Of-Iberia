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

İlk aday yol, uzak spawn koordinatlarını doğrudan bağladığı için kullanıcı kontrolünde yanlış güzergâha gitti ve takıldı. Sunucu kaydı, otomatik eklenen ara noktada gerçek zeminin yaklaşık 77, hedef yüksekliğinin yaklaşık 90 olduğunu gösterdi. Bu yüzden yatay konuma ulaşsa da dikey varış kontrolü geçilemiyordu.

Yeni yol, kullanıcının açıkça başlatıp Remings'e vardığında bitirdiği Marad–Remings yürüyüşünden alınan 34 zemin noktasından oluşur. Önceki, kullanıcının kullanılmamasını istediği kayıt dışarıda tutuldu. Noktalar arasında en fazla 9,15 birim yatay aralık vardır; zemin yüksekliği en düşük 75,52'ye iner. Type 6 için sunucunun eski otomatik ara nokta ekleme davranışı devre dışı bırakıldı. Askerin yeni yolu tekrar etmesi ayrıca oyun içinde doğrulanmalıdır.

## Dosyalar ve geri alma

- `world/yesode/soldiers/caelen.json`: kimlik, ekipman, koordinatlar ve davranış tanımı.
- `scripts/prepare_soldier.py`: mevcut TMon'u okuyarak tek kayıt ekleyen aday ve doğrulamalı SQL üretir. Mevcut 2.359 kayıt bayt düzeyinde korunur.
- `scripts/Install-YesodeSoldier.ps1`: kapalı istemciyi şart koşar; dört mevcut sunucuyu durdurur; COPY_ONLY/CHECKSUM yedeği ve RESTORE VERIFYONLY kontrolü alır; işlemi mevcut LocalDB üzerinde uygular.
- Aynı betiğin `-Rollback` seçeneği yalnız askerin 32700 kimlikli kayıtlarını kaldırır, önceki TMon ve Map EXE'sini hash kontrollü geri getirir. Oyun kapalı olmalıdır.
- Yedekler, aday dosyalar, kurulum manifesti ve SQL yedeği Git dışında `runtime/soldier-caelen/` altında tutulur.
- `scripts/import_soldier_walk.py`: tamamlanmış yürüyüşü kırpar; kopuk kayıtları reddeder, gerçek yükseklikleri korur ve aday JSON üretir.
- `scripts/Update-YesodeSoldierRoute.ps1`: yalnız mevcut Caelen'in başlangıcını ve yol noktalarını değiştirir; Map EXE'sini yedekli yükler. Login/World süreçlerini durdurmaz. `-Rollback` son rota güncellemesini geri alır.
- `RouteSurvey.enabled` yalnız açıkça istenen kayıt sırasında Map EXE'sinin yanında bulunur. Bu dosya yokken koordinat kaydı yapılmaz. Tamamlanan CSV ve tanılama günlükleri Git'e alınmaz.

## Doğrulama

Kaynak Map derlemesi başarıyla bağlandı. Kurulum sonrası SQL kontrolü: 1 asker, 9 yol noktası, önceki 30 sakin korunmuş. TMon adayı tekrar ayrıştırıldı, önceki tüm kayıtlar birebir karşılaştırıldı. İlk Map açılışında Windows C++ exception (0xe06d7363) kaydetti; yeniden başlatmada dört yerel port açıldı. İlk açılış hatasının kök nedeni belirlenmiş değildir; tekrar ederse ayrıca incelenmelidir. Oyun içi görsel yürüyüş kabulü bu kontrollerden ayrı tutulur.

Tanılama, Caelen'in Marad yanında 289 HP ile doğduğunu, doğru hücreye eklendiğini ve yakındaki istemciye gönderildiğini doğruladı. Kullanıcı daha sonra hareketini gördü ve rota hatasını bildirdi. Yürüyüş dönüştürücüsünün vadi yüksekliğini koruma, eksik bitişi reddetme ve ışınlanma/kayıt boşluğunu bağlamama testleri geçti. 34 noktalı düzeltmenin oyun içi kabulü bekleniyor. Ayrı olarak bildirilen sunucu seçimi mesajı Login süreci yenilendikten sonra kullanıcı denemesinde tekrarlamadı; bu durumun kök nedeni kanıtlanmış sayılmıyor.

34 noktalı kayıtlı rota mevcut oyuna yedekli uygulandı. Yalnız Map süreci yeniden başlatıldı; Login/World süreçleri açık kaldı. SQL son nokta kontrolü ve sunucu günlüğü doğrulandı: 34 kayıtlı nokta + motorun başlangıç noktası = 35 bellek noktası. Önceki yanlış yükseklikte otomatik ara nokta eklenmiyor. Mevcut 30 sakin korunuyor; rota kaydı devre dışı. Caelen’in yeni rotayı oyun içinde tamamlayıp Remings yanında durmasının kullanıcı kabulü bekleniyor.

Kullanıcı Caelen’in Remings’e vardığını doğruladı; yürüyüşte duraksama bildirdi. Ortak koridor veri modeline geçiş ve mevcut yerel yol dosyalarının denetimi `docs/navigation/YESODE_ROAD_NETWORK.md` içinde kayıtlıdır. Bu geçiş sırasında çalışan oyun yeniden başlatılmadı.


## İkinci acemi — Edric

32701 kimlikli Edric, insan erkek Warrior olarak mevcut oyuna eklendi. Derion seviye 1 kılıç/kalkan ve Bronze Lightweight zırh takımı kullanır. İnsan erkek görünüşü kabul edilmiş Tovan şablonundan (32606, yüz 6506), davranış/stat şablonu Caelen'den alındı; boy ölçeği 0,75. Caelen'in yüzü ve ölçeği korunur.

`world/yesode/soldiers/edric.json` kendi yol noktalarını içermez: Yesode bölgesinde Marad → Remings hedeflerini seçer. Ortak koridorun ikinci noktasından başlar (`startWaypoint=1`); böylece Caelen ile üst üste doğmaz. Son 33 nokta ortak planlayıcıdan alınır, hedef aynı Remings durağıdır. Yeni yürüyüş kaydı alınmadı.

Hazırlama: `python scripts/prepare_soldier.py --config world/yesode/soldiers/edric.json`.
Yükleme/geri alma: oyun kapalıyken `scripts/Install-AdditionalSoldier.ps1 -Name edric` veya `-Name edric -Rollback`. İlk Caelen kurulumunun geri alma paketine dokunulmaz. Sonradan başka TMon değişikliği varsa hash kontrolü toplu geri almaya izin vermez; önce daha yeni eklemenin kendi paketi ele alınmalıdır.

Yükleme sırasında COPY_ONLY/CHECKSUM SQL yedeği ve VERIFYONLY kontrolü alındı; yalnız Map yeniden başlatıldı. Önceki bütün statik monster/spawn/mapmon/path satırları dışlanan yeni ID dışında sayım ve checksum ile karşılaştırıldı. Önceki 2.360 istemci kaydı, Caelen dahil, bayt düzeyinde aynı kaldı. Veritabanı 30 sakin ve 2 asker içeriyor; Caelen 34, Edric 33 SQL yol noktası kullanıyor. Sunucu Edric'in başlangıçta 289 HP ile doğru harita hücresine girdiğini kaydetti. Görünüş ve yürüyüşün kullanıcı kontrolü bekleniyor; önceki duraksama davranışına bu eklemede müdahale edilmedi.
