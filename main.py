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

async def main():
    print(f"DEBUG: ID trovato -> {IG_ID} (Lunghezza: {len(IG_ID)})")
    print(f"DEBUG: Token trovato (Lunghezza: {len(IG_TOKEN)})")
    
    if len(IG_ID) < 5 or len(IG_TOKEN) < 10:
        print("❌ ERRORE: I Secrets di Instagram non sono stati caricati correttamente da GitHub.")
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
        subprocess.run(['ffmpeg', '-i', raw_path, '-vf', 'scale=-2:720', '-vcodec', 'libx264', '-crf', '32', '-preset', 'ultrafast', '-acodec', 'aac', '-y', out_name])
        
        video_url = f"https://raw.githubusercontent.com{REPO}/main/{out_name}"
        target_url = f"https://graph.facebook.com{IG_ID}/media"
        
        try:
            r = requests.post(target_url, data={
                'media_type': 'REELS', 'video_url': video_url, 
                'caption': 'Catania Latin Lovers 🌋', 'access_token': IG_TOKEN
            }).json()
            
            if 'id' in r:
                print(f"✅ OK! Attesa 90s...")
                time.sleep(90)
                requests.post(f"https://graph.facebook.com{IG_ID}/media_publish", data={'creation_id': r['id'], 'access_token': IG_TOKEN})
                with open('pubblicati.txt', 'a') as f: f.write(f"{video_m.id}\n")
                print("🔥 PUBBLICATO")
            else:
                print(f"❌ Errore Instagram: {r}")
        except Exception as e:
            print(f"❌ Errore critico: {e}")
        
        if os.path.exists(raw_path): os.remove(raw_path)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
