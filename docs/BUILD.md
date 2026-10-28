# Derleme durumu

## Doğrulanabilen dar adım

Windows ve Visual Studio C++ Build Tools olan makinede `scripts\Build-MapRouteSmoke.cmd`, Yesode rota mantığının üç C++ dosyasını bu deponun `source/` ağacından derler. Çıktı `build/route-smoke/` altında kalır ve Git tarafından izlenmez.

28 Ekim 2026 denemesi: VS 2019 Build Tools `14.16.27023` ile `AmbientRoutes.cpp`, `TAICmdRoam.cpp` ve `TMonster.cpp` başarıyla derlendi. Derleyici yalnız eski `/Zc:forScope-` seçeneğinin ileride kaldırılacağı uyarısını verdi.

`python world\yesode\Compile-AmbientRoutes.py` rota ağının veri denetimini yapar ve `AmbientRoutes.csv` üretir. Rota CSV dosyasının sunucuda kullanımı ayrıca tam Map sunucusu derlemesi ve oyun oturumuyla doğrulanmalıdır.

28 Ekim 2026 denemesi: 1 harita, 26 düğüm ve 30 kenar doğrulandı; üretilen CSV'nin SHA-256 değeri kayıtlı dosyayla aynı kaldı.

## Henüz taşınmayan tam derleme

Önceki 3.3 derlemesinde üretilen nesne dosyaları ve yerel çalışma ayarları eski klasörde duruyor. `scripts/legacy-prototype/` betikleri eski mutlak yollara ve bu çıktılara bağlı. Bunlar yeni depoda tekrarlanabilir tam sunucu derlemesi sayılmaz. Sonraki iş temiz ağaçtan dört hizmeti üretmek ve kaynak istemciyi derlemektir.

