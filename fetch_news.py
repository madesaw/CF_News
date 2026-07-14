import urllib.request
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# Menggunakan feed XML mingguan Forex Factory
url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"

try:
    print("Mengunduh data kalender Forex Factory...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    xml_data = response.read()

    print("Mem-parsing data XML dan menyaring negara...")
    root = ET.fromstring(xml_data)
    
    high_impact_news = []
    
    # Format header sesuai pembacaan V11.6 / V12.2
    high_impact_news.append(["Title", "Country", "Date", "Time", "Impact", "Forecast", "Previous", "URL"])

    # DOKTRIN FILTER: Hanya Negara Tier-1
    target_countries = ["USD", "GBP", "EUR", "JPY", "AUD"]

    for event in root.findall('event'):
        impact = event.find('impact').text
        
        # HANYA ambil yang High Impact
        if impact == "High":
            country = event.find('country').text
            
            # HANYA ambil negara target
            if country in target_countries:
                title = event.find('title').text
                date_str = event.find('date').text
                time_str = event.find('time').text
                
                # --- TIME SHIFTER ENGINE (UTC -> UTC+3) ---
                if time_str.lower() != "all day" and time_str != "":
                    try:
                        # Gabungkan tanggal dan waktu untuk diparse (contoh: "07-14-2026 12:30pm")
                        dt_obj = datetime.strptime(f"{date_str} {time_str}", "%m-%d-%Y %I:%M%p")
                        
                        # Tambahkan Offset Broker (+3 Jam)
                        dt_obj += timedelta(hours=3)
                        
                        # Pecah kembali menjadi string untuk CSV
                        date_str = dt_obj.strftime("%m-%d-%Y")
                        # lstrip("0") untuk membuang angka 0 di depan (03:30pm -> 3:30pm) agar sesuai parser MQL4
                        time_str = dt_obj.strftime("%I:%M%p").lstrip("0").lower()
                    except ValueError:
                        pass # Abaikan konversi jika format waktu FF sedang anomali
                        
                # Simpan ke memori
                high_impact_news.append([
                    title, 
                    country, 
                    date_str, 
                    time_str, 
                    impact, 
                    "", "", "" # Dikosongkan agar file ringan
                ])

    print(f"Ditemukan {len(high_impact_news)-1} berita High Impact dari negara target.")

    # Tulis ke file CSV
    print("Menyimpan ke ff_calendar_thisweek.csv (Waktu Broker UTC+3)...")
    with open('ff_calendar_thisweek.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(high_impact_news)
        
    print("Selesai!")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")
