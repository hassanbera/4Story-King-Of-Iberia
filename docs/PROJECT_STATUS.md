# Proje durumu — 29 Ekim 2026

## Kanıtlananlar

- OldSchool 3.3 sunucu kaynaklarından dört hizmetin yerel Windows derlemesi çalıştırıldı.
- Ayrı LocalDB ortamında kullanıcı giriş yaptı ve Kuznez haritasına girdi.
- Kaynakta geliştirilen Yesode rota ağıyla 30 sakin oyun içinde gözlendi; kullanıcı görünüş, hareket ve performansı kabul etti.
- Yeni depodan Yesode rota mantığının üç C++ dosyası derlendi; rota verisi aynı CSV'yi yeniden üretti. Ayrıntı: `docs/BUILD.md`.
- Yeni depodan ağ kütüphanesi ve dört 32 bit sunucu EXE'si temiz `build/server/` klasöründe derlenip bağlandı. Yeni çıktılarla oyun oturumu henüz sınanmadı.

## Açık işler

Kaynak istemci EXE'si üretildi ve aynı oyunda yedekli aday olarak açıldı. Kullanıcı giriş ve karakter ekranını gördü. Beni hatırla yerleşimi ve boş mesaj yığınını kapatırken oluşan çökme düzeltildi; son sürümün giriş, hatırlama ve geri dönüş kontrolleri kullanıcı tarafından onaylandı. Ayrıntı `docs/LOCAL_CLIENT_BUILD.md` içinde.

1. Geliştirmeye, kullanıcının onayladığı mevcut PhilipMorris 3.3 oyunu ve mevcut veritabanı üzerinden devam etmek. Yesode'deki 30 sakin ve kabul edilmiş rota ağı korunacak. Yeni paralel oyun/veritabanı açmak çalışma planının parçası değildir.
2. Bundan sonraki veritabanı ve içerik değişikliklerini mevcut ortama uygulanabilir, yedekli değişiklikler olarak kaydetmek. Oyuncu verisi içeren yedekleri Git'e eklememek.
3. Kaynak istemcinin harita ve diğer oyun özelliklerini geliştirmeler sırasında doğrulamak. Giriş, hatırlama ve karakter ekranından geri dönüş kabul edildi.
4. Kaynak istemcinin özgün imleçlerini tamamlamak; geçici imleç kaynaklarını nihai saymamak.
5. Bundan sonraki yaşayan dünya değişikliklerini bu depoda küçük commit'lerle izlemek.

Bu depo oluşturulurken çalışan oyun kurulumu veya veritabanı değiştirilmedi.

