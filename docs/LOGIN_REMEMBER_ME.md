# Beni hatırla — uygulama durumu

Durum: kaynak EXE üretildi ve aynı oyun klasöründe aday olarak açıldı. Kullanıcı giriş ekranını gördü; ilk adayda kutucuk görünmedi. Yerleşim düzeltmesi üretildi, görsel ve gerçek hesapla yeniden açma testi bekliyor.

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

İlk tam istemci denemesinde boş SDK ve motor kütüphaneleri tespit edildi. Motor ve arayüz kütüphaneleri yeniden derlendi; eksik ticari SDK'ları kullanmayan ve yalnız yerel sunucuya bağlanan profil ile tam EXE üretildi. Güncel derleme ve kurulum adımları `docs/LOCAL_CLIENT_BUILD.md` içindedir.

Özgün istemcinin yedeği saklanıyor. Oyun içinde görünüm ve yeniden başlatma testi geçmeden özellik tamamlanmış olarak işaretlenmeyecek.
