# Depo düzeni ve kontrol sonucu

28 Ekim 2026: Git çalışma ağacı ve GitHub `main` geçmişi kontrol edildi. Takip edilen dosyalarda EXE, DLL, SQL yedeği, veritabanı veri dosyası veya derleme nesnesi bulunmadı. Kaynak paketindeki üçüncü taraf statik kütüphaneler (`.lib`) depoda tutuluyor.

| Konum | Kullanım |
| --- | --- |
| `source/` | PhilipMorris 3.3 kaynakları; istemci, sunucu, protokol ve araçlar |
| `world/yesode/` | Kabul edilen Yesode rota verileri ve CSV üreticisi |
| `scripts/build_server.py` | Güncel kaynak sunucu derlemesi |
| `scripts/Build-MapRouteSmoke.cmd` | Üç rota kaynak dosyasının dar derleme kontrolü |
| `scripts/legacy-prototype/` | Önceki deney betiklerinin arşivi; doğrudan çalıştırma giriş noktası değil |
| `docs/WORKING_BASELINE.md` | Tek çalışma temeli, mevcut oyun konumu ve portları |
| `docs/BUILD.md` | Derleme kanıtı ve sınırları |
| `build/`, `runtime/` | Yerel, Git dışında tutulan çıktılar ve veriler |

## Henüz depoda tam temsil edilmeyenler

- Çalışan sunucular ve mevcut veritabanı önceki yerel çalışma konumunda çalışıyor. Bu deponun oluşturulması çalışan oyunu başka yere taşımadı.
- 30 sakinin kabul edilmiş durumu mevcut veritabanı ve istemci verisinde bulunuyor. Depodaki rota dosyaları bunun tamamını tek başına yeniden kurmaya yetmez; görünüş ve SQL içerik değişikliklerinin eksiksiz kurulum/migrasyon kaydı henüz hazırlanmadı.
- Kaynak istemci derlemesi tamamlanmadı; istemci varlıkları Git'e alınmadı.
- `source/TClient/` altındaki `TClient` ve `TClientA` ağaçları kaynak paketinden birlikte geldi. Derleme hedefi belirlenmeden biri silinmedi.

Bu sınırlar mevcut oyun üzerinde geliştirmeyi engellemez; deponun tek başına taşınabilir bir oyun dağıtımı olduğu anlamına gelmediğini gösterir. Bundan sonraki kod ve içerik değişiklikleri bu depoda küçük, açıklanmış commit'lerle kaydedilecek.
