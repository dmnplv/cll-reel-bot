import os
import requests
import time
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# Caricamento credenziali dai Secrets di GitHub
API_ID = int(os.getenv('TG_API_ID'))
API_HASH = os.getenv('TG_API_HASH')
SESSION_STR = os.getenv('TG_SESSION')
IG_ID = os.getenv('IG_BUSINESS_ID')
IG_TOKEN = os.getenv('IG_PAGE_TOKEN')

# Lista canali da monitorare
CHANNELS = ['phorig'] 

async def main():
    client = TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    await client.connect()

    # Gestione memoria per non duplicare i post
    if not os.path.exists('pubblicati.txt'): 
        with open('pubblicati.txt', 'w') as f: f.write("")
    
    with open('pubblicati.txt', 'r') as f: 
        gia_postati = f.read().splitlines()

    video_da_postare = None
    for channel in CHANNELS:
        print(f"Controllo canale: {channel}...")
        async for message in client.iter_messages(channel, limit=15):
            # Filtro: solo video e non ancora postati
            if message.video and str(message.id) not in gia_postati:
                video_da_postare = message
                break
        if video_da_postare: break

    if video_da_postare:
        print(f"Nuovo video trovato (ID Telegram: {video_da_postare.id}). Scaricamento...")
        path = await video_da_postare.download_media()
        print(f"Download completato: {path}")
        
        # 1. Hosting temporaneo su tmpfiles.org
        video_url = None
        try:
            with open(path, 'rb') as f:
                r_file = requests.post('https://tmpfiles.org', files={'file': f})
                # Trasformiamo il link in "direct download" per Instagram
                video_url = r_file.json()['data']['url'].replace('https://tmpfiles.org', 'https://tmpfiles.orgdl/')
                print(f"URL Video pronto per Instagram: {video_url}")
        except Exception as e:
            print(f"Errore caricamento su hosting: {e}")

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
                print(f"Video inviato a Instagram (ID: {creation_id}). Elaborazione in corso...")
                # Aspettiamo che Instagram elabori il video (fondamentale per i .mov)
                time.sleep(90) 
                
                # 3. Pubblicazione finale
                publish_url = f"https://graph.facebook.com{IG_ID}/media_publish"
                pub_res = requests.post(publish_url, data={'creation_id': creation_id, 'access_token': IG_TOKEN}).json()
                
                if 'id' in pub_res:
                    # Segna come pubblicato solo se Instagram conferma il successo
                    with open('pubblicati.txt', 'a') as f: f.write(f"{video_da_postare.id}\n")
                    print("✅ REEL PUBBLICATO CON SUCCESSO!")
                else:
                    print(f"❌ Errore pubblicazione finale: {pub_res}")
            else:
                print(f"❌ Errore creazione container Instagram: {r}")
        
        # Pulizia file locale per non occupare spazio sul server GitHub
        if os.path.exists(path): os.remove(path)
    else:
        print("Nessun nuovo video trovato nei canali selezionati.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
