import os, requests, time, asyncio, subprocess
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

def c(v): return str(v or "").strip().replace('*', '').replace(' ', '')

API_ID = int(c(os.getenv('TG_API_ID')) or 0)
API_HASH = c(os.getenv('TG_API_HASH'))
SESSION_STR = c(os.getenv('TG_SESSION'))
IG_ID = c(os.getenv('IG_BUSINESS_ID'))
IG_TOKEN = c(os.getenv('IG_PAGE_TOKEN'))
REPO = os.getenv('GITHUB_REPOSITORY') 

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: gia_postati = f.read().splitlines()

    # 1. TENTA DI PUBBLICARE IL VIDEO DELL'ORA PRECEDENTE (se esiste)
    if os.path.exists('ready.mp4'):
        video_url = f"https://raw.githubusercontent.com/{REPO}/main/ready.mp4"
        print(f"🚀 Tentativo pubblicazione video caricato: {video_url}")
        
        target_url = f"https://graph.facebook.com/{IG_ID}/media"
        r = requests.post(target_url, data={
            'media_type': 'REELS', 'video_url': video_url, 
            'caption': 'Catania Latin Lovers 🌋 #bachata #salsa', 'access_token': IG_TOKEN
        }).json()
        
        if 'id' in r:
            print(f"✅ Container OK. Attesa 90s...")
            time.sleep(90)
            requests.post(f"https://graph.facebook.com/{IG_ID}/media_publish", 
                          data={'creation_id': r['id'], 'access_token': IG_TOKEN})
            os.remove('ready.mp4')
            print("🔥 REEL PUBBLICATO!")
        else:
            print(f"Instagram non vede ancora il file (normale se è il primo run): {r}")

    # 2. SCARICA E PREPARA IL PROSSIMO VIDEO
    async for m in client.iter_messages('phorig', limit=10):
        if m.video and str(m.id) not in gia_postati:
            print(f"🎬 Preparazione nuovo video (ID: {m.id})...")
            raw_path = await m.download_media()
            # Compressione
            subprocess.run(['ffmpeg', '-i', raw_path, '-vf', 'scale=-2:720', '-vcodec', 'libx264', '-crf', '32', '-preset', 'ultrafast', '-acodec', 'aac', '-y', 'ready.mp4'])
            with open('pubblicati.txt', 'a') as f: f.write(f"{m.id}\n")
            if os.path.exists(raw_path): os.remove(raw_path)
            print("✅ Prossimo video pronto nel repo.")
            break

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
