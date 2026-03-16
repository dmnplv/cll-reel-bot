import os
import requests
import time
from telethon.sync import TelegramClient

# Credenziali
api_id = int(os.getenv('TG_API_ID'))
api_hash = os.getenv('TG_API_HASH')
ig_id = os.getenv('IG_BUSINESS_ID')
ig_token = os.getenv('IG_PAGE_TOKEN')
channels = ['phorig', 'ALTRO_CANALE'] # Aggiungi qui gli altri username

client = TelegramClient('session', api_id, api_hash)

async def main():
    # Carica ID già pubblicati per non duplicare
    if not os.path.exists('pubblicati.txt'): open('pubblicati.txt', 'w').close()
    with open('pubblicati.txt', 'r') as f: gia_postati = f.read().splitlines()

    video_da_postare = None
    
    for channel in channels:
        async for message in client.iter_messages(channel, limit=20):
            # Filtro: deve essere un video e non deve essere già stato postato
            if message.video and str(message.id) not in gia_postati:
                video_da_postare = message
                break # Ne prendiamo solo uno per volta (pianificazione lenta)
        if video_da_postare: break

    if video_da_postare:
        print(f"Nuovo video trovato (ID: {video_da_postare.id}). Scaricamento...")
        path = await video_da_postare.download_media()
        
        # Hosting temporaneo
        with open(path, 'rb') as f:
            video_url = requests.post('https://file.io', files={'file': f}).json()['link']
        
        # Instagram Post
        post_url = f"https://graph.facebook.com{ig_id}/media"
        payload = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': "Catania Latin Lovers 🌋 #bachata #salsa",
            'access_token': ig_token
        }
        r = requests.post(post_url, data=payload)
        creation_id = r.json().get('id')
        
        if creation_id:
            time.sleep(40) # Attesa elaborazione
            requests.post(f"https://graph.facebook.com{ig_id}/media_publish", 
                          data={'creation_id': creation_id, 'access_token': ig_token})
            
            # Salva l'ID per non ripostarlo
            with open('pubblicati.txt', 'a') as f: f.write(f"{video_da_postare.id}\n")
            print("Reel inviato!")
        
        os.remove(path)

with client:
    client.loop.run_until_complete(main())
