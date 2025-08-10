# Hava Durumu Uygulaması — README

**Kısa Açıklama**

Bu proje, OpenWeatherMap API'sinden veri çeken, Tkinter ile yapılmış basit bir masaüstü hava durumu uygulamasıdır. Arka plan görseli, ana ikon, 5 günlük tahmin kartları ve kenar yumuşatma / beyaz halo temizleme (ikon kenarındaki aydınlık pikselleri kaldırma) özellikleri içerir.

---

## Özellikler

- Anlık hava verisi (sıcaklık, açıklama, ikon)
- 5 günlük tahmin gösterimi (gündüz / gece sıcaklıkları)
- Arka plan resmi desteği
- Kartlar ve ikonlar için koyu tema ve yuvarlatılmış arka planlar
- İkonlardaki beyaz/aydınlık kenarları temizleyen `remove_white_halo` fonksiyonu (arka planla uyum için)

---

## Gereksinimler

- Python 3.8+ (3.10 önerilir)
- Aşağıdaki paketler:

```bash
pip install pillow requests
```

Tkinter çoğu sistemde Python ile birlikte gelir. Eğer yoksa işletim sistemine göre yükleyin (örn. Ubuntu: `sudo apt install python3-tk`).

---

## Kurulum ve Çalıştırma

1. Bu havadurumu uygulamasının `.py` dosyasını bir klasöre koyun.
2. `API_KEY` değişkenine kendi **OpenWeatherMap** API anahtarınızı yazın ([https://openweathermap.org](https://openweathermap.org)).
3. Opsiyonel: `BG_IMAGE_URL` değişkenini istediğiniz arka plan görselinin URL'si ile değiştirin.
4. Gerekli Python paketlerini yükleyin:

```bash
pip install pillow requests
```

5. Uygulamayı çalıştırın:

```bash
python main.py
```

---

## Ana Dosya ve Önemli Bölümler

- `API_KEY` — OpenWeatherMap API anahtarınızı buraya koyun.
- `BG_IMAGE_URL` — Arka plan görseli URL'si.
- `WIDTH, HEIGHT` — Pencere boyutu.
- `create_rounded_rectangle` — Canvas üzerinde yuvarlatılmış dikdörtgen çizer.
- `remove_white_halo(img, white_thresh, alpha_thresh, blur_radius, bg_color)` — İkonlardaki beyaz/yarı saydam kenarları temizler ve sonucu arka plan rengine (`bg_color`) göre harmanlar.
- `getir_hava(sehir)` — Veriyi alıp GUI öğelerini güncelleyen ana fonksiyon.

---

## `remove_white_halo` ayarları (ince ayar)

`remove_white_halo` fonksiyonunu şu parametrelerle kontrol edebilirsiniz:

- `white_thresh` (default `235`): RGB değerleri bu eşiğin üzerinde olan pikseller "çok açık" kabul edilir. Değeri düşürmek (ör. 220) daha fazla pikselin temizlenmesine neden olur; artırmak daha az temizler.
- `alpha_thresh` (default `200`): Alfa (opaklık) eşiği. Bu değerin altındaki (yarı şeffaf) pikseller temizleme adımına dahil edilir. Daha düşük değer, yalnızca çok şeffaf pikselleri hedefler.
- `blur_radius` (default `1`): Alfa kanalına uygulanacak küçük Gaussian blur. Kenarların daha yumuşak görünmesini sağlar. `0` yaparak devre dışı bırakabilirsiniz.
- `bg_color` (default `#222222`): Son görüntüyü harmanlayacağınız arka plan rengi.

**Örnek:** Eğer kenarlar hâlâ beyaz görünüyorsa `white_thresh=230, alpha_thresh=210, blur_radius=1` deneyin. Çok agresif ayarlar ikonun içindeki açık detayları da kaybettirebilir; bu yüzden küçük artışlarla deneme yapın.

---

## Hata Giderme / İpuçları

- **Arka plan resmi yüklenemedi hatası**: URL doğru mu kontrol edin. İnternet bağlantınız varsa tarayıcıda URL’yi açın. HTTP hata kodu mesajı hata kutusunda gösterilir.
- **Tkinter penceresi açılmıyor**: Python sürümü ve tkinter kurulumu kontrol edin.
- **İkonların etrafında beyaz/aydınlık halo kalıyor**: `remove_white_halo` parametrelerini ayarlayın (yukarıya bakın). Eğer yine kalıyorsa ikonun farklı bir boyut/format (ör. `@2x` yerine normal) ile deneyin.
- **Yazılar sığmıyor / taşma yapıyor**: `WIDTH`, `HEIGHT`, `frame_width`, `frame_height` veya ilgili `padx/pady` değerlerini değiştirin.

---

## Özelleştirme Önerileri

- Kart arka plan rengini değiştirmek için `fill="#222222"` değerini düzenleyin.
- Ana sıcaklık fontunu küçültmek için `sicaklik_label` oluşturulurken font boyutunu değiştirin.
- İkon boyutunu küçültmek istiyorsanız OpenWeatherMap 2x yerine normal ikonları (`@2x` yerine normal) kullanın.

---

## SSS

**S: İkonlar neden PNG'de farklı boyutta geliyor?**
C: OpenWeatherMap’in ikon seti farklı boyutlarda sunulabiliyor. Kod `@2x` ile büyük ikon istiyor; istersen `@2x` yok ederek daha küçük ikon kullanabilirsin.

**S: Kodu mobil/başka bir GUI kütüphanesine taşımak mümkün mü?**
A: Evet, web veya mobil için React/Flutter’a taşınabilir. İkon işleme mantığı (halo temizleme) Pillow kodu benzer şekilde kullanılabilir.

---

## Lisans

Bu README ve örnek uygulama MIT benzeri serbest kullanım içindir. Kodu kullanıp değiştirebilirsiniz. Proje sahibine atıf isterseniz hoş olur, ama zorunlu değildir.

---
