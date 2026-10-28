# Proje durumu — 28 Ekim 2026

## Kanıtlananlar

- OldSchool 3.3 sunucu kaynaklarından dört hizmetin yerel Windows derlemesi çalıştırıldı.
- Ayrı LocalDB ortamında kullanıcı giriş yaptı ve Kuznez haritasına girdi.
- Kaynakta geliştirilen Yesode rota ağıyla 30 sakin oyun içinde gözlendi; kullanıcı görünüş, hareket ve performansı kabul etti.

## Açık işler

1. Derleme betiklerini bu deponun göreli yollarına ve temiz çıktı klasörlerine taşımak. Eski betikler `scripts/legacy-prototype/` altında yalnız kayıt amaçlı duruyor.
2. Yerel veritabanını ve içerik değişikliklerini şemasal, tekrarlanabilir bir kurulum/migrasyon haline getirmek. Oyuncu verisi içeren yedekleri Git'e eklememek.
3. Eski Visual Studio proje biçimini güncel Windows araç zinciriyle derlemek ve **kaynak istemciyi** yerel sunucuya bağlayarak doğrulamak. Bugün kullanılan Classic4Story ikilisi bunun yerine geçmez.
4. Yeni adı, derlenen istemcinin başlığına/arayüzüne ve yeni başlatıcıya uygulayıp oyun içinde sınamak.
5. Bundan sonraki yaşayan dünya değişikliklerini bu depoda küçük commit'lerle izlemek.

Bu depo oluşturulurken çalışan oyun kurulumu veya veritabanı değiştirilmedi.

