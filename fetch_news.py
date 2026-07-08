import urllib.request
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

# Menggunakan feed XML mingguan Forex Factory (legal dan ringan)
url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"

try:
    print("Mengunduh data kalender Forex Factory...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    xml_data = response.read()

    print("Mem-parsing data XML...")
    root = ET.fromstring(xml_data)
    
    high_impact_news = []
    
    # Format header sesuai pembacaan V11.6
    # Title,Country,Date,Time,Impact,Forecast,Previous,URL
    high_impact_news.append(["Title", "Country", "Date", "Time", "Impact", "Forecast", "Previous", "URL"])

    for event in root.findall('event'):
        impact = event.find('impact').text
        
        # HANYA ambil yang High Impact
        if impact == "High":
            title = event.find('title').text
            country = event.find('country').text
            
            # Konversi format tanggal FF (MM-DD-YYYY) agar konsisten dengan parser MQL4
            date_str = event.find('date').text
            # Waktu bisa berupa "All Day" atau format "HH:MMam/pm"
            time_str = event.find('time').text
            
            # Kita simpan dengan format raw FF, karena V11.6 sudah dibekali Parser cerdas
            high_impact_news.append([
                title, 
                country, 
                date_str, 
                time_str, 
                impact, 
                "", "", "" # Forecast, Previous, URL dikosongkan untuk meringankan file
            ])

    print(f"Ditemukan {len(high_impact_news)-1} berita High Impact.")

    # Tulis ke file CSV
    print("Menyimpan ke ff_calendar_thisweek.csv...")
    with open('ff_calendar_thisweek.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(high_impact_news)

    print("Selesai! File berhasil dibuat.")

except Exception as e:
    print(f"Gagal mengunduh atau memproses data: {e}")
