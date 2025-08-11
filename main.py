import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
import requests
from io import BytesIO
import datetime

# konfigürasyon
API_KEY = "7440736a215399e6c35a30f32d716d50"
BG_IMAGE_URL = "https://i.postimg.cc/GtjYrJrc/photo-1520034475321-cbe63696469a.jpg"
WIDTH, HEIGHT = 650, 600
BG_COLOR = "#222222"

# global kütüphane/önbellek
icon_cache = {}

#pencere
pencere = tk.Tk()
pencere.title("Hava Durumu Uygulaması")
pencere.geometry(f"{WIDTH}x{HEIGHT}")
pencere.resizable(False, False)

#arka plan resmini indirip ImageTk.PhotoImage olarak döndür
try:
    resp = requests.get(BG_IMAGE_URL)
    resp.raise_for_status()
    _bg_img = Image.open(BytesIO(resp.content)).resize((WIDTH, HEIGHT))
    bg_tk = ImageTk.PhotoImage(_bg_img)
except Exception as e:
    messagebox.showerror("Hata", f"Arka plan resmi yüklenemedi: {e}")
    pencere.destroy()
    raise

canvas = tk.Canvas(pencere, width=WIDTH, height=HEIGHT)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_tk, anchor="nw")

#WIDGETLAR
sehir_entry = tk.Entry(pencere, font=("Arial", 14))
canvas.create_window(WIDTH // 2 - 40, 30, window=sehir_entry, width=200, height=30)

buton = tk.Button(pencere, text="Getir", font=("Arial", 12), command=lambda: getir_hava(sehir_entry.get()))
canvas.create_window(WIDTH // 2 + 130, 30, window=buton, width=60, height=30)

# yuvarlatılmış dikdörtgen
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

# beyaz halo temizleme fonksiyonu
def remove_white_halo(img, white_thresh=235, alpha_thresh=200, blur_radius=1, bg_color=BG_COLOR):
    img = img.convert("RGBA")
    pixels = list(img.getdata())
    new_pixels = []
    for (r, g, b, a) in pixels:
        if a < alpha_thresh and r >= white_thresh and g >= white_thresh and b >= white_thresh:
            new_pixels.append((r, g, b, 0))
        else:
            new_pixels.append((r, g, b, a))
    img.putdata(new_pixels)

    if blur_radius and blur_radius > 0:
        alpha = img.split()[3].filter(ImageFilter.GaussianBlur(blur_radius))
        img.putalpha(alpha)

    bg = Image.new("RGBA", img.size, bg_color)
    result = Image.alpha_composite(bg, img)
    return result

# ikonları indirip işleyip ImageTk.PhotoImage olarak döndüren yardımcı (cache'li)
def load_and_process_icon(icon_code, size=None, use_2x=False):
    """
    icon_code: örn '10d' veya tam olarak '10d@2x' gibi değer
    size: (w, h) tuple ile yeniden boyutlandırma
    use_2x: True ise @2x versiyonunu alır
    """
    key = f"{icon_code}_{size}_{use_2x}"
    if key in icon_cache:
        return icon_cache[key]

    suffix = "@2x" if use_2x else ""
    url = f"http://openweathermap.org/img/wn/{icon_code}{suffix}.png"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGBA")
        img = remove_white_halo(img, white_thresh=235, alpha_thresh=200, blur_radius=1, bg_color=BG_COLOR)
        if size:
            img = img.resize(size, Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        icon_cache[key] = tk_img
        return tk_img
    except Exception:
        # hata durumunda boş bir görsel yerine küçük bir renkli kare
        placeholder = Image.new("RGBA", size if size else (50, 50), BG_COLOR)
        tk_img = ImageTk.PhotoImage(placeholder)
        icon_cache[key] = tk_img
        return tk_img

# ana gösterge kısımları
main_frame_width = 220
main_frame_height = 80
main_frame_x1 = WIDTH - 260
main_frame_y1 = 65
main_frame_x2 = main_frame_x1 + main_frame_width
main_frame_y2 = main_frame_y1 + main_frame_height
canvas.create_rectangle(main_frame_x1, main_frame_y1, main_frame_x2, main_frame_y2, fill=BG_COLOR)

main_frame = tk.Frame(pencere, bg=BG_COLOR, padx=15, pady=15)
canvas.create_window((main_frame_x1 + main_frame_x2) // 2, (main_frame_y1 + main_frame_y2) // 2, window=main_frame, width=main_frame_width, height=main_frame_height)

sicaklik_label = tk.Label(main_frame, font=("Arial", 36, "bold"), fg="white", bg=BG_COLOR, text="")
sicaklik_label.pack(side="left")

gunduz_label = tk.Label(main_frame, text="", font=("Arial", 14, "bold"), fg="white", bg=BG_COLOR)
gunduz_label.pack(side="left", padx=(10, 0))

# açıklama kutusu
aciklama_x1, aciklama_y1 = 40, 70
aciklama_width, aciklama_height = 220, 80
aciklama_x2 = aciklama_x1 + aciklama_width
aciklama_y2 = aciklama_y1 + aciklama_height
create_rounded_rectangle(canvas, aciklama_x1, aciklama_y1, aciklama_x2, aciklama_y2, radius=25, fill=BG_COLOR, outline=BG_COLOR, width=1)

aciklama_label = tk.Label(pencere, font=("Arial", 20), fg="white", bg=BG_COLOR, wraplength=aciklama_width - 20, justify="center")
canvas.create_window(aciklama_x1 + aciklama_width // 2, aciklama_y1 + aciklama_height // 2, window=aciklama_label, width=aciklama_width - 20)

# ana ikon arka planı
ikon_bg_radius = 75
ikon_center_x = WIDTH // 2
ikon_center_y = 200 + 40
canvas.create_oval(
    ikon_center_x - ikon_bg_radius,
    ikon_center_y - ikon_bg_radius,
    ikon_center_x + ikon_bg_radius,
    ikon_center_y + ikon_bg_radius,
    fill=BG_COLOR, outline=BG_COLOR, width=1
)

ikon_label = tk.Label(pencere, bg=BG_COLOR, pady=5, padx=5)
canvas.create_window(ikon_center_x, ikon_center_y, window=ikon_label)

# 5 günlük forecast widget'ları
forecast_frames = []
frame_width = 95
frame_height = 160
left_margin = 40
space_between = 12
bottom_y = HEIGHT - 120

for i in range(5):
    if i == 0:
        x1 = left_margin + 30
    else:
        x1 = left_margin + 30 + i * (frame_width + space_between)
    y1 = bottom_y - frame_height // 2
    x2 = x1 + frame_width
    y2 = y1 + frame_height

    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, fill=BG_COLOR, outline=BG_COLOR, width=1)

    gun_label = tk.Label(pencere, text="", font=("Arial", 12, "bold"), fg="white", bg=BG_COLOR)
    ikon_label_f = tk.Label(pencere, bg=BG_COLOR)
    sicaklik_label_f = tk.Label(pencere, font=("Arial", 10), fg="white", bg=BG_COLOR)
    temp_label = tk.Label(pencere, font=("Arial", 10), fg="white", bg=BG_COLOR, wraplength=frame_width - 20, justify="center")

    canvas.create_window((x1 + x2) // 2, y1 + 20, window=gun_label)
    canvas.create_window((x1 + x2) // 2, y1 + 60, window=ikon_label_f)
    canvas.create_window((x1 + x2) // 2, y1 + 100, window=sicaklik_label_f)
    canvas.create_window((x1 + x2) // 2, y1 + 130, window=temp_label)

    forecast_frames.append({
        "gun": gun_label,
        "ikon": ikon_label_f,
        "sicaklik": sicaklik_label_f,
        "gece_gunduz": temp_label
    })

# API için

def api_get(url, params=None):
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Ağ hatası: {e}")


def fetch_current_weather(sehir):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": sehir, "appid": API_KEY, "lang": "tr", "units": "metric"}
    data = api_get(url, params)
    if data.get("cod") != 200 and data.get("cod") != "200":
        raise ValueError("Şehir bulunamadı")
    return data


def fetch_forecast(sehir):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": sehir, "appid": API_KEY, "lang": "tr", "units": "metric"}
    return api_get(url, params)

# ana fonksiyon
def getir_hava(sehir):
    if not sehir or not sehir.strip():
        messagebox.showwarning("Uyarı", "Lütfen bir şehir adı girin!")
        return

    try:
        # güncel veriyi al
        veri = fetch_current_weather(sehir)
        temp = round(veri["main"]["temp"])
        desc = veri["weather"][0]["description"].title()
        icon_code = veri["weather"][0]["icon"]

        sicaklik_label.config(text=f"{temp}°")
        gunduz_label.config(text="Gündüz")
        aciklama_label.config(text=desc)

        # ana ikon: @2x
        ana_icon = load_and_process_icon(icon_code, use_2x=True)
        ikon_label.config(image=ana_icon)
        ikon_label.image = ana_icon

        # tahmin verisini al
        forecast_data = fetch_forecast(sehir)

        # tarih bazlı grupla
        daily_data = {}
        for entry in forecast_data.get("list", []):
            tarih_str = entry["dt_txt"].split(" ")[0]
            daily_data.setdefault(tarih_str, []).append(entry)

        bugun = datetime.datetime.now().date()
        gun_isimleri = ["Paz", "Pzt", "Sal", "Çar", "Per", "Cum", "Cmt"]

        i = 0
        # ilk 5 günü işleme
        for tarih_str, entries in list(daily_data.items())[:5]:
            dt_sample = datetime.datetime.strptime(tarih_str, "%Y-%m-%d").date()
            gun_adi = "Bugün" if dt_sample == bugun else gun_isimleri[dt_sample.weekday()]

            gece_temp = None
            gun_temp = None
            gece_icon = None
            gun_icon = None

            for e in entries:
                zaman = datetime.datetime.strptime(e["dt_txt"], "%Y-%m-%d %H:%M:%S")
                saat = zaman.time()
                # Gece: 00:00 - 05:59
                if datetime.time(0, 0) <= saat < datetime.time(6, 0):
                    if gece_temp is None:
                        gece_temp = round(e["main"]["temp"])
                        gece_icon = e["weather"][0]["icon"]
                # gündüz: 12:00 - 18:00 aralığı
                if datetime.time(12, 0) <= saat <= datetime.time(18, 0):
                    if gun_temp is None:
                        gun_temp = round(e["main"]["temp"])
                        gun_icon = e["weather"][0]["icon"]

            # eğer belirlenen aralıklarda değer yoksa en baştaki değeri kullan
            if gun_temp is None:
                gun_temp = round(entries[0]["main"]["temp"])
                gun_icon = entries[0]["weather"][0]["icon"]

            if gece_temp is None:
                gece_temp = round(entries[0]["main"]["temp"])
                gece_icon = entries[0]["weather"][0]["icon"]

            # Forecast için ikon
            ikon_tk = load_and_process_icon(gun_icon, size=(50, 50), use_2x=False)

            forecast_frames[i]["gun"].config(text=gun_adi)
            forecast_frames[i]["ikon"].config(image=ikon_tk)
            forecast_frames[i]["ikon"].image = ikon_tk
            forecast_frames[i]["sicaklik"].config(text=f"{gun_temp}°")
            forecast_frames[i]["gece_gunduz"].config(text=f"Gece {gece_temp}°")

            i += 1

    except ValueError as ve:
        messagebox.showerror("Hata", str(ve))
    except RuntimeError as re:
        messagebox.showerror("Hata", str(re))
    except Exception as e:
        messagebox.showerror("Hata", f"Veri alınamadı: {e}")

#çalıştır
if __name__ == '__main__':
    pencere.mainloop()
