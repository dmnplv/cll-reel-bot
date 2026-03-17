import os, requests, time, asyncio, subprocess
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Pulizia dei Secret
def c(v): return str(v or "").strip().replace('*', '').replace(' ', '')

API_ID = int(c(os.getenv('TG_API_ID')) or 0)
API_HASH = c(os.getenv('TG_API_HASH'))
SESSION_STR = c(os.getenv('TG_SESSION'))
IG_ID = c(os.getenv('IG_BUSINESS_ID'))
IG_TOKEN = c(os.getenv('IG_PAGE_TOKEN'))
REPO = os.getenv('GITHUB_REPOSITORY') 
CHANNELS = ['phorig'] 

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    # 0. Carica database ID
    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: 
        gia_postati = [line.strip() for line in f.read().splitlines() if line.strip()]

    # 1. PUBBLICAZIONE (Video preparato nell'ora precedente)
    if os.path.exists('ready.mp4'):
        video_url = f"https://raw.githubusercontent.com/{REPO}/main/ready.mp4"
        print(f"🚀 Pubblicazione Reel HQ: {video_url}")
        
        target_url = f"https://graph.facebook.com/{IG_ID}/media"
        r = requests.post(target_url, data={
            'media_type': 'REELS', 'video_url': video_url, 
            'caption': 'Catania Latin Lovers 🌋 #bachata #salsa', 'access_token': IG_TOKEN
        }).json()
        
        if 'id' in r:
            print(f"✅ Container OK: {r['id']}. Elaborazione (90s)...")
            time.sleep(90)
            requests.post(f"https://graph.facebook.com/{IG_ID}/media_publish", 
                          data={'creation_id': r['id'], 'access_token': IG_TOKEN})
            os.remove('ready.mp4')
            print("🔥 REEL PUBBLICATO!")
        else:
            print(f"Instagram non pronto o errore: {r}")

    # 2. PREPARAZIONE (Scarica il prossimo nuovo video)
    video_m = None
    for ch in CHANNELS:
        async for m in client.iter_messages(ch, limit=20):
            msg_id = str(m.id).strip()
            if m.video and msg_id not in gia_postati:
                print(f"🎬 Trovato nuovo video ID: {msg_id}. Compressione 1080p...")
                raw_path = await m.download_media()
                
                # Compressione Alta Qualità (CRF 22)
                subprocess.run(['ffmpeg', '-i', raw_path, '-vf', 'scale=-2:1080', '-vcodec', 'libx264', '-crf', '22', '-preset', 'faster', '-acodec', 'aac', '-b:a', '192k', '-y', 'ready.mp4'])
                
                # Aggiorna database (ultimi 100 ID)
                gia_postati.append(msg_id)
                with open('pubblicati.txt', 'w') as f:
                    f.write("\n".join(gia_postati[-100:]))
                
                if os.path.exists(raw_path): os.remove(raw_path)
                print(f"✅ Video {msg_id} pronto nel repo.")
                video_m = m
                break
        if video_m: break

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
