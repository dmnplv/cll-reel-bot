import os, requests, time, asyncio, subprocess
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
SESSION_STR = os.getenv('TG_SESSION')
IG_ID = os.getenv('IG_BUSINESS_ID')
IG_TOKEN = os.getenv('IG_PAGE_TOKEN')
CHANNELS = ['phorig']

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: gia_postati = f.read().splitlines()

    video_m = None
    for ch in CHANNELS:
        async for m in client.iter_messages(ch, limit=10):
            if m.video and str(m.id) not in gia_postati:
                video_m = m
                break
        if video_m: break

    if video_m:
        path = await video_m.download_media()
        out = "ready.mp4"
        print(f"Compressione aggressiva in corso...")
        
        # Forza 720p e qualità CRF 35 (file molto piccolo, perfetto per Instagram)
        cmd = [
            'ffmpeg', '-i', path, 
            '-vf', 'scale=-2:720', 
            '-vcodec', 'libx264', '-crf', '35', '-preset', 'ultrafast', 
            '-acodec', 'aac', '-ar', '44100', '-y', out
        ]
        subprocess.run(cmd)
        
        print(f"Caricamento su Catbox...")
        with open(out, 'rb') as f:
            r = requests.post('https://catbox.moe', data={'reqtype': 'fileupload'}, files={'file': f})
            url = r.text.strip()

        if url.startswith("https"):
            print(f"URL pronto: {url}. Invio a Instagram...")
            # URL pulito senza variabili esterne che possono contenere asterischi
            target_url = "https://graph.facebook.com" + str(IG_ID) + "/media"
            payload = {
                'media_type': 'REELS',
                'video_url': url,
                'caption': 'Catania Latin Lovers 🌋',
                'access_token': IG_TOKEN
            }
            post = requests.post(target_url, data=payload).json()
            
            c_id = post.get('id')
            if c_id:
                print(f"Elaborazione IG (ID: {c_id}). Attesa 60s...")
                time.sleep(60)
                pub_url = "https://graph.facebook.com" + str(IG_ID) + "/media_publish"
                requests.post(pub_url, data={'creation_id': c_id, 'access_token': IG_TOKEN})
                with open('pubblicati.txt', 'a') as f: f.write(f"{video_m.id}\n")
                print("✅ REEL PUBBLICATO")
            else: 
                print(f"Errore Instagram: {post}")
        else:
            print("Errore Hosting: Il file è ancora troppo grande (>200MB) dopo la compressione.")
        
        for f_del in [path, out]:
            if os.path.exists(f_del): os.remove(f_del)
    else:
        print("Nessun nuovo video trovato.")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
