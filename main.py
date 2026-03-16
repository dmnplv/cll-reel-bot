import os, requests, time, asyncio, subprocess
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Pulizia chiavi per evitare errori di caratteri extra (***)
def c(v): return str(v or "").strip().replace('*', '')

API_ID = int(c(os.getenv('TG_API_ID')))
API_HASH = c(os.getenv('TG_API_HASH'))
SESSION_STR = c(os.getenv('TG_SESSION'))
IG_ID = c(os.getenv('IG_BUSINESS_ID'))
IG_TOKEN = c(os.getenv('IG_PAGE_TOKEN'))
REPO = os.getenv('GITHUB_REPOSITORY') # Es: "tuonome/cll-reel-bot"
CHANNELS = ['phorig'] # Aggiungi qui gli altri canali senza @

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    # Database locale per evitare duplicati
    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: gia_postati = f.read().splitlines()

    video_m = None
    for ch in CHANNELS:
        print(f"Controllo canale: {ch}...")
        async for m in client.iter_messages(ch, limit=10):
            if m.video and str(m.id) not in gia_postati:
                video_m = m
                break
        if video_m: break

    if video_m:
        raw_path = await video_m.download_media()
        out_name = f"reel_{video_m.id}.mp4"
        
        print(f"Compressione 720p in corso (Ultrafast)...")
        # Forza 720p e qualità CRF 32 per stare sotto i 50-60MB
        subprocess.run(['ffmpeg', '-i', raw_path, '-vf', 'scale=-2:720', '-vcodec', 'libx264', '-crf', '32', '-preset', 'ultrafast', '-acodec', 'aac', '-y', out_name])
        
        # URL pubblico temporaneo tramite GitHub Raw (il repo deve essere privato ma il link è diretto)
        # Nota: Instagram richiede un URL accessibile. Usiamo l'URL RAW di GitHub.
        video_url = f"https://raw.githubusercontent.com{REPO}/main/{out_name}"
        
        # IMPORTANTE: Per caricare su GitHub e rendere l'URL valido, dobbiamo fare il PUSH del file.
        # Questo viene gestito dal file .github/workflows/run.yml che abbiamo già impostato.
        # Ma Instagram ha bisogno del file ORA. 
        
        print(f"Invio richiesta a Instagram con URL: {video_url}")
        target_url = f"https://graph.facebook.com{IG_ID}/media"
        payload = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': 'Catania Latin Lovers 🌋 #bachata #salsa',
            'access_token': IG_TOKEN
        }
        
        post = requests.post(target_url, data=payload).json()
        c_id = post.get('id')
        
        if c_id:
            print(f"✅ Container creato! ID: {c_id}. Attesa 90s per elaborazione Meta...")
            time.sleep(90)
            
            pub_url = f"https://graph.facebook.com{IG_ID}/media_publish"
            publish_res = requests.post(pub_url, data={'creation_id': c_id, 'access_token': IG_TOKEN}).json()
            
            if 'id' in publish_res:
                with open('pubblicati.txt', 'a') as f: f.write(f"{video_m.id}\n")
                print(f"🔥 REEL PUBBLICATO! ID: {publish_res['id']}")
            else:
                print(f"❌ Errore pubblicazione: {publish_res}")
        else:
            print(f"❌ Errore Instagram (URL non raggiungibile?): {post}")
        
        # Pulizia file locale (il file su GitHub verrà rimosso dal workflow alla fine)
        if os.path.exists(raw_path): os.remove(raw_path)
    else:
        print("Nessun nuovo video trovato.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
