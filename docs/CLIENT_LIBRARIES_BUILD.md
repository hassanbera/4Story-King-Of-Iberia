# İstemci kütüphaneleri — 29 Ekim 2026

PhilipMorris kaynaklarından `TCML.lib`, `EngineLib.lib` ve `TUIs.lib` yeniden üretildi. Çıktılar yalnız `build/client-libraries/lib/` altında; kaynak paketindeki kütüphaneler, çalışan oyun EXE'si ve veritabanı değiştirilmedi.

## Derleme

Gerekli araçlar: VS 2019 Build Tools v141 (`14.16.27023`), x86 MFC, Windows 10 SDK ve `dmusici.h` içeren eski DirectX 9 SDK başlıkları.

```powershell
python scripts/build_client_libraries.py --dx-include "DIRECTX_SDK_INCLUDE_KLASORU"
```

Tek kütüphane için `--library TCML`, `--library EngineLib` veya `--library TUIs` kullanılabilir. Dosya listeleri ilgili kaynak `.vcproj` dosyalarından okunur; nesne dosyaları ve loglar kütüphaneye ait `build/` alt klasöründe tutulur. Sonuçlar Git'e eklenmez.

## Kaynak uyarlamaları

- Motorun harita kodundaki türü belirtilmemiş `offset` dizisine `int` eklendi.
- Motor ve araç arayüzünün `OnNcHitTest` dönüş tipleri güncel MFC'nin beklediği `LRESULT` ile eşleştirildi.
- Kaldırılmış MFC kenarlık sabitleri yerine Windows kenarlık ölçüleri kullanıldı.
- Shell Unicode dönüşümünde yanlış `USHORT*` dönüşümü kaldırıldı; çıktı tamponu uzunluğu bayt yerine karakter sayısı olarak verildi.

## Sıkıştırma bağımlılığı

Paketli `zlib.lib` de boş olduğundan resmî `https://github.com/madler/zlib` kaynağının `v1.3.1` etiketi (`51b7f2abdade71cd9bb0e7a373ef2610ec6f9daf`) `build/vendor/zlib/` içine alındı. Bu kaynak oyun tabanının değişmesi anlamına gelmez; motorun sıkıştırma bağımlılığıdır.

```powershell
git clone --depth 1 --branch v1.3.1 https://github.com/madler/zlib.git build/vendor/zlib
python scripts/build_client_libraries.py --dx-include "DIRECTX_SDK_INCLUDE_KLASORU" --zlib-source build/vendor/zlib
```

`LegacyZlibSmoke.cpp`, oyunun mevcut eski zlib başlığıyla yeni kütüphaneyi bağlayıp sıkıştırma ve açma işlemlerini çalıştırdı; geri elde edilen veri özgün veriyle aynı çıktı. Bu test geçti.

## Doğrulama sınırı

Üç kütüphanenin kaynakları derlendi, COFF arşivleri üretildi ve arşiv üye listeleri açıldı. Bu kanıt kütüphane üretimini doğrular; oyun içi çalışmayı doğrulamaz.

Tam istemcinin bağlanması henüz tamamlanmadı. Kaynak paketindeki `NPGameLib.lib`, `XTrap4Client_mt.lib`, `AHClientInterface.lib` ve `HSUpChk.lib` dosyalarının başlarında geçerli arşiv imzası yerine sıfır baytlar bulundu. Bu dış SDK bağımlılıkları ve istemcinin önceki kaynak/arayüz uyarlamaları ayrıca ele alınmalı. Çalışan oyunun güvenlik entegrasyonlarına bu adımda değişiklik yapılmadı.
