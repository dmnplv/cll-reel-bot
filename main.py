import os
import requests
import time
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Caricamento credenziali dai Secrets
api_id = int(os.getenv('TG_API_ID'))
api_hash = os.getenv('TG_API_HASH')
session_str = os.getenv('TG_SESSION')
ig_id = os.getenv('IG_BUSINESS_ID')
ig_token = os.getenv('IG_PAGE_TOKEN')

# Lista canali (aggiungi qui gli altri link pubblici dopo 'phorig')
channels = ['phorig'] 

client = TelegramClient(StringSession(session_str), api_id, api_hash)

async def main():
    # Gestione memoria per non duplicare i post
    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: gia_postati = f.read().splitlines()

    video_da_postare = None
    for channel in channels:
        async for message in client.iter_messages(channel, limit=20):
            # Filtro: solo video, non ancora postati
            if message.video and str(message.id) not in gia_postati:
                video_da_postare = message
                break
        if video_da_postare: break

    if video_da_postare:
        print(f"Video trovato! ID: {video_da_postare.id}")
        path = await video_da_postare.download_media()
        
        # Hosting temporaneo (necessario per Instagram)
        with open(path, 'rb') as f:
            r_file = requests.post('https://file.io', files={'file': f}).json()
            video_url = r_file.get('link')

        if video_url:
            # 1. Crea il Reel
            post_url = f"https://graph.facebook.com{ig_id}/media"
            payload = {
                'media_type': 'REELS',
                'video_url': video_url,
                'caption': "Catania Latin Lovers 🌋 #bachata #salsa",
                'access_token': ig_token
            }
            r = requests.post(post_url, data=payload).json()
            creation_id = r.get('id')
            
            if creation_id:
                print("Elaborazione su Instagram...")
                time.sleep(60) # Aspettiamo 1 minuto per i file pesanti
                # 2. Pubblica
                requests.post(f"https://graph.facebook.com{ig_id}/media_publish", 
                              data={'creation_id': creation_id, 'access_token': ig_token})
                
                with open('pubblicati.txt', 'a') as f: f.write(f"{video_da_postare.id}\n")
                print("✅ Reel pubblicato!")
        
        if os.path.exists(path): os.remove(path)

with client:
    client.loop.run_until_complete(main())
