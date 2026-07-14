import urllib.request
import csv
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta

url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
file_path = 'ff_calendar_thisweek.csv'

try:
    print("Mengunduh data kalender Forex Factory...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    xml_data = response.read()

    print("Mem-parsing data XML...")
    root = ET.fromstring(xml_data)
    
    # 1. BACA DATA LOKAL YANG SUDAH ADA (SMART MERGE)
    existing_news = {}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None) # Abaikan header saat membaca
            for row in reader:
                if len(row) >= 4:
                    # Buat Kunci Unik: Judul + Negara + Tanggal + Waktu
                    unique_key = f"{row[0]}_{row[1]}_{row[2]}_{row[3]}"
                    existing_news[unique_key] = row
    
    # 2. PROSES DATA BARU DARI INTERNET
    target_countries = ["USD", "GBP", "EUR", "JPY", "AUD"]
    new_entries_count = 0

    for event in root.findall('event'):
        impact = event.find('impact').text
        
        if impact == "High":
            country = event.find('country').text
            
            if country in target_countries:
                title = event.find('title').text
                date_str = event.find('date').text
                time_str = event.find('time').text
                
                # Time Shifter (UTC ke UTC+3)
                if time_str.lower() != "all day" and time_str != "":
                    try:
                        dt_obj = datetime.strptime(f"{date_str} {time_str}", "%m-%d-%Y %I:%M%p")
                        dt_obj += timedelta(hours=3)
                        date_str = dt_obj.strftime("%m-%d-%Y")
                        time_str = dt_obj.strftime("%I:%M%p").lstrip("0").lower()
                    except ValueError:
                        pass
                        
                # 3. FILTER DUPLIKASI
                unique_key = f"{title}_{country}_{date_str}_{time_str}"
                
                # Jika berita ini BELUM ADA di data lokal, tambahkan!
                if unique_key not in existing_news:
                    existing_news[unique_key] = [title, country, date_str, time_str, impact, "", "", ""]
                    new_entries_count += 1

    print(f"Ditemukan {new_entries_count} berita High Impact BARU untuk disuntikkan.")

    # 4. TULIS ULANG SEMUA DATA (GABUNGAN LAMA + BARU)
    print(f"Menyimpan ke {file_path} (Total data kini: {len(existing_news)})...")
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Tulis Header
        writer.writerow(["Title", "Country", "Date", "Time", "Impact", "Forecast", "Previous", "URL"])
        # Tulis seluruh data (Lama + Baru)
        writer.writerows(existing_news.values())
        
    print("Selesai! File lokal sukses diperbarui tanpa merusak/menghapus data lama.")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")
