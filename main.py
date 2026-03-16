import os, requests, time, asyncio, subprocess
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Pulizia estrema per rimuovere residui di GitHub (asterischi, spazi)
def c(v): return str(v).strip().replace('*', '')

API_ID = int(c(os.getenv('TG_API_ID')))
API_HASH = c(os.getenv('TG_API_HASH'))
SESSION_STR = c(os.getenv('TG_SESSION'))
IG_ID = c(os.getenv('IG_BUSINESS_ID'))
IG_TOKEN = c(os.getenv('IG_PAGE_TOKEN'))
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
        print(f"Compressione 720p in corso...")
        subprocess.run(['ffmpeg', '-i', path, '-vf', 'scale=-2:720', '-vcodec', 'libx264', '-crf', '30', '-preset', 'ultrafast', '-acodec', 'aac', '-y', out])
        
        print(f"Caricamento su TmpFiles...")
        video_url = None
        try:
            with open(out, 'rb') as f:
                r = requests.post('https://tmpfiles.org', files={'file': f}).json()
                # Trasformiamo l'URL in link diretto scaricabile
                video_url = r['data']['url'].replace('https://tmpfiles.org', 'https://tmpfiles.orgdl/')
                print(f"URL pronto: {video_url}")
        except Exception as e:
            print(f"Errore Hosting: {e}")

        if video_url and "https" in video_url:
            print(f"Invio a Instagram...")
            base_url = f"https://graph.facebook.com{IG_ID}/media"
            payload = {'media_type': 'REELS', 'video_url': video_url, 'caption': 'Catania Latin Lovers 🌋', 'access_token': IG_TOKEN}
            post = requests.post(base_url, data=payload).json()
            
            c_id = post.get('id')
            if c_id:
                print(f"Elaborazione IG (ID: {c_id})...")
                time.sleep(60)
                requests.post(f"https://graph.facebook.com{IG_ID}/media_publish", data={'creation_id': c_id, 'access_token': IG_TOKEN})
                with open('pubblicati.txt', 'a') as f: f.write(f"{video_m.id}\n")
                print("✅ REEL PUBBLICATO")
            else:
                print(f"Errore Instagram: {post}")
        
        for f_del in [path, out]:
            if os.path.exists(f_del): os.remove(f_del)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
