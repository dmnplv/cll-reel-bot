import os
import requests
import time
from telethon.sync import TelegramClient

# Caricamento credenziali dai Secrets di GitHub
api_id = int(os.getenv('TG_API_ID'))
api_hash = os.getenv('TG_API_HASH')
ig_id = os.getenv('IG_BUSINESS_ID')
ig_token = os.getenv('IG_PAGE_TOKEN')
source_channel = 'phorig' # Il canale del videomaker

client = TelegramClient('session', api_id, api_hash)

async def main():
    async for message in client.iter_messages(source_channel, limit=1):
        if message.video:
            print("Video trovato! Scaricamento...")
            path = await message.download_media()
            
            # Caricamento su un hosting temporaneo (file.io) per dare un URL a Instagram
            with open(path, 'rb') as f:
                response = requests.post('https://file.io', files={'file': f})
                video_url = response.json()['link']
            
            # 1. Creazione del Reel Container su Instagram
            post_url = f"https://graph.facebook.com{ig_id}/media"
            payload = {
                'media_type': 'REELS',
                'video_url': video_url,
                'caption': message.text or "Nuovo Reel! #bachata #salsa",
                'access_token': ig_token
            }
            r = requests.post(post_url, data=payload)
            creation_id = r.json().get('id')
            
            if creation_id:
                print("Elaborazione video in corso su Instagram...")
                time.sleep(30) # Attendiamo che Instagram elabori il video
                
                # 2. Pubblicazione finale del Reel
                publish_url = f"https://graph.facebook.com{ig_id}/media_publish"
                requests.post(publish_url, data={'creation_id': creation_id, 'access_token': ig_token})
                print("Reel pubblicato con successo!")
            else:
                print(f"Errore Instagram: {r.text}")
            
            os.remove(path) # Pulizia file locale

with client:
    client.loop.run_until_complete(main())
