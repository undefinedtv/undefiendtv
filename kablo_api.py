#!/usr/bin/env python3
import requests
import json
from datetime import datetime

# API Konfigürasyon
API_URL = "https://core-api.kablowebtv.com/api/channels"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Referer": "https://tvheryerde.com",
    "Origin": "https://tvheryerde.com",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJMSVZFIiwiaXBiIjoiMCIsImNnZCI6IjA5M2Q3MjBhLTUwMmMtNDFlZC1hODBmLTJiODE2OTg0ZmI5NSIsImNzaCI6IlRSS1NUIiwiZGN0IjoiRTFDNjQiLCJkaSI6Ijg5MTlmNjYwLTBhZGUtNGYwMS1hMTVlLTc2MDZjNjI4ZTc5MyIsInNnZCI6IjM5MTY0ZjIwLTZlZjUtNDRlZS04ZjAyLWEzODRjOTg1ZTY5MyIsInNwZ2QiOiI5ZjJlYWE1NC01NDM2LTQ0ZTgtYTkyNy00MzQ2NjlkMTU1MWEiLCJpY2giOiIwIiwiaWRtIjoiMCIsImlhIjoiOjpmZmZmOjEwLjAuMC41IiwiYXB2IjoiMS4wLjAiLCJhYm4iOiIxMDAwIiwibmJmIjoxNzQzNDY1MzY5LCJleHAiOjE3NDM0NjU0MjksImlhdCI6MTc0MzQ2NTM2OX0.YWdVfOL5hEZTrd4f4qkmPCPmUUlaiG7I2REW5H0p6Gw"
}

def generate_m3u():
    try:
        # API'den veri çekme
        response = requests.get(API_URL, headers=HEADERS, timeout=20)
        response.raise_for_status()

        data = response.json()

        # PHP'deki gibi validasyon
        if not data.get('IsSucceeded') or not data.get('Data', {}).get('AllChannels'):
            raise ValueError("API geçersiz yanıt verdi")

        # M3U oluşturma
        m3u_lines = ["#EXTM3U"]
        for channel in data['Data']['AllChannels']:
            if not channel.get('Name') or not channel.get('StreamData', {}).get('HlsStreamUrl'):
                continue

            group = channel.get('Categories', [{}])[0].get('Name', 'Genel')
            if group == "Bilgilendirme":
                continue

            m3u_lines.append(
                f'#EXTINF:-1 tvg-id="{channel.get("Id", "")}" tvg-name="{channel["Name"]}" '
                f'tvg-logo="{channel.get("PrimaryLogoImageUrl", "")}" '
                f'group-title="{group}",{channel["Name"]}\n'
                f'{channel["StreamData"]["HlsStreamUrl"]}'
            )

        # Dosyaya yaz
        with open("kablo_tv.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))

        print("✅ M3U başarıyla oluşturuldu!")
        return True

    except Exception as e:
        error_msg = f"{datetime.now().isoformat()} - HATA: {str(e)}"
        print(error_msg)
        with open("error.log", "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")
        return False

if __name__ == "__main__":
    generate_m3u()
