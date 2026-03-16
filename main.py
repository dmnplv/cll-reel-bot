import os
import requests
import time
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# Credenziali dai Secrets di GitHub
API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
SESSION_STR = os.getenv('TG_SESSION')
IG_ID = os.getenv('IG_BUSINESS_ID')
IG_TOKEN = os.getenv('IG_PAGE_TOKEN')

# Lista canali (aggiungi qui gli altri username senza @)
CHANNELS = ['phorig'] 

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    # Database locale per evitare duplicati
    if not os.path.exists('pubblicati.txt'): 
        open('pubblicati.txt', 'w').close()
    
    with open('pubblicati.txt', 'r') as f: 
        gia_postati = f.read().splitlines()

    video_da_postare = None
    for channel in CHANNELS:
        print(f"Controllo canale: {channel}...")
        async for message in client.iter_messages(channel, limit=15):
            if message.video and str(message.id) not in gia_postati:
                video_da_postare = message
                break
        if video_da_postare: break

    if video_da_postare:
        print(f"Video trovato (ID: {video_da_postare.id}). Download...")
        path = await video_da_postare.download_media()
        print(f"File scaricato: {path}")
        
        # 1. Hosting temporaneo su Catbox.moe
        video_url = None
        try:
            with open(path, 'rb') as f:
                # Catbox è molto più veloce e stabile per i file video
                r = requests.post('https://catbox.moe', 
                                  data={'reqtype': 'fileupload'}, 
                                  files={'file': f})
                video_url = r.text.strip()
                if "https" in video_url:
                    print(f"URL Video pronto: {video_url}")
                else:
                    print(f"Errore Catbox: {video_url}")
                    video_url = None
        except Exception as e:
            print(f"Errore durante l'upload: {e}")

        if video_url:
            # 2. Creazione Reel Container su Instagram
            post_url = f"https://graph.facebook.com{IG_ID}/media"
            payload = {
                'media_type': 'REELS',
                'video_url': video_url,
                'caption': "Catania Latin Lovers 🌋 #bachata #salsa",
                'access_token': IG_TOKEN
            }
            r = requests.post(post_url, data=payload).json()
            creation_id = r.get('id')
            
            if creation_id:
                print(f"Elaborazione Instagram (ID: {creation_id}). Attesa 90s...")
                time.sleep(90) 
                
                # 3. Pubblicazione finale
                publish_url = f"https://graph.facebook.com{IG_ID}/media_publish"
                pub_res = requests.post(publish_url, data={'creation_id': creation_id, 'access_token': IG_TOKEN}).json()
                
                if 'id' in pub_res:
                    with open('pubblicati.txt', 'a') as f: f.write(f"{video_da_postare.id}\n")
                    print("✅ REEL PUBBLICATO!")
                else:
                    print(f"❌ Errore pubblicazione: {pub_res}")
            else:
                print(f"❌ Errore Instagram Container: {r}")
        
        if os.path.exists(path): os.remove(path)
    else:
        print("Nessun nuovo video trovato.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
