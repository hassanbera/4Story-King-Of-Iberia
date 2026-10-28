# Beni hatırla — uygulama durumu

Durum: kaynak kodu hazır ve değişen dosyalar derlendi; çalışan oyun istemcisine henüz yüklenmedi.

## Hazırlanan davranış

- Giriş çerçevesine `Beni hatirla` kutucuğu ekleniyor.
- Kullanıcı kutucuğu seçip Login'e basınca kullanıcı adı ve parola kaydediliyor.
- Sonraki açılışta aynı sunucu için alanlar ve kutucuk dolduruluyor. Login'e kullanıcı basıyor; otomatik giriş yapılmıyor.
- Kutucuğun işareti kaldırılınca kaydedilmiş bilgiler siliniyor.
- Bilgiler `HKCU\Software\4Story King Of Iberia\RememberLogin` altında sunucu adresi/portuna göre ayrılmış DPAPI şifreli veri olarak tutuluyor. Parola kaynak koduna, dosyaya veya Git'e düz metin yazılmıyor.

## Doğrulama

`scripts/Test-RememberLogin.cmd` sahte test bilgileriyle kaydetme, yeniden okuma, farklı sunucu ayrımı, şifreli içerik, bozuk kayıt ve silme testlerini geçti. Test kendi kayıt değerini siliyor.

`scripts/Compile-LoginChange.cmd "legacy-DirectX9-Include-klasörü"` ile `TClientWnd.cpp` ve `TNetGM.cpp` derlendi. Bu komut, eski DirectX SDK başlıklarına ve kurulu VS C++ araçlarına ihtiyaç duyar. Aynı dosyadaki mevcut MessageBox çağrısında belirsiz sıfır parametreleri açık boş CString değerleriyle düzeltildi.

## Oyuna yüklemeyi engelleyen durum

İlk tam istemci denemesinde boş `EngineLib.lib`, `TUIs.lib` ve `TCML.lib` dosyaları tespit edildi. 29 Ekim'de bu üç kütüphane kaynaklarından yeniden üretildi; zlib bağımlılığı da derlenip sınandı. Güncel durum `docs/CLIENT_LIBRARIES_BUILD.md` içindedir. Tam EXE üretimi hâlâ dış SDK kütüphaneleri ve önceki istemci kaynak/arayüz uyarlamaları nedeniyle tamamlanmadı.

Çalışan istemci EXE'si değiştirilmedi. Kullanıcı mevcut oyunda kutucuğu henüz göremez. Oyun içinde görünüm ve yeniden başlatma testi bekliyor; özellik tamamlanmış olarak işaretlenmedi.
