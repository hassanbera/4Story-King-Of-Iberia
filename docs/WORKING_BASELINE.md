# Tek çalışma temeli

Kullanıcının 28 Ekim 2026 kararı: 4Story King Of Iberia, PhilipMorris OldSchool 3.3 kaynaklarından çalıştırılan mevcut oyunun devamıdır. Mevcut veritabanı, 30 Yesode sakini, kabul edilen görünüşler ve rota ağı bu projenin başlangıç durumudur.

Masaüstündeki Git deposu bu çalışmanın kod geçmişidir. Yeni bir oyun veya sıfırdan veritabanı kurma görevi değildir. Geliştirmeler mevcut oyuna uygulanacak; geçmiş alternatif sürümleri yeniden değerlendirmek gerekmez.

Mevcut çalışma konumu:

- Çalışan sunucular: önceki çalışma klasöründeki `work/philipmorris-oldschool/build-probe/`.
- Mevcut LocalDB örneği: `PM33Probe20261027`.
- Mevcut yerel portlar: Control 17442, World 14422, Login 15336, Map 11225.
- Takip edilen kaynaklar: bu deponun `source/` ve `world/yesode/` klasörleri.

Gereksiz paralel ortam hazırlığı durduruldu. `KOIDev20261028` kopyası kapalıdır; bu kopyada oyun oturumu başlatılmadı. Kopya ve yedek dosyaları mevcut oyun verisinin yerine kullanılmayacak. Kesilen derlemenin `build/server/` çıktıları karışık servis adları içerebileceğinden yeniden derlenmeden çalıştırılmamalıdır.
