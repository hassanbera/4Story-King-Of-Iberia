# Derleme durumu

## Doğrulanabilen dar adım

Windows ve Visual Studio C++ Build Tools olan makinede `scripts\Build-MapRouteSmoke.cmd`, Yesode rota mantığının üç C++ dosyasını bu deponun `source/` ağacından derler. Çıktı `build/route-smoke/` altında kalır ve Git tarafından izlenmez.

28 Ekim 2026 denemesi: VS 2019 Build Tools `14.16.27023` ile `AmbientRoutes.cpp`, `TAICmdRoam.cpp` ve `TMonster.cpp` başarıyla derlendi. Derleyici yalnız eski `/Zc:forScope-` seçeneğinin ileride kaldırılacağı uyarısını verdi.

`python world\yesode\Compile-AmbientRoutes.py` rota ağının veri denetimini yapar ve `AmbientRoutes.csv` üretir. Rota CSV dosyasının sunucuda kullanımı ayrıca tam Map sunucusu derlemesi ve oyun oturumuyla doğrulanmalıdır.

28 Ekim 2026 denemesi: 1 harita, 26 düğüm ve 30 kenar doğrulandı; üretilen CSV'nin SHA-256 değeri kayıtlı dosyayla aynı kaldı.

## Tam sunucu derlemesi

`python scripts\build_server.py` yeni depodaki C++ kaynaklarından 32 bit `TNetLib.localdb.lib` ile Control, World, Login ve Map EXE'lerini `build/server/` altında üretir. Derleme, Windows üzerindeki Visual Studio 2019 Build Tools `14.16.27023` ve Windows 10 SDK `10.0.19041.0` ile doğrulandı. Yerel test için kaynak kopyalarına yapılan loopback, LocalDB ve Map sözdizimi uyarlamaları yalnız `build/server/` alanında hazırlanır; `source/` değişmez.

28 Ekim 2026'da dört EXE de temiz `build/server/` alanından derlenip bağlandı ve PE başlıklarında `0x14c` (x86) doğrulandı. Bu sonuç **derleme kanıtıdır**. Bu yeni EXE'ler henüz oyun oturumunda çalıştırılmadı; önceki çalışan 3.3 derlemesiyle runtime eşdeğerliği ayrıca sınanacak.

## Kalan işler

`scripts/legacy-prototype/` betikleri mevcut çalışan ortamın mutlak yollarını içerir. Kaynak derlemesi için `scripts/build_server.py` kullanılabilir. Geliştirme mevcut PhilipMorris oyunu, veritabanı ve 30 sakin üzerinden sürecek; yeni paralel ortam planlanmıyor. Çalışma kararı `docs/WORKING_BASELINE.md` içinde kayıtlıdır.

