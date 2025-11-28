import requests
import json
import gzip
import re
from io import BytesIO
from urllib.parse import urlparse, parse_qs

def get_canli_tv_m3u():
    """CanliTV API'den kanal listesini alır ve güncel token ile M3U dosyası oluşturur"""

    url = "https://core-api.kablowebtv.com/api/channels"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJjZ2QiOiIwOTNkNzIwYS01MDJjLTQxZWQtYTgwZi0yYjgxNjk4NGZiOTUiLCJkaSI6IjBmYTAzNTlkLWExOWItNDFiMi05ZTczLTI5ZWNiNjk2OTY0MCIsImFwdiI6IjEuMC4wIiwiZW52IjoiTElWRSIsImFibiI6IjEwMDAiLCJzcGdkIjoiYTA5MDg3ODQtZDEyOC00NjFmLWI3NmItYTU3ZGViMWI4MGNjIiwiaWNoIjoiMCIsInNnZCI6ImViODc3NDRjLTk4NDItNDUwNy05YjBhLTQ0N2RmYjg2NjJhZCIsImlkbSI6IjAiLCJkY3QiOiIzRUY3NSIsImlhIjoiOjpmZmZmOjEwLjAuMC41IiwiY3NoIjoiVFJLU1QiLCJpcGIiOiIwIn0.bT8PK2SvGy2CdmbcCnwlr8RatdDiBe_08k7YlnuQqJE"
    }

    try:
        print("📡 CanliTV API'den veri alınıyor...")

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Gzip decode
        try:
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
                content = gz.read().decode('utf-8')
        except:
            content = response.content.decode('utf-8')

        data = json.loads(content)

        if not data.get('IsSucceeded') or not data.get('Data', {}).get('AllChannels'):
            print("❌ CanliTV API'den geçerli veri alınamadı!")
            return False

        channels = data['Data']['AllChannels']
        print(f"✅ {len(channels)} kanal bulundu")

        # İlk kanaldan güncel token'ı al
        # Token'ı token.txt dosyasından oku
        current_token = None
        try:
            with open("token.txt", "r", encoding="utf-8") as token_file:
                current_token = token_file.read().strip()
                print(f"🔑 Token dosyadan okundu: {current_token[:30]}...")
        except FileNotFoundError:
            print("⚠️ token.txt dosyası bulunamadı! URL'ler orijinal haliyle kaydedilecek.")
        except Exception as e:
            print(f"⚠️ Token okuma hatası: {e}")

        if not current_token:
            print("⚠️ Token bulunamadı! URL'ler orijinal haliyle kaydedilecek.")

        # M3U dosyası oluştur
        with open("yeni.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

            kanal_sayisi = 0
            kanal_index = 1

            for channel in channels:
                name = channel.get('Name')
                stream_data = channel.get('StreamData', {})
                hls_url = stream_data.get('HlsStreamUrl') if stream_data else None
                logo = channel.get('PrimaryLogoImageUrl', '')
                categories = channel.get('Categories', [])

                if not name or not hls_url:
                    continue

                group = categories[0].get('Name', 'Genel') if categories else 'Genel'

                # Bilgilendirme kategorisini atla
                if group == "Bilgilendirme":
                    continue

                # URL'deki eski token'ı yeni token ile değiştir
                if current_token:
                    # Eski token'ı bul ve yeni token ile değiştir
                    updated_url = re.sub(
                        r'wmsAuthSign=[^&]*',
                        f'wmsAuthSign={current_token}',
                        hls_url
                    )
                else:
                    updated_url = hls_url

                tvg_id = str(kanal_index)

                f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{name}\n')
                f.write(f'{updated_url}\n')

                kanal_sayisi += 1
                kanal_index += 1

        print(f"📺 yeni.m3u dosyası oluşturuldu! ({kanal_sayisi} kanal)")
        print(f"💾 Token token.txt dosyasına kaydedildi")
        return True

    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    get_canli_tv_m3u()
