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

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: gia_postati = f.read().splitlines()

    # STEP 1: PUBBLICAZIONE (Se esiste un video già caricato nel repo)
    if os.path.exists('ready.mp4'):
        # URL Raw di GitHub (funziona solo se il repo è PUBLIC)
        video_url = f"https://raw.githubusercontent.com{REPO}/main/ready.mp4"
        print(f"🚀 Tentativo di pubblicazione su Instagram: {video_url}")
        
        target_url = f"https://graph.facebook.com/{IG_ID}/media"
        payload = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': 'Catania Latin Lovers 🌋 #bachata #salsa',
            'access_token': IG_TOKEN
        }
        
        r = requests.post(target_url, data=payload).json()
        c_id = r.get('id')
        
        if c_id:
            print(f"✅ Container creato: {c_id}. Attesa 90s per elaborazione...")
            time.sleep(90)
            pub_url = f"https://graph.facebook.com/{IG_ID}/media_publish"
            requests.post(pub_url, data={'creation_id': c_id, 'access_token': IG_TOKEN})
            # Rimuoviamo il video locale; verrà rimosso dal repo al prossimo push
            os.remove('ready.mp4')
            print("🔥 REEL PUBBLICATO CON SUCCESSO!")
        else:
            print(f"Instagram non può ancora scaricare il file (attesa push) o errore: {r}")

    # STEP 2: PREPARAZIONE (Scarica il prossimo video per l'ora successiva)
    video_m = None
    async for m in client.iter_messages('phorig', limit=10):
        if m.video and str(m.id) not in gia_postati:
            video_m = m
            break

    if video_m and not os.path.exists('ready.mp4'):
        print(f"Preparazione video (ID Telegram: {video_m.id})...")
        raw_path = await video_m.download_media()
        
        # Compressione per garantire compatibilità e leggerezza (sotto i 100MB)
        subprocess.run([
            'ffmpeg', '-i', raw_path, 
            '-vf', 'scale=-2:720', 
            '-vcodec', 'libx264', '-crf', '32', '-preset', 'ultrafast', 
            '-acodec', 'aac', '-y', 'ready.mp4'
        ])
        
        # Segna come "in coda" per non scaricarlo di nuovo
        with open('pubblicati.txt', 'a') as f: f.write(f"{video_m.id}\n")
        
        if os.path.exists(raw_path): os.remove(raw_path)
        print("✅ Video pronto nel repository per il prossimo invio.")
    else:
        print("Nessun nuovo video da preparare o coda piena.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
