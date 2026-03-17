import os, requests, time, asyncio, subprocess
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# PULIZIA TOTALE: Rimuove qualsiasi carattere non numerico o non alfanumerico dai Secret
def clean_id(v): return "".join(filter(str.isdigit, str(v)))
def clean_str(v): return str(v).strip().replace('*', '').replace(' ', '')

API_ID = int(clean_id(os.getenv('TG_API_ID')))
API_HASH = clean_str(os.getenv('TG_API_HASH'))
SESSION_STR = clean_str(os.getenv('TG_SESSION'))
IG_ID = clean_id(os.getenv('IG_BUSINESS_ID'))
IG_TOKEN = clean_str(os.getenv('IG_PAGE_TOKEN'))
REPO = os.getenv('GITHUB_REPOSITORY') 
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
        raw_path = await video_m.download_media()
        out_name = "ready.mp4"
        
        print(f"Compressione in corso...")
        subprocess.run(['ffmpeg', '-i', raw_path, '-vf', 'scale=-2:720', '-vcodec', 'libx264', '-crf', '32', '-preset', 'ultrafast', '-acodec', 'aac', '-y', out_name])
        
        # URL corretto con lo slash mancante
        video_url = f"https://raw.githubusercontent.com{REPO}/main/{out_name}"
        
        print(f"Invio a Instagram. ID: {IG_ID}")
        # URL costruito senza variabili che contengono asterischi
        target_url = f"https://graph.facebook.com{IG_ID}/media"
        
        payload = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': 'Catania Latin Lovers 🌋',
            'access_token': IG_TOKEN
        }
        
        try:
            post = requests.post(target_url, data=payload).json()
            c_id = post.get('id')
            
            if c_id:
                print(f"✅ Container creato: {c_id}. Attesa 90s...")
                time.sleep(90)
                pub_url = f"https://graph.facebook.com{IG_ID}/media_publish"
                requests.post(pub_url, data={'creation_id': c_id, 'access_token': IG_TOKEN})
                with open('pubblicati.txt', 'a') as f: f.write(f"{video_m.id}\n")
                print("🔥 REEL PUBBLICATO!")
            else:
                print(f"❌ Errore Instagram: {post}")
        except Exception as e:
            print(f"❌ Errore di connessione: {e}")
        
        if os.path.exists(raw_path): os.remove(raw_path)
    else:
        print("Nessun nuovo video.")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
