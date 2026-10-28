# Proje durumu — 28 Ekim 2026

## Kanıtlananlar

- OldSchool 3.3 sunucu kaynaklarından dört hizmetin yerel Windows derlemesi çalıştırıldı.
- Ayrı LocalDB ortamında kullanıcı giriş yaptı ve Kuznez haritasına girdi.
- Kaynakta geliştirilen Yesode rota ağıyla 30 sakin oyun içinde gözlendi; kullanıcı görünüş, hareket ve performansı kabul etti.
- Yeni depodan Yesode rota mantığının üç C++ dosyası derlendi; rota verisi aynı CSV'yi yeniden üretti. Ayrıntı: `docs/BUILD.md`.
- Yeni depodan ağ kütüphanesi ve dört 32 bit sunucu EXE'si temiz `build/server/` klasöründe derlenip bağlandı. Yeni çıktılarla oyun oturumu henüz sınanmadı.

## Açık işler

Girişte Beni hatırla değişikliğinin kaynak kodu ve kayıt testleri hazır. EngineLib, TCML, TUIs ve zlib yeniden üretildi. Tam istemci EXE'si için kalan dış SDK bağımlılıkları ve derleme uyarlamaları var; ayrıntı `docs/LOGIN_REMEMBER_ME.md` ve `docs/CLIENT_LIBRARIES_BUILD.md` içinde.

1. Geliştirmeye, kullanıcının onayladığı mevcut PhilipMorris 3.3 oyunu ve mevcut veritabanı üzerinden devam etmek. Yesode'deki 30 sakin ve kabul edilmiş rota ağı korunacak. Yeni paralel oyun/veritabanı açmak çalışma planının parçası değildir.
2. Bundan sonraki veritabanı ve içerik değişikliklerini mevcut ortama uygulanabilir, yedekli değişiklikler olarak kaydetmek. Oyuncu verisi içeren yedekleri Git'e eklememek.
3. Eski Visual Studio proje biçimini güncel Windows araç zinciriyle derlemek ve **kaynak istemciyi** yerel sunucuya bağlayarak doğrulamak. Bugün kullanılan Classic4Story ikilisi bunun yerine geçmez.
4. Yeni adı, derlenen istemcinin başlığına/arayüzüne ve yeni başlatıcıya uygulayıp oyun içinde sınamak.
5. Bundan sonraki yaşayan dünya değişikliklerini bu depoda küçük commit'lerle izlemek.

Bu depo oluşturulurken çalışan oyun kurulumu veya veritabanı değiştirilmedi.

