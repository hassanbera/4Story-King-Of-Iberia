# 4Story King Of Iberia

Bu depo, kaynak kodlu OldSchool 3.3 tabanından geliştirdiğimiz yerel 4Story projesinin yeni çalışma alanıdır. Kod ve değişiklik geçmişi burada tutulacak. VS Code ile bu klasörü doğrudan açabilirsiniz.

Klasörlerin görevleri ve mevcut sınırlar: [depo rehberi](docs/REPOSITORY_GUIDE.md).

## Başlangıç durumu

- `source/`: PhilipMorris OldSchool 3.3 C++ istemci, sunucu, protokol ve araç kaynaklarının 28 Ekim 2026 çalışma kopyası. Yesode sakinleri için geliştirdiğimiz rota kodu da bu kopyada.
- `world/yesode/`: 30 sakinin Kuznez rota ağı ve onu üreten veriler.
- `scripts/legacy-prototype/`: eski çalışma yoluna bağlı deney betikleri. Taşınabilir kurulum aracı olarak henüz doğrulanmadılar.
- Yerel 3.3 sunucunun Control, World, Login ve Map bileşenleri kaynaklardan derlenerek oynanabilir biçimde test edildi. 30 sakin Kuznez'de gözlendi; kullanıcı hareketleri ve performansı uygun buldu.
- 29 Ekim'de kaynak istemci EXE'si üretildi ve aynı oyun klasöründe yedekli aday olarak açıldı. Kullanıcı giriş ve karakter ekranına ulaştı; Beni hatırla yerleşimi ve geri dönüşteki çökme için düzeltmeler deneme aşamasında. Güncel durum [yerel istemci derlemesinde](docs/LOCAL_CLIENT_BUILD.md).
- Veritabanı yedekleri, istemci varlıkları, hesaplar ve çalıştırılabilir dosyalar Git deposuna alınmadı. Mevcut yerel oyun kurulumu bu depo oluşturulurken değiştirilmedi.

Geliştirme, mevcut PhilipMorris 3.3 oyunu ve veritabanındaki 30 Yesode sakini üzerinden sürer. Bu depo aynı çalışmanın kod geçmişidir. [Tek çalışma temeli](docs/WORKING_BASELINE.md), [proje durumu](docs/PROJECT_STATUS.md) ve [kaynak kökeni](docs/SOURCE_PROVENANCE.md) belgelerine bakın.

İlk bağımsız kaynak kontrolü: `scripts\Build-MapRouteSmoke.cmd`. Dört sunucunun kaynak derlemesi: `python scripts\build_server.py`. Derleme kanıtı ve kalan adımlar [derleme durumunda](docs/BUILD.md).

