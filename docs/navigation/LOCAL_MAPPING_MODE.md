# Yerel haritalama modu

29 Ekim 2026. Kullanıcının kendi karakteriyle daha hızlı Yesode yollarını gezmesi için, yalnız `KOI_LOCAL_CLIENT` kaynak derlemesinde çalışan isteğe bağlı araç.

## Kullanım

Masaüstündeki `4Story King Of Iberia - Haritalama.cmd` veya proje kökünde:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Start-LocalGame.ps1 -Mode survey
```

Mevcut hesapla normal giriş yapılır. Başlangıçta 3x hız ve kayıt açıktır; haritaya girince pencere başlığı durumlarını gösterir. `Ctrl+Shift+F8` normal/3x hızı, `Ctrl+Shift+F9` kaydı açıp kapatır. Bu kısayollar beceri çubuğunu ayrıca tetiklemez. Normal başlatıcı survey ortam değişkenlerini temizler; normal hızda ve kayıt kapalı açılır. Profil değiştirmek için istemci yeniden açılır, mod içindeki hız/kayıt geçişleri için kapanma gerekmez.

İlk kullanımda kısa bir düz yol ve dönüş denenmeli; bütün Yesode kaydına hız ve kayıt kullanıcı tarafından doğrulandıktan sonra başlanmalı. Zıplamak, binek kullanmak veya düşmek yasaklanmaz; bu örnekler güvenli yol adayı sayılmaz ve kaydı parçalara ayırır. Duvardan geçme, uçma veya hasarsızlık eklenmedi. Yüksek hız tek başına güvenli geçiş kanıtı değildir.

## Kaynak davranışı

`LocalSurveyMode.h`, ana karakterin mevcut hız faktörünü yalnız hareket hesaplama çağrısı boyunca geçici olarak çarpar ve kapsam sonunda aynen geri koyar. Gerçek temel hız `TDEF_SPEED=0.9`; üst sınır bunun üç katıdır. Diğer oyuncuların, askerlerin ve sakinlerin hızı değiştirilmez. Sunucu veritabanına kalıcı hız/ekipman değişikliği yazılmaz. Kaynak istemcinin mevcut loopback bağlantı sınırlaması geçerlidir.

Normal zemin, eğim ve çarpışma kontrolleri çalışmaya devam eder. Mod aktifken normal karelerde sahne hesaplama aralığı en fazla 25 ms'dir; normal profilde önceki aralık korunur. 150 ms'den uzun karede hız artışı uygulanmaz ve örnek güvenilir zemin örneği sayılmaz. Zıplama, düşme, yüzme, hayalet/ölü olma veya başka nesneyi/bineği kontrol etme sırasında hız artışı uygulanmaz.

Kaydedilen alanlar: zaman, harita, gerçek XYZ, motorun hesapladığı zemin yüksekliği, hareket durumu, zıplama/düşme/yüzme/ölüm/engel bayrakları, yaya kontrolü, pencere odağı, kare süresi ve mod geçiş sayacı. Kullanıcı adı, parola, sohbet veya ağ paket içeriği kaydedilmez. Zemin örneği bayrağı yalnız ana haritada (map 0), yaya, odaklı, zemine yakın ve engellenmeyen hareket için verilir. Map 0 birden fazla bölgeyi kapsayabilir; bu bayrak Yesode sınır tespiti yerine geçmez.

Kayıt `runtime/surveys/<oturum>/session.json` ve `walk.csv` altındadır. CSV yaklaşık 60 ms aralıkla örneklenir. Normal oyun oturumunda bu dosyalar oluşturulmaz. Önceki sunucu tarafı `RouteSurvey.enabled` mekanizması bu modun parçası değildir ve kapalı bırakılır.

## Analiz

Kayıt duraklatıldıktan veya istemci kapandıktan sonra:

```powershell
python scripts/import_mapping_survey.py runtime/surveys/<oturum>
```

Araç `corridor-candidates.json` üretir. Hava/engel/odak/kare hataları, mod geçişleri, harita değişimi, uzun zaman veya konum sıçramaları ayrı segmentler oluşturur. Boşlukların arasına varsayımsal çizgi eklenmez. Çıktı yalnız ileri yönlü aday koridorlardır; NPC'ler için doğrulanmış sayılmaz ve çalışan oyuna otomatik yüklenmez. Büyük yolları mevcut sunucunun kısa yol noktası dizilerine bölmek ve yeni kavşakları doğrulamak ayrı adımdır.

## Derleme ve doğrulama

Mevcut SDK ile `scripts/build_client.py --dx-sdk <sdk> --allow-cursor-fallback --unit TClientGame` derlemesi hazırlandı. `--unit` yalnız değişen derleme birimini mevcut uyumlu PCH ile derler; sınıf düzeni veya ortak başlıklar değişirse tam derleme yapılmalıdır. Yeni mod sınıf düzenini değiştirmez.

C++ hız kontrolü normal profilin kapalı oluşunu, 3x sınırını, geçici faktörün geri konmasını, yaya dışı ve uzun kare durumunda hız artışı yapılmamasını sınadı. Dört Python testi, düşme ve kesintileri bağlamamayı, mod geçişlerini ayırmayı ve bozuk/uygunsuz veriyi eleme davranışını sınadı. Bu kontroller, oyunda hissedilen hızın ve gerçek koordinat kaydının kullanıcı kabulü yerine geçmez.

İstemci yüklemesi `Install-LocalClient.ps1` ile eski EXE'nin doğrulanmış yedeği alınarak yapılır; mevcut DB, TCD dosyaları, 30 sakin ve iki acemi korunur. Haritalama testi başarısızsa normal başlatıcı aynı EXE'nin normal profilini açar; gerektiğinde yükleme manifestindeki `ReplacedClientBackup` önceki kabul edilmiş kaynak EXE'sini içerir. `Backup` alanı daha eski özgün başlangıç yedeği olabilir; ikisi karıştırılmamalıdır.

Durum: derleme ve otomatik kontroller geçti. Oyun içi 3x yürüyüş, kısayollar ve gerçek kayıt kontrolü henüz bekleniyor.
