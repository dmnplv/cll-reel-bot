import os, requests, time, asyncio, subprocess
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Pulizia radicale
def clean(v): return str(v or "").strip().replace('*', '').replace(' ', '')

API_ID = int(clean(os.getenv('TG_API_ID')) or 0)
API_HASH = clean(os.getenv('TG_API_HASH'))
SESSION_STR = clean(os.getenv('TG_SESSION'))
IG_ID = clean(os.getenv('IG_BUSINESS_ID'))
IG_TOKEN = clean(os.getenv('IG_PAGE_TOKEN'))
REPO = os.getenv('GITHUB_REPOSITORY')
GH_TOKEN = os.getenv('GITHUB_TOKEN') 

async def main():
    print(f"DEBUG: ID trovato -> {IG_ID}")
    
    if not IG_ID or not IG_TOKEN:
        print("❌ ERRORE: Secrets Instagram mancanti.")
        return

    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: gia_postati = f.read().splitlines()

    video_m = None
    async for m in client.iter_messages('phorig', limit=10):
        if m.video and str(m.id) not in gia_postati:
            video_m = m
            break

    if video_m:
        raw_path = await video_m.download_media()
        out_name = "ready.mp4"
        print(f"Compressione 720p...")
        subprocess.run(['ffmpeg', '-i', raw_path, '-vf', 'scale=-2:720', '-vcodec', 'libx264', '-crf', '30', '-preset', 'ultrafast', '-acodec', 'aac', '-y', out_name])
        
        # URL con token per repo privato
        video_url = f"https://{GH_TOKEN}@://raw.githubusercontent.com{REPO}/main/{out_name}"
        
        # FIX QUI: Aggiunto lo slash "/" prima di {IG_ID}
        target_url = f"https://graph.facebook.com/{IG_ID}/media"
        
        try:
            print(f"Inviando URL a Instagram...")
            r = requests.post(target_url, data={
                'media_type': 'REELS', 
                'video_url': video_url, 
                'caption': 'Catania Latin Lovers 🌋', 
                'access_token': IG_TOKEN
            }).json()
            
            if 'id' in r:
                creation_id = r['id']
                print(f"✅ Container creato: {creation_id}. Attesa 120s...")
                time.sleep(120)
                
                # FIX ANCHE QUI: Aggiunto lo slash "/" prima di {IG_ID}
                publish_url = f"https://graph.facebook.com/{IG_ID}/media_publish"
                p = requests.post(publish_url, data={
                    'creation_id': creation_id, 
                    'access_token': IG_TOKEN
                }).json()
                
                if 'id' in p:
                    with open('pubblicati.txt', 'a') as f: f.write(f"{video_m.id}\n")
                    print("🔥 PUBBLICATO")
                else:
                    print(f"❌ Errore pubblicazione: {p}")
            else:
                print(f"❌ Errore Instagram (Container): {r}")
        except Exception as e:
            print(f"❌ Errore critico: {e}")
        
        if os.path.exists(raw_path): os.remove(raw_path)
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
