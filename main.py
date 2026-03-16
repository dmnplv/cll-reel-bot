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
        print(f"Compressione in corso: {path}...")
        
        # Comprime il video per renderlo compatibile e leggero
        subprocess.run(['ffmpeg', '-i', path, '-vcodec', 'libx264', '-crf', '28', '-preset', 'faster', '-acodec', 'aac', '-y', out])
        
        with open(out, 'rb') as f:
            r = requests.post('https://catbox.moe', data={'reqtype': 'fileupload'}, files={'file': f})
            url = r.text.strip()

        if "https" in url:
            print(f"URL pronto: {url}. Invio a Instagram...")
            post = requests.post(f"https://graph.facebook.com{IG_ID}/media", data={
                'media_type': 'REELS', 'video_url': url, 'access_token': IG_TOKEN, 'caption': 'Catania Latin Lovers 🌋'
            }).json()
            
            c_id = post.get('id')
            if c_id:
                time.sleep(60)
                requests.post(f"https://graph.facebook.com{IG_ID}/media_publish", data={'creation_id': c_id, 'access_token': IG_TOKEN})
                with open('pubblicati.txt', 'a') as f: f.write(f"{video_m.id}\n")
                print("✅ PUBBLICATO")
            else: print(f"Errore IG: {post}")
        
        for f_del in [path, out]:
            if os.path.exists(f_del): os.remove(f_del)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
