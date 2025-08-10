import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
import requests
from io import BytesIO
import datetime

API_KEY = "7440736a215399e6c35a30f32d716d50"
BG_IMAGE_URL = "https://i.postimg.cc/GtjYrJrc/photo-1520034475321-cbe63696469a.jpg"

WIDTH, HEIGHT = 650, 600

pencere = tk.Tk()
pencere.title("Hava Durumu Uygulaması")
pencere.geometry(f"{WIDTH}x{HEIGHT}")
pencere.resizable(False, False)

try:
    response = requests.get(BG_IMAGE_URL)
    response.raise_for_status()
    bg_img = Image.open(BytesIO(response.content)).resize((WIDTH, HEIGHT))
    bg_tk = ImageTk.PhotoImage(bg_img)
except Exception as e:
    messagebox.showerror("Hata", f"Arka plan resmi yüklenemedi: {e}")
    pencere.destroy()
    exit()

canvas = tk.Canvas(pencere, width=WIDTH, height=HEIGHT)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_tk, anchor="nw")

sehir_entry = tk.Entry(pencere, font=("Arial", 14))
canvas.create_window(WIDTH // 2 - 40, 30, window=sehir_entry, width=200, height=30)

buton = tk.Button(pencere, text="Getir", font=("Arial", 12), command=lambda: getir_hava(sehir_entry.get()))
canvas.create_window(WIDTH // 2 + 130, 30, window=buton, width=60, height=30)


# yuvarlatılmış dikdörtgen çizme fonksiyonu
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


# yeni: beyaz halo'yu temizleyen fonksiyon
def remove_white_halo(img, white_thresh=235, alpha_thresh=200, blur_radius=1, bg_color="#222222"):
    """
    - white_thresh: RGB > this -> considered 'very light' (candidate for halo)
    - alpha_thresh: only pixels with alpha < alpha_thresh are considered halo (preserve opaque whites)
    - blur_radius: small blur on alpha to smooth edges (0 to disable)
    - Returns RGBA image already composited onto bg_color (so it will match canvas background)
    """
    img = img.convert("RGBA")
    pixels = list(img.getdata())
    new_pixels = []
    for (r, g, b, a) in pixels:
        # sadece yarı saydam, çok açık renkli pikselleri şeffaf yapma
        if a < alpha_thresh and r >= white_thresh and g >= white_thresh and b >= white_thresh:
            new_pixels.append((r, g, b, 0))
        else:
            new_pixels.append((r, g, b, a))
    img.putdata(new_pixels)

    # yumuşatma: alpha kanalını blur ile yumuşatıp tekrar koy
    if blur_radius and blur_radius > 0:
        alpha = img.split()[3].filter(ImageFilter.GaussianBlur(blur_radius))
        img.putalpha(alpha)

    #arka planla blend ve sonucu döndür
    bg = Image.new("RGBA", img.size, bg_color)
    result = Image.alpha_composite(bg, img)
    return result


#ana sıcaklık ve gündüz etiketleri için arka plan kutusu
main_frame_width = 220
main_frame_height = 80
main_frame_x1 = WIDTH - 260
main_frame_y1 = 65
main_frame_x2 = main_frame_x1 + main_frame_width
main_frame_y2 = main_frame_y1 + main_frame_height
canvas.create_rectangle(main_frame_x1, main_frame_y1, main_frame_x2, main_frame_y2, fill="#222222")


#iç boşluk (padding) ekleyerek Frame oluşturdum
main_frame = tk.Frame(pencere, bg="#222222", padx=15, pady=15)
canvas.create_window((main_frame_x1 + main_frame_x2)//2, (main_frame_y1 + main_frame_y2)//2, window=main_frame, width=main_frame_width, height=main_frame_height)

sicaklik_label = tk.Label(main_frame, font=("Arial", 36, "bold"), fg="white", bg="#222222", text="")  # Başlangıçta boş
sicaklik_label.pack(side="left")

gunduz_label = tk.Label(main_frame, text="", font=("Arial", 14, "bold"), fg="white", bg="#222222")  # Başlangıçta boş
gunduz_label.pack(side="left", padx=(10, 0))


#açıklama için arka plan kutusu
aciklama_x1, aciklama_y1 = 40, 70
aciklama_width, aciklama_height = 220, 80
aciklama_x2 = aciklama_x1 + aciklama_width
aciklama_y2 = aciklama_y1 + aciklama_height
create_rounded_rectangle(canvas, aciklama_x1, aciklama_y1, aciklama_x2, aciklama_y2, radius=25, fill="#222222", outline="#222222", width=1)

aciklama_label = tk.Label(pencere, font=("Arial", 20), fg="white", bg="#222222", wraplength=aciklama_width-20, justify="center")
canvas.create_window(aciklama_x1 + aciklama_width//2, aciklama_y1 + aciklama_height//2, window=aciklama_label, width=aciklama_width-20)

#ikon için yuvarlak arka plan
ikon_bg_radius = 75
ikon_center_x = WIDTH // 2
ikon_center_y = 200 + 40
canvas.create_oval(
    ikon_center_x - ikon_bg_radius,
    ikon_center_y - ikon_bg_radius,
    ikon_center_x + ikon_bg_radius,
    ikon_center_y + ikon_bg_radius,
    fill="#222222", outline="#222222", width=1
)

ikon_label = tk.Label(pencere, bg="#222222", pady=5, padx=5)
canvas.create_window(ikon_center_x, ikon_center_y, window=ikon_label)

#5 günlük widgetlar
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

    create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, fill="#222222", outline="#222222", width=1)

    gun_label = tk.Label(pencere, text="", font=("Arial", 12, "bold"), fg="white", bg="#222222")
    ikon_label_f = tk.Label(pencere, bg="#222222")
    sicaklik_label_f = tk.Label(pencere, font=("Arial", 10), fg="white", bg="#222222")
    temp_label = tk.Label(pencere, font=("Arial", 10), fg="white", bg="#222222", wraplength=frame_width - 20, justify="center")

    canvas.create_window((x1 + x2)//2, y1 + 20, window=gun_label)
    canvas.create_window((x1 + x2)//2, y1 + 60, window=ikon_label_f)
    canvas.create_window((x1 + x2)//2, y1 + 100, window=sicaklik_label_f)
    canvas.create_window((x1 + x2)//2, y1 + 130, window=temp_label)

    forecast_frames.append({
        "gun": gun_label,
        "ikon": ikon_label_f,
        "sicaklik": sicaklik_label_f,
        "gece_gunduz": temp_label
    })


def getir_hava(sehir):
    if not sehir.strip():
        messagebox.showwarning("Uyarı", "Lütfen bir şehir adı girin!")
        return

    try:
        url_current = f"https://api.openweathermap.org/data/2.5/weather?q={sehir}&appid={API_KEY}&lang=tr&units=metric"
        veri = requests.get(url_current).json()

        if veri.get("cod") != 200:
            messagebox.showerror("Hata", "Şehir bulunamadı!")
            return

        temp = round(veri["main"]["temp"])
        desc = veri["weather"][0]["description"].title()
        icon_code = veri["weather"][0]["icon"]

        sicaklik_label.config(text=f"{temp}°")
        gunduz_label.config(text="Gündüz")
        aciklama_label.config(text=desc)

        # ana ikon
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_img = Image.open(BytesIO(requests.get(icon_url).content)).convert("RGBA")
        icon_img = remove_white_halo(icon_img, white_thresh=235, alpha_thresh=200, blur_radius=1, bg_color="#222222")
        icon_tk = ImageTk.PhotoImage(icon_img)
        ikon_label.config(image=icon_tk)
        ikon_label.image = icon_tk

        url_forecast = f"https://api.openweathermap.org/data/2.5/forecast?q={sehir}&appid={API_KEY}&lang=tr&units=metric"
        forecast_data = requests.get(url_forecast).json()

        daily_data = {}
        for entry in forecast_data["list"]:
            tarih_str = entry["dt_txt"].split(" ")[0]
            if tarih_str not in daily_data:
                daily_data[tarih_str] = []
            daily_data[tarih_str].append(entry)

        bugun = datetime.datetime.now().date()
        gun_isimleri = ["Paz", "Pzt", "Sal", "Çar", "Per", "Cum", "Cmt"]

        i = 0
        for tarih_str, entries in list(daily_data.items())[:5]:
            dt_sample = datetime.datetime.strptime(tarih_str, "%Y-%m-%d").date()
            if dt_sample == bugun:
                gun_adi = "Bugün"
            else:
                gun_adi = gun_isimleri[dt_sample.weekday()]

            gece_temp = None
            gun_temp = None
            gece_icon = None
            gun_icon = None

            for e in entries:
                saat = e["dt_txt"].split(" ")[1][:5]
                if saat >= "00:00" and saat < "06:00":
                    if gece_temp is None:
                        gece_temp = round(e["main"]["temp"])
                        gece_icon = e["weather"][0]["icon"]
                if saat >= "12:00" and saat <= "18:00":
                    if gun_temp is None:
                        gun_temp = round(e["main"]["temp"])
                        gun_icon = e["weather"][0]["icon"]

            if gun_temp is None:
                gun_temp = round(entries[0]["main"]["temp"])
                gun_icon = entries[0]["weather"][0]["icon"]

            if gece_temp is None:
                gece_temp = round(entries[0]["main"]["temp"])
                gece_icon = entries[0]["weather"][0]["icon"]

            # tahmin ikonları için
            icon_url = f"http://openweathermap.org/img/wn/{gun_icon}.png"
            icon_img = Image.open(BytesIO(requests.get(icon_url).content)).convert("RGBA")
            icon_img = remove_white_halo(icon_img, white_thresh=235, alpha_thresh=200, blur_radius=1, bg_color="#222222")
            icon_tk = ImageTk.PhotoImage(icon_img)

            forecast_frames[i]["gun"].config(text=gun_adi)
            forecast_frames[i]["ikon"].config(image=icon_tk)
            forecast_frames[i]["ikon"].image = icon_tk

            forecast_frames[i]["sicaklik"].config(text=f"{gun_temp}°")
            forecast_frames[i]["gece_gunduz"].config(text=f"Gece {gece_temp}°")

            i += 1

    except Exception as e:
        messagebox.showerror("Hata", f"Veri alınamadı: {e}")

pencere.mainloop()
