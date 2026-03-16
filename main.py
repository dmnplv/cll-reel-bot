import os, requests, time, asyncio, subprocess
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Pulizia automatica delle variabili (rimuove eventuali spazi o asterischi)
def clean(val): return str(val).strip().replace('*', '')

API_ID = int(clean(os.getenv('TG_API_ID')))
API_HASH = clean(os.getenv('TG_API_HASH'))
SESSION_STR = clean(os.getenv('TG_SESSION'))
IG_ID = clean(os.getenv('IG_BUSINESS_ID'))
IG_TOKEN = clean(os.getenv('IG_PAGE_TOKEN'))
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
        print(f"Compressione in corso (720p)...")
        
        # Forza il video a 720p e qualità CRF 30 (ottimo compromesso peso/qualità)
        subprocess.run(['ffmpeg', '-i', path, '-vf', 'scale=-2:720', '-vcodec', 'libx264', '-crf', '30', '-preset', 'ultrafast', '-acodec', 'aac', '-y', out])
        
        print(f"Caricamento su Catbox...")
        with open(out, 'rb') as f:
            r = requests.post('https://catbox.moe', data={'reqtype': 'fileupload'}, files={'file': f})
            url = r.text.strip()

        if url.startswith("https"):
            print(f"URL pronto: {url}. Invio a Instagram...")
            # Costruiamo l'URL in modo ultra-sicuro
            base_url = "https://graph.facebook.com" + IG_ID + "/media"
            payload = {
                'media_type': 'REELS',
                'video_url': url,
                'caption': 'Catania Latin Lovers 🌋',
                'access_token': IG_TOKEN
            }
            post = requests.post(base_url, data=payload).json()
            
            c_id = post.get('id')
            if c_id:
                print(f"Elaborazione IG (ID: {c_id}). Attesa 60s...")
                time.sleep(60)
                pub_url = "https://graph.facebook.com" + IG_ID + "/media_publish"
                requests.post(pub_url, data={'creation_id': c_id, 'access_token': IG_TOKEN})
                with open('pubblicati.txt', 'a') as f: f.write(f"{video_m.id}\n")
                print("✅ REEL PUBBLICATO")
            else: 
                print(f"Errore Instagram: {post}")
        else:
            print(f"Errore Hosting (File ancora troppo grande?): {url[:100]}")
        
        for f_del in [path, out]:
            if os.path.exists(f_del): os.remove(f_del)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
