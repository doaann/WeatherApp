import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import datetime

# ===== AYARLAR =====
API_KEY = "7440736a215399e6c35a30f32d716d50"
BG_IMAGE_URL = "https://i.pinimg.com/736x/8d/96/c3/8d96c31ecb480ba85abd181e09a31e3a.jpg"
WIDTH, HEIGHT = 600, 600  # Genişliği artırdık

# ===== ANA PENCERE =====
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

sicaklik_label = tk.Label(pencere, font=("Arial", 48, "bold"), fg="white", bg="#222222")
canvas.create_window(WIDTH - 100, 100, window=sicaklik_label, width=120)

aciklama_label = tk.Label(pencere, font=("Arial", 16), fg="white", bg="#222222")
canvas.create_window(120, 100, window=aciklama_label, width=200)

ikon_label = tk.Label(pencere, bg="#222222")
canvas.create_window(WIDTH // 2, 170, window=ikon_label)

forecast_frames = []
for i in range(5):
    frame = tk.Frame(pencere, bg="#222222", bd=2, relief="ridge")
    canvas.create_window(70 + i * 110, HEIGHT - 110, window=frame, width=100, height=150)  # Yüksekliği 150 yaptık

    gun_label = tk.Label(frame, text="", font=("Arial", 11, "bold"), fg="white", bg="#222222")
    gun_label.pack(pady=(6, 2))

    ikon_label_f = tk.Label(frame, bg="#222222")
    ikon_label_f.pack(pady=8)

    sicaklik_label_f = tk.Label(frame, font=("Arial", 9), fg="white", bg="#222222")
    sicaklik_label_f.pack(pady=(2, 8))

    temp_label = tk.Label(frame, font=("Arial", 9), fg="white", bg="#222222")
    temp_label.pack(pady=(2, 8))

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
        aciklama_label.config(text=desc)

        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_img = Image.open(BytesIO(requests.get(icon_url).content))
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

            icon_url = f"http://openweathermap.org/img/wn/{gun_icon}.png"
            icon_img = Image.open(BytesIO(requests.get(icon_url).content))
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
