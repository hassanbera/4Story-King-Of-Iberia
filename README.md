# 4Story King Of Iberia

Bu depo, kaynak kodlu OldSchool 3.3 tabanından geliştirdiğimiz yerel 4Story projesinin yeni çalışma alanıdır. Kod ve değişiklik geçmişi burada tutulacak. VS Code ile bu klasörü doğrudan açabilirsiniz.

## Başlangıç durumu

- `source/`: PhilipMorris OldSchool 3.3 C++ istemci, sunucu, protokol ve araç kaynaklarının 28 Ekim 2026 çalışma kopyası. Yesode sakinleri için geliştirdiğimiz rota kodu da bu kopyada.
- `world/yesode/`: 30 sakinin Kuznez rota ağı ve onu üreten veriler.
- `scripts/legacy-prototype/`: eski çalışma yoluna bağlı deney betikleri. Taşınabilir kurulum aracı olarak henüz doğrulanmadılar.
- Yerel 3.3 sunucunun Control, World, Login ve Map bileşenleri kaynaklardan derlenerek oynanabilir biçimde test edildi. 30 sakin Kuznez'de gözlendi; kullanıcı hareketleri ve performansı uygun buldu.
- İstemci kaynakları mevcut, fakat bu kaynaklardan yeni bir istemci derlemesi henüz tamamlanmadı. Şu an oyuna girilen Classic4Story istemcisi ayrı bir ikilidir. Kaynak istemciyle birebir eşleşme doğrulanmadı.
- Veritabanı yedekleri, istemci varlıkları, hesaplar ve çalıştırılabilir dosyalar Git deposuna alınmadı. Mevcut yerel oyun kurulumu bu depo oluşturulurken değiştirilmedi.

Öncelik, bu depodan tekrarlanabilir sunucu ve istemci derlemesi ile yerel kurulum üretmek; ardından yaşayan dünya davranışlarını burada geliştirmektir. Kaynak geçmişi ve sınırlar için [proje durumu](docs/PROJECT_STATUS.md) ile [kaynak kökeni](docs/SOURCE_PROVENANCE.md) belgelerine bakın.

İlk bağımsız kaynak kontrolü: `scripts\Build-MapRouteSmoke.cmd`. Derleme kanıtı ve kalan adımlar [derleme durumunda](docs/BUILD.md).

