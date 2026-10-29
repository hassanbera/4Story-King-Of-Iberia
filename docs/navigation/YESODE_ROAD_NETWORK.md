# Yesode ortak yol ağı — ilk uygulama

29 Ekim 2026. Tek oyun ve mevcut veritabanı korunarak, çalışan sunucuya müdahale etmeden hazırlandı.

## Sonuç

Ortak bölge planlayıcısı artık `marad` ve `remings` adlı ulaşım noktaları arasında yol üretebiliyor. Yaklaşık 224,88 oyun birimlik yol, kullanıcının kaydettiği ve Caelen'in hedefe ulaşarak doğruladığı 34 zemin noktasını kullanır. Yürüyüşteki duraksama bu değişiklikle giderilmiş değildir.

Yolun sahibi artık bir asker değildir: `world/navigation/corridors/kuznez-remings.json` ortak koridordur. Caelen yalnız `navigation.region/from/to` alanlarıyla bölge ve hedeflerini seçer. Önceki `waypoints` alanı eski araçlarla uyumluluk için aynı verinin kopyası olarak tutulur; yeni hazırlama/güncelleme araçları ortak planlayıcı sonucunu kullanır.

## Mevcut yol dosyalarında bulunanlar

- Mevcut istemcinin map-0 kapsamındaki 20 TPF dosyası okundu. Toplam 309.981 nokta ve 3.189.170 yönlü referans var. Bu 20 dosya yalnız Yesode sınırı değildir.
- Her dosya alan alan tekrar serileştirildi ve özgün baytlarıyla birebir karşılaştırıldı. Dosyalara yazılmadı.
- Pilot dosya `TFLAG00000405.tpf`: 19.355 nokta, 276.373 kullanılabilir yönlü bağlantı, dosyada karşılığı bulunamayan 242 referans ve 472 ayrı zayıf bağlı bileşen. Karşılığı bulunmayan bağlantılar kullanılmıyor; bu pilot dosyadaki eksik referansların hepsi aynı birimin kimliklerini işaret ediyor.
- Marad ve Remings çevresinde yakın yol noktaları bulundu, ancak mevcut pilot bağlantıları aralarında yol vermedi. Büyük nokta sayısı, bütün haritanın dolaşılabildiğinin kanıtı değildir.
- Yol noktalarının Y değeri ile zemin aynı değildir. Kaynak üretici `TPATH_HEIGHT=0.3` ekler. Ulaşım noktası adayları karşılaştırılırken bu fark dikkate alındı; dosya değerleri değiştirilmedi.
- Pilot dikdörtgendeki 60 Derion NPC'sinin konumu salt okunur SQL sorgusuyla alındı. 51 konumda yakın bir yerel yol noktası adayı, 9 konumda eşik içinde aday yok. Yakın aday bulunması, NPC'ye çarpışmasız ulaşımın doğrulandığı anlamına gelmez. Bunlar oyuna etkin durak olarak yüklenmedi.

Kaynak izleri: `TClientMAP.cpp::LoadTFLAG`, `CTClientMAP::FindPath/GetTargetPoint`, `TExplorer/TCMDHandler.cpp::OnTCMD_FINDPATH`, `TExplorerType.h` ve `TClientType.h`. Kaynak üreticide eğim ve `CanMove` kontrolü vardır. Dosya biçiminin eşleşmesi, kurulu dosyaların güncel dünyadaki bütün engellere karşı yeniden sınandığını kanıtlamaz. Ayrıntılı dosya hash'leri ve sayımlar `NATIVE_PATH_AUDIT.json` içindedir.

## Ağın mevcut sınırı

Ortak modelde 26 noktalı kabul edilmiş Kuznez ağı ve 34 noktalı kayıtlı koridor var. Bunlar aynı bölge modelindeki iki ayrı bileşendir; birbirine tamamen bağlı oldukları iddia edilmiyor. Aralarında 1,35–3,71 birim uzunlukta dört birleşim adayı bulundu. Bu adaylar grafiğin etkin kenarları değildir. Yakınlık, duvar veya merdiven üzerinden geçiş için yeterli kanıt sayılmadı.

Kaydedilen koridor yalnız Marad → Remings yönünde doğrulandı. Ters yön istenirse planlayıcı doğrulanmış yol bulunamadığını bildirir; geri dönüşü kendiliğinden etkinleştirmez. Yeni bölgeler, ana ağlar ve koridorlar bölge JSON dosyalarına eklenebilir. Aktör sayısı, sınıfı ve kimlikleri ortak A* kodunun parçası değildir.

Ortak planlayıcıda 200/BYTE düğüm sınırı yoktur. Mevcut sunucunun asker rota yürütücüsünde hâlâ sınırlı yol noktası dizisi vardır; bütün TPF dosyaları eski `AmbientRoutes` belleğine veya onun tüm-çiftler tablosuna doldurulmadı. Büyük dünya ağı için sunucu tarafında bölgesel planlama ve rota parçalama ayrıca entegre edilmelidir.

## Çalıştırma

Proje kökünde:

```powershell
python scripts/audit_navigation.py
python scripts/plan_navigation.py --region yesode --from marad --to remings --output runtime/navigation/marad-remings.json
python scripts/render_navigation.py
python -m unittest discover -s tests -p test_navigation.py -v
```

Denetim, `runtime/local-game.json` içindeki mevcut istemciden okur. NPC adaylarının rapora katılması için `runtime/navigation-npcs.json` adlı salt okunur koordinat çıktısı kullanılır; hesap/parola bilgisi içermez. Temel denetim ve planlayıcı Python standart kütüphanesiyle çalışır; isteğe bağlı PNG çizimi Matplotlib kullanır. SVG çizimi standart kütüphaneyle denetim sırasında üretilir.

Çıktılar: `runtime/navigation/audit.json`, `accepted-network.json`, `npc-access-candidates.json`, `marad-remings.json`, `overview.svg` ve isteğe bağlı `overview.png`. Yerel asset dosyaları ve büyük analiz çıktıları Git'e alınmaz.

## Doğrulama ve sonraki teknik iş

Yedi test: TPF alanlarının birebir dönüşümü, bozuk/truncated kayıtların reddi, geçersiz referansların kullanılmaması, yalnız mevcut kenarlardan yol bulma, yön kısıtı, köprü/zemin yüksekliğinin ayrılması, BYTE sınırından büyük grafik ve gerçek bölge koridorunun aynen üretilmesi kontrollerini kapsar. Önceki üç yürüyüş kaydı testi de geçti. Testler oyun içi yeni yolların kabulü yerine geçmez.

Bu aşamada SQL verisi, çalışan EXE, 30 sakinin rotaları ve açık oyun değiştirilmedi. Rota kaydı kapalı kaldı. Yeni hazırlama araçlarının ortak planlayıcıyı kullanması hazırlandı; çalışan oyunda yeni bir yol seçme sürümü devreye alınmadı.

Sonraki iş, dört kısa birleşimi motorun gerçek yükseklik/çarpışma sorgularıyla doğrulayacak bir adaptör hazırlamak ve bunu Marad çevresinde sınamak. Ardından ortak ağ genişletilebilir. Tam haritayı kullanıcıya gezdirmek yerine, otomatik verinin kapsamadığı belirli bağlantılar için kısa kontrol istenir.
