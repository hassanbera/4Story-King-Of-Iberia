# Kaynak istemci — 29 Ekim 2026

`build/client-local/TClient.exe` kaynaklardan bağlandı. Bu aday mevcut PhilipMorris oyununun verileri ve aynı sunucuyla deneniyor. Yeni veritabanı veya paralel sunucu oluşturulmadı.

## Tekrarlanabilir derleme

VS 2019 Build Tools v141, x86 MFC, Windows 10 SDK ve eski DirectX 9 SDK gerekir. `--dx-sdk` ile verilen SDK kökü hem `Include` hem `Lib` klasörünü içermeli. Zlib kaynağını hazırlama adımı `CLIENT_LIBRARIES_BUILD.md` içindedir.

```powershell
python scripts/build_client_libraries.py --local-client --zlib-source build/vendor/zlib --dx-include "DIRECTX_SDK/Include"
python scripts/build_client.py --dx-sdk "DIRECTX_SDK" --allow-cursor-fallback
```

Yerel kütüphaneler `build/client-libraries-local/lib/` içine yazılır. TCML, motor, TUIs, TComp, TChatFilter, TChart ve zlib aynı araç zinciriyle üretilir. `--link-only` mevcut nesneleri yeniden bağlar; kaynak veya başlık değişince tam derleme gerekir.

## Yerel profil

`KOI_LOCAL_CLIENT`, eksik ticari SDK entegrasyonlarını derleme dışında tutar. SDK başarısını taklit eden yeni fonksiyonlar eklenmedi. Bu profil TEST_MODE genel oyun/debug davranışlarını açmaz. Motorun oyun oturumları yalnız `127.0.0.0/8` adreslerine bağlanabilir ve mevcut sunucu bağlantısı için `127.0.0.4` kaynak adresini kullanır. Kaynak istemci için eski Frida bağlantı başlatıcısına ihtiyaç yoktur.

Eski C++/MFC uyumsuzlukları giderildi: açık sayısal türler, boş CString değerleri, const karşılaştırıcı parametreleri, set anahtarlarını silip yeniden ekleyen metin aralığı güncellemeleri ve doğru callback imzaları. Metin aralığı değişiklikleri için oyun içi sohbet/bağlantı biçimlendirmesi henüz sınanmadı.

Paketin dört imleç dosyası geçersiz olduğu için `--allow-cursor-fallback` yalnız üretilen RC kopyasında geçerli Sword.cur dosyasını kullanır. Normal imleç yerel profilde Windows ok imlecine ayarlanır. Özgün imleçlerin tamamı henüz yeniden sağlanmadı. Yerel istemci başlangıçta pencere moduna geçer.

## Aynı oyuna kurma ve geri dönüş

`Install-LocalClient.ps1`, açık TClient varsa durur; mevcut EXE'nin doğrulanmış yedeğini `runtime/client-backups/` içine alıp yalnız istemci EXE'sini değiştirir. Tekrarlanan aday yüklemelerinde özgün yedek korunur. Sunucu ve veritabanına değişiklik yapmaz.

`Start-LocalGame.ps1`, `runtime/local-game.json` içindeki mevcut sunucu başlatıcısını ve oyun klasörünü kullanır. Masaüstündeki `4Story King Of Iberia.cmd` bu betiği açar. `Restore-LocalClient.ps1`, oyun kapalıyken doğrulanmış özgün istemciyi ve önceki başlatma yolunu geri yükler.

## Gözlemler

- Kaynak EXE x86 olarak bağlandı; dış SDK DLL'leri import listesinde yok.
- Yeni başlıkla açılan işlem yanıt verdi. Kullanıcı giriş alanlarının göründüğünü doğruladı.
- İlk adayda Beni hatırla kutucuğu görünmedi. Giriş çerçevesinin altına göre konumlandırmak yerine parola/Login alanlarına göre konumlandırma düzeltildi; kontrol açıkça görünür ve etkin yapıldı. Bu düzeltmenin oyun içi kontrolü bekliyor.
- Kaydetme, yeniden yükleme, sunucu ayrımı, bozuk kayıt ve silme DPAPI testleri geçti. Gerçek hesapla yeniden başlatma testi bekliyor.
- Kullanıcı sonraki adayda karakter ekranına ulaştı, fakat geri dönünce uygulama çöktü. Windows hata kaydı `0xc0000005`, EXE ofseti `0x001feb82` bildirdi. Aynı kod bölümüyle üretilen MAP dosyası bu adresi `deque<TMESSAGEBOX>::pop_back` içine eşledi. `CloseMessageBox(FALSE)` boş yığını kontrol etmeden `pop()` çağırıyordu; bu çağrıya boşluk kontrolü eklendi. Geri dönüş regresyon testi kullanıcıdan bekleniyor.
- Kutucuk görseli artık büyütülmüyor; yazı kendi tıklanabilir kontrolünde yanına yerleştiriliyor. Kullanıcının ilk hatırlama denemesinden sonra mevcut sunucu için şifreli kayıt oluştuğu gözlendi; içeriği loglanmadı.
- Kullanıcı adı yeniden doldu, fakat parola geri dönüşte temizlendi. Kaydedilen bilgilerin beklenen yerel test hesabıyla eşleştiği içerik yazdırılmadan doğrulandı. Login'e dönüşteki parola temizleme işleminden sonra kaydı yeniden yükleme ve editörün ClearText/InsertString yöntemleriyle caret durumunu güncelleme düzeltmesi hazırlandı. Bu son düzeltmenin kullanıcı testi bekliyor.
